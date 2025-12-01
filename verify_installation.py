#!/usr/bin/env python3
"""
安装验证脚本
验证所有依赖是否正确安装
"""

import sys
import shutil

def check_python_version():
    """检查Python版本"""
    print("=" * 60)
    print("检查Python版本")
    print("=" * 60)

    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    print(f"Python版本: {version_str}")

    if version.major == 3 and version.minor >= 8:
        print("✅ Python版本符合要求（3.8+）")
        return True
    else:
        print("❌ Python版本过低，需要3.8或更高版本")
        return False

def check_python_packages():
    """检查Python包"""
    print("\n" + "=" * 60)
    print("检查Python包")
    print("=" * 60)

    packages = {
        'cv2': 'opencv-python',
        'mediapipe': 'mediapipe',
        'numpy': 'numpy',
        'flask': 'Flask',
        'flask_socketio': 'Flask-SocketIO',
        'socketio': 'python-socketio',
        'engineio': 'python-engineio',
        'yaml': 'PyYAML'
        # 'scipy': 'scipy'  # 已移除：当前代码未使用
    }

    results = []
    for module_name, package_name in packages.items():
        try:
            module = __import__(module_name)
            version = getattr(module, '__version__', 'unknown')
            print(f"✅ {package_name:20s} : {version}")
            results.append(True)
        except ImportError:
            print(f"❌ {package_name:20s} : 未安装")
            results.append(False)

    return all(results)

def check_system_dependencies():
    """检查系统依赖"""
    print("\n" + "=" * 60)
    print("检查系统依赖")
    print("=" * 60)

    dependencies = {
        'espeak': 'espeak（语音合成）',
        'v4l2-ctl': 'v4l-utils（摄像头工具）',
    }

    results = []
    for cmd, description in dependencies.items():
        path = shutil.which(cmd)
        if path:
            print(f"✅ {description:30s} : {path}")
            results.append(True)
        else:
            print(f"❌ {description:30s} : 未安装")
            results.append(False)

    return all(results)

def check_camera_devices():
    """检查摄像头设备"""
    print("\n" + "=" * 60)
    print("检查摄像头设备")
    print("=" * 60)

    import os
    import glob

    video_devices = glob.glob('/dev/video*')

    if video_devices:
        print(f"✅ 检测到 {len(video_devices)} 个视频设备:")
        for device in video_devices:
            print(f"   - {device}")
        return True
    else:
        print("❌ 未检测到摄像头设备")
        print("   请检查摄像头是否正确连接")
        return False

def test_opencv_camera():
    """测试OpenCV摄像头访问"""
    print("\n" + "=" * 60)
    print("测试OpenCV摄像头访问")
    print("=" * 60)

    try:
        import cv2
        cap = cv2.VideoCapture(0)

        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                h, w = frame.shape[:2]
                print(f"✅ 摄像头访问成功")
                print(f"   分辨率: {w}x{h}")
                cap.release()
                return True
            else:
                print("❌ 无法读取摄像头帧")
                cap.release()
                return False
        else:
            print("❌ 无法打开摄像头")
            return False
    except Exception as e:
        print(f"❌ 摄像头测试失败: {e}")
        return False

def test_mediapipe():
    """测试MediaPipe"""
    print("\n" + "=" * 60)
    print("测试MediaPipe人脸检测")
    print("=" * 60)

    try:
        import mediapipe as mp
        mp_face_mesh = mp.solutions.face_mesh

        face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            min_detection_confidence=0.5
        )

        print("✅ MediaPipe初始化成功")
        face_mesh.close()
        return True
    except Exception as e:
        print(f"❌ MediaPipe测试失败: {e}")
        return False

def print_summary(results):
    """打印总结"""
    print("\n" + "=" * 60)
    print("验证总结")
    print("=" * 60)

    test_names = [
        "Python版本",
        "Python包",
        "系统依赖",
        "摄像头设备",
        "OpenCV摄像头",
        "MediaPipe"
    ]

    for name, passed in zip(test_names, results):
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name:20s}: {status}")

    passed_count = sum(results)
    total_count = len(results)

    print(f"\n总计: {passed_count}/{total_count} 检查通过")

    if passed_count == total_count:
        print("\n🎉 所有依赖安装正确！系统可以正常运行。")
        print("\n下一步:")
        print("  python main.py    # 运行主程序（传统GUI模式）")
        print("  python app.py     # 运行Web服务器模式")
    else:
        print("\n⚠️  部分依赖未正确安装，请根据上述错误信息进行修复。")
        print("\n建议:")
        print("  1. 运行 ./install_ubuntu_deps.sh 安装系统依赖")
        print("  2. 运行 pip install -r requirements.txt 安装Python包")
        print("  3. 重新运行此验证脚本")

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("智能桌面疲劳监测系统 - 安装验证")
    print("=" * 60)
    print()

    results = []

    # 1. 检查Python版本
    results.append(check_python_version())

    # 2. 检查Python包
    results.append(check_python_packages())

    # 3. 检查系统依赖
    results.append(check_system_dependencies())

    # 4. 检查摄像头设备
    results.append(check_camera_devices())

    # 5. 测试OpenCV摄像头
    results.append(test_opencv_camera())

    # 6. 测试MediaPipe
    results.append(test_mediapipe())

    # 打印总结
    print_summary(results)

if __name__ == "__main__":
    main()
