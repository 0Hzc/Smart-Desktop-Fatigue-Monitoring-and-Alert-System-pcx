"""
坐姿监测模块
功能：基于头部姿态估计判断坐姿是否正确
- 使用PnP算法估计头部姿态
- 计算俯仰角（Pitch）、偏航角（Yaw）、翻滚角（Roll）
- 检测低头、仰头等不良坐姿
"""

import numpy as np
import cv2
import math
from typing import Tuple, Dict
import time


class PostureMonitor:
    """坐姿监测器类"""

    def __init__(
        self,
        pitch_threshold_down: float = 12.0,
        pitch_threshold_up: float = -8.0,
        warning_duration: float = 60.0,
        focal_length: float = 600.0,
        image_width: int = 640,
        image_height: int = 480
    ):
        """
        初始化坐姿监测器

        Args:
            pitch_threshold_down: 低头角度阈值（度），超过此值判定为低头
            pitch_threshold_up: 仰头角度阈值（度），低于此值判定为仰头
            warning_duration: 持续时长（秒），持续不良坐姿多久后触发提醒
            focal_length: 摄像头焦距（像素）
            image_width: 图像宽度
            image_height: 图像高度
        """
        self.pitch_threshold_down = pitch_threshold_down
        self.pitch_threshold_up = pitch_threshold_up
        self.warning_duration = warning_duration

        # 当前姿态角度
        self.pitch = 0.0  # 俯仰角（低头/仰头）
        self.yaw = 0.0    # 偏航角（左转/右转）
        self.roll = 0.0   # 翻滚角（左倾/右倾）

        # 状态变量
        self.bad_posture_start = None
        self.bad_posture_duration = 0.0
        self.is_bad_posture = False
        self.posture_type = "Normal"

        # 3D人脸模型点（标准人脸模型，单位：毫米）
        self.model_points = np.array([
            (0.0, 0.0, 0.0),          # 鼻尖
            (0.0, -330.0, -65.0),     # 下巴
            (-225.0, 170.0, -135.0),  # 左眼角
            (225.0, 170.0, -135.0),   # 右眼角
            (-150.0, -150.0, -125.0), # 左嘴角
            (150.0, -150.0, -125.0)   # 右嘴角
        ], dtype=np.float64)

        # 相机内参矩阵
        self.camera_matrix = np.array([
            [focal_length, 0, image_width / 2],
            [0, focal_length, image_height / 2],
            [0, 0, 1]
        ], dtype=np.float64)

        # 畸变系数（假设无畸变）
        self.dist_coeffs = np.zeros((4, 1))

        print("✓ 坐姿监测器初始化成功")
        print(f"  - 低头阈值: {pitch_threshold_down}°")
        print(f"  - 仰头阈值: {pitch_threshold_up}°")
        print(f"  - 持续时长阈值: {warning_duration} s")

    def estimate_head_pose(
        self,
        landmarks_array: np.ndarray,
        landmark_indices: list = None
    ) -> Tuple[bool, np.ndarray, np.ndarray]:
        """
        估计头部姿态

        Args:
            landmarks_array: 所有关键点数组
            landmark_indices: 用于姿态估计的关键点索引
                              默认：[1, 152, 33, 263, 61, 291]
                              分别对应：鼻尖、下巴、左眼角、右眼角、左嘴角、右嘴角

        Returns:
            (是否成功, 旋转向量, 平移向量)
        """
        # 默认关键点索引
        if landmark_indices is None:
            landmark_indices = [1, 152, 33, 263, 61, 291]

        # 提取2D图像点
        image_points = []
        for idx in landmark_indices:
            if idx < len(landmarks_array):
                point = landmarks_array[idx][:2]  # 只取x, y
                image_points.append(point)
            else:
                return False, None, None

        image_points = np.array(image_points, dtype=np.float64)

        # 使用solvePnP求解姿态
        success, rotation_vector, translation_vector = cv2.solvePnP(
            self.model_points,
            image_points,
            self.camera_matrix,
            self.dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )

        return success, rotation_vector, translation_vector

    def rotation_vector_to_euler_angles(
        self,
        rotation_vector: np.ndarray
    ) -> Tuple[float, float, float]:
        """
        将旋转向量转换为欧拉角

        使用标准的XYZ欧拉角提取方法（Tait-Bryan angles）

        Args:
            rotation_vector: 旋转向量

        Returns:
            (pitch, yaw, roll) 俯仰角、偏航角、翻滚角（度）
            - pitch: 俯仰角，低头为正，仰头为负
            - yaw: 偏航角，左转为负，右转为正
            - roll: 翻滚角，左倾为负，右倾为正
        """
        # 转换为旋转矩阵
        rotation_matrix, _ = cv2.Rodrigues(rotation_vector)

        # 使用标准的XYZ欧拉角提取公式
        # 参考: https://www.gregslabaugh.net/publications/euler.pdf

        # 检查是否接近万向锁 (当R[2,0] 接近 ±1)
        sy = math.sqrt(rotation_matrix[0, 0]**2 + rotation_matrix[1, 0]**2)

        singular = sy < 1e-6

        if not singular:
            # 正常情况 - 使用标准公式
            # Roll (绕X轴) - 头部左右倾斜
            roll = math.atan2(rotation_matrix[2, 1], rotation_matrix[2, 2])

            # Pitch (绕Y轴) - 头部上下点头
            pitch = math.atan2(-rotation_matrix[2, 0], sy)

            # Yaw (绕Z轴) - 头部左右摇头
            yaw = math.atan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
        else:
            # 万向锁情况
            roll = math.atan2(-rotation_matrix[1, 2], rotation_matrix[1, 1])
            pitch = math.atan2(-rotation_matrix[2, 0], sy)
            yaw = 0

        # 转换为度
        pitch_deg = math.degrees(pitch)
        yaw_deg = math.degrees(yaw)
        roll_deg = math.degrees(roll)

        return pitch_deg, yaw_deg, roll_deg

    def update(
        self,
        landmarks_array: np.ndarray,
        timestamp: float = None
    ) -> Dict:
        """
        更新坐姿监测

        Args:
            landmarks_array: 人脸关键点数组
            timestamp: 时间戳

        Returns:
            监测结果字典
        """
        if timestamp is None:
            timestamp = time.time()

        # 1. 估计头部姿态
        success, rotation_vector, translation_vector = self.estimate_head_pose(landmarks_array)

        if success:
            # 2. 计算欧拉角
            self.pitch, self.yaw, self.roll = self.rotation_vector_to_euler_angles(rotation_vector)

            # 3. 判断坐姿类型
            if self.pitch > self.pitch_threshold_down:
                self.posture_type = "Head Down"
                is_currently_bad = True
            elif self.pitch < self.pitch_threshold_up:
                self.posture_type = "Head Up"
                is_currently_bad = True
            else:
                self.posture_type = "Normal"
                is_currently_bad = False

            # 4. 更新持续时间
            if is_currently_bad:
                if self.bad_posture_start is None:
                    self.bad_posture_start = timestamp
                    self.bad_posture_duration = 0.0
                else:
                    self.bad_posture_duration = timestamp - self.bad_posture_start

                # 判断是否需要警告
                if self.bad_posture_duration >= self.warning_duration:
                    self.is_bad_posture = True
                else:
                    self.is_bad_posture = False
            else:
                self.bad_posture_start = None
                self.bad_posture_duration = 0.0
                self.is_bad_posture = False
        else:
            # 姿态估计失败
            self.posture_type = "Unknown"
            self.is_bad_posture = False

        return self.get_status()

    def get_status(self) -> Dict:
        """
        获取当前坐姿状态

        Returns:
            状态字典
        """
        return {
            'pitch': self.pitch,
            'yaw': self.yaw,
            'roll': self.roll,
            'posture_type': self.posture_type,
            'bad_posture_duration': self.bad_posture_duration,
            'is_bad_posture': self.is_bad_posture
        }

    def draw_axis(
        self,
        frame: np.ndarray,
        rotation_vector: np.ndarray,
        translation_vector: np.ndarray,
        length: float = 100.0
    ) -> np.ndarray:
        """
        在图像上绘制坐标轴（用于调试和可视化）

        Args:
            frame: 输入图像
            rotation_vector: 旋转向量
            translation_vector: 平移向量
            length: 轴长度

        Returns:
            绘制后的图像
        """
        # 定义3D坐标轴点
        axis_points = np.array([
            [0, 0, 0],           # 原点
            [length, 0, 0],      # X轴（红色）
            [0, length, 0],      # Y轴（绿色）
            [0, 0, length]       # Z轴（蓝色）
        ], dtype=np.float64)

        # 投影到2D
        projected_points, _ = cv2.projectPoints(
            axis_points,
            rotation_vector,
            translation_vector,
            self.camera_matrix,
            self.dist_coeffs
        )

        projected_points = projected_points.reshape(-1, 2).astype(int)

        # 绘制坐标轴
        origin = tuple(projected_points[0])
        x_axis = tuple(projected_points[1])
        y_axis = tuple(projected_points[2])
        z_axis = tuple(projected_points[3])

        # X轴 - 红色
        cv2.line(frame, origin, x_axis, (0, 0, 255), 3)
        # Y轴 - 绿色
        cv2.line(frame, origin, y_axis, (0, 255, 0), 3)
        # Z轴 - 蓝色
        cv2.line(frame, origin, z_axis, (255, 0, 0), 3)

        return frame

    def reset(self):
        """重置状态"""
        self.pitch = 0.0
        self.yaw = 0.0
        self.roll = 0.0
        self.bad_posture_start = None
        self.bad_posture_duration = 0.0
        self.is_bad_posture = False
        self.posture_type = "Normal"
        print("✓ 坐姿监测器已重置")


