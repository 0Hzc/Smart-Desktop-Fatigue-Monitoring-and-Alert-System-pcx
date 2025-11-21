# Ubuntu系统依赖安装指南

## 📋 系统要求

### 推荐配置

| 项目 | 要求 | 说明 |
|------|------|------|
| **操作系统** | Ubuntu 20.04+ | Ubuntu 18.04部分兼容 |
| **Python版本** | 3.8+ | 推荐3.8或3.10 |
| **glibc版本** | 2.31+ | mediapipe要求 |
| **内存** | 4GB+ | 推荐8GB |
| **存储空间** | 2GB+ | 用于依赖包 |
| **摄像头** | USB/CSI | 支持Video4Linux |

### 兼容性测试

| Ubuntu版本 | Python | 测试结果 | 备注 |
|-----------|--------|---------|------|
| Ubuntu 18.04 | 3.6 | ⚠️ 部分兼容 | mediapipe可能不支持 |
| **Ubuntu 20.04** | **3.8** | ✅ **完全兼容** | **推荐** |
| Ubuntu 22.04 | 3.10 | ✅ 完全兼容 | 所有功能正常 |
| Ubuntu 24.04 | 3.12 | ⚠️ 测试中 | 部分包可能需要更新 |

---

## 🚀 快速安装（推荐）

### 方法1：使用自动化脚本

```bash
# 1. 进入项目目录
cd Smart-Desktop-Fatigue-Monitoring-and-Alert-System-pcx

# 2. 运行安装脚本
./install_ubuntu_deps.sh

# 3. 按照提示完成安装
```

### 方法2：手动安装

按照以下步骤逐步安装所有依赖。

---

## 📦 详细安装步骤

### 步骤1：更新软件源

```bash
sudo apt-get update
```

**说明**：更新软件包索引，确保安装最新版本的软件。

---

### 步骤2：安装编译工具链（必需）

```bash
sudo apt-get install -y build-essential python3-dev python3-pip cmake pkg-config
```

**包含内容**：
- `build-essential` - GCC编译器、make等基本编译工具
- `python3-dev` - Python头文件，用于编译Python C扩展
- `python3-pip` - Python包管理器
- `cmake` - 跨平台构建工具
- `pkg-config` - 管理库的编译和链接参数

**为什么需要**：numpy、scipy等科学计算包可能需要从源码编译。

---

### 步骤3：安装OpenCV系统依赖（必需）

```bash
sudo apt-get install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 libgtk-3-0
```

**包含内容**：
- `libgl1-mesa-glx` - OpenGL图形库（解决libGL.so.1错误）
- `libglib2.0-0` - GLib库
- `libsm6, libxext6, libxrender-dev` - X11图形库
- `libgomp1` - OpenMP多线程支持
- `libgtk-3-0` - GTK图形界面库

**为什么需要**：opencv-python需要这些库来显示图像窗口和进行图形处理。

---

### 步骤4：安装摄像头支持（必需）

```bash
sudo apt-get install -y v4l-utils libv4l-dev
```

**包含内容**：
- `v4l-utils` - Video4Linux工具集，用于测试摄像头
- `libv4l-dev` - 摄像头驱动开发库

**为什么需要**：Linux下的摄像头访问依赖Video4Linux(V4L2)。

**测试摄像头**：
```bash
# 列出所有摄像头设备
ls /dev/video*

# 查看摄像头信息
v4l2-ctl --list-devices

# 测试摄像头捕获
v4l2-ctl --device=/dev/video0 --list-formats-ext
```

---

### 步骤5：安装音频系统（语音播报功能需要）

```bash
sudo apt-get install -y espeak espeak-data libespeak-dev libportaudio2 portaudio19-dev alsa-utils pulseaudio
```

**包含内容**：
- `espeak` - 文本转语音引擎（pyttsx3的Linux后端）
- `espeak-data` - espeak语音数据
- `libespeak-dev` - espeak开发库
- `libportaudio2, portaudio19-dev` - 音频I/O库
- `alsa-utils` - ALSA音频工具
- `pulseaudio` - PulseAudio音频服务器

**为什么需要**：pyttsx3在Linux上依赖espeak进行语音合成。

**测试音频**：
```bash
# 测试espeak
espeak "Hello, this is a test"

# 测试音频输出
speaker-test -c 2 -t wav
```

---

### 步骤6：安装科学计算库依赖（scipy需要）

```bash
sudo apt-get install -y libatlas-base-dev libhdf5-dev
```

**包含内容**：
- `libatlas-base-dev` - BLAS/LAPACK线性代数库
- `libhdf5-dev` - HDF5数据格式库

**为什么需要**：scipy需要BLAS/LAPACK进行矩阵运算优化。

