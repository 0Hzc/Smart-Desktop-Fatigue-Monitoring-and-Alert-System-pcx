"""
智能桌面疲劳监测系统 - 主程序
功能：系统主入口，整合所有模块
"""

import cv2
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from camera.camera_capture import CameraCapture
from detection.face_detector import FaceDetector, LandmarkIndices
from analysis.fatigue_analyzer import FatigueAnalyzer
from analysis.distance_monitor import DistanceMonitor
from analysis.posture_monitor import PostureMonitor
from utils.config_loader import get_config
from alert.alert_manager import AlertManager, AlertType, AlertLevel
from alert.voice_alert import VoiceAlert
from alert.led_alert import LEDAlert


class FatigueMonitorSystem:
    """疲劳监测系统主类"""

    def __init__(self, config_path: str = "config.yaml"):
        """
        初始化系统

        Args:
            config_path: 配置文件路径
        """
        print("=" * 50)
        print("智能桌面疲劳监测系统")
        print("版本: v1.0")
        print("=" * 50)

        # 加载配置
        self.config = get_config(config_path)

        # 初始化摄像头
        camera_config = self.config.get_camera_config()
        self.camera = CameraCapture(
            camera_id=0,
            resolution=(
                camera_config['resolution']['width'],
                camera_config['resolution']['height']
            ),
            fps=camera_config['fps'],
            flip=camera_config['flip']
        )

        # 初始化人脸检测器
        face_config = self.config.get_face_detection_config()
        self.face_detector = FaceDetector(
            max_num_faces=face_config['max_num_faces'],
            min_detection_confidence=face_config['min_detection_confidence'],
            min_tracking_confidence=face_config['min_tracking_confidence'],
            refine_landmarks=face_config['refine_landmarks']
        )

        # 初始化疲劳分析器
        fatigue_config = self.config.get_fatigue_config()
        self.fatigue_analyzer = FatigueAnalyzer(
            ear_threshold=fatigue_config['ear_threshold'],
            perclos_threshold=fatigue_config['perclos_threshold'],
            perclos_window=fatigue_config['perclos_window'],
            blink_min=fatigue_config['blink_min'],
            blink_max=fatigue_config['blink_max'],
            closed_eye_duration=fatigue_config['closed_eye_duration']
        )

        # 初始化距离监测器
        distance_config = self.config.get_distance_config()
        self.distance_monitor = DistanceMonitor(
            warning_distance=distance_config['warning_distance'],
            warning_duration=distance_config['warning_duration'],
            known_face_width=distance_config['known_face_width'],
            focal_length=distance_config['focal_length']
        )

        # 初始化坐姿监测器
        posture_config = self.config.get_posture_config()
        camera_res = camera_config['resolution']
        self.posture_monitor = PostureMonitor(
            pitch_threshold_down=posture_config['pitch_threshold_down'],
            pitch_threshold_up=posture_config['pitch_threshold_up'],
            warning_duration=posture_config['warning_duration'],
            focal_length=distance_config['focal_length'],
            image_width=camera_res['width'],
            image_height=camera_res['height']
        )

        # 性能配置
        self.perf_config = self.config.get_performance_config()
        self.skip_frames = self.perf_config['skip_frames']
        self.display_fps = self.perf_config['display_fps']

        # 初始化提醒系统
        alert_config = self.config.get_alert_config()
        self.alert_manager = AlertManager(
            enable_voice=alert_config['enable_voice'],
            enable_led=alert_config['enable_led'],
            cooldown_time=alert_config['cooldown_time']
        )

        # 初始化各类提醒器
        if alert_config['enable_voice']:
            voice_alert = VoiceAlert(rate=150, volume=0.9)
            self.alert_manager.set_voice_alert(voice_alert)

        if alert_config['enable_led']:
            led_config = self.config.get_led_config()
            led_alert = LEDAlert(
                pin=led_config['pin'],
                blink_duration=led_config['blink_duration']
            )
            self.alert_manager.set_led_alert(led_alert)

        # 帧计数器
        self.frame_counter = 0

        print("\n✓ 系统初始化完成\n")

    def run(self):
        """运行主循环"""
        print("启动系统...")

        if not self.camera.start():
            print("✗ 摄像头启动失败！")
            return

        window_name = "Fatigue Monitor System [Press Q to quit]"
        cv2.namedWindow(window_name)

        print("✓ 系统运行中... 按 'Q' 键退出\n")

        try:
            while True:
                # 读取视频帧
                ret, frame = self.camera.read()
                if not ret:
                    print("✗ 无法读取视频帧")
                    break

                # 跳帧优化（如果配置了跳帧）
                self.frame_counter += 1
                if self.skip_frames > 0 and self.frame_counter % (self.skip_frames + 1) != 0:
                    continue

                # 创建显示帧的副本
                display_frame = frame.copy()

                # 检测人脸
                detected, face_landmarks_list = self.face_detector.detect(frame)

                if detected and face_landmarks_list:
                    for face_landmarks in face_landmarks_list:
                        h, w = frame.shape[:2]

                        # 获取关键点数组
                        landmarks_array = self.face_detector.get_landmarks_array(
                            face_landmarks, w, h
                        )

                        # 绘制人脸网格
                        display_frame = self.face_detector.draw_landmarks(
                            display_frame,
                            face_landmarks,
                            draw_contours=True
                        )

                        # 高亮显示眼部关键点
                        display_frame = self.face_detector.draw_specific_landmarks(
                            display_frame,
                            landmarks_array,
                            LandmarkIndices.LEFT_EYE,
                            color=(255, 0, 0),
                            radius=3
                        )
                        display_frame = self.face_detector.draw_specific_landmarks(
                            display_frame,
                            landmarks_array,
                            LandmarkIndices.RIGHT_EYE,
                            color=(255, 0, 0),
                            radius=3
                        )

                        # 绘制人脸边界框
                        x_min, y_min, x_max, y_max = self.face_detector.get_face_bounding_box(
                            landmarks_array
                        )
                        cv2.rectangle(
                            display_frame,
                            (x_min, y_min),
                            (x_max, y_max),
                            (0, 255, 0),
                            2
                        )

                        # === 疲劳分析 ===
                        # 提取眼部关键点
                        left_eye = landmarks_array[LandmarkIndices.LEFT_EYE]
                        right_eye = landmarks_array[LandmarkIndices.RIGHT_EYE]

                        # 更新疲劳分析
                        fatigue_status = self.fatigue_analyzer.update(left_eye, right_eye)

                        # === 距离监测 ===
                        distance_status = self.distance_monitor.update(
                            face_box_width=(x_max - x_min),
                            left_eye_landmarks=left_eye,
                            right_eye_landmarks=right_eye
                        )

                        # === 坐姿监测 ===
                        posture_status = self.posture_monitor.update(landmarks_array)

                        # === 提醒触发 ===
                        self._check_and_trigger_alerts(fatigue_status, distance_status, posture_status)

                        # 显示所有分析结果
                        self._draw_analysis_info(
                            display_frame,
                            fatigue_status,
                            distance_status,
                            posture_status
                        )

                else:
                    # 未检测到人脸
                    cv2.putText(
                        display_frame,
                        "No Face Detected",
                        (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2
                    )

                # 显示FPS
                if self.display_fps:
                    fps_text = f"FPS: {self.camera.get_fps():.1f}"
                    cv2.putText(
                        display_frame,
                        fps_text,
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2
                    )

                # 显示帧计数
                cv2.putText(
                    display_frame,
                    f"Frame: {self.frame_counter}",
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )

                # 显示图像
                cv2.imshow(window_name, display_frame)

                # 按键检测
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == ord('Q'):
                    print("\n用户请求退出")
                    break

        except KeyboardInterrupt:
            print("\n\n系统被用户中断")

        except Exception as e:
            print(f"\n✗ 系统错误: {e}")
            import traceback
            traceback.print_exc()

        finally:
            self.cleanup()

    def _draw_analysis_info(self, frame, fatigue_status: dict, distance_status: dict, posture_status: dict):
        """
        在画面上绘制所有分析信息

        Args:
            frame: 视频帧
            fatigue_status: 疲劳状态字典
            distance_status: 距离状态字典
            posture_status: 坐姿状态字典
        """
        h, w = frame.shape[:2]
        y_offset = 90
        line_height = 30

        # 定义疲劳等级颜色
        fatigue_colors = {
            0: (0, 255, 0),      # 绿色 - 正常
            1: (0, 255, 255),    # 黄色 - 轻度
            2: (0, 165, 255),    # 橙色 - 中度
            3: (0, 0, 255)       # 红色 - 重度
        }

        # === 疲劳检测信息 ===
        # 1. EAR值
        ear_color = (0, 255, 0) if not fatigue_status['is_closed'] else (0, 0, 255)
        ear_text = f"EAR: {fatigue_status['avg_ear']:.3f}"
        if fatigue_status['is_closed']:
            ear_text += " (CLOSED)"
        cv2.putText(frame, ear_text, (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, ear_color, 2)
        y_offset += line_height

        # 2. PERCLOS
        perclos_color = (0, 255, 0) if fatigue_status['perclos'] < 0.15 else (0, 165, 255)
        perclos_text = f"PERCLOS: {fatigue_status['perclos_percentage']:.1f}%"
        cv2.putText(frame, perclos_text, (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, perclos_color, 2)
        y_offset += line_height

        # 3. 疲劳状态
        fatigue_level = fatigue_status['fatigue_level']
        fatigue_color = fatigue_colors.get(fatigue_level, (255, 255, 255))
        fatigue_text = f"Fatigue: {fatigue_status['fatigue_description']}"
        cv2.putText(frame, fatigue_text, (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, fatigue_color, 2)
        y_offset += line_height

        # === 距离监测信息 ===
        # 4. 当前距离
        distance_color = (0, 0, 255) if distance_status['is_too_close'] else (0, 255, 0)
        distance_text = f"Distance: {distance_status['current_distance']:.1f} cm"
        cv2.putText(frame, distance_text, (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, distance_color, 2)
        y_offset += line_height

        # === 坐姿监测信息 ===
        # 5. 头部姿态
        pitch_color = (0, 255, 0)
        if posture_status['posture_type'] == "Head Down":
            pitch_color = (0, 0, 255)
        elif posture_status['posture_type'] == "Head Up":
            pitch_color = (0, 165, 255)

        posture_text = f"Posture: {posture_status['posture_type']}"
        cv2.putText(frame, posture_text, (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, pitch_color, 2)
        y_offset += line_height

        # === 警告信息（屏幕中央）===
        warnings = []
        if fatigue_status['is_drowsy']:
            warnings.append("DROWSINESS!")
        if distance_status['is_too_close']:
            warnings.append("TOO CLOSE!")
        if posture_status['is_bad_posture']:
            warnings.append(posture_status['posture_type'].upper() + "!")

        if warnings:
            warning_text = " | ".join(warnings)
            text_size = cv2.getTextSize(warning_text, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 3)[0]
            text_x = (w - text_size[0]) // 2
            text_y = h - 50

            # 绘制背景矩形
            padding = 10
            cv2.rectangle(frame,
                         (text_x - padding, text_y - text_size[1] - padding),
                         (text_x + text_size[0] + padding, text_y + padding),
                         (0, 0, 255), -1)

            # 绘制警告文本
            cv2.putText(frame, warning_text, (text_x, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)

        # === 综合健康指示条（右上角）===
        # 计算综合健康分数 (0-100)
        health_score = 100
        if fatigue_level == 1:
            health_score -= 20
        elif fatigue_level == 2:
            health_score -= 40
        elif fatigue_level == 3:
            health_score -= 60

        if distance_status['is_too_close']:
            health_score -= 20

        if posture_status['is_bad_posture']:
            health_score -= 20

        health_score = max(0, health_score)

        # 绘制健康指示条
        bar_width = 200
        bar_height = 25
        bar_x = w - bar_width - 20
        bar_y = 50

        # 背景
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height),
                     (100, 100, 100), -1)

        # 根据健康分数选择颜色
        if health_score >= 80:
            bar_color = (0, 255, 0)  # 绿色
        elif health_score >= 60:
            bar_color = (0, 255, 255)  # 黄色
        elif health_score >= 40:
            bar_color = (0, 165, 255)  # 橙色
        else:
            bar_color = (0, 0, 255)  # 红色

        # 填充
        fill_width = int(bar_width * (health_score / 100))
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_width, bar_y + bar_height),
                     bar_color, -1)

        # 边框
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height),
                     (255, 255, 255), 2)

        # 显示分数
        score_text = f"{health_score}%"
        cv2.putText(frame, score_text, (bar_x + bar_width // 2 - 30, bar_y + 18),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    def _check_and_trigger_alerts(self, fatigue_status: dict, distance_status: dict, posture_status: dict):
        """
        检查并触发提醒

        Args:
            fatigue_status: 疲劳状态字典
            distance_status: 距离状态字典
            posture_status: 坐姿状态字典
        """
        # 检查严重疲劳（最高优先级）
        if fatigue_status['fatigue_level'] == 3:
            self.alert_manager.trigger_alert(
                AlertType.SEVERE_FATIGUE,
                "Severe fatigue detected! Please rest immediately.",
                AlertLevel.CRITICAL
            )
            return  # 严重疲劳时不再检查其他提醒

        # 检查一般疲劳
        if fatigue_status['fatigue_level'] >= 1:
            fatigue_desc = fatigue_status['fatigue_description']
            self.alert_manager.trigger_alert(
                AlertType.FATIGUE,
                f"{fatigue_desc}. Please take a break to rest.",
                AlertLevel.WARNING
            )

        # 检查距离过近
        if distance_status['is_too_close']:
            self.alert_manager.trigger_alert(
                AlertType.DISTANCE,
                "You are too close to the screen. Please move back.",
                AlertLevel.WARNING
            )

        # 检查坐姿不良
        if posture_status['is_bad_posture']:
            posture_type = posture_status['posture_type']
            self.alert_manager.trigger_alert(
                AlertType.POSTURE,
                f"Poor posture detected: {posture_type}. Please adjust your sitting position.",
                AlertLevel.WARNING
            )

    def cleanup(self):
        """清理资源"""
        print("\n清理资源...")
        self.face_detector.close()
        self.camera.release()
        self.alert_manager.cleanup()
        cv2.destroyAllWindows()
        print("✓ 系统已关闭")


def main():
    """主函数"""
    # 创建并运行系统
    system = FatigueMonitorSystem()
    system.run()


if __name__ == "__main__":
    main()
