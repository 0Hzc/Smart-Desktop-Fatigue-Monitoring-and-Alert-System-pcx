# Ubuntu/Linux 环境安装指南

## 系统要求

- **操作系统**: Ubuntu 20.04+ / Raspberry Pi OS (Debian-based)
- **Python**: 3.9+
- **硬件**: 树莓派 4B (推荐) 或 Ubuntu PC

---

## 一、系统依赖安装

### 1. 更新系统

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### 2. 安装Python和基础工具

```bash
sudo apt-get install -y python3 python3-pip python3-dev
sudo apt-get install -y build-essential cmake pkg-config
```

### 3. 安装OpenCV依赖

```bash
sudo apt-get install -y libopencv-dev python3-opencv
sudo apt-get install -y libjpeg-dev libtiff5-dev libpng-dev
sudo apt-get install -y libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt-get install -y libxvidcore-dev libx264-dev
```

### 4. 安装语音合成依赖（pyttsx3）

```bash
sudo apt-get install -y espeak espeak-data libespeak-dev
sudo apt-get install -y libportaudio2 portaudio19-dev
```

### 5. 安装其他依赖

```bash
sudo apt-get install -y libatlas-base-dev gfortran
sudo apt-get install -y libhdf5-dev libhdf5-serial-dev libhdf5-103
```

---

## 二、Python依赖安装

### 1. 创建虚拟环境（推荐）

```bash
# 安装虚拟环境工具
sudo pip3 install virtualenv

# 创建虚拟环境
cd ~/Smart-Desktop-Fatigue-Monitoring-and-Alert-System-pcx
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate
```

### 2. 升级pip

```bash
pip install --upgrade pip setuptools wheel
```

### 3. 安装Python依赖

```bash
pip install -r requirements.txt
```

**常见问题**：

如果安装`mediapipe`失败，尝试：
```bash
# 树莓派ARM架构需要特殊版本
pip install mediapipe-rpi4  # 树莓派4B专用

# 或使用预编译wheel
pip install https://github.com/PINTO0309/mediapipe-bin/releases/download/v0.10.0/mediapipe-0.10.0-cp39-cp39-linux_aarch64.whl
```

如果安装`opencv-python`失败：
```bash
# Ubuntu通常可以直接使用系统OpenCV
sudo apt-get install python3-opencv
```

---

## 三、GPIO支持（仅树莓派）

### 1. 安装RPi.GPIO

```bash
pip install RPi.GPIO
```

### 2. 配置GPIO权限

```bash
# 将当前用户添加到gpio组
sudo usermod -a -G gpio $USER

# 重启生效
sudo reboot
```

### 3. 测试GPIO

```bash
# 测试LED（外设到货后）
python src/alert/led_alert.py

# 测试蜂鸣器（外设到货后）
python src/alert/buzzer_alert.py
```

**临时使用sudo运行（不推荐）**：
```bash
sudo python app.py
```

---

## 四、摄像头配置

### 1. USB摄像头

```bash
# 检查摄像头设备
ls -l /dev/video*

# 应该看到 /dev/video0 等设备

# 测试摄像头
sudo apt-get install cheese
cheese  # 图形界面摄像头测试工具
```

### 2. 树莓派CSI摄像头

```bash
# 启用摄像头
sudo raspi-config
# 选择 Interface Options -> Camera -> Enable

# 重启
sudo reboot

# 测试
libcamera-hello --list-cameras
```

如果使用CSI摄像头，修改代码使用`picamera2`：
```bash
pip install picamera2
```

---

## 五、Web服务器配置

### 1. 防火墙设置

```bash
# 允许5000端口访问（Flask默认端口）
sudo ufw allow 5000/tcp
sudo ufw enable
```

### 2. 查看树莓派IP地址

```bash
hostname -I
# 或
ip addr show
```

### 3. 启动Web服务器

```bash
python app.py
```

### 4. 访问Web界面

- **本地访问**: http://localhost:5000
- **局域网访问**: http://<树莓派IP>:5000
  - 例如: http://192.168.1.100:5000

---

## 六、开机自启动配置（可选）

### 方法1：使用systemd服务

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
WorkingDirectory=/home/pi/Smart-Desktop-Fatigue-Monitoring-and-Alert-System-pcx
ExecStart=/home/pi/Smart-Desktop-Fatigue-Monitoring-and-Alert-System-pcx/venv/bin/python app.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启用服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable fatigue-monitor
sudo systemctl start fatigue-monitor

# 查看状态
sudo systemctl status fatigue-monitor

