# Web版疲劳监测系统测试指南

## 测试环境

- **服务器**: 树莓派 4B / Ubuntu PC
- **客户端**: 任意带浏览器的设备（PC/手机/平板）
- **网络**: 局域网（WiFi或有线）

---

## 一、环境准备

### 1. 服务器端（树莓派/Ubuntu）

#### 更新代码
```bash
cd ~/Smart-Desktop-Fatigue-Monitoring-and-Alert-System-pcx
git pull origin claude/review-project-plan-01HbXoRc4U8EzYeKMA6bxPxz
```

#### 安装依赖
```bash
# 安装系统依赖（首次运行）
sudo apt-get update
sudo apt-get install -y python3-opencv espeak

# 安装Python依赖
pip install -r requirements.txt
```

#### 检查IP地址
```bash
# 查看树莓派IP地址
hostname -I
# 或
ip addr show | grep "inet "

# 示例输出：192.168.1.100
```

### 2. 客户端（浏览器）

推荐浏览器：
- ✅ Chrome / Edge (最佳兼容性)
- ✅ Firefox
- ✅ Safari (Mac/iPhone)
- ⚠️ 移动端浏览器（需要支持WebRTC和Web Speech API）

---

## 二、启动Web服务器

### 方法1：直接运行

```bash
cd ~/Smart-Desktop-Fatigue-Monitoring-and-Alert-System-pcx
python app.py
```

**预期输出**：
```
==================================================
智能桌面疲劳监测系统 - Web版
版本: v2.0 (Web Interface)
==================================================

✓ 摄像头初始化成功
✓ 人脸检测器初始化成功
✓ 疲劳分析器初始化成功
✓ 距离监测器初始化成功
✓ 坐姿监测器初始化成功
✓ 提醒管理器初始化完成
✓ Web提醒器初始化成功
  - SocketIO已连接，可向浏览器推送提醒
✓ 蜂鸣器初始化（模拟模式 - print输出，GPIO 18）

==================================================
Web服务器启动中...
请在浏览器中访问: http://0.0.0.0:5000
局域网访问: http://<树莓派IP>:5000
按 Ctrl+C 停止服务器
==================================================

 * Running on http://0.0.0.0:5000
```

### 方法2：后台运行

```bash
# 使用nohup后台运行
nohup python app.py > fatigue-monitor.log 2>&1 &

# 查看进程
ps aux | grep app.py

# 查看日志
tail -f fatigue-monitor.log

# 停止服务
pkill -f app.py
```

---

## 三、访问Web界面

### 1. 本地访问（服务器本机）

打开浏览器，访问：
```
http://localhost:5000
```

### 2. 局域网访问（其他设备）

打开浏览器，访问：
```
http://192.168.1.100:5000
```
（将IP替换为实际的树莓派IP）

### 3. 手机访问

在手机浏览器中输入：
```
http://192.168.1.100:5000
```

**注意**：
- 确保手机和树莓派在同一WiFi网络
- 某些浏览器需要HTTPS才能使用语音功能

---

## 四、功能测试

### 测试1：视频流显示

**操作**：打开Web界面

**预期结果**：
- ✅ 视频流正常显示
- ✅ 能看到人脸检测框（绿色矩形）
- ✅ 显示FPS（帧率）
- ✅ 右上角显示"● 已连接"（绿色）

**如果视频不显示**：
1. 检查摄像头是否连接：`ls /dev/video*`
2. 检查浏览器控制台是否有错误
3. 尝试刷新页面

### 测试2：状态实时更新

**操作**：面对摄像头，进行各种动作

**预期结果**：

| 动作 | 状态卡片变化 |
|------|-------------|
| **正常坐姿** | 疲劳状态：Normal（绿色）<br>距离：显示实时距离<br>坐姿：Normal（绿色） |
| **闭眼** | 疲劳状态：变为Warning/Danger（黄/红色）<br>EAR值降低<br>PERCLOS增加 |
| **靠近屏幕** | 距离状态：显示"过近！"（红色）<br>距离值减小（<50cm） |
| **低头** | 坐姿状态：显示"Head Down"（红色）<br>Pitch值为正（>12°） |
| **抬头** | 坐姿状态：显示"Head Up"（红色）<br>Pitch值为负（<-8°） |

**验证点**：
- ✅ 状态更新实时（无明显延迟）
- ✅ 数值变化流畅
- ✅ 颜色正确（绿色=正常，黄色=警告，红色=危险）

### 测试3：提醒弹窗

**操作**：触发任一提醒条件

**触发方法**：
1. **疲劳提醒**：连续闭眼2秒
2. **距离提醒**：靠近屏幕<50cm，持续30秒
3. **坐姿提醒**：低头/抬头，持续60秒

**预期结果**：
- ✅ 弹出提醒窗口（中央半透明背景）
- ✅ 显示相应图标（⚠️ 或 🚨）
- ✅ 显示标题和消息
- ✅ 5秒后自动关闭或点击"我知道了"关闭

**弹窗样式**：
- 警告级别：黄色标题 + ⚠️ 图标
- 严重级别：红色标题 + 🚨 图标

### 测试4：Web语音播放

**操作**：触发任一提醒

**预期结果**：
- ✅ 浏览器播放英文语音提示
- ✅ 声音从浏览器所在设备的扬声器输出
- ✅ 音量适中，语速正常

