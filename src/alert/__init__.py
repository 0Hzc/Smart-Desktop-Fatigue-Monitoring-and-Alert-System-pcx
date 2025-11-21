"""
提醒模块
包含多种提醒方式：语音、LED、Web提醒、蜂鸣器
注意：传统GUI提醒已移除，改用Web界面
"""

from .alert_manager import AlertManager, AlertType, AlertLevel
from .voice_alert import VoiceAlert
from .led_alert import LEDAlert
from .web_alert import WebAlert
from .buzzer_alert import BuzzerAlert

__all__ = [
    'AlertManager',
    'AlertType',
    'AlertLevel',
    'VoiceAlert',
    'LEDAlert',
    'WebAlert',
    'BuzzerAlert'
]
