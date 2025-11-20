"""
距离监测模块
功能：估算用户与屏幕的距离，判断是否过近用眼
- 基于人脸框宽度估算距离
- 基于双眼间距估算距离（更准确）
- 距离过近时触发提醒
"""

import numpy as np
from typing import Tuple, Dict
import time


class DistanceMonitor:
    """距离监测器类"""

    def __init__(
        self,
        warning_distance: float = 50.0,
        warning_duration: float = 30.0,
        known_face_width: float = 14.5,
        focal_length: float = 600.0
    ):
        """
        初始化距离监测器

        Args:
            warning_distance: 警告距离（厘米），小于此距离触发提醒
            warning_duration: 持续时长（秒），持续过近多久后触发提醒
            known_face_width: 平均人脸宽度（厘米），用于距离估算
            focal_length: 摄像头焦距（像素），需要校准
        """
        self.warning_distance = warning_distance
        self.warning_duration = warning_duration
        self.known_face_width = known_face_width
        self.focal_length = focal_length

        # 状态变量
        self.current_distance = 0.0
        self.too_close_start = None
        self.too_close_duration = 0.0
        self.is_too_close = False

        # 距离历史（用于平滑）
        self.distance_history = []
        self.history_max_len = 10

        print("✓ 距离监测器初始化成功")
        print(f"  - 警告距离: {warning_distance} cm")
        print(f"  - 持续时长阈值: {warning_duration} s")
        print(f"  - 人脸宽度: {known_face_width} cm")
        print(f"  - 焦距: {focal_length} px")

    def calculate_distance_by_face_width(
        self,
        face_box_width: int
    ) -> float:
        """
        基于人脸框宽度估算距离

        Args:
            face_box_width: 人脸边界框宽度（像素）

        Returns:
            估算距离（厘米）

        公式：
            distance = (known_face_width × focal_length) / face_box_width
        """
        if face_box_width == 0:
            return 0.0

        distance = (self.known_face_width * self.focal_length) / face_box_width
        return distance

    def calculate_distance_by_eye_distance(
        self,
        left_eye_center: np.ndarray,
        right_eye_center: np.ndarray,
        known_eye_distance: float = 6.3
    ) -> float:
        """
        基于双眼间距估算距离（更准确）

        Args:
            left_eye_center: 左眼中心点坐标 [x, y]
            right_eye_center: 右眼中心点坐标 [x, y]
            known_eye_distance: 平均双眼间距（厘米），默认6.3cm

        Returns:
            估算距离（厘米）
        """
        # 计算双眼像素距离
        eye_distance_pixels = np.linalg.norm(left_eye_center - right_eye_center)

        if eye_distance_pixels == 0:
            return 0.0

        # 使用相似三角形原理估算距离
        distance = (known_eye_distance * self.focal_length) / eye_distance_pixels
        return distance

    @staticmethod
    def get_eye_center(eye_landmarks: np.ndarray) -> np.ndarray:
        """
        计算眼睛中心点

        Args:
            eye_landmarks: 眼部关键点数组

        Returns:
            眼睛中心点坐标 [x, y]
        """
        # 取所有关键点的平均值作为中心
        center = np.mean(eye_landmarks[:, :2], axis=0)
        return center

    def update(
        self,
        face_box_width: int = None,
        left_eye_landmarks: np.ndarray = None,
        right_eye_landmarks: np.ndarray = None,
        timestamp: float = None,
        use_eye_distance: bool = True
    ) -> Dict:
        """
        更新距离监测

        Args:
            face_box_width: 人脸框宽度（像素）
            left_eye_landmarks: 左眼关键点
            right_eye_landmarks: 右眼关键点
            timestamp: 时间戳
            use_eye_distance: 是否优先使用眼距法

        Returns:
            监测结果字典
        """
        if timestamp is None:
            timestamp = time.time()

        # 1. 计算距离
        distance = 0.0

        if use_eye_distance and left_eye_landmarks is not None and right_eye_landmarks is not None:
            # 优先使用眼距法（更准确）
            left_eye_center = self.get_eye_center(left_eye_landmarks)
            right_eye_center = self.get_eye_center(right_eye_landmarks)
            distance = self.calculate_distance_by_eye_distance(left_eye_center, right_eye_center)
        elif face_box_width is not None and face_box_width > 0:
            # 备用：使用人脸框宽度法
            distance = self.calculate_distance_by_face_width(face_box_width)

        # 2. 平滑距离值（使用滑动平均）
        if distance > 0:
            self.distance_history.append(distance)
            if len(self.distance_history) > self.history_max_len:
                self.distance_history.pop(0)

            # 计算平均距离
            self.current_distance = np.mean(self.distance_history)
        else:
            self.current_distance = 0.0

        # 3. 判断是否距离过近
        is_currently_close = self.current_distance > 0 and self.current_distance < self.warning_distance

        # 4. 更新持续时间
        if is_currently_close:
            if self.too_close_start is None:
                # 刚开始距离过近
                self.too_close_start = timestamp
                self.too_close_duration = 0.0
            else:
                # 持续距离过近
                self.too_close_duration = timestamp - self.too_close_start

            # 判断是否需要警告
            if self.too_close_duration >= self.warning_duration:
                self.is_too_close = True
            else:
                self.is_too_close = False
        else:
            # 距离正常
            self.too_close_start = None
            self.too_close_duration = 0.0
            self.is_too_close = False

        return self.get_status()

    def get_status(self) -> Dict:
        """
        获取当前距离状态

        Returns:
            状态字典
        """
        return {
            'current_distance': self.current_distance,
            'warning_distance': self.warning_distance,
            'too_close_duration': self.too_close_duration,
            'is_too_close': self.is_too_close,
            'distance_status': self._get_distance_status()
        }

    def _get_distance_status(self) -> str:
        """获取距离状态描述"""
        if self.current_distance == 0:
            return "Unknown"
        elif self.current_distance < self.warning_distance * 0.7:
            return "Too Close"
        elif self.current_distance < self.warning_distance:
            return "Close"
        elif self.current_distance < self.warning_distance * 1.5:
            return "Normal"
        else:
            return "Far"

    def reset(self):
        """重置状态"""
        self.current_distance = 0.0
        self.too_close_start = None
        self.too_close_duration = 0.0
        self.is_too_close = False
        self.distance_history.clear()
        print("✓ 距离监测器已重置")

    def calibrate_focal_length(
        self,
        measured_distance: float,
        face_box_width: int
    ) -> float:
        """
        校准摄像头焦距

        Args:
            measured_distance: 实际测量距离（厘米）
            face_box_width: 对应的人脸框宽度（像素）

        Returns:
            校准后的焦距值

        使用方法：
        1. 用尺子测量实际距离（如50cm）
        2. 记录此时的人脸框宽度
        3. 调用此方法计算焦距
        4. 更新config.yaml中的focal_length
        """
        focal_length = (measured_distance * face_box_width) / self.known_face_width
        print(f"✓ 焦距校准完成: {focal_length:.1f} px")
        print(f"  - 测量距离: {measured_distance} cm")
        print(f"  - 人脸框宽度: {face_box_width} px")
        print(f"  - 请更新config.yaml中的focal_length为: {focal_length:.1f}")
        return focal_length


