# 系统升级说明 - Web版架构

## 版本信息

- **旧版本**: v1.0 (Tkinter GUI)
- **新版本**: v2.0 (Flask Web)
- **升级日期**: 2025-01-20
- **升级原因**: 适配树莓派无显示器场景，支持局域网访问

---

## 重大变更

### 1. GUI架构变更

#### 变更前
```python
# 使用Tkinter创建本地GUI窗口
from tkinter import Toplevel
window = Toplevel()
```

#### 变更后
```python
# 使用Flask Web服务器 + WebSocket
from flask import Flask, render_template
from flask_socketio import SocketIO
app = Flask(__name__)
socketio = SocketIO(app)
```

**影响**：
- ✅ 无需显示器，任意设备浏览器访问
- ✅ 支持多客户端同时监控
- ✅ 响应式界面，支持手机/平板
- ⚠️ 需要安装Flask相关依赖

### 2. 语音提醒双重方案

#### 变更前
```python
# 仅使用pyttsx3本地语音
voice_alert = VoiceAlert()
voice_alert.speak("Warning message")
```

#### 变更后
```python
# 树莓派：蜂鸣器提示音
buzzer = BuzzerAlert(pin=18)
buzzer.speak_alert('fatigue')

# Web端：浏览器TTS
# 通过WebSocket推送，浏览器Web Speech API播放
```

**影响**：
- ✅ Web端使用访问设备的扬声器
- ✅ 树莓派本地使用蜂鸣器（成本更低）
- ✅ 双重提醒，更可靠

### 3. GPIO默认模拟模式

#### 变更前
```python
# 直接使用GPIO，无GPIO时报错
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
```

#### 变更后
```python
# 自动检测，无GPIO时使用print模拟
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except:
    GPIO_AVAILABLE = False
    print("[模拟] LED ON")
```

**影响**：
- ✅ Ubuntu开发环境可正常运行
- ✅ 外设未到货可先测试
- ✅ 切换真实GPIO只需修改一个参数

---

## 新增功能

### 1. 实时视频流

- **技术**: MJPEG over HTTP
- **路由**: `/video_feed`
- **帧率**: ~30 FPS（可配置）

### 2. WebSocket实时通信

- **库**: Flask-SocketIO
- **事件**:
  - `status_update`: 状态实时推送
  - `alert`: 提醒推送
  - `connect/disconnect`: 连接管理

### 3. Web前端界面

- **技术**: HTML5 + CSS3 + JavaScript
- **特性**:
  - 响应式设计（Grid布局）
  - 实时状态卡片
  - 提醒弹窗动画
  - Web Speech API语音

### 4. 蜂鸣器模块

- **文件**: `src/alert/buzzer_alert.py`
- **引脚**: GPIO 18（BCM编号）
- **模式**: 4种预定义节奏（疲劳/距离/坐姿/严重）

---

## 新增文件

```
├── app.py                        # Flask Web服务器主程序 ⭐
├── templates/
│   └── index.html                # Web前端界面 ⭐
├── src/alert/
│   ├── web_alert.py              # Web提醒器 ⭐
│   └── buzzer_alert.py           # 蜂鸣器控制 ⭐
├── docs/
│   ├── Ubuntu安装指南.md         # Ubuntu环境配置 ⭐
│   └── Web版测试指南.md          # Web版测试文档 ⭐
└── 快速启动指南.md               # 快速上手文档 ⭐
```

---

## 依赖变更

### 新增Python包

```bash
pip install Flask==3.0.0
pip install Flask-SocketIO==5.3.5
pip install python-socketio==5.10.0
pip install python-engineio==4.8.0
```

### 新增系统依赖

```bash
sudo apt-get install espeak espeak-data libespeak-dev
```

---

## 配置文件变更

### config.yaml

**未变更**：所有原有配置保持兼容

**说明**：
- `alert.enable_gui`: 现在控制Web提醒（而非Tkinter）
- `alert.enable_voice`: 建议设为false（Web端使用浏览器TTS）
- `alert.enable_led`: 外设未到货时建议设为false

---

## 迁移指南

### 从v1.0（Tkinter）迁移到v2.0（Web）

#### 步骤1：备份旧版本（可选）

