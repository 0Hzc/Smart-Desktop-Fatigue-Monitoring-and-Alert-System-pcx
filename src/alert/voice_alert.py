"""
语音提醒模块
功能：使用pyttsx3实现离线语音提醒
"""

import pyttsx3
from threading import Lock


class VoiceAlert:
    """语音提醒器类"""

    def __init__(
        self,
        rate: int = 150,
        volume: float = 0.9,
        voice_index: int = 0
    ):
        """
        初始化语音提醒器

        Args:
            rate: 语速（words per minute），默认150
            volume: 音量（0.0-1.0），默认0.9
            voice_index: 语音索引，0为默认语音
        """
        try:
            self.engine = pyttsx3.init()
            self.lock = Lock()

            # 设置语速
            self.engine.setProperty('rate', rate)

            # 设置音量
            self.engine.setProperty('volume', volume)

            # 获取可用语音
            voices = self.engine.getProperty('voices')
            if voices and voice_index < len(voices):
                self.engine.setProperty('voice', voices[voice_index].id)

            # 预定义提醒文本
            self.alert_messages = {
                'fatigue': "You look tired. Please take a break.",
                'distance': "You are too close to the screen. Please move back.",
                'posture': "Poor posture detected. Please sit up straight.",
                'severe': "Severe fatigue detected! Please rest immediately.",
            }

            print("✓ 语音提醒器初始化成功")
            print(f"  - 语速: {rate} wpm")
            print(f"  - 音量: {int(volume * 100)}%")

        except Exception as e:
            print(f"✗ 语音提醒器初始化失败: {e}")
            self.engine = None

    def speak(self, message: str):
        """
        播放语音提醒

        Args:
            message: 提醒消息
        """
        if not self.engine:
            print("✗ 语音引擎未初始化")
            return

        try:
            with self.lock:
                self.engine.say(message)
                self.engine.runAndWait()
                print(f"✓ 语音提醒播放完成: {message}")
        except Exception as e:
            print(f"✗ 语音播放失败: {e}")

    def speak_alert(self, alert_type: str):
        """
        根据提醒类型播放预定义消息

        Args:
            alert_type: 提醒类型（'fatigue', 'distance', 'posture', 'severe'）
        """
        message = self.alert_messages.get(alert_type, "Warning: Please pay attention to your health.")
        self.speak(message)

    def test(self):
        """测试语音提醒"""
        print("\n=== 语音提醒测试 ===")
        test_messages = [
            "System initialized successfully.",
            "This is a test of the voice alert system.",
            "Thank you for using the fatigue monitoring system."
        ]

        for i, msg in enumerate(test_messages, 1):
            print(f"\n测试 {i}/{len(test_messages)}: {msg}")
            self.speak(msg)

        print("\n✓ 语音测试完成")

    def cleanup(self):
        """清理资源"""
        if self.engine:
            try:
                self.engine.stop()
                print("✓ 语音引擎已停止")
            except:
                pass


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

    # 清理
    voice.cleanup()
    print("\n测试结束")


if __name__ == "__main__":
    test_voice_alert()
