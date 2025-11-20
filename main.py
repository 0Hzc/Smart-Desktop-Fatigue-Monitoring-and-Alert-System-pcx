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

                        # 显示状态文本
                        cv2.putText(
                            display_frame,
                            "Face Detected",
                            (10, 90),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 255, 0),
                            2
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
