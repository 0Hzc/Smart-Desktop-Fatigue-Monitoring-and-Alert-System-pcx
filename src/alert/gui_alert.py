"""
GUI弹窗提醒模块
功能：使用Tkinter创建美观的提醒弹窗
"""

import tkinter as tk
from tkinter import messagebox
from threading import Thread
import time


class GUIAlert:
    """GUI提醒器类"""

    def __init__(self, auto_close_delay: float = 5.0):
        """
        初始化GUI提醒器

        Args:
            auto_close_delay: 自动关闭延迟（秒），0表示不自动关闭
        """
        self.auto_close_delay = auto_close_delay
        self.current_window = None

        # 颜色主题
        self.colors = {
            'info': {'bg': '#D4EDFF', 'fg': '#003D82', 'title': 'Information'},
            'warning': {'bg': '#FFF4CE', 'fg': '#7D5C00', 'title': 'Warning'},
            'critical': {'bg': '#FFE0E0', 'fg': '#8B0000', 'title': 'Critical Alert'}
        }

        # 提醒图标（使用文字符号）
        self.icons = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'critical': '🚨'
        }

        # 提醒消息模板
        self.messages = {
            'fatigue': "Fatigue Detected!\n\nYou appear tired. Please take a break to rest your eyes and body.",
            'distance': "Too Close to Screen!\n\nYou are sitting too close. Please move back to protect your eyesight.",
            'posture': "Poor Posture Detected!\n\nPlease sit up straight to avoid back and neck problems.",
            'severe': "Severe Fatigue Warning!\n\nImmediate rest required! You've been working too long without a break."
        }

        print("✓ GUI提醒器初始化成功")
        print(f"  - 自动关闭延迟: {auto_close_delay}秒" if auto_close_delay > 0 else "  - 手动关闭模式")

    def show(self, alert_type, message: str, level):
        """
        显示提醒窗口

        Args:
            alert_type: 提醒类型
            message: 提醒消息
            level: 提醒级别
        """
        # 确定样式
        level_name = 'info' if level.value == 1 else ('warning' if level.value == 2 else 'critical')
        color_theme = self.colors[level_name]

        # 在主线程中创建窗口
        self._create_alert_window(message, color_theme, level_name)

    def _create_alert_window(self, message: str, color_theme: dict, level_name: str):
        """创建提醒窗口"""
        # 创建顶层窗口
        window = tk.Toplevel()
        self.current_window = window

        window.title(color_theme['title'])
        window.geometry("400x250")
        window.resizable(False, False)

        # 窗口置顶
        window.attributes('-topmost', True)

        # 设置背景颜色
        window.configure(bg=color_theme['bg'])

        # 图标标签
        icon_label = tk.Label(
            window,
            text=self.icons[level_name],
            font=("Arial", 48),
            bg=color_theme['bg'],
            fg=color_theme['fg']
        )
        icon_label.pack(pady=(20, 10))

        # 消息标签
        message_label = tk.Label(
            window,
            text=message,
            font=("Arial", 12),
            bg=color_theme['bg'],
            fg=color_theme['fg'],
            wraplength=350,
            justify=tk.CENTER
        )
        message_label.pack(pady=10)

        # 关闭按钮
        close_button = tk.Button(
            window,
            text="I Understand",
            command=window.destroy,
            font=("Arial", 11, "bold"),
            bg=color_theme['fg'],
            fg="white",
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2"
        )
        close_button.pack(pady=20)

        # 自动关闭计时器
        if self.auto_close_delay > 0:
            window.after(int(self.auto_close_delay * 1000), window.destroy)

        # 居中显示
        window.update_idletasks()
        x = (window.winfo_screenwidth() // 2) - (window.winfo_width() // 2)
        y = (window.winfo_screenheight() // 2) - (window.winfo_height() // 2)
        window.geometry(f"+{x}+{y}")

        print(f"✓ GUI提醒窗口已显示: {message[:30]}...")

    def show_simple_message(self, title: str, message: str, msg_type: str = "info"):
        """
        显示简单消息框（阻塞式）

        Args:
            title: 标题
            message: 消息
            msg_type: 消息类型（'info', 'warning', 'error'）
        """
        if msg_type == "info":
            messagebox.showinfo(title, message)
        elif msg_type == "warning":
            messagebox.showwarning(title, message)
        elif msg_type == "error":
            messagebox.showerror(title, message)

    def test(self):
        """测试GUI提醒"""
        print("\n=== GUI提醒器测试 ===\n")

        # 创建根窗口（隐藏）
        root = tk.Tk()
        root.withdraw()

        from alert_manager import AlertType, AlertLevel

        # 测试不同级别的提醒
        test_cases = [
            (AlertType.FATIGUE, self.messages['fatigue'], AlertLevel.WARNING),
            (AlertType.DISTANCE, self.messages['distance'], AlertLevel.WARNING),
            (AlertType.POSTURE, self.messages['posture'], AlertLevel.WARNING),
            (AlertType.FATIGUE, self.messages['severe'], AlertLevel.CRITICAL)
        ]

        for i, (alert_type, message, level) in enumerate(test_cases, 1):
            print(f"\n测试 {i}/{len(test_cases)}: {alert_type.value}")
            self.show(alert_type, message, level)
            time.sleep(self.auto_close_delay + 1)

        root.destroy()
        print("\n✓ GUI测试完成")


def test_gui_alert():
    """测试GUI提醒器"""
    print("=== GUI提醒器独立测试 ===\n")

    # 初始化
    gui = GUIAlert(auto_close_delay=3.0)

    # 运行测试
    gui.test()

    print("\n测试结束")


if __name__ == "__main__":
    test_gui_alert()