**语音内容**：
- 疲劳："You look tired. Please take a break."
- 距离："You are too close to the screen. Please move back."
- 坐姿："Poor posture detected. Please sit up straight."
- 严重："Severe fatigue detected! Please rest immediately."

**如果无声音**：
1. 检查浏览器音量
2. 打开浏览器控制台查看是否有语音API错误
3. Chrome：检查是否允许autoplay
4. Safari：可能需要用户手动交互后才能播放

### 测试5：蜂鸣器提醒（树莓派本地）

**操作**：触发任一提醒

**预期结果**（模拟模式）：
- ✅ 服务器终端输出：
  ```
  [模拟蜂鸣模式: fatigue]
  [模拟蜂鸣] BEEP 0.1s -> SILENCE 0.1s
  [模拟蜂鸣] BEEP 0.1s -> SILENCE 0.1s
  [模拟蜂鸣] BEEP 0.1s -> SILENCE 0.5s
  ✓ 模拟蜂鸣模式 'fatigue' 完成
  ```

**外设到货后**：
- 设置`buzzer = BuzzerAlert(pin=18, simulate=False)`
- 连接蜂鸣器到GPIO 18
- 真实蜂鸣器会发出相应节奏的提示音

### 测试6：多客户端同时访问

**操作**：
1. 在PC上打开Web界面
2. 在手机上同时打开Web界面

**预期结果**：
- ✅ 两个设备都能看到视频流
- ✅ 状态更新同步到所有客户端
- ✅ 提醒同时显示在所有客户端
- ✅ 互不干扰

### 测试7：冷却时间机制

**操作**：
1. 触发疲劳提醒（闭眼）
2. 恢复正常
3. 5分钟内再次触发

**预期结果**：
- ✅ 第一次提醒正常显示和播放
- ✅ 5分钟内的第二次提醒**不会**显示（冷却中）
- ✅ 服务器日志显示："[提醒触发] ..."

**修改冷却时间**（测试用）：
```yaml
# config.yaml
alert:
  cooldown_time: 30  # 改为30秒方便测试
```

---

## 五、性能测试

### 测试8：FPS帧率

**预期值**：
- PC/Ubuntu: ≥20 FPS
- 树莓派 4B: ≥15 FPS

**如果FPS过低**：
1. 降低分辨率：
   ```yaml
   camera:
     resolution:
       width: 320
       height: 240
   ```

2. 增加跳帧：
   ```yaml
   performance:
     skip_frames: 2
   ```

### 测试9：网络延迟

**测试方法**：
- 在视频前挥手，观察Web界面延迟

**预期延迟**：
- 局域网：< 500ms
- WiFi：< 1s

---

## 六、故障排除

### 问题1：视频流404错误

**原因**：Flask路由未正确加载

**解决**：
```bash
# 检查app.py是否正确
python -c "from app import app; print(app.url_map)"

# 重启服务器
pkill -f app.py
python app.py
```

### 问题2：WebSocket连接失败

**症状**：右上角一直显示"● 未连接"

**解决**：
```bash
# 检查Flask-SocketIO是否安装
pip list | grep Flask-SocketIO

# 重新安装
pip install --upgrade Flask-SocketIO

# 检查防火墙
sudo ufw allow 5000/tcp
```

### 问题3：摄像头无法打开

**解决**：
```bash
# 检查摄像头设备
ls -l /dev/video*

# 检查权限
sudo usermod -a -G video $USER

# 重启
sudo reboot
```

### 问题4：语音不播放

**Chrome/Edge**：
- 打开chrome://flags
- 搜索"autoplay"
- 设置为"No user gesture required"

**Firefox**：
- about:preferences
- Privacy & Security
- Permissions -> Autoplay
- 设置为"Allow Audio and Video"

**Safari**：
- 偏好设置 -> 网站 -> 自动播放
- 允许所有自动播放

### 问题5：手机访问不了

**检查清单**：
- [ ] 手机和树莓派在同一WiFi
- [ ] 防火墙允许5000端口
- [ ] IP地址正确
- [ ] 服务器正在运行

**调试命令**：
```bash
# 在手机上ping树莓派
ping 192.168.1.100

# 检查端口是否开放
nmap -p 5000 192.168.1.100
```

---

## 七、验收清单

### 基础功能
- [ ] Web界面可以访问
- [ ] 视频流正常显示
- [ ] 人脸检测正常工作
- [ ] 状态实时更新

### 提醒功能
- [ ] 疲劳提醒能触发
- [ ] 距离提醒能触发
- [ ] 坐姿提醒能触发
- [ ] 提醒弹窗显示正常
- [ ] Web语音播放正常
- [ ] 蜂鸣器模拟输出正常
- [ ] 冷却时间机制生效

### 性能指标
- [ ] FPS ≥ 15
- [ ] 网络延迟 < 1s
- [ ] 多客户端可同时访问

### 兼容性
- [ ] PC浏览器正常
- [ ] 手机浏览器正常
- [ ] 不同WiFi设备均可访问

---

## 八、下一步

测试通过后，可以：

1. **部署到实际环境**：
   - 设置开机自启动
   - 配置systemd服务
   - 添加日志记录

2. **扩展功能**：
   - 添加历史数据记录
   - 添加统计图表
   - 添加设置页面

3. **等待外设到货**：
   - 连接真实LED
   - 连接真实蜂鸣器
   - 切换到GPIO真实模式

---

**文档版本**: v1.0
**创建日期**: 2025-01-20
**对应提交**: commit 09fb576