---

### 步骤7：清理系统

```bash
sudo apt-get autoremove -y
sudo apt-get autoclean
```

**说明**：清理不再需要的软件包和缓存，释放磁盘空间。

---

## 🐍 Python依赖安装

### 1. 创建虚拟环境（推荐）

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 验证虚拟环境
which python  # 应该显示 .../venv/bin/python
```

**为什么使用虚拟环境**：
- 隔离项目依赖，避免版本冲突
- 不污染系统Python环境
- 方便管理和迁移

### 2. 升级pip

```bash
pip install --upgrade pip
```

### 3. 安装项目依赖

```bash
pip install -r requirements.txt
```

**预计安装时间**：5-10分钟（取决于网络速度）

### 4. 验证安装

```bash
python -c "import cv2; print('OpenCV版本:', cv2.__version__)"
python -c "import mediapipe; print('MediaPipe版本:', mediapipe.__version__)"
python -c "import flask; print('Flask版本:', flask.__version__)"
python -c "import numpy; print('NumPy版本:', numpy.__version__)"
python -c "import scipy; print('SciPy版本:', scipy.__version__)"
```

**一键测试**：
```bash
python -c "import cv2, mediapipe, flask, numpy, scipy, pyttsx3; print('✅ 所有依赖安装成功！')"
```

---

## 🔧 常见问题排查

### 问题1：ImportError: libGL.so.1: cannot open shared object file

**错误信息**：
```
ImportError: libGL.so.1: cannot open shared object file: No such file or directory
```

**原因**：缺少OpenGL图形库

**解决方案**：
```bash
sudo apt-get install -y libgl1-mesa-glx
```

---

### 问题2：摄像头无法打开

**错误信息**：
```
[ WARN:0] global /opencv/modules/videoio/src/cap_v4l.cpp (802) open VIDEOIO(V4L2:/dev/video0): can't open camera by index
```

**排查步骤**：

1. **检查摄像头设备**：
```bash
ls /dev/video*
# 如果没有输出，说明系统未识别摄像头
```

2. **检查摄像头权限**：
```bash
# 查看当前用户所属组
groups

# 将当前用户添加到video组
sudo usermod -a -G video $USER

# 重新登录使权限生效
# 或者使用：newgrp video
```

3. **测试摄像头**：
```bash
# 使用v4l2查看摄像头信息
v4l2-ctl --list-devices

# 查看支持的分辨率和格式
v4l2-ctl --device=/dev/video0 --list-formats-ext
```

4. **使用OpenCV测试**：
```python
import cv2
cap = cv2.VideoCapture(0)
if cap.isOpened():
    print("✅ 摄像头打开成功")
    ret, frame = cap.read()
    if ret:
        print(f"✅ 读取帧成功，分辨率：{frame.shape}")
    else:
        print("❌ 无法读取帧")
    cap.release()
else:
    print("❌ 无法打开摄像头")
```

---

### 问题3：pyttsx3语音播报无声音

**错误信息**：
- 程序运行无报错，但听不到声音
- 或报错：`RuntimeError: driver not found`

**排查步骤**：

1. **检查espeak安装**：
```bash
which espeak
# 应该显示：/usr/bin/espeak

# 测试espeak
espeak "Hello, this is a test"
```

2. **检查音频设备**：
```bash
# 测试音频输出
speaker-test -c 2 -t wav

# 调整音量
alsamixer
```

3. **检查pyttsx3驱动**：
```python
import pyttsx3

# 列出可用驱动
engine = pyttsx3.init()
print("驱动名称:", engine._driverName)
```

4. **手动指定espeak驱动**：
```python
import pyttsx3
engine = pyttsx3.init('espeak')  # 明确指定espeak驱动
engine.say("Hello World")
engine.runAndWait()
```

---

### 问题4：mediapipe导入失败

**错误信息**：
```
ImportError: /lib/x86_64-linux-gnu/libc.so.6: version `GLIBC_2.34' not found
```

**原因**：glibc版本过低（mediapipe需要glibc 2.31+）

**检查glibc版本**：
```bash
ldd --version
# 输出第一行显示glibc版本
```

**解决方案**：
- **Ubuntu 18.04**：glibc 2.27 → ❌ 不支持，建议升级到Ubuntu 20.04
- **Ubuntu 20.04**：glibc 2.31 → ✅ 支持
- **Ubuntu 22.04**：glibc 2.35 → ✅ 支持

**升级Ubuntu版本**（不推荐，建议全新安装）：
```bash
# 备份重要数据后执行
sudo do-release-upgrade
```

---

### 问题5：Flask Web界面无法从其他设备访问

