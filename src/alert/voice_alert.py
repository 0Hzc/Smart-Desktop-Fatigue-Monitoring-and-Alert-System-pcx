"""
语音提醒模块
功能：直接使用espeak实现离线语音提醒（Ubuntu/Linux兼容）
"""

import subprocess
import shutil
from threading import Lock, Thread


class VoiceAlert:
    """语音提醒器类（基于espeak）"""

    def __init__(
        self,
        rate: int = 150,
        volume: float = 0.9,
        voice: str = "en"
    ):
        """
        初始化语音提醒器

        Args:
            rate: 语速（words per minute），默认150
            volume: 音量（0-100），默认90
            voice: 语言/语音，默认"en"（英语）
                   可选：en, en-us, en-gb, zh等
        """
        # 检查espeak是否安装
        self.espeak_available = shutil.which('espeak') is not None

        if not self.espeak_available:
            print("⚠️  espeak未安装，语音提醒将不可用")
            print("   安装方法：sudo apt-get install -y espeak espeak-data")
            return

        self.lock = Lock()

        # 设置参数
        self.rate = rate
        self.volume = int(volume * 100)  # 转换为0-100范围
        self.voice = voice

        # 预定义提醒文本
        self.alert_messages = {
            'fatigue': "You look tired. Please take a break.",
            'distance': "You are too close to the screen. Please move back.",
            'posture': "Poor posture detected. Please sit up straight.",
            'severe': "Severe fatigue detected! Please rest immediately.",
        }

        print("✓ 语音提醒器初始化成功（espeak）")
        print(f"  - 语速: {rate} wpm")
        print(f"  - 音量: {self.volume}%")
        print(f"  - 语音: {voice}")

    def speak(self, message: str, background: bool = True):
        """
        播放语音提醒

        Args:
            message: 提醒消息
            background: 是否在后台播放（不阻塞），默认True
        """
        if not self.espeak_available:
            print(f"[语音模拟] {message}")
            return

        if background:
            # 在后台线程播放，不阻塞主程序
            thread = Thread(target=self._speak_blocking, args=(message,))
            thread.daemon = True
            thread.start()
        else:
            # 阻塞式播放
            self._speak_blocking(message)

    def _speak_blocking(self, message: str):
        """
        阻塞式播放语音（内部方法）

        Args:
            message: 提醒消息
        """
        try:
            with self.lock:
                # 构建espeak命令
                # -s: 语速（默认175，范围80-450）
                # -a: 音量（默认100，范围0-200）
                # -v: 语音/语言
                cmd = [
                    'espeak',
                    '-s', str(self.rate),
                    '-a', str(self.volume),
                    '-v', self.voice,
                    message
                ]

                # 执行espeak命令
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=10  # 10秒超时
                )

                if result.returncode == 0:
                    print(f"✓ 语音提醒播放完成: {message}")
                else:
                    print(f"✗ 语音播放失败: {result.stderr.decode()}")

        except subprocess.TimeoutExpired:
            print(f"✗ 语音播放超时: {message}")
        except Exception as e:
            print(f"✗ 语音播放失败: {e}")

    def speak_alert(self, alert_type: str):
        """
        根据提醒类型播放预定义消息

        Args:
            alert_type: 提醒类型（'fatigue', 'distance', 'posture', 'severe'）
        """
        message = self.alert_messages.get(
            alert_type,
            "Warning: Please pay attention to your health."
        )
        self.speak(message)

    def test(self):
        """测试语音提醒"""
        print("\n=== 语音提醒测试 ===")

        if not self.espeak_available:
            print("✗ espeak未安装，无法测试")
            return

        test_messages = [
            "System initialized successfully.",
            "This is a test of the voice alert system.",
            "Thank you for using the fatigue monitoring system."
        ]

        for i, msg in enumerate(test_messages, 1):
            print(f"\n测试 {i}/{len(test_messages)}: {msg}")
            self.speak(msg, background=False)  # 测试时使用阻塞模式

        print("\n✓ 语音测试完成")

    def cleanup(self):
        """清理资源"""
        # espeak使用命令行调用，无需清理
        print("✓ 语音提醒器已清理")


def test_voice_alert():
    """测试语音提醒器"""
    print("=== 语音提醒器独立测试 ===\n")

    # 初始化
    voice = VoiceAlert(rate=150, volume=0.9)

    # 测试基本语音
    voice.test()

    # 测试预定义提醒
    print("\n=== 测试预定义提醒消息 ===")
    for alert_type in ['fatigue', 'distance', 'posture', 'severe']:
        print(f"\n播放 {alert_type} 提醒...")
        voice.speak_alert(alert_type)
        # 等待一下，避免消息重叠
        import time
        time.sleep(2)

    # 清理
    voice.cleanup()
    print("\n测试结束")


if __name__ == "__main__":
    test_voice_alert()