def test_distance_monitor():
    """测试距离监测器"""
    print("=== 距离监测器测试 ===\n")

    # 导入必要模块
    import sys
    import os
    import cv2
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from camera.camera_capture import CameraCapture
    from detection.face_detector import FaceDetector, LandmarkIndices

    # 初始化模块
    camera = CameraCapture(resolution=(640, 480))
    if not camera.start():
        return

    detector = FaceDetector()
    monitor = DistanceMonitor(
        warning_distance=50.0,
        warning_duration=5.0,  # 测试时缩短为5秒
        focal_length=600.0
    )

    window_name = "Distance Monitor Test [Press Q to quit, C to calibrate]"
    cv2.namedWindow(window_name)

    print("✓ 系统运行中...")
    print("提示：")
    print("  - 按 'Q' 键退出")
    print("  - 按 'C' 键进行焦距校准（请先用尺子测量距离）")
    print("  - 尝试靠近/远离摄像头观察距离变化\n")

    try:
        while True:
            ret, frame = camera.read()
            if not ret:
                break

            # 检测人脸
            detected, face_landmarks_list = detector.detect(frame)

            if detected and face_landmarks_list:
                face_landmarks = face_landmarks_list[0]
                h, w = frame.shape[:2]

                # 获取关键点
                landmarks_array = detector.get_landmarks_array(face_landmarks, w, h)

                # 获取人脸框
                x_min, y_min, x_max, y_max = detector.get_face_bounding_box(landmarks_array)
                face_box_width = x_max - x_min

                # 提取眼部关键点
                left_eye = landmarks_array[LandmarkIndices.LEFT_EYE]
                right_eye = landmarks_array[LandmarkIndices.RIGHT_EYE]

                # 更新距离监测
                status = monitor.update(
                    face_box_width=face_box_width,
                    left_eye_landmarks=left_eye,
                    right_eye_landmarks=right_eye
                )

                # 绘制人脸框
                box_color = (0, 0, 255) if status['is_too_close'] else (0, 255, 0)
                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), box_color, 2)

                # 显示距离信息
                y_offset = 30
                line_height = 30

                # 当前距离
                distance_color = (0, 0, 255) if status['is_too_close'] else (0, 255, 0)
                distance_text = f"Distance: {status['current_distance']:.1f} cm"
                cv2.putText(frame, distance_text, (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, distance_color, 2)
                y_offset += line_height

                # 距离状态
                status_text = f"Status: {status['distance_status']}"
                cv2.putText(frame, status_text, (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                y_offset += line_height

                # 如果距离过近，显示持续时长
                if status['too_close_duration'] > 0:
                    duration_text = f"Too Close: {status['too_close_duration']:.1f}s"
                    cv2.putText(frame, duration_text, (10, y_offset),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
                    y_offset += line_height

                # 警告
                if status['is_too_close']:
                    warning_text = "! TOO CLOSE WARNING !"
                    text_size = cv2.getTextSize(warning_text, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 3)[0]
                    text_x = (w - text_size[0]) // 2
                    text_y = h - 50

                    # 背景
                    padding = 10
                    cv2.rectangle(frame,
                                 (text_x - padding, text_y - text_size[1] - padding),
                                 (text_x + text_size[0] + padding, text_y + padding),
                                 (0, 0, 255), -1)

                    # 文字
                    cv2.putText(frame, warning_text, (text_x, text_y),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)

            else:
                cv2.putText(frame, "No Face Detected", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # 显示FPS
            cv2.putText(frame, f"FPS: {camera.get_fps():.1f}",
                       (w - 120, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            cv2.imshow(window_name, frame)

            # 按键处理
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q'):
                break
            elif key == ord('c') or key == ord('C'):
                # 焦距校准
                print("\n=== 焦距校准模式 ===")
                measured_dist = float(input("请输入实际测量距离（厘米）: "))
                if detected and face_landmarks_list:
                    focal = monitor.calibrate_focal_length(measured_dist, face_box_width)
                    monitor.focal_length = focal
                else:
                    print("✗ 未检测到人脸，无法校准")

    except KeyboardInterrupt:
        print("\n用户中断")

    finally:
        detector.close()
        camera.release()
        cv2.destroyAllWindows()
        print("测试结束")


if __name__ == "__main__":
    test_distance_monitor()
