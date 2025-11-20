"""
疲劳状态分析模块
功能：基于眼部关键点分析疲劳状态
- EAR (Eye Aspect Ratio) 计算
- 眨眼检测与统计
- PERCLOS (Percentage of Eyelid Closure) 计算
- 长时间闭眼检测
"""

import numpy as np
from typing import Tuple, List, Dict
from collections import deque
import time


class FatigueAnalyzer:
    """疲劳分析器类"""

    def __init__(
        self,
        ear_threshold: float = 0.25,
        perclos_threshold: float = 0.15,
        perclos_window: int = 60,
        blink_min: int = 10,
        blink_max: int = 30,
        closed_eye_duration: float = 2.0
    ):
        """
        初始化疲劳分析器

        Args:
            ear_threshold: EAR阈值，低于此值判定为闭眼
            perclos_threshold: PERCLOS阈值，超过此值判定为疲劳
            perclos_window: PERCLOS统计窗口（秒）
            blink_min: 每分钟最少眨眼次数
            blink_max: 每分钟最多眨眼次数
            closed_eye_duration: 连续闭眼触发警报时长（秒）
        """
        # 阈值参数
        self.ear_threshold = ear_threshold
        self.perclos_threshold = perclos_threshold
        self.perclos_window = perclos_window
        self.blink_min = blink_min
        self.blink_max = blink_max
        self.closed_eye_duration = closed_eye_duration

        # 状态变量
        self.left_ear = 0.0
        self.right_ear = 0.0
        self.avg_ear = 0.0

        # 眨眼检测
        self.blink_counter = 0
        self.is_blinking = False
        self.last_blink_time = time.time()
        self.blinks_per_minute = 0

        # PERCLOS计算（使用滑动窗口）
        self.eye_state_history = deque(maxlen=perclos_window * 30)  # 假设30fps
        self.perclos_value = 0.0

        # 闭眼时长检测
        self.eye_closed_start = None
        self.eye_closed_duration = 0.0
        self.is_drowsy = False

        # 疲劳状态
        self.fatigue_level = 0  # 0: 正常, 1: 轻度疲劳, 2: 中度疲劳, 3: 重度疲劳

        print("✓ 疲劳分析器初始化成功")
        print(f"  - EAR阈值: {ear_threshold}")
        print(f"  - PERCLOS阈值: {perclos_threshold * 100}%")
        print(f"  - PERCLOS窗口: {perclos_window}秒")
        print(f"  - 眨眼频率范围: {blink_min}-{blink_max}次/分钟")
        print(f"  - 闭眼警报时长: {closed_eye_duration}秒")

    @staticmethod
    def calculate_ear(eye_landmarks: np.ndarray) -> float:
        """
        计算眼睛纵横比 (Eye Aspect Ratio)

        Args:
            eye_landmarks: 眼部6个关键点坐标，形状为(6, 2)或(6, 3)
                          点的顺序：
                          [0]: 左眼角
                          [1]: 上眼睑左
                          [2]: 上眼睑右
                          [3]: 右眼角
                          [4]: 下眼睑右
                          [5]: 下眼睑左

        Returns:
            EAR值

        公式：
            EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
            其中 p1-p6 对应 eye_landmarks[0-5]
        """
        # 提取x, y坐标（忽略z坐标）
        points = eye_landmarks[:, :2]

        # 计算垂直距离
        vertical_1 = np.linalg.norm(points[1] - points[5])  # 上左 - 下左
        vertical_2 = np.linalg.norm(points[2] - points[4])  # 上右 - 下右

        # 计算水平距离
        horizontal = np.linalg.norm(points[0] - points[3])  # 左眼角 - 右眼角

        # 计算EAR
        if horizontal == 0:
            return 0.0

        ear = (vertical_1 + vertical_2) / (2.0 * horizontal)
        return ear

    def update(
        self,
        left_eye_landmarks: np.ndarray,
        right_eye_landmarks: np.ndarray,
        timestamp: float = None
    ) -> Dict:
        """
        更新疲劳状态分析

        Args:
            left_eye_landmarks: 左眼6个关键点
            right_eye_landmarks: 右眼6个关键点
            timestamp: 时间戳（秒），如果为None则使用当前时间

        Returns:
            分析结果字典
        """
        if timestamp is None:
            timestamp = time.time()

        # 1. 计算左右眼EAR
        self.left_ear = self.calculate_ear(left_eye_landmarks)
        self.right_ear = self.calculate_ear(right_eye_landmarks)
        self.avg_ear = (self.left_ear + self.right_ear) / 2.0

        # 2. 判断眼睛是否闭合
        is_closed = self.avg_ear < self.ear_threshold

        # 3. 更新眨眼检测
        self._update_blink_detection(is_closed, timestamp)

        # 4. 更新PERCLOS统计
        self._update_perclos(is_closed)

        # 5. 更新闭眼时长检测
        self._update_closed_eye_duration(is_closed, timestamp)

        # 6. 计算疲劳等级
        self._calculate_fatigue_level()

        # 返回分析结果
        return self.get_status()

    def _update_blink_detection(self, is_closed: bool, timestamp: float):
        """
        更新眨眼检测

        Args:
            is_closed: 当前眼睛是否闭合
            timestamp: 当前时间戳
        """
        # 检测眨眼：从睁眼到闭眼的转换
        if is_closed and not self.is_blinking:
            self.is_blinking = True
            self.blink_counter += 1
            self.last_blink_time = timestamp

        # 检测睁眼：从闭眼到睁眼的转换
        elif not is_closed and self.is_blinking:
            self.is_blinking = False

        # 计算每分钟眨眼次数（滑动窗口：最近60秒）
        # 简化实现：每10秒更新一次统计
        if timestamp - self.last_blink_time > 60:
            self.blinks_per_minute = self.blink_counter
            self.blink_counter = 0
            self.last_blink_time = timestamp

    def _update_perclos(self, is_closed: bool):
        """
        更新PERCLOS统计

        Args:
            is_closed: 当前眼睛是否闭合
        """
        # 添加当前状态到历史队列
        self.eye_state_history.append(1 if is_closed else 0)

        # 计算PERCLOS（闭眼帧数占总帧数的比例）
        if len(self.eye_state_history) > 0:
            closed_frames = sum(self.eye_state_history)
            total_frames = len(self.eye_state_history)
            self.perclos_value = closed_frames / total_frames
        else:
            self.perclos_value = 0.0

    def _update_closed_eye_duration(self, is_closed: bool, timestamp: float):
        """
        更新闭眼时长检测

        Args:
            is_closed: 当前眼睛是否闭合
            timestamp: 当前时间戳
        """
        if is_closed:
            # 眼睛闭合
            if self.eye_closed_start is None:
                # 刚开始闭眼
                self.eye_closed_start = timestamp
                self.eye_closed_duration = 0.0
            else:
                # 持续闭眼
                self.eye_closed_duration = timestamp - self.eye_closed_start

            # 判断是否打瞌睡
            if self.eye_closed_duration > self.closed_eye_duration:
                self.is_drowsy = True
            else:
                self.is_drowsy = False
        else:
            # 眼睛睁开
            self.eye_closed_start = None
            self.eye_closed_duration = 0.0
            self.is_drowsy = False

    def _calculate_fatigue_level(self):
        """
        计算疲劳等级

        等级定义：
        0: 正常 - PERCLOS < 10%, 眨眼正常
        1: 轻度疲劳 - PERCLOS 10-15% 或 眨眼频率异常
        2: 中度疲劳 - PERCLOS 15-20% 或 短暂打瞌睡(1-2秒)
        3: 重度疲劳 - PERCLOS > 20% 或 打瞌睡(>2秒)
        """
        # 重度疲劳
        if self.perclos_value > 0.20 or self.is_drowsy:
            self.fatigue_level = 3

        # 中度疲劳
        elif self.perclos_value > self.perclos_threshold or self.eye_closed_duration > 1.0:
            self.fatigue_level = 2

        # 轻度疲劳
        elif (self.perclos_value > 0.10 or
              self.blinks_per_minute < self.blink_min or
              self.blinks_per_minute > self.blink_max):
            self.fatigue_level = 1

        # 正常
        else:
            self.fatigue_level = 0

    def get_status(self) -> Dict:
        """
        获取当前疲劳状态

        Returns:
            状态字典，包含所有检测指标
        """
        return {
            # EAR相关
            'left_ear': self.left_ear,
            'right_ear': self.right_ear,
            'avg_ear': self.avg_ear,
            'is_closed': self.avg_ear < self.ear_threshold,

            # 眨眼相关
            'blink_counter': self.blink_counter,
            'blinks_per_minute': self.blinks_per_minute,
            'is_blinking': self.is_blinking,

            # PERCLOS
            'perclos': self.perclos_value,
            'perclos_percentage': self.perclos_value * 100,

            # 闭眼时长
            'eye_closed_duration': self.eye_closed_duration,
            'is_drowsy': self.is_drowsy,

            # 疲劳等级
            'fatigue_level': self.fatigue_level,
            'fatigue_description': self._get_fatigue_description()
        }

    def _get_fatigue_description(self) -> str:
        """获取疲劳等级描述"""
        descriptions = {
            0: "正常",
            1: "轻度疲劳",
            2: "中度疲劳",
            3: "重度疲劳"
        }
        return descriptions.get(self.fatigue_level, "未知")

    def reset(self):
        """重置所有状态"""
        self.blink_counter = 0
        self.is_blinking = False
        self.eye_state_history.clear()
        self.perclos_value = 0.0
        self.eye_closed_start = None
        self.eye_closed_duration = 0.0
        self.is_drowsy = False
        self.fatigue_level = 0
        print("✓ 疲劳分析器已重置")


