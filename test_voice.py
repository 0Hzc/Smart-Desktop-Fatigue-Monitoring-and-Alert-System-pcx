#!/usr/bin/env python3
"""
语音模块测试脚本
快速验证espeak语音功能是否正常
"""

import sys
import shutil

def test_espeak_installation():
    """测试espeak是否安装"""
    print("=" * 50)
    print("检查espeak安装状态")
    print("=" * 50)

    espeak_path = shutil.which('espeak')
    if espeak_path:
        print(f"✅ espeak已安装: {espeak_path}")
        return True
    else:
        print("❌ espeak未安装")
        print("\n安装方法：")
        print("  sudo apt-get update")
        print("  sudo apt-get install -y espeak espeak-data")
        return False

def test_voice_alert_import():
    """测试VoiceAlert模块导入"""
    print("\n" + "=" * 50)
    print("测试VoiceAlert模块导入")
    print("=" * 50)

    try:
        sys.path.insert(0, 'src')
        from alert.voice_alert import VoiceAlert
        print("✅ VoiceAlert模块导入成功")
        return VoiceAlert
    except Exception as e:
        print(f"❌ VoiceAlert模块导入失败: {e}")
        return None

def test_voice_alert_basic(VoiceAlert):
    """测试基本语音功能"""
    print("\n" + "=" * 50)
    print("测试基本语音功能")
    print("=" * 50)

    try:
        voice = VoiceAlert(rate=150, volume=0.9)
        print("✅ VoiceAlert初始化成功")

        print("\n播放测试语音...")
        voice.speak("Hello, this is a test.", background=False)

        print("✅ 语音播放成功")
        return True
    except Exception as e:
        print(f"❌ 语音功能测试失败: {e}")
        return False

def test_alert_types(VoiceAlert):
    """测试预定义提醒类型"""
    print("\n" + "=" * 50)
    print("测试预定义提醒类型")
    print("=" * 50)

    try:
        voice = VoiceAlert(rate=150, volume=0.9)

        alert_types = ['fatigue', 'distance', 'posture', 'severe']
        for alert_type in alert_types:
            print(f"\n测试 {alert_type} 提醒...")
            voice.speak_alert(alert_type)
            import time
            time.sleep(1)

        print("\n✅ 所有提醒类型测试成功")
        return True
    except Exception as e:
        print(f"❌ 提醒类型测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("\n" + "=" * 50)
    print("智能桌面疲劳监测系统 - 语音模块测试")
    print("=" * 50)

    results = []

    # 测试1：检查espeak安装
    results.append(("espeak安装", test_espeak_installation()))

    if not results[0][1]:
        print("\n⚠️  espeak未安装，跳过后续测试")
        print_summary(results)
        return

    # 测试2：导入VoiceAlert模块
    VoiceAlert = test_voice_alert_import()
    results.append(("VoiceAlert导入", VoiceAlert is not None))

    if VoiceAlert is None:
        print_summary(results)
        return

    # 测试3：基本语音功能
    results.append(("基本语音功能", test_voice_alert_basic(VoiceAlert)))

    # 测试4：预定义提醒类型
    results.append(("预定义提醒", test_alert_types(VoiceAlert)))

    # 打印总结
    print_summary(results)

def print_summary(results):
    """打印测试总结"""
    print("\n" + "=" * 50)
    print("测试总结")
    print("=" * 50)

    for test_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name:20s}: {status}")

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    print(f"\n总计: {passed_count}/{total_count} 测试通过")

    if passed_count == total_count:
        print("\n🎉 所有测试通过！语音功能正常。")
    else:
        print("\n⚠️  部分测试失败，请检查错误信息。")

if __name__ == "__main__":
    main()
