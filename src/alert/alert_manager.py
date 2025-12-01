"""
提醒管理器模块
功能：统一管理多种提醒方式（语音、LED），防止频繁提醒
注意：GUI提醒已移除，改用Web界面
"""

import time
from enum import Enum
from typing import Dict, List, Optional
from threading import Thread, Lock


class AlertType(Enum):
    """提醒类型枚举"""
    FATIGUE = "fatigue"           # 疲劳提醒
    DISTANCE = "distance"         # 距离过近提醒
    POSTURE = "posture"           # 坐姿不良提醒
    SEVERE_FATIGUE = "severe"     # 严重疲劳提醒


class AlertLevel(Enum):
    """提醒级别枚举"""
    INFO = 1      # 信息级（蓝色）
    WARNING = 2   # 警告级（黄色）
    CRITICAL = 3  # 严重级（红色）


class AlertManager:
    """提醒管理器类 - 统一管理多种提醒方式"""

    def __init__(
        self,
        enable_voice: bool = True,
        enable_led: bool = False,
        cooldown_time: float = 300.0
    ):
        """
        初始化提醒管理器

        Args:
            enable_voice: 是否启用语音提醒
            enable_led: 是否启用LED提醒
            cooldown_time: 冷却时间（秒），防止频繁提醒
        """
        self.enable_voice = enable_voice
        self.enable_led = enable_led
        self.cooldown_time = cooldown_time

        # 各类提醒器
        self.voice_alert = None
        self.led_alert = None
        self.gui_alert = None  # Web提醒器

        # 冷却时间跟踪（记录每种提醒类型的上次触发时间）
        self.last_alert_time: Dict[AlertType, float] = {}

        # 线程锁
        self.lock = Lock()

        print("✓ 提醒管理器初始化完成")
        print(f"  - 语音提醒: {'启用' if enable_voice else '禁用'}")
        print(f"  - LED提醒: {'启用' if enable_led else '禁用'}")
        print(f"  - 冷却时间: {cooldown_time}秒")

    def set_voice_alert(self, voice_alert):
        """设置语音提醒器"""
        self.voice_alert = voice_alert
        print("✓ 语音提醒器已注册")

    def set_led_alert(self, led_alert):
        """设置LED提醒器"""
        self.led_alert = led_alert
        print("✓ LED提醒器已注册")
    
    def set_gui_alert(self, gui_alert):
        """设置GUI/Web提醒器"""
        self.gui_alert = gui_alert
    print("✓ Web提醒器已注册")

    def can_alert(self, alert_type: AlertType) -> bool:
        """
        检查是否可以发送提醒（冷却时间检查）

        Args:
            alert_type: 提醒类型

        Returns:
            是否可以提醒
        """
        current_time = time.time()

        with self.lock:
            if alert_type not in self.last_alert_time:
                return True

            time_since_last = current_time - self.last_alert_time[alert_type]
            return time_since_last >= self.cooldown_time

    def trigger_alert(
        self,
        alert_type: AlertType,
        message: str,
        level: AlertLevel = AlertLevel.WARNING
    ):
        """
        触发提醒

        Args:
            alert_type: 提醒类型
            message: 提醒消息
            level: 提醒级别
        """
        # 检查冷却时间
        if not self.can_alert(alert_type):
            return

        # 更新上次提醒时间
        with self.lock:
            self.last_alert_time[alert_type] = time.time()

        print(f"\n[提醒触发] {alert_type.value}: {message}")

        # 语音提醒
        if self.enable_voice and self.voice_alert:
            Thread(target=self._trigger_voice, args=(message,), daemon=True).start()

        # LED提醒
        if self.gui_alert:
            Thread(target=self._trigger_gui, args=(alert_type, message, level), daemon=True).start()

    def _trigger_voice(self, message: str):
        """触发语音提醒（后台线程）"""
        try:
            self.voice_alert.speak(message)
        except Exception as e:
            print(f"✗ 语音提醒失败: {e}")

    def _trigger_led(self, level: AlertLevel):
        """触发LED提醒（后台线程）"""
        try:
            self.led_alert.blink(level)
        except Exception as e:
            print(f"✗ LED提醒失败: {e}")
    def _trigger_gui(self, alert_type: AlertType, message: str, level: AlertLevel):
        """触发GUI/Web提醒（后台线程）"""
        try:
            self.gui_alert.show_alert(alert_type, message, level)
        except Exception as e:
            print(f"✗ GUI/Web提醒失败: {e}")
    def reset_cooldown(self, alert_type: Optional[AlertType] = None):
        """
        重置冷却时间

        Args:
            alert_type: 要重置的提醒类型，None表示重置所有
        """
        with self.lock:
            if alert_type is None:
                self.last_alert_time.clear()
                print("✓ 已重置所有提醒冷却时间")
            elif alert_type in self.last_alert_time:
                del self.last_alert_time[alert_type]
                print(f"✓ 已重置 {alert_type.value} 提醒冷却时间")

    def cleanup(self):
        """清理资源"""
        print("\n清理提醒管理器...")
        if self.led_alert:
            self.led_alert.cleanup()
        print("✓ 提醒管理器资源已清理")