```bash
cd ~/Smart-Desktop-Fatigue-Monitoring-and-Alert-System-pcx
git branch backup-v1.0  # 创建备份分支
```

#### 步骤2：拉取新版本

```bash
git pull origin claude/review-project-plan-01HbXoRc4U8EzYeKMA6bxPxz
```

#### 步骤3：安装新依赖

```bash
pip install -r requirements.txt
```

#### 步骤4：测试运行

```bash
# 旧版运行方式
# python main.py  # ❌ 不再推荐

# 新版运行方式
python app.py     # ✅ Web服务器
```

#### 步骤5：访问Web界面

浏览器访问：`http://<树莓派IP>:5000`

---

## 兼容性说明

### 保留的文件

以下文件保留但不再推荐直接使用：

| 文件 | 状态 | 说明 |
|------|------|------|
| `main.py` | ⚠️ 保留 | 原Tkinter版，建议使用app.py |
| `src/alert/gui_alert.py` | ⚠️ 保留 | Tkinter弹窗，Web版不使用 |
| `src/alert/voice_alert.py` | ⚠️ 保留 | pyttsx3语音，Web版不使用 |

### 移除的依赖

无移除，仅新增。所有v1.0功能仍可用。

---

## 性能对比

| 指标 | v1.0 (Tkinter) | v2.0 (Web) |
|------|---------------|-----------|
| **访问方式** | 本地显示器 | 局域网任意设备 |
| **FPS** | 20-30 | 15-30 |
| **内存占用** | ~300MB | ~350MB |
| **多客户端** | ❌ | ✅ |
| **移动端** | ❌ | ✅ |
| **语音输出** | 本地扬声器 | 浏览器设备扬声器 |

---

## 已知限制

### Web版限制

1. **HTTPS**：部分浏览器需要HTTPS才能使用语音
   - 解决：局域网HTTP通常允许
   
2. **网络延迟**：WiFi环境可能有延迟
   - 解决：使用有线连接或5G WiFi

3. **浏览器兼容性**：Web Speech API支持
   - Chrome/Edge: ✅ 完全支持
   - Firefox: ✅ 支持
   - Safari: ⚠️ 部分功能需手动交互
   - 移动端: ⚠️ 取决于浏览器

### 模拟模式限制

1. **蜂鸣器/LED**：外设到货前仅print输出
2. **真实性**：模拟模式无法测试硬件功能

---

## 回退方案

如果需要回退到v1.0：

```bash
# 方法1：切换到备份分支
git checkout backup-v1.0

# 方法2：运行旧版程序
python main.py  # 仍可运行Tkinter版本

# 方法3：回退依赖
pip uninstall Flask Flask-SocketIO
```

---

## 后续计划

### 阶段5：数据记录与统计（下一步）

- [ ] SQLite数据库集成
- [ ] 每日数据统计
- [ ] 历史数据图表
- [ ] 健康报告生成

### 阶段6：性能优化

- [ ] 视频流压缩优化
- [ ] 缓存机制
- [ ] 多线程优化

### 阶段7：硬件集成（外设到货后）

- [ ] 真实LED控制
- [ ] 真实蜂鸣器控制
- [ ] GPIO权限配置

---

## 常见问题（FAQ）

### Q: 为什么从Tkinter改为Flask？

**A**: 树莓派4B无显示器，Tkinter GUI无法显示。Flask Web可通过局域网访问，任意设备都能查看监控画面。

### Q: 旧版main.py还能用吗？

**A**: 可以，但需要连接显示器。推荐使用新版app.py。

### Q: pyttsx3还需要吗？

**A**: Web版不再使用pyttsx3（树莓派端改用蜂鸣器）。但依赖保留，不影响系统。

### Q: 如何切换到真实GPIO？

**A**: 外设到货后，修改app.py：
```python
self.buzzer = BuzzerAlert(pin=18, simulate=False)
```

### Q: Web界面支持手机吗？

**A**: 完全支持。响应式设计，自动适配手机屏幕。

---

## 技术支持

- **文档**: 查看`docs/`目录
- **问题**: 检查`docs/Ubuntu安装指南.md`故障排除章节
- **测试**: 参考`docs/Web版测试指南.md`

---

**版本**: v2.0
**文档日期**: 2025-01-20
**升级类型**: 架构升级（向下兼容）