# 查看日志
sudo journalctl -u fatigue-monitor -f
```

### 方法2：使用crontab

```bash
crontab -e
```

添加：
```cron
@reboot cd /home/pi/Smart-Desktop-Fatigue-Monitoring-and-Alert-System-pcx && /home/pi/Smart-Desktop-Fatigue-Monitoring-and-Alert-System-pcx/venv/bin/python app.py > /home/pi/fatigue-monitor.log 2>&1
```

---

## 七、测试清单

### 基础功能测试

```bash
# 1. 测试摄像头
python src/camera/camera_capture.py

# 2. 测试人脸检测
python src/detection/face_detector.py

# 3. 测试疲劳分析
python src/analysis/fatigue_analyzer.py

# 4. 测试距离监测
python src/analysis/distance_monitor.py

# 5. 测试坐姿监测
python src/analysis/posture_monitor.py
```

### 提醒功能测试

```bash
# 1. 测试LED（模拟模式）
python src/alert/led_alert.py

# 2. 测试蜂鸣器（模拟模式）
python src/alert/buzzer_alert.py

# 3. 测试Web服务器
python app.py
# 然后在浏览器访问 http://localhost:5000
```

### 完整系统测试

```bash
# 启动Web服务器
python app.py

# 在浏览器中打开
# http://<树莓派IP>:5000

# 测试：
# - 视频流是否正常
# - 人脸检测是否工作
# - 状态更新是否实时
# - 提醒弹窗是否显示
# - Web语音是否播放
```

---

## 八、故障排除

### 问题1：导入OpenCV失败

```bash
# 检查OpenCV安装
python3 -c "import cv2; print(cv2.__version__)"

# 如果失败，重新安装
pip uninstall opencv-python opencv-contrib-python
pip install opencv-python==4.8.1.78
```

### 问题2：MediaPipe导入失败

```bash
# 树莓派需要特定版本
pip install mediapipe-rpi4

# 或从源码编译（耗时较长）
```

### 问题3：语音合成无声音

```bash
# 检查espeak安装
espeak "test"

# 重新安装espeak
sudo apt-get install --reinstall espeak espeak-data

# 测试pyttsx3
python3 -c "import pyttsx3; engine = pyttsx3.init(); engine.say('test'); engine.runAndWait()"
```

### 问题4：GPIO权限错误

```bash
# 使用sudo运行
sudo python app.py

# 或添加到gpio组
sudo usermod -a -G gpio $USER
# 然后注销重新登录
```

### 问题5：Web服务器端口被占用

```bash
# 查看5000端口占用
sudo lsof -i :5000

# 杀死进程
sudo kill -9 <PID>

# 或修改app.py使用其他端口
socketio.run(app, host='0.0.0.0', port=8080)
```

---

## 九、性能优化建议

### 树莓派4B优化

1. **降低分辨率**：
   ```yaml
   # config.yaml
   camera:
     resolution:
       width: 320
       height: 240
   ```

2. **跳帧处理**：
   ```yaml
   performance:
     skip_frames: 2  # 每2帧处理一次
   ```

3. **禁用不必要的功能**：
   ```yaml
   alert:
     enable_led: false  # 外设未到货时禁用
   ```

4. **增加交换空间**（如果内存不足）：
   ```bash
   sudo dphys-swapfile swapoff
   sudo nano /etc/dphys-swapfile
   # 设置 CONF_SWAPSIZE=2048
   sudo dphys-swapfile setup
   sudo dphys-swapfile swapon
   ```

---

## 十、硬件连接图（外设到货后）

### LED连接
```
LED正极 → GPIO 17 (Pin 11)
LED负极 → 330Ω电阻 → GND (Pin 6)
```

### 蜂鸣器连接
```
蜂鸣器+ → GPIO 18 (Pin 12)
蜂鸣器- → GND (Pin 14)
```

### GPIO引脚图
```
树莓派4B GPIO (BCM编号)
┌─────────┬─────────┐
│ 3.3V  1 │ 2  5V   │
│ GPIO2 3 │ 4  5V   │
│ GPIO3 5 │ 6  GND  │
│ GPIO4 7 │ 8  GPIO14│
│ GND   9 │10 GPIO15│
│GPIO17 11│12 GPIO18│← 蜂鸣器
│GPIO27 13│14  GND  │
│GPIO22 15│16 GPIO23│
│ 3.3V 17│18 GPIO24│
│GPIO10 19│20  GND  │
└─────────┴─────────┘
```

---

**文档版本**: v1.0
**创建日期**: 2025-01-20
**适用系统**: Ubuntu 20.04+ / Raspberry Pi OS
