# 树莓派 4B 部署指南

## 📋 目录
- [系统要求](#系统要求)
- [硬件准备](#硬件准备)
- [部署步骤](#部署步骤)
- [运行系统](#运行系统)
- [常见问题](#常见问题)
- [性能优化](#性能优化)

---

## 系统要求

### 硬件配置
- **树莓派**: 树莓派 4B（已确认）
- **摄像头**: OV5647 (树莓派官方 Camera Module v1) ✅ 已连接并正常工作
- **系统**: 树莓派 OS (Debian Trixie/Bookworm) ✅ 已安装
- **存储**: MicroSD 卡（≥32GB）
- **内存**: 建议 4GB 或以上

### 软件配置
- **Python**: 3.9+
- **驱动**: libcamera（已加载）✅
- **摄像头工具**: rpicam-* 命令和 picamera2 库

### 你的摄像头状态 ✅
根据你提供的信息，摄像头已完全就绪：
- ✅ OV5647 摄像头正常工作
- ✅ libcamera 驱动已加载
- ✅ 可使用 `rpicam-still`、`rpicam-hello`、`rpicam-vid` 命令
- ✅ 支持 Python picamera2 库
- ✅ 支持分辨率: 640x480, 1296x972, 1920x1080, 2592x1944

---

## 硬件准备

### 1. 摄像头连接确认
你的摄像头已连接好，可以跳过此步骤。如需确认：

```bash
# 列出摄像头（✅ 你已完成）
rpicam-hello --list-cameras

# 应该看到：
# 0 : ov5647 [2592x1944] (/base/soc/i2c0mux/i2c@1/ov5647@36)
```

### 2. 可选硬件（增强提醒功能）
- **LED 灯**: 用于视觉提醒（可选）
- **蜂鸣器**: 用于声音提醒（可选）
- **扬声器/耳机**: 用于语音提醒（推荐）

---

## 部署步骤

### 步骤 1: 更新系统

```bash
# 更新软件包列表
sudo apt-get update

# 升级已安装的软件包
sudo apt-get upgrade -y

# 确认 Python 版本（应该是 3.9+）
python3 --version
```

### 步骤 2: 安装系统依赖

```bash
# 安装编译工具链
sudo apt-get install -y build-essential python3-dev python3-pip cmake pkg-config

# 安装 OpenCV 系统依赖
sudo apt-get install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 libgtk-3-0

# 安装摄像头支持工具
sudo apt-get install -y v4l-utils libv4l-dev

# 安装音频系统（语音提醒）
sudo apt-get install -y espeak espeak-data libespeak-dev alsa-utils pulseaudio

# 清理
sudo apt-get autoremove -y && sudo apt-get autoclean
```

### 步骤 3: 克隆项目代码

```bash
# 进入工作目录
cd ~

# 克隆项目（从你的分支）
git clone <你的仓库地址> fatigue-monitor
cd fatigue-monitor

# 切换到正确的分支
git checkout claude/review-project-plan-01HbXoRc4U8EzYeKMA6bxPxz
```

### 步骤 4: 创建 Python 虚拟环境（推荐）

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级 pip
pip install --upgrade pip
```

### 步骤 5: 安装 Python 依赖

```bash
# 安装核心依赖（使用清华镜像加速）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 安装树莓派专用库
pip install picamera2 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**⚠️ 注意**: 如果 `pip install picamera2` 失败，可以使用系统包：

```bash
# 安装系统版本的 picamera2
sudo apt-get install -y python3-picamera2

# 或者使用 OpenCV 模式（无需 picamera2）
```

### 步骤 6: 验证安装

```bash
# 运行验证脚本
python verify_installation.py

# 你应该看到所有依赖都安装成功的提示
```

### 步骤 7: 配置摄像头

根据你的摄像头类型，修改 `config.yaml`：

```bash
# 编辑配置文件
nano config.yaml
```

**对于你的 OV5647 摄像头，推荐配置：**

```yaml
camera:
  resolution:
    width: 640      # 推荐 640x480，性能最佳
    height: 480
  fps: 30
  flip: false        # 如果画面倒置，改为 true
```

**⚠️ 重要**: 项目会自动检测并使用 picamera2，如果失败会回退到 OpenCV 模式。

### 步骤 8: 测试摄像头

#### 方式 1: 使用 rpicam 命令测试（推荐）

```bash
# 拍一张测试照片
rpicam-still -o test_photo.jpg

# 预览 5 秒
rpicam-hello -t 5000
```

#### 方式 2: 使用项目代码测试

```bash
# 测试摄像头模块
cd ~/fatigue-monitor
source venv/bin/activate
python src/camera/camera_capture.py
```

如果看到摄像头画面，说明配置成功！按 `q` 退出。

---

## 运行系统

项目提供两种运行模式：

### 模式 1: Web 服务器模式（推荐 ⭐）

**适用场景**:
- 树莓派无显示器
- 通过局域网访问（从电脑/手机浏览器）
- 无头模式运行

**运行步骤**:

```bash
# 1. 进入项目目录
cd ~/fatigue-monitor

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 运行 Web 服务器
python app.py
```

**访问界面**:

```
# 从树莓派本机访问
http://localhost:5000

# 从局域网其他设备访问
http://<树莓派IP地址>:5000

# 查看树莓派IP地址
hostname -I
```

**预期输出**:

```
==================================================
智能桌面疲劳监测系统 - Web版
版本: v2.0 (Web Interface)
==================================================

✓ 树莓派摄像头启动成功: 640x480
✓ Web系统初始化完成

==================================================
Web服务器启动中...
请在浏览器中访问: http://0.0.0.0:5000
局域网访问: http://<树莓派IP>:5000
按 Ctrl+C 停止服务器
==================================================
```

### 模式 2: GUI 桌面模式

**适用场景**:
- 树莓派连接了显示器
- 想在本地直接查看画面

**运行步骤**:

```bash
# 1. 进入项目目录
cd ~/fatigue-monitor

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 运行主程序
python main.py
```

**预期输出**:

```
==================================================
智能桌面疲劳监测系统
版本: v1.0
==================================================

✓ 树莓派摄像头启动成功: 640x480
✓ 系统初始化完成

启动系统...
✓ 系统运行中... 按 'Q' 键退出
```

按 `Q` 键退出程序。

---

## 常见问题

### 问题 1: 摄像头无法打开

**症状**:
```
✗ 无法打开摄像头 0
```

**解决方案**:

```bash
# 1. 检查摄像头是否被占用
sudo fuser /dev/video0

# 2. 重启摄像头服务
sudo systemctl restart libcamera

# 3. 检查摄像头权限
ls -l /dev/video*
sudo usermod -a -G video $USER
newgrp video

# 4. 重启树莓派
sudo reboot
```

### 问题 2: picamera2 导入失败

**症状**:
```
ImportError: No module named 'picamera2'
```

**解决方案 A**: 使用系统包

```bash
sudo apt-get install -y python3-picamera2
```

**解决方案 B**: 使用 OpenCV 模式

项目会自动回退到 OpenCV 模式，无需手动干预。你会看到：

```
⚠ picamera2未安装，切换到OpenCV模式
✓ 摄像头启动成功: 640x480
```

### 问题 3: MediaPipe 导入失败

**症状**:
```
ImportError: libstdc++.so.6: version `GLIBCXX_3.4.29' not found
```

**解决方案**:

```bash
# 更新系统到最新版本
sudo apt-get update && sudo apt-get upgrade -y

# 检查 glibc 版本（需要 2.31+）
ldd --version

# 如果版本过低，建议升级到 Debian Bookworm 或更新版本
```

### 问题 4: 语音播报无声音

**症状**: 系统运行正常，但听不到语音提醒。

**解决方案**:

```bash
# 1. 测试 espeak
espeak "test"

# 2. 测试音频输出
speaker-test -c 2 -t wav

# 3. 调整音量
alsamixer

# 4. 检查音频设备
aplay -l

# 5. 设置默认音频输出（如果使用 HDMI 或 3.5mm）
sudo raspi-config
# 选择: System Options -> Audio -> 选择输出设备
```

### 问题 5: Web 界面无法远程访问

**症状**: 从其他设备无法访问 `http://<树莓派IP>:5000`

**解决方案**:

```bash
# 1. 检查防火墙（如果启用）
sudo ufw status

# 2. 开放 5000 端口
sudo ufw allow 5000

# 3. 或临时关闭防火墙（仅测试用）
sudo ufw disable

# 4. 确认树莓派 IP 地址
hostname -I

# 5. 确认程序监听 0.0.0.0（而非 127.0.0.1）
# app.py 中应该有: socketio.run(app, host='0.0.0.0', port=5000)
```

### 问题 6: 帧率过低

**症状**: FPS 低于 10

**解决方案**: 参见下一节"性能优化"。

---

## 性能优化

### 优化 1: 降低分辨率

编辑 `config.yaml`:

```yaml
camera:
  resolution:
    width: 320    # 从 640 降低到 320
    height: 240   # 从 480 降低到 240
```

### 优化 2: 启用跳帧

编辑 `config.yaml`:

```yaml
performance:
  skip_frames: 2  # 每处理 1 帧，跳过 2 帧（实际帧率 = 摄像头帧率 / 3）
```

### 优化 3: 禁用不必要的功能

编辑 `config.yaml`:

```yaml
face_detection:
  refine_landmarks: false  # 禁用精细关键点（提升性能）

performance:
  display_fps: false  # 禁用 FPS 显示（轻微提升）
```

### 优化 4: 使用 picamera2 而非 OpenCV

picamera2 在树莓派上性能更好。如果当前使用 OpenCV，尝试安装 picamera2：

```bash
pip install picamera2
# 或
sudo apt-get install python3-picamera2
```

### 优化 5: 超频树莓派（高级）

**⚠️ 警告**: 超频可能导致系统不稳定，需要良好的散热。

```bash
sudo nano /boot/firmware/config.txt

# 添加以下行（树莓派 4B）
arm_freq=2000      # CPU 频率（默认 1500）
over_voltage=6     # 电压（默认 0，最大 6）
gpu_freq=750       # GPU 频率（默认 500）

# 保存后重启
sudo reboot
```

### 性能基准参考

| 配置 | 预期 FPS | 说明 |
|------|---------|------|
| 640x480 + picamera2 | 20-25 FPS | 推荐配置 ✅ |
| 640x480 + OpenCV | 15-20 FPS | 良好 |
| 320x240 + picamera2 | 30+ FPS | 最佳性能 |
| 1920x1080 + picamera2 | 8-12 FPS | 不推荐 |

---

## 开机自启动（可选）

### 方式 1: 使用 systemd 服务（推荐）

创建服务文件：

```bash
sudo nano /etc/systemd/system/fatigue-monitor.service
```

内容：

```ini
[Unit]
Description=Fatigue Monitoring System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/fatigue-monitor
Environment="PATH=/home/pi/fatigue-monitor/venv/bin"
ExecStart=/home/pi/fatigue-monitor/venv/bin/python /home/pi/fatigue-monitor/app.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启用服务：

```bash
# 重载 systemd
sudo systemctl daemon-reload

# 启用开机自启
sudo systemctl enable fatigue-monitor.service

# 立即启动服务
sudo systemctl start fatigue-monitor.service

# 查看状态
sudo systemctl status fatigue-monitor.service

# 查看日志
sudo journalctl -u fatigue-monitor.service -f
```

停止自启动：

```bash
sudo systemctl disable fatigue-monitor.service
sudo systemctl stop fatigue-monitor.service
```

### 方式 2: 使用 crontab

```bash
crontab -e

# 添加以下行
@reboot sleep 30 && cd /home/pi/fatigue-monitor && /home/pi/fatigue-monitor/venv/bin/python app.py > /home/pi/fatigue-monitor.log 2>&1
```

---

## 测试清单

在完成部署后，请按以下清单测试：

- [ ] **摄像头测试**: 运行 `rpicam-hello -t 5000`，看到画面
- [ ] **Python 环境**: 运行 `python verify_installation.py`，所有依赖通过
- [ ] **摄像头捕获**: 运行 `python src/camera/camera_capture.py`，看到实时画面
- [ ] **人脸检测**: 运行主程序，检测到人脸并显示关键点
- [ ] **疲劳检测**: 闭眼测试，看到 EAR 值变化
- [ ] **距离监测**: 靠近/远离摄像头，看到距离值变化
- [ ] **坐姿监测**: 低头/抬头，看到姿态角度变化
- [ ] **语音提醒**: 触发疲劳，听到语音播报
- [ ] **Web 界面** (Web 模式): 浏览器访问并看到实时视频流
- [ ] **帧率测试**: FPS ≥ 15

---

## 下一步

1. **调整参数**: 根据实际使用情况，在 `config.yaml` 中调整阈值
2. **长期测试**: 让系统运行几小时，观察稳定性
3. **数据记录**: 开发阶段 5-6 的数据库和统计功能
4. **优化提醒**: 调整提醒冷却时间，避免过于频繁

---

## 快速命令参考

```bash
# 启动 Web 模式
cd ~/fatigue-monitor && source venv/bin/activate && python app.py

# 启动 GUI 模式
cd ~/fatigue-monitor && source venv/bin/activate && python main.py

# 测试摄像头
rpicam-hello -t 5000

# 查看树莓派 IP
hostname -I

# 查看系统资源
htop

# 查看进程
ps aux | grep python

# 停止后台程序
pkill -f "python app.py"
```

---

## 支持

如果遇到问题：

1. 查看本文档的"常见问题"章节
2. 查看项目的其他文档（QUICK_START.md、PROJECT_PLAN.md）
3. 检查系统日志：`sudo journalctl -xe`
4. 查看 Python 错误信息，并根据提示排查

---

**部署文档版本**: v1.0
**最后更新**: 2025-11-25
**适用系统**: 树莓派 OS (Debian Bookworm/Trixie)
**作者**: Claude AI Assistant

祝部署顺利！🎉
