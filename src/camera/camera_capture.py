"""
摄像头采集模块
功能：实时视频流采集，支持普通USB摄像头和树莓派摄像头
"""

import cv2
import numpy as np
from typing import Tuple, Optional
import time


class CameraCapture:
    """摄像头采集类"""

    def __init__(
        self,
        camera_id: int = 0,
        resolution: Tuple[int, int] = (640, 480),
        fps: int = 30,
        flip: bool = False,
        use_pi_camera: bool = False
    ):
        """
        初始化摄像头

        Args:
            camera_id: 摄像头ID（0表示默认摄像头）
            resolution: 分辨率 (宽, 高)
            fps: 目标帧率
            flip: 是否翻转画面
            use_pi_camera: 是否使用树莓派摄像头
        """
        self.camera_id = camera_id
        self.width, self.height = resolution
        self.fps = fps
        self.flip = flip
        self.use_pi_camera = use_pi_camera

        self.cap = None
        self.is_opened = False

        # 性能统计
        self.frame_count = 0
        self.start_time = time.time()
        self.current_fps = 0

    def start(self) -> bool:
        """
        启动摄像头

        Returns:
            是否成功启动
        """
        try:
            if self.use_pi_camera:
                # 使用树莓派摄像头（需要picamera2库）
                try:
                    from picamera2 import Picamera2
                    self.cap = Picamera2()
                    config = self.cap.create_preview_configuration(
                        main={"size": (self.width, self.height)}
                    )
                    self.cap.configure(config)
                    self.cap.start()
                    print(f"✓ 树莓派摄像头启动成功: {self.width}x{self.height}")
                except ImportError:
                    print("⚠ picamera2未安装，切换到OpenCV模式")
                    self.use_pi_camera = False
                    return self.start()
            else:
                # 使用OpenCV打开摄像头
                self.cap = cv2.VideoCapture(self.camera_id)

                if not self.cap.isOpened():
                    print(f"✗ 无法打开摄像头 {self.camera_id}")
                    return False

                # 设置分辨率
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                self.cap.set(cv2.CAP_PROP_FPS, self.fps)

                # 验证实际分辨率
                actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                print(f"✓ 摄像头启动成功: {actual_width}x{actual_height}")

            self.is_opened = True
            self.start_time = time.time()
            return True

        except Exception as e:
            print(f"✗ 摄像头启动失败: {e}")
            return False

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        读取一帧图像

        Returns:
            (是否成功, 图像帧)
        """
        if not self.is_opened:
            return False, None

        try:
            if self.use_pi_camera:
                # 从树莓派摄像头读取
                frame = self.cap.capture_array()
                ret = True
            else:
                # 从OpenCV摄像头读取
                ret, frame = self.cap.read()

            if not ret or frame is None:
                return False, None

            # 翻转画面（如果需要）
            if self.flip:
                frame = cv2.flip(frame, 1)

            # 更新帧率统计
            self.frame_count += 1
            if self.frame_count % 30 == 0:  # 每30帧更新一次
                elapsed_time = time.time() - self.start_time
                self.current_fps = self.frame_count / elapsed_time

            return True, frame

        except Exception as e:
            print(f"✗ 读取帧失败: {e}")
            return False, None

    def release(self):
        """释放摄像头资源"""
        if self.cap is not None:
            if self.use_pi_camera:
                try:
                    self.cap.stop()
                except:
                    pass
            else:
                self.cap.release()

            self.is_opened = False
            print("✓ 摄像头已释放")

    def get_fps(self) -> float:
        """
        获取当前帧率

        Returns:
            当前FPS
        """
        return self.current_fps

    def get_resolution(self) -> Tuple[int, int]:
        """
        获取分辨率

        Returns:
            (宽, 高)
        """
        return (self.width, self.height)

    def __enter__(self):
        """上下文管理器入口"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.release()


def test_camera():
    """测试摄像头功能"""
    print("=== 摄像头测试 ===")
    print("按 'q' 键退出\n")

    # 创建摄像头实例
    camera = CameraCapture(
        camera_id=0,
        resolution=(640, 480),
        fps=30,
        flip=False
    )

    if not camera.start():
        print("摄像头启动失败！")
        return

    window_name = "Camera Test"
    cv2.namedWindow(window_name)

    try:
        while True:
            ret, frame = camera.read()

            if not ret:
                print("无法读取帧")
                break

            # 显示帧率
            fps_text = f"FPS: {camera.get_fps():.1f}"
            cv2.putText(
                frame,
                fps_text,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

            # 显示图像
            cv2.imshow(window_name, frame)

            # 按'q'退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\n用户中断")

    finally:
        camera.release()
        cv2.destroyAllWindows()
        print("测试结束")


if __name__ == "__main__":
    test_camera()