def test_posture_monitor():
    """测试坐姿监测器"""
    print("=== 坐姿监测器测试 ===\n")

    # 导入必要模块
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from camera.camera_capture import CameraCapture
    from detection.face_detector import FaceDetector
    from utils.config_loader import get_config

    # 加载配置
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.yaml')
    config = get_config(config_path)
    posture_config = config.get_posture_config()

    # 初始化模块
    camera = CameraCapture(resolution=(640, 480))
    if not camera.start():
        return

    detector = FaceDetector()
    monitor = PostureMonitor(
        pitch_threshold_down=posture_config['pitch_threshold_down'],
        pitch_threshold_up=posture_config['pitch_threshold_up'],
        warning_duration=5.0  # 测试时缩短为5秒
    )

    window_name = "Posture Monitor Test [Press Q to quit]"
    cv2.namedWindow(window_name)

    print("✓ 系统运行中... 按 'Q' 键退出")
    print("提示：尝试低头、仰头、转头观察姿态变化\n")

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

                # 更新坐姿监测
                status = monitor.update(landmarks_array)

                # 估计头部姿态并绘制坐标轴
                success, rotation_vector, translation_vector = monitor.estimate_head_pose(landmarks_array)
                if success:
                    frame = monitor.draw_axis(frame, rotation_vector, translation_vector, length=150)

                # 显示姿态信息
                y_offset = 30
                line_height = 30

                # 俯仰角
                pitch_color = (0, 255, 0)
                if status['pitch'] > monitor.pitch_threshold_down:
                    pitch_color = (0, 0, 255)  # 红色 - 低头
                elif status['pitch'] < monitor.pitch_threshold_up:
                    pitch_color = (0, 165, 255)  # 橙色 - 仰头

                pitch_text = f"Pitch: {status['pitch']:.1f} deg"
                cv2.putText(frame, pitch_text, (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, pitch_color, 2)
                y_offset += line_height

                # 偏航角
                yaw_text = f"Yaw: {status['yaw']:.1f} deg"
                cv2.putText(frame, yaw_text, (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                y_offset += line_height

                # 翻滚角
                roll_text = f"Roll: {status['roll']:.1f} deg"
                cv2.putText(frame, roll_text, (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                y_offset += line_height

                # 坐姿类型
                posture_color = (0, 0, 255) if status['is_bad_posture'] else (0, 255, 0)
                posture_text = f"Posture: {status['posture_type']}"
                cv2.putText(frame, posture_text, (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, posture_color, 2)
                y_offset += line_height

                # 如果坐姿不良，显示持续时长
                if status['bad_posture_duration'] > 0:
                    duration_text = f"Bad Duration: {status['bad_posture_duration']:.1f}s"
                    cv2.putText(frame, duration_text, (10, y_offset),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
                    y_offset += line_height

                # 警告
                if status['is_bad_posture']:
                    warning_text = "! BAD POSTURE WARNING !"
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

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\n用户中断")

    finally:
        detector.close()
        camera.release()
        cv2.destroyAllWindows()
        print("测试结束")


if __name__ == "__main__":
    test_posture_monitor()
