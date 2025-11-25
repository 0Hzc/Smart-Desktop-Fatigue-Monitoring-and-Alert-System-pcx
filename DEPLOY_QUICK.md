# 树莓派快速部署（5分钟）

> 适用于你的树莓派 4B + OV5647 摄像头配置

## 前提条件 ✅

你的配置已就绪：
- ✅ 树莓派 4B + 树莓派 OS (Debian Trixie/Bookworm)
- ✅ OV5647 摄像头已连接并正常工作
- ✅ libcamera 驱动已加载
- ✅ 可使用 rpicam-* 命令

## 快速部署

### 1. 安装系统依赖（3分钟）

```bash
# 更新系统
sudo apt-get update && sudo apt-get upgrade -y

# 安装所有依赖（一键式）
sudo apt-get install -y build-essential python3-dev python3-pip cmake pkg-config \
    libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 libgtk-3-0 \
    v4l-utils libv4l-dev espeak espeak-data libespeak-dev alsa-utils pulseaudio \
    python3-picamera2

# 清理
sudo apt-get autoremove -y && sudo apt-get autoclean
```

### 2. 克隆项目（1分钟）

```bash
cd ~
git clone <你的仓库地址> fatigue-monitor
cd fatigue-monitor
git checkout claude/review-project-plan-01HbXoRc4U8EzYeKMA6bxPxz
```

### 3. 安装 Python 依赖（2分钟）

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖（使用清华镜像加速）
pip install --upgrade pip
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 4. 启动系统

#### 方式 A: Web 模式（推荐，无需显示器）

```bash
cd ~/fatigue-monitor
source venv/bin/activate
python app.py
```

然后在浏览器访问：`http://<树莓派IP>:5000`

查看 IP 地址：
```bash
hostname -I
```

#### 方式 B: GUI 模式（需要显示器）

```bash
cd ~/fatigue-monitor
source venv/bin/activate
python main.py
```

按 `Q` 键退出。

## 验证测试

```bash
# 1. 测试摄像头
rpicam-hello -t 5000

# 2. 验证 Python 环境
cd ~/fatigue-monitor
source venv/bin/activate
python verify_installation.py

# 3. 测试摄像头模块
python src/camera/camera_capture.py
```

## 配置调整（可选）

编辑 `config.yaml` 调整参数：

```bash
nano ~/fatigue-monitor/config.yaml
```

**推荐配置（针对你的 OV5647）**：

```yaml
camera:
  resolution:
    width: 640      # 推荐 640x480，性能最佳
    height: 480
  fps: 30
  flip: false

performance:
  skip_frames: 1    # 如果卡顿，改为 2
```

## 常用命令

```bash
# 启动 Web 服务
cd ~/fatigue-monitor && source venv/bin/activate && python app.py

# 查看树莓派 IP
hostname -I

# 测试语音
espeak "Hello world"

# 查看 CPU/内存
htop

# 停止后台运行的程序
pkill -f "python app.py"
```

## 问题排查

### 摄像头无法打开
```bash
sudo systemctl restart libcamera
sudo usermod -a -G video $USER
newgrp video
```

### 语音无声音
```bash
espeak "test"
speaker-test -c 2
alsamixer  # 调整音量
```

### Web 无法远程访问
```bash
sudo ufw allow 5000
# 或临时关闭防火墙
sudo ufw disable
```

## 性能优化

如果 FPS 低于 15，尝试：

1. **降低分辨率** (config.yaml)：
   ```yaml
   camera:
     resolution:
       width: 320
       height: 240
   ```

2. **启用跳帧** (config.yaml)：
   ```yaml
   performance:
     skip_frames: 2
   ```

## 预期效果

- **帧率**: 20-25 FPS（640x480 + picamera2）
- **启动时间**: 5-10 秒
- **CPU 占用**: 50-70%
- **内存占用**: 500-800 MB

## 开机自启（可选）

```bash
# 创建服务文件
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

[Install]
WantedBy=multi-user.target
```

启用：
```bash
sudo systemctl daemon-reload
sudo systemctl enable fatigue-monitor.service
sudo systemctl start fatigue-monitor.service
```

---

**完整文档**: 参见 `RASPBERRY_PI_DEPLOYMENT_GUIDE.md`

**部署时间**: ≤ 10 分钟
**难度**: ⭐⭐☆☆☆ (简单)

祝部署顺利！🎉
