"""
人脸检测与关键点提取模块
功能：使用MediaPipe检测人脸并提取468个3D关键点
"""

import cv2
import mediapipe as mp
import numpy as np
from typing import List, Tuple, Optional, Dict


class FaceDetector:
    """人脸检测器类"""

    def __init__(
        self,
        max_num_faces: int = 1,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        refine_landmarks: bool = False
    ):
        """
        初始化人脸检测器

        Args:
            max_num_faces: 最多检测人脸数
            min_detection_confidence: 最小检测置信度
            min_tracking_confidence: 最小跟踪置信度
            refine_landmarks: 是否使用精细关键点
        """
        self.max_num_faces = max_num_faces
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence

        # 初始化MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=max_num_faces,
            refine_landmarks=refine_landmarks,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )

        print(f"✓ MediaPipe人脸检测器初始化成功")
        print(f"  - 最多检测人脸数: {max_num_faces}")
        print(f"  - 检测置信度: {min_detection_confidence}")
        print(f"  - 跟踪置信度: {min_tracking_confidence}")

    def detect(self, frame: np.ndarray) -> Tuple[bool, Optional[List]]:
        """
        检测人脸并提取关键点

        Args:
            frame: 输入图像帧（BGR格式）

        Returns:
            (是否检测到人脸, 人脸关键点列表)
        """
        # 转换为RGB（MediaPipe需要RGB格式）
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 提高性能：设置图像不可写
        rgb_frame.flags.writeable = False

        # 检测人脸
        results = self.face_mesh.process(rgb_frame)

        # 恢复可写
        rgb_frame.flags.writeable = True

        if results.multi_face_landmarks:
            return True, results.multi_face_landmarks
        else:
            return False, None

    def get_landmarks_array(
        self,
        face_landmarks,
        frame_width: int,
        frame_height: int
    ) -> np.ndarray:
        """
        将关键点转换为NumPy数组（像素坐标）

        Args:
            face_landmarks: MediaPipe人脸关键点对象
            frame_width: 图像宽度
            frame_height: 图像高度

        Returns:
            关键点数组，形状为 (468, 3)，包含 [x, y, z]
        """
        landmarks = []

        for landmark in face_landmarks.landmark:
            x = int(landmark.x * frame_width)
            y = int(landmark.y * frame_height)
            z = landmark.z  # 相对深度

            landmarks.append([x, y, z])

        return np.array(landmarks)

    def get_specific_landmarks(
        self,
        landmarks_array: np.ndarray,
        indices: List[int]
    ) -> np.ndarray:
        """
        获取特定索引的关键点

        Args:
            landmarks_array: 完整关键点数组
            indices: 关键点索引列表

        Returns:
            特定关键点数组
        """
        return landmarks_array[indices]

    def draw_landmarks(
        self,
        frame: np.ndarray,
        face_landmarks,
        draw_contours: bool = True
    ) -> np.ndarray:
        """
        在图像上绘制关键点

        Args:
            frame: 输入图像
            face_landmarks: 人脸关键点
            draw_contours: 是否绘制轮廓线

        Returns:
            绘制后的图像
        """
        if draw_contours:
            # 绘制完整的人脸网格
            self.mp_drawing.draw_landmarks(
                image=frame,
                landmark_list=face_landmarks,
                connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_tesselation_style()
            )

            # 绘制轮廓
            self.mp_drawing.draw_landmarks(
                image=frame,
                landmark_list=face_landmarks,
                connections=self.mp_face_mesh.FACEMESH_CONTOURS,
                landmark_drawing_spec=None,
                connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_contours_style()
            )
        else:
            # 只绘制关键点
            h, w = frame.shape[:2]
            for landmark in face_landmarks.landmark:
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)

        return frame

    def draw_specific_landmarks(
        self,
        frame: np.ndarray,
        landmarks_array: np.ndarray,
        indices: List[int],
        color: Tuple[int, int, int] = (0, 255, 0),
        radius: int = 3
    ) -> np.ndarray:
        """
        绘制特定关键点

        Args:
            frame: 输入图像
            landmarks_array: 关键点数组
            indices: 要绘制的关键点索引
            color: 颜色 (B, G, R)
            radius: 圆点半径

        Returns:
            绘制后的图像
        """
        for idx in indices:
            if idx < len(landmarks_array):
                x, y = landmarks_array[idx][:2].astype(int)
                cv2.circle(frame, (x, y), radius, color, -1)
                # 显示索引号
                cv2.putText(
                    frame,
                    str(idx),
                    (x + 5, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.3,
                    color,
                    1
                )

        return frame

    def get_face_bounding_box(
        self,
        landmarks_array: np.ndarray
    ) -> Tuple[int, int, int, int]:
        """
        获取人脸边界框

        Args:
            landmarks_array: 关键点数组

        Returns:
            (x_min, y_min, x_max, y_max)
        """
        x_coords = landmarks_array[:, 0]
        y_coords = landmarks_array[:, 1]

        x_min = int(np.min(x_coords))
        x_max = int(np.max(x_coords))
        y_min = int(np.min(y_coords))
        y_max = int(np.max(y_coords))

        return x_min, y_min, x_max, y_max

    def close(self):
        """释放资源"""
        self.face_mesh.close()
        print("✓ 人脸检测器已关闭")


# MediaPipe关键点索引常量
class LandmarkIndices:
    """MediaPipe Face Mesh 关键点索引"""

    # 左眼关键点 (6个点用于EAR计算)
    LEFT_EYE = [33, 160, 158, 133, 153, 144]

    # 右眼关键点 (6个点用于EAR计算)
    RIGHT_EYE = [362, 385, 387, 263, 373, 380]

    # 左眼简化版（3个点）
    LEFT_EYE_SIMPLE = [33, 160, 144]

    # 右眼简化版（3个点）
    RIGHT_EYE_SIMPLE = [362, 385, 380]

    # 用于头部姿态估计的关键点
    POSE_ESTIMATION_POINTS = [
        1,    # 鼻尖
        152,  # 下巴
        33,   # 左眼角
        263,  # 右眼角
        61,   # 左嘴角
        291   # 右嘴角
    ]

    # 鼻尖
    NOSE_TIP = 1

    # 下巴
    CHIN = 152

    # 左眼中心点
    LEFT_EYE_CENTER = 468  # 注意：需要计算

    # 右眼中心点
    RIGHT_EYE_CENTER = 473  # 注意：需要计算


def test_face_detector():
    """测试人脸检测器"""
    print("=== 人脸检测器测试 ===")
    print("按 'q' 键退出\n")

    # 导入摄像头模块
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from camera.camera_capture import CameraCapture

    # 初始化摄像头
    camera = CameraCapture(resolution=(640, 480))
    if not camera.start():
        return

    # 初始化人脸检测器
    detector = FaceDetector()

    window_name = "Face Detection Test"
    cv2.namedWindow(window_name)

    try:
        while True:
            ret, frame = camera.read()
            if not ret:
                break

            # 检测人脸
            detected, face_landmarks_list = detector.detect(frame)

            if detected and face_landmarks_list:
                for face_landmarks in face_landmarks_list:
                    # 绘制关键点
                    frame = detector.draw_landmarks(frame, face_landmarks)

                    # 获取关键点数组
                    h, w = frame.shape[:2]
                    landmarks_array = detector.get_landmarks_array(face_landmarks, w, h)

                    # 绘制眼部关键点（高亮显示）
                    frame = detector.draw_specific_landmarks(
                        frame,
                        landmarks_array,
                        LandmarkIndices.LEFT_EYE,
                        color=(255, 0, 0),
                        radius=3
                    )
                    frame = detector.draw_specific_landmarks(
                        frame,
                        landmarks_array,
                        LandmarkIndices.RIGHT_EYE,
                        color=(255, 0, 0),
                        radius=3
                    )

                    # 显示人脸框
                    x_min, y_min, x_max, y_max = detector.get_face_bounding_box(landmarks_array)
                    cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

                    # 显示关键点数量
                    cv2.putText(
                        frame,
                        f"Landmarks: {len(landmarks_array)}",
                        (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2
                    )

            # 显示FPS
            fps_text = f"FPS: {camera.get_fps():.1f}"
            cv2.putText(frame, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # 显示图像
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
    test_face_detector()
