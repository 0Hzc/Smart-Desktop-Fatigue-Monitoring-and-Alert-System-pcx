"""
Web提醒模块
功能：通过WebSocket向浏览器推送提醒消息，支持Web端语音播放
用于树莓派无显示器场景，通过局域网访问Web界面
"""

from flask_socketio import SocketIO
from typing import Optional
import time


class WebAlert:
    """Web提醒器类"""

    def __init__(self, socketio: Optional[SocketIO] = None):
        """
        初始化Web提醒器

        Args:
            socketio: Flask-SocketIO实例，用于向浏览器推送消息
        """
        self.socketio = socketio

        # 提醒消息模板
        self.messages = {
            'fatigue': {
                'title': 'Fatigue Detected',
                'message': 'You look tired. Please take a break to rest your eyes and body.',
                'level': 'warning',
                'voice': 'You look tired. Please take a break.'
            },
            'distance': {
                'title': 'Too Close to Screen',
                'message': 'You are sitting too close. Please move back to protect your eyesight.',
                'level': 'warning',
                'voice': 'You are too close to the screen. Please move back.'
            },
            'posture': {
                'title': 'Poor Posture Detected',
                'message': 'Please sit up straight to avoid back and neck problems.',
                'level': 'warning',
                'voice': 'Poor posture detected. Please sit up straight.'
            },
            'severe': {
                'title': 'Severe Fatigue Warning',
                'message': 'Immediate rest required! You have been working too long without a break.',
                'level': 'critical',
                'voice': 'Severe fatigue detected! Please rest immediately.'
            }
        }

        print("✓ Web提醒器初始化成功")
        if socketio:
            print("  - SocketIO已连接，可向浏览器推送提醒")
        else:
            print("  - 警告：SocketIO未设置，Web提醒将无法发送")

    def set_socketio(self, socketio: SocketIO):
        """设置SocketIO实例"""
        self.socketio = socketio
        print("✓ SocketIO已设置")

    def show(self, alert_type, message: str, level):
        """
        发送Web提醒

        Args:
            alert_type: 提醒类型（AlertType枚举）
            message: 提醒消息
            level: 提醒级别（AlertLevel枚举）
        """
        if not self.socketio:
            print("✗ SocketIO未设置，无法发送Web提醒")
            return

        # 获取提醒类型对应的模板
        alert_key = alert_type.value if hasattr(alert_type, 'value') else str(alert_type)
        template = self.messages.get(alert_key, {
            'title': 'Alert',
            'message': message,
            'level': 'warning',
            'voice': message
        })

        # 构建提醒数据
        alert_data = {
            'type': alert_key,
            'title': template['title'],
            'message': template['message'],
            'level': template['level'],
            'voice_text': template['voice'],
            'timestamp': time.time()
        }

        # 通过WebSocket发送到所有连接的客户端
        try:
            self.socketio.emit('alert', alert_data, namespace='/')
            print(f"✓ Web提醒已发送: {template['title']}")
        except Exception as e:
            print(f"✗ Web提醒发送失败: {e}")

    def send_status_update(self, status_data: dict):
        """
        发送状态更新到Web界面

        Args:
            status_data: 状态数据字典（疲劳、距离、坐姿等）
        """
        if not self.socketio:
            return

        try:
            self.socketio.emit('status_update', status_data, namespace='/')
        except Exception as e:
            print(f"✗ 状态更新发送失败: {e}")

    def test(self):
        """测试Web提醒（需要先启动Web服务器）"""
        print("\n=== Web提醒器测试 ===")

        if not self.socketio:
            print("✗ 无法测试：SocketIO未设置")
            print("  请先启动Web服务器再测试")
            return

        print("\n提示：请在浏览器中访问 http://localhost:5000 查看提醒效果\n")

        # 模拟发送各种提醒
        from alert_manager import AlertType, AlertLevel

        test_cases = [
            (AlertType.FATIGUE, self.messages['fatigue']['message'], AlertLevel.WARNING),
            (AlertType.DISTANCE, self.messages['distance']['message'], AlertLevel.WARNING),
            (AlertType.POSTURE, self.messages['posture']['message'], AlertLevel.WARNING),
            (AlertType.SEVERE_FATIGUE, self.messages['severe']['message'], AlertLevel.CRITICAL)
        ]

        for i, (alert_type, message, level) in enumerate(test_cases, 1):
            print(f"测试 {i}/4: {alert_type.value}")
            self.show(alert_type, message, level)
            time.sleep(2)

        print("\n✓ Web提醒测试完成")


if __name__ == "__main__":
    print("=== Web提醒器独立测试 ===\n")
    print("提示：Web提醒器需要在Flask应用中运行")
    print("     请使用 python app.py 启动完整Web服务器")
