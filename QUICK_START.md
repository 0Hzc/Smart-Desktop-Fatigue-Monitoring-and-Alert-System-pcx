# 快速开始指南

## 🚀 一键安装（Ubuntu 20.04+）

### 步骤1：克隆项目

```bash
git clone <repository-url>
cd Smart-Desktop-Fatigue-Monitoring-and-Alert-System-pcx
```

### 步骤2：安装系统依赖

```bash
# 运行自动化安装脚本
./install_ubuntu_deps.sh

# 或手动安装
sudo apt-get update
sudo apt-get install -y build-essential python3-dev python3-pip cmake pkg-config
sudo apt-get install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 libgtk-3-0
sudo apt-get install -y v4l-utils libv4l-dev
sudo apt-get install -y espeak espeak-data libespeak-dev
```

### 步骤3：创建虚拟环境（推荐）

```bash
python3 -m venv venv
source venv/bin/activate
```

### 步骤4：安装Python依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt

# 如果安装慢，使用国内镜像：
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 步骤5：验证安装

```bash
# 完整验证
python verify_installation.py

# 单独测试语音
python test_voice.py

# 快速测试
python -c "import cv2, mediapipe, flask; print('✅ 核心依赖安装成功！')"
```

### 步骤6：运行系统

```bash
# 方式1：传统GUI模式（需要显示器）
python main.py

# 方式2：Web服务器模式（无需显示器，推荐树莓派）
python app.py
# 然后在浏览器访问：http://localhost:5000
# 或从其他设备访问：http://<树莓派IP>:5000
```

---

## 📦 核心依赖清单

### Python包（8个）

| 包名 | 版本 | 用途 |
|------|------|------|
| opencv-python | 4.8.1.78 | 计算机视觉 |
| mediapipe | 0.10.8 | 人脸检测 |
| numpy | 1.24.3 | 数值计算 |
| Flask | 3.0.0 | Web框架 |
| Flask-SocketIO | 5.3.5 | WebSocket |
| python-socketio | 5.10.0 | Socket.IO客户端 |
| python-engineio | 4.8.0 | Engine.IO核心 |
| PyYAML | 6.0.1 | 配置解析 |

### 系统依赖

- **编译工具**：build-essential, python3-dev, cmake
- **OpenCV**：libgl1-mesa-glx, libgtk-3-0等
- **摄像头**：v4l-utils, libv4l-dev
- **语音**：espeak, espeak-data

---

## 🎯 功能模块

### 已完成（阶段1-4）

- ✅ **摄像头捕获** - USB/CSI摄像头支持
- ✅ **人脸检测** - MediaPipe 468点面部关键点
- ✅ **疲劳检测** - EAR、PERCLOS、眨眼频率、打瞌睡
- ✅ **距离监测** - 双重估算、距离平滑
- ✅ **坐姿监测** - 头部姿态、欧拉角、不良坐姿
- ✅ **多模态提醒** - 语音、LED、GUI
- ✅ **Web界面** - Flask实时监控

### 待开发（阶段5-7）

- ⏳ **数据记录** - SQLite数据库
- ⏳ **数据统计** - 每日报告
- ⏳ **设置界面** - 参数调整
- ⏳ **性能优化** - 跳帧、多线程
- ⏳ **开机自启** - systemd服务
- ⏳ **文档完善** - 用户手册、开发文档

---

## 🔧 常用命令

### 开发调试

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行主程序
python main.py

# 运行Web服务器
python app.py

# 测试单个模块
python src/analysis/fatigue_analyzer.py
python src/analysis/distance_monitor.py
python src/analysis/posture_monitor.py

# 测试语音
python test_voice.py
espeak "Hello, this is a test"

# 验证安装
python verify_installation.py
```

### 摄像头调试

```bash
# 列出摄像头设备
ls /dev/video*

# 查看摄像头信息
v4l2-ctl --list-devices

# 查看支持的分辨率
v4l2-ctl --device=/dev/video0 --list-formats-ext