**现象**：在本机可以访问`http://localhost:5000`，但从手机/平板无法访问

**排查步骤**：

1. **检查Flask是否监听所有接口**：
```python
# 确保使用 host='0.0.0.0'
app.run(host='0.0.0.0', port=5000)
```

2. **检查防火墙**：
```bash
# 查看防火墙状态
sudo ufw status

# 允许5000端口
sudo ufw allow 5000

# 或临时关闭防火墙（仅用于测试）
sudo ufw disable
```

3. **获取本机IP地址**：
```bash
# 查看IP地址
ip addr show
# 或
hostname -I
```

4. **从其他设备测试**：
```bash
# 在手机浏览器输入：
http://192.168.1.xxx:5000
# 替换192.168.1.xxx为上一步获取的IP地址
```

---

### 问题6：pip安装速度慢

**解决方案**：使用国内镜像源

**临时使用**：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**永久配置**：
```bash
# 创建pip配置目录
mkdir -p ~/.pip

# 编辑配置文件
cat > ~/.pip/pip.conf << EOF
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF
```

**国内镜像源列表**：
- 清华大学：https://pypi.tuna.tsinghua.edu.cn/simple
- 阿里云：https://mirrors.aliyun.com/pypi/simple
- 中科大：https://pypi.mirrors.ustc.edu.cn/simple

---

### 问题7：scipy安装失败

**错误信息**：
```
ERROR: Failed building wheel for scipy
```

**原因**：缺少BLAS/LAPACK库

**解决方案**：
```bash
# 安装BLAS/LAPACK
sudo apt-get install -y libatlas-base-dev gfortran

# 清理pip缓存
pip cache purge

# 重新安装scipy
pip install scipy==1.11.4
```

---

## 🍓 树莓派特殊配置

### 硬件要求

- **型号**：树莓派4B（推荐4GB/8GB内存版本）
- **系统**：树莓派OS（Bullseye 64位推荐）
- **存储**：16GB+ MicroSD卡（推荐Class 10或更高）

### 摄像头配置

#### CSI摄像头（树莓派官方摄像头）

1. **物理连接**：
   - 将CSI排线正确插入树莓派摄像头接口
   - 注意排线金属触点朝向

2. **启用摄像头**：
```bash
sudo raspi-config
# 选择：3 Interface Options → I1 Camera → Yes
```

3. **重启生效**：
```bash
sudo reboot
```

4. **测试摄像头**：
```bash
# 使用libcamera测试（树莓派OS Bullseye+）
libcamera-hello

# 或使用raspistill
raspistill -o test.jpg

# 检查摄像头设备
ls /dev/video*
```

#### USB摄像头

USB摄像头无需特殊配置，即插即用。

### GPIO配置

```bash
# 添加用户到gpio组
sudo usermod -a -G gpio $USER

# 安装RPi.GPIO（取消requirements.txt中的注释）
pip install RPi.GPIO==0.7.1

# 测试GPIO
python -c "import RPi.GPIO as GPIO; print('GPIO版本:', GPIO.VERSION)"
```

### 性能优化建议

1. **降低分辨率**：
```yaml
# config.yaml
camera:
  resolution:
    width: 480  # 从640降低到480
    height: 360  # 从480降低到360
```

2. **启用跳帧**：
```yaml
# config.yaml
performance:
  skip_frames: 2  # 每处理1帧跳过2帧
```

3. **超频（可选，注意散热）**：
```bash
sudo raspi-config
# Performance Options → Overclock
```

---

## ✅ 验证清单

安装完成后，请逐项检查：

- [ ] 系统依赖全部安装成功
- [ ] Python虚拟环境已创建并激活
- [ ] 所有Python包安装成功
- [ ] 导入测试无报错
- [ ] 摄像头设备可识别（`ls /dev/video*`）
- [ ] 摄像头可打开（OpenCV测试）
- [ ] espeak语音测试成功
- [ ] 音频输出正常
- [ ] Web服务器可启动
- [ ] 局域网可访问Web界面（如适用）

---

## 📚 参考资料

- [OpenCV官方文档](https://docs.opencv.org/)
- [MediaPipe官方文档](https://google.github.io/mediapipe/)
- [Flask官方文档](https://flask.palletsprojects.com/)
- [pyttsx3文档](https://pyttsx3.readthedocs.io/)
- [树莓派官方文档](https://www.raspberrypi.org/documentation/)

---

## 💬 获取帮助

如果遇到本文档未涵盖的问题，请：

1. 检查错误日志，定位具体问题
2. 搜索错误信息，查找解决方案
3. 在项目GitHub Issues中提问
4. 提供详细的错误信息和系统环境

---

**最后更新**：2024年11月
**维护者**：项目开发团队
