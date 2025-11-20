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
from utils.config_loader import get_config


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

        # 性能配置
        self.perf_config = self.config.get_performance_config()
        self.skip_frames = self.perf_config['skip_frames']
        self.display_fps = self.perf_config['display_fps']

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

                        # 显示疲劳分析结果
                        self._draw_fatigue_info(display_frame, fatigue_status)

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

    def _draw_fatigue_info(self, frame, status: dict):
        """
        在画面上绘制疲劳分析信息

        Args:
            frame: 视频帧
            status: 疲劳状态字典
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

        # 1. EAR值
        ear_color = (0, 255, 0) if not status['is_closed'] else (0, 0, 255)
        ear_text = f"EAR: {status['avg_ear']:.3f}"
        if status['is_closed']:
            ear_text += " (CLOSED)"
        cv2.putText(frame, ear_text, (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, ear_color, 2)
        y_offset += line_height

        # 2. 眨眼计数
        blink_text = f"Blinks: {status['blink_counter']}"
        if status['blinks_per_minute'] > 0:
            blink_text += f" ({status['blinks_per_minute']}/min)"
        cv2.putText(frame, blink_text, (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        y_offset += line_height

        # 3. PERCLOS
        perclos_color = (0, 255, 0) if status['perclos'] < 0.15 else (0, 165, 255)
        perclos_text = f"PERCLOS: {status['perclos_percentage']:.1f}%"
        cv2.putText(frame, perclos_text, (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, perclos_color, 2)
        y_offset += line_height

        # 4. 闭眼时长（仅在闭眼时显示）
        if status['eye_closed_duration'] > 0.5:
            closed_color = (0, 0, 255) if status['is_drowsy'] else (0, 165, 255)
            closed_text = f"Closed: {status['eye_closed_duration']:.1f}s"
            cv2.putText(frame, closed_text, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, closed_color, 2)
            y_offset += line_height

        # 5. 疲劳等级（大字显示）
        fatigue_level = status['fatigue_level']
        fatigue_color = fatigue_colors.get(fatigue_level, (255, 255, 255))
        fatigue_text = f"Status: {status['fatigue_description']}"
        cv2.putText(frame, fatigue_text, (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, fatigue_color, 2)

        # 6. 打瞌睡警告（屏幕中央）
        if status['is_drowsy']:
            warning_text = "! DROWSINESS ALERT !"
            text_size = cv2.getTextSize(warning_text, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)[0]
            text_x = (w - text_size[0]) // 2
            text_y = h - 60

            # 绘制背景矩形
            padding = 10
            cv2.rectangle(frame,
                         (text_x - padding, text_y - text_size[1] - padding),
                         (text_x + text_size[0] + padding, text_y + padding),
                         (0, 0, 255), -1)

            # 绘制警告文本
            cv2.putText(frame, warning_text, (text_x, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)

        # 7. 疲劳等级指示条（右上角）
        if fatigue_level > 0:
            bar_width = 200
            bar_height = 20
            bar_x = w - bar_width - 20
            bar_y = 50

            # 背景
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height),
                         (100, 100, 100), -1)

            # 疲劳等级填充
            fill_width = int(bar_width * (fatigue_level / 3))
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_width, bar_y + bar_height),
                         fatigue_color, -1)

            # 边框
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height),
                         (255, 255, 255), 2)

    def cleanup(self):
        """清理资源"""
        print("\n清理资源...")
        self.face_detector.close()
        self.camera.release()
        cv2.destroyAllWindows()
        print("✓ 系统已关闭")


def main():
    """主函数"""
    # 创建并运行系统
    system = FatigueMonitorSystem()
    system.run()


if __name__ == "__main__":
    main()