# 测试摄像头捕获
python -c "import cv2; cap = cv2.VideoCapture(0); print('摄像头可用' if cap.isOpened() else '摄像头不可用'); cap.release()"
```

### Git操作

```bash
# 查看当前分支
git branch

# 拉取最新代码
git pull origin <branch-name>

# 查看修改
git status
git diff

# 提交更改
git add .
git commit -m "描述"
git push
```

---

## 🐛 故障排查

### 问题1：ImportError: libGL.so.1 not found

```bash
sudo apt-get install -y libgl1-mesa-glx
```

### 问题2：摄像头无法打开

```bash
# 检查设备
ls /dev/video*

# 添加权限
sudo usermod -a -G video $USER
newgrp video
```

### 问题3：espeak无声音

```bash
# 测试espeak
espeak "test"

# 测试音频输出
speaker-test -c 2

# 调整音量
alsamixer
```

### 问题4：Flask无法远程访问

```bash
# 开放端口
sudo ufw allow 5000

# 或关闭防火墙（仅测试用）
sudo ufw disable

# 确保使用0.0.0.0监听
# app.run(host='0.0.0.0', port=5000)
```

### 问题5：mediapipe导入失败

```bash
# 检查glibc版本
ldd --version
# 需要glibc 2.31+，建议使用Ubuntu 20.04+
```

---

## 📚 文档索引

- [Ubuntu系统依赖指南](docs/Ubuntu系统依赖指南.md) - 完整的安装说明
- [语音模块升级说明](docs/语音模块升级说明.md) - pyttsx3迁移到espeak
- [阶段1测试指南](docs/阶段1测试指南.md) - 环境搭建测试
- [阶段2测试指南](docs/阶段2测试指南.md) - 疲劳检测测试
- [阶段3测试指南](docs/阶段3测试指南.md) - 距离和坐姿测试
- [姿态监测修复说明](docs/姿态监测修复说明.md) - 调试历史

---

## 🔑 配置文件

### config.yaml

主要配置项：

```yaml
camera:
  resolution:
    width: 640      # 摄像头分辨率
    height: 480
  fps: 30

fatigue:
  ear_threshold: 0.25         # EAR阈值
  perclos_threshold: 0.15     # PERCLOS阈值（15%）
  closed_eye_duration: 2.0    # 打瞌睡阈值（秒）

distance:
  warning_distance: 50        # 警告距离（厘米）
  focal_length: 600           # 摄像头焦距

posture:
  pitch_threshold_down: 12    # 低头阈值（度）
  pitch_threshold_up: -8      # 仰头阈值（度）

alert:
  enable_voice: true          # 启用语音提醒
  enable_led: false           # 启用LED提醒
  enable_gui: true            # 启用GUI弹窗
  cooldown_time: 300          # 提醒冷却时间（秒）
```

---

## 💡 使用建议

### 开发环境

- **系统**：Ubuntu 20.04 或 22.04
- **Python**：3.8 或 3.10
- **内存**：至少4GB（推荐8GB）
- **摄像头**：USB摄像头或笔记本内置摄像头

### 生产部署（树莓派）

- **型号**：树莓派4B（4GB/8GB）
- **系统**：树莓派OS 64位（Bullseye）
- **摄像头**：USB摄像头或CSI摄像头
- **模式**：使用Web服务器模式（无需显示器）
- **优化**：降低分辨率、启用跳帧

---

## 🆘 获取帮助

### 常见资源

- **项目文档**：查看`docs/`目录
- **测试脚本**：运行`python verify_installation.py`
- **Issue反馈**：GitHub Issues
- **社区讨论**：GitHub Discussions

### 报告问题时请提供

1. 系统信息：`uname -a`
2. Python版本：`python --version`
3. 错误日志：完整的错误信息
4. 安装验证：`python verify_installation.py`的输出

---

## 📄 许可证

本项目为毕业设计项目，请遵守相关使用规范。

---

**最后更新**：2024年11月
**版本**：v2.1
**维护者**：项目开发团队
