"""
蜂鸣器提醒模块
功能：使用树莓派GPIO控制蜂鸣器发出不同节奏的提示音
用于替代pyttsx3语音，在树莓派本地发出提醒
"""

import time
from threading import Thread

# 尝试导入RPi.GPIO，如果不在树莓派上则使用模拟模式
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    GPIO_AVAILABLE = False
    print("注意：RPi.GPIO不可用，蜂鸣器将在模拟模式(print)下运行")


class BuzzerAlert:
    """蜂鸣器提醒器类"""

    def __init__(self, pin: int = 18, simulate: bool = False):
        """
        初始化蜂鸣器提醒器

        Args:
            pin: GPIO引脚号（BCM模式）
            simulate: 强制使用模拟模式（print替代，用于外设未到货时测试）
        """
        self.pin = pin
        self.gpio_initialized = False
        self.simulate = simulate or not GPIO_AVAILABLE

        if not self.simulate and GPIO_AVAILABLE:
            try:
                # 设置GPIO模式为BCM
                GPIO.setmode(GPIO.BCM)
                GPIO.setwarnings(False)

                # 设置引脚为输出模式
                GPIO.setup(self.pin, GPIO.OUT)

                # 初始状态为关闭
                GPIO.output(self.pin, GPIO.LOW)

                self.gpio_initialized = True
                print(f"✓ 蜂鸣器初始化成功 (GPIO {pin})")

            except Exception as e:
                print(f"✗ 蜂鸣器初始化失败: {e}")
                print("  切换到模拟模式")
                self.simulate = True
        else:
            print(f"✓ 蜂鸣器初始化（模拟模式 - print输出，GPIO {pin}）")
            print("  提示：外设到货后设置 simulate=False 启用真实GPIO控制")

        # 不同提醒类型的蜂鸣模式（频率、持续时间、重复次数）
        self.beep_patterns = {
            'fatigue': [(0.1, 0.1), (0.1, 0.1), (0.1, 0.5)],  # 短-短-短
            'distance': [(0.2, 0.2), (0.2, 0.5)],             # 长-长
            'posture': [(0.15, 0.15), (0.15, 0.15), (0.15, 0.5)],  # 中-中-中
            'severe': [(0.3, 0.1), (0.3, 0.1), (0.3, 0.1), (0.3, 0.5)]  # 长-长-长-长（急促）
        }

    def beep(self, on_time: float = 0.1, off_time: float = 0.1):
        """
        发出一次蜂鸣

        Args:
            on_time: 蜂鸣持续时间（秒）
            off_time: 静音持续时间（秒）
        """
        if self.simulate:
            print(f"[模拟蜂鸣] BEEP {on_time}s", end='')
            time.sleep(on_time)
            print(f" -> SILENCE {off_time}s")
            time.sleep(off_time)
        else:
            try:
                GPIO.output(self.pin, GPIO.HIGH)
                time.sleep(on_time)
                GPIO.output(self.pin, GPIO.LOW)
                time.sleep(off_time)
            except Exception as e:
                print(f"✗ 蜂鸣失败: {e}")

    def play_pattern(self, pattern_name: str):
        """
        播放预定义的蜂鸣模式

        Args:
            pattern_name: 模式名称（'fatigue', 'distance', 'posture', 'severe'）
        """
        pattern = self.beep_patterns.get(pattern_name, [(0.2, 0.5)])

        if self.simulate:
            print(f"\n[模拟蜂鸣模式: {pattern_name}]")

        for on_time, off_time in pattern:
            self.beep(on_time, off_time)

        if self.simulate:
            print(f"✓ 模拟蜂鸣模式 '{pattern_name}' 完成\n")
        else:
            print(f"✓ 蜂鸣模式 '{pattern_name}' 完成")

    def speak_alert(self, alert_type: str):
        """
        根据提醒类型播放相应的蜂鸣模式（替代语音）

        Args:
            alert_type: 提醒类型（'fatigue', 'distance', 'posture', 'severe'）
        """
        self.play_pattern(alert_type)

    def test(self):
        """测试蜂鸣器"""
        print("\n=== 蜂鸣器测试 ===\n")

        # 测试所有预定义模式
        for pattern_name in ['fatigue', 'distance', 'posture', 'severe']:
            print(f"测试模式: {pattern_name}")
            self.play_pattern(pattern_name)
            time.sleep(0.5)

        print("\n✓ 蜂鸣器测试完成")

    def cleanup(self):
        """清理GPIO资源"""
        if self.gpio_initialized:
            try:
                GPIO.output(self.pin, GPIO.LOW)
                GPIO.cleanup(self.pin)
                print("✓ 蜂鸣器GPIO资源已清理")
            except Exception as e:
                print(f"✗ GPIO清理失败: {e}")
        else:
            print("✓ 模拟蜂鸣器清理完成")


def test_buzzer_alert():
    """测试蜂鸣器提醒器"""
    print("=== 蜂鸣器提醒器独立测试 ===\n")

    # 初始化（强制模拟模式用于测试）
    buzzer = BuzzerAlert(pin=18, simulate=True)

    # 运行测试
    buzzer.test()

    # 清理资源
    buzzer.cleanup()
    print("\n测试结束")


if __name__ == "__main__":
    test_buzzer_alert()
