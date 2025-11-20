"""
LED提醒模块
功能：使用树莓派GPIO控制LED闪烁提醒
"""

import time
from threading import Thread

# 尝试导入RPi.GPIO，如果不在树莓派上则使用模拟模式
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    GPIO_AVAILABLE = False
    print("注意：RPi.GPIO不可用，LED提醒将在模拟模式下运行")


class LEDAlert:
    """LED提醒器类"""

    def __init__(
        self,
        pin: int = 17,
        blink_duration: float = 2.0
    ):
        """
        初始化LED提醒器

        Args:
            pin: GPIO引脚号（BCM模式）
            blink_duration: 闪烁持续时间（秒）
        """
        self.pin = pin
        self.blink_duration = blink_duration
        self.gpio_initialized = False

        if GPIO_AVAILABLE:
            try:
                # 设置GPIO模式为BCM
                GPIO.setmode(GPIO.BCM)

                # 禁用警告
                GPIO.setwarnings(False)

                # 设置引脚为输出模式
                GPIO.setup(self.pin, GPIO.OUT)

                # 初始状态为关闭
                GPIO.output(self.pin, GPIO.LOW)

                self.gpio_initialized = True
                print(f"✓ LED提醒器初始化成功 (GPIO {pin})")
                print(f"  - 闪烁持续时间: {blink_duration}秒")

            except Exception as e:
                print(f"✗ LED提醒器初始化失败: {e}")
                print("  LED提醒将在模拟模式下运行")
        else:
            print(f"✓ LED提醒器初始化（模拟模式，GPIO {pin}）")
            print(f"  - 闪烁持续时间: {blink_duration}秒")

    def blink(self, level=None, times: int = 3, interval: float = 0.5):
        """
        LED闪烁

        Args:
            level: 提醒级别（暂未使用，可扩展为不同闪烁模式）
            times: 闪烁次数
            interval: 闪烁间隔（秒）
        """
        if self.gpio_initialized:
            self._blink_real(times, interval)
        else:
            self._blink_simulated(times, interval)

    def _blink_real(self, times: int, interval: float):
        """真实LED闪烁"""
        try:
            for i in range(times):
                GPIO.output(self.pin, GPIO.HIGH)
                time.sleep(interval)
                GPIO.output(self.pin, GPIO.LOW)
                time.sleep(interval)
            print(f"✓ LED闪烁 {times} 次完成")
        except Exception as e:
            print(f"✗ LED闪烁失败: {e}")

    def _blink_simulated(self, times: int, interval: float):
        """模拟LED闪烁（用于非树莓派环境）"""
        print(f"[模拟] LED闪烁 {times} 次")
        for i in range(times):
            print(f"  闪烁 {i+1}/{times}: ON", end='')
            time.sleep(interval)
            print(" -> OFF")
            time.sleep(interval)
        print("✓ 模拟LED闪烁完成")

    def on(self):
        """打开LED"""
        if self.gpio_initialized:
            try:
                GPIO.output(self.pin, GPIO.HIGH)
                print("✓ LED已打开")
            except Exception as e:
                print(f"✗ LED打开失败: {e}")
        else:
            print("[模拟] LED ON")

    def off(self):
        """关闭LED"""
        if self.gpio_initialized:
            try:
                GPIO.output(self.pin, GPIO.LOW)
                print("✓ LED已关闭")
            except Exception as e:
                print(f"✗ LED关闭失败: {e}")
        else:
            print("[模拟] LED OFF")

    def test(self):
        """测试LED"""
        print("\n=== LED提醒器测试 ===\n")

        # 测试1：单次闪烁
        print("测试1: 单次闪烁")
        self.blink(times=1, interval=0.5)
        time.sleep(1)

        # 测试2：快速闪烁
        print("\n测试2: 快速闪烁")
        self.blink(times=5, interval=0.2)
        time.sleep(1)

        # 测试3：持续亮起
        print("\n测试3: 持续亮起2秒")
        self.on()
        time.sleep(2)
        self.off()

        print("\n✓ LED测试完成")

    def cleanup(self):
        """清理GPIO资源"""
        if self.gpio_initialized:
            try:
                GPIO.output(self.pin, GPIO.LOW)
                GPIO.cleanup(self.pin)
                print("✓ GPIO资源已清理")
            except Exception as e:
                print(f"✗ GPIO清理失败: {e}")
        else:
            print("✓ 模拟GPIO清理完成")


def test_led_alert():
    """测试LED提醒器"""
    print("=== LED提醒器独立测试 ===\n")

    # 初始化
    led = LEDAlert(pin=17, blink_duration=2.0)

    # 运行测试
    led.test()

    # 清理资源
    led.cleanup()
    print("\n测试结束")


if __name__ == "__main__":
    test_led_alert()
