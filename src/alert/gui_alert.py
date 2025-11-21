"""
GUI弹窗提醒模块
功能：使用Tkinter创建美观的提醒弹窗
如果tkinter不可用，自动降级为print模拟模式
"""

# 尝试导入tkinter，如果不可用则使用模拟模式
try:
    import tkinter as tk
    from tkinter import messagebox
    TKINTER_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    TKINTER_AVAILABLE = False
    print("注意：tkinter不可用，GUI提醒将在模拟模式下运行（使用print输出）")

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
        self.simulate = not TKINTER_AVAILABLE

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

        if self.simulate:
            print("✓ GUI提醒器初始化成功（模拟模式）")
            print("  - 模式: print输出模拟")
        else:
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
        if self.simulate:
            # 模拟模式：使用print输出
            self._simulate_alert(alert_type, message, level)
        else:
            # 实际模式：显示GUI窗口
            # 确定样式
            level_name = 'info' if level.value == 1 else ('warning' if level.value == 2 else 'critical')
            color_theme = self.colors[level_name]

            # 在主线程中创建窗口
            self._create_alert_window(message, color_theme, level_name)

    def _simulate_alert(self, alert_type, message: str, level):
        """模拟GUI提醒（使用print）"""
        level_name = 'INFO' if level.value == 1 else ('WARNING' if level.value == 2 else 'CRITICAL')
        icon = self.icons.get('info' if level.value == 1 else ('warning' if level.value == 2 else 'critical'), '⚠️')

        print("\n" + "=" * 60)
        print(f"[GUI提醒模拟] {icon} {level_name}")
        print("=" * 60)
        print(f"类型: {alert_type.value if hasattr(alert_type, 'value') else alert_type}")
        print(f"消息: {message}")
        print("=" * 60 + "\n")

    def _create_alert_window(self, message: str, color_theme: dict, level_name: str):
        """创建提醒窗口"""
        if self.simulate:
            return

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
            justify='center'
        )
        message_label.pack(pady=(0, 20))

        # 确定按钮
        close_button = tk.Button(
            window,
            text="OK",
            font=("Arial", 12, "bold"),
            bg=color_theme['fg'],
            fg='white',
            activebackground=color_theme['fg'],
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            width=10,
            command=window.destroy
        )
        close_button.pack(pady=(0, 20))

        # 自动关闭
        if self.auto_close_delay > 0:
            window.after(int(self.auto_close_delay * 1000), window.destroy)

        # 居中显示
        window.update_idletasks()
        x = (window.winfo_screenwidth() // 2) - (window.winfo_width() // 2)
        y = (window.winfo_screenheight() // 2) - (window.winfo_height() // 2)
        window.geometry(f"+{x}+{y}")

    def close_current(self):
        """关闭当前打开的提醒窗口"""
        if self.simulate:
            print("[GUI提醒模拟] 关闭提醒窗口")
            return

        if self.current_window:
            try:
                self.current_window.destroy()
                self.current_window = None
            except:
                pass

    def cleanup(self):
        """清理资源"""
        self.close_current()
        if not self.simulate:
            print("✓ GUI提醒器已清理")


def test_gui_alert():
    """测试GUI提醒器"""
    print("=== GUI提醒器测试 ===\n")

    # 初始化
    gui = GUIAlert(auto_close_delay=3.0)

    if TKINTER_AVAILABLE:
        # 创建主窗口（tkinter需要主窗口）
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口

    print("\n测试不同级别的提醒...")

    # 测试信息级别
    print("\n1. 测试信息级别提醒")
    from alert.alert_manager import AlertType, AlertLevel
    gui.show(AlertType.FATIGUE, "This is a test information message", AlertLevel.INFO)
    time.sleep(4)

    # 测试警告级别
    print("\n2. 测试警告级别提醒")
    gui.show(AlertType.DISTANCE, "This is a test warning message", AlertLevel.WARNING)
    time.sleep(4)

    # 测试严重级别
    print("\n3. 测试严重级别提醒")
    gui.show(AlertType.POSTURE, "This is a test critical message", AlertLevel.CRITICAL)
    time.sleep(4)

    # 清理
    gui.cleanup()

    if TKINTER_AVAILABLE:
        root.destroy()

    print("\n✓ 测试完成")


if __name__ == "__main__":
    test_gui_alert()