def test_fatigue_analyzer():
    """测试疲劳分析器"""
    print("=== 疲劳分析器测试 ===\n")

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
    analyzer = FatigueAnalyzer(
        ear_threshold=0.25,
        perclos_threshold=0.15,
        closed_eye_duration=2.0
    )

    window_name = "Fatigue Analyzer Test [Press Q to quit]"
    cv2.namedWindow(window_name)

    print("✓ 系统运行中... 按 'Q' 键退出")
    print("提示：尝试眨眼、闭眼等动作来测试检测效果\n")

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

                # 获取关键点数组
                landmarks_array = detector.get_landmarks_array(face_landmarks, w, h)

                # 提取眼部关键点
                left_eye = landmarks_array[LandmarkIndices.LEFT_EYE]
                right_eye = landmarks_array[LandmarkIndices.RIGHT_EYE]

                # 更新疲劳分析
                status = analyzer.update(left_eye, right_eye)

                # 绘制人脸关键点
                frame = detector.draw_landmarks(frame, face_landmarks, draw_contours=False)

                # 高亮眼部
                frame = detector.draw_specific_landmarks(
                    frame, landmarks_array, LandmarkIndices.LEFT_EYE,
                    color=(255, 0, 0), radius=2
                )
                frame = detector.draw_specific_landmarks(
                    frame, landmarks_array, LandmarkIndices.RIGHT_EYE,
                    color=(255, 0, 0), radius=2
                )

                # 显示分析结果
                y_offset = 30
                line_height = 25

                # EAR值
                ear_color = (0, 255, 0) if not status['is_closed'] else (0, 0, 255)
                cv2.putText(frame, f"EAR: {status['avg_ear']:.3f}",
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, ear_color, 2)
                y_offset += line_height

                # 眨眼次数
                cv2.putText(frame, f"Blinks: {status['blink_counter']}",
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                y_offset += line_height

                # PERCLOS
                perclos_color = (0, 255, 0) if status['perclos'] < 0.15 else (0, 165, 255)
                cv2.putText(frame, f"PERCLOS: {status['perclos_percentage']:.1f}%",
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, perclos_color, 2)
                y_offset += line_height

                # 闭眼时长
                if status['eye_closed_duration'] > 0:
                    drowsy_color = (0, 0, 255) if status['is_drowsy'] else (0, 165, 255)
                    cv2.putText(frame, f"Closed: {status['eye_closed_duration']:.1f}s",
                               (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, drowsy_color, 2)
                    y_offset += line_height

                # 疲劳等级
                fatigue_colors = {
                    0: (0, 255, 0),    # 绿色 - 正常
                    1: (0, 255, 255),  # 黄色 - 轻度
                    2: (0, 165, 255),  # 橙色 - 中度
                    3: (0, 0, 255)     # 红色 - 重度
                }
                fatigue_color = fatigue_colors.get(status['fatigue_level'], (255, 255, 255))
                cv2.putText(frame, f"Status: {status['fatigue_description']}",
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, fatigue_color, 2)

                # 如果打瞌睡，显示警告
                if status['is_drowsy']:
                    warning_text = "! DROWSY DETECTED !"
                    text_size = cv2.getTextSize(warning_text, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 3)[0]
                    text_x = (w - text_size[0]) // 2
                    text_y = h - 50
                    cv2.putText(frame, warning_text, (text_x, text_y),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

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
    test_fatigue_analyzer()
