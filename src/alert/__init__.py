"""
提醒模块
包含多种提醒方式：语音、LED、Web提醒、蜂鸣器
注意：传统GUI提醒已移除，改用Web界面
"""

from .alert_manager import AlertManager, AlertType, AlertLevel
from .voice_alert import VoiceAlert
from .led_alert import LEDAlert

# Web相关模块使用懒加载，避免强制依赖Flask
# 仅在app.py中使用Web功能时才需要导入
try:
    from .web_alert import WebAlert
    from .buzzer_alert import BuzzerAlert
    WEB_AVAILABLE = True
except ImportError:
    WebAlert = None
    BuzzerAlert = None
    WEB_AVAILABLE = False

__all__ = [
    'AlertManager',
    'AlertType',
    'AlertLevel',
    'VoiceAlert',
    'LEDAlert',
    'WebAlert',
    'BuzzerAlert',
    'WEB_AVAILABLE'
]
