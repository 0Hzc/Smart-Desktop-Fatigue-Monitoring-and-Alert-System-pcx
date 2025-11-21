#!/bin/bash

# ============================================
# 智能桌面疲劳监测系统
# Ubuntu系统依赖自动安装脚本
# 适用于：Ubuntu 20.04+ / 树莓派OS
# ============================================

echo "============================================"
echo "智能桌面疲劳监测系统 - Ubuntu依赖安装"
echo "============================================"
echo ""

# 检查是否以root权限运行
if [ "$EUID" -eq 0 ]; then
   echo "⚠️  警告：请不要使用root用户运行此脚本"
   echo "正确用法：./install_ubuntu_deps.sh"
   exit 1
fi

# 检查Ubuntu版本
echo "📋 检查系统信息..."
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "操作系统: $NAME $VERSION"
else
    echo "⚠️  警告：无法识别操作系统版本"
fi

# 检查Python版本
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python版本: $PYTHON_VERSION"

# 检查glibc版本（mediapipe需要2.31+）
GLIBC_VERSION=$(ldd --version | head -n1 | awk '{print $NF}')
echo "glibc版本: $GLIBC_VERSION"
echo ""

# 询问用户确认
read -p "是否继续安装系统依赖？(y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "安装已取消"
    exit 0
fi

echo ""
echo "开始安装系统依赖..."
echo "============================================"

# 1. 更新软件源
echo ""
echo "📦 [1/7] 更新软件源..."
sudo apt-get update

# 2. 安装编译工具链
echo ""
echo "🔧 [2/7] 安装编译工具链..."
sudo apt-get install -y build-essential python3-dev python3-pip cmake pkg-config
if [ $? -eq 0 ]; then
    echo "✅ 编译工具链安装完成"
else
    echo "❌ 编译工具链安装失败"
    exit 1
fi

# 3. 安装OpenCV系统依赖
echo ""
echo "🎨 [3/7] 安装OpenCV系统依赖..."
sudo apt-get install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 libgtk-3-0
if [ $? -eq 0 ]; then
    echo "✅ OpenCV系统依赖安装完成"
else
    echo "❌ OpenCV系统依赖安装失败"
    exit 1
fi

# 4. 安装摄像头支持
echo ""
echo "📷 [4/7] 安装摄像头支持..."
sudo apt-get install -y v4l-utils libv4l-dev
if [ $? -eq 0 ]; then
    echo "✅ 摄像头支持安装完成"
else
    echo "❌ 摄像头支持安装失败"
    exit 1
fi

# 5. 安装音频系统
echo ""
echo "🔊 [5/7] 安装音频系统（语音播报）..."
sudo apt-get install -y espeak espeak-data libespeak-dev libportaudio2 portaudio19-dev alsa-utils pulseaudio
if [ $? -eq 0 ]; then
    echo "✅ 音频系统安装完成"
else
    echo "❌ 音频系统安装失败"
    exit 1
fi

# 6. 安装科学计算库依赖
echo ""
echo "🔬 [6/7] 安装科学计算库依赖..."
sudo apt-get install -y libatlas-base-dev libhdf5-dev
if [ $? -eq 0 ]; then
    echo "✅ 科学计算库依赖安装完成"
else
    echo "❌ 科学计算库依赖安装失败"
    exit 1
fi

# 7. 清理
echo ""
echo "🧹 [7/7] 清理缓存..."
sudo apt-get autoremove -y
sudo apt-get autoclean
echo "✅ 清理完成"

echo ""
echo "============================================"
echo "✅ 所有系统依赖安装完成！"
echo "============================================"
echo ""

# 检查摄像头设备
echo "📷 检查摄像头设备..."
if ls /dev/video* 1> /dev/null 2>&1; then
    echo "✅ 检测到摄像头设备："
    ls /dev/video*
else
    echo "⚠️  未检测到摄像头设备"
    echo "如果您有USB摄像头，请确保已连接并重新插拔"
fi

echo ""
echo "📋 下一步操作："
echo "1. 创建Python虚拟环境："
echo "   python3 -m venv venv"
echo "   source venv/bin/activate"
echo ""
echo "2. 升级pip："
echo "   pip install --upgrade pip"
echo ""
echo "3. 安装Python依赖："
echo "   pip install -r requirements.txt"
echo ""
echo "4. 测试安装："
echo "   python -c \"import cv2; import mediapipe; import flask; print('✅ 所有依赖安装成功！')\""
echo ""
echo "============================================"
