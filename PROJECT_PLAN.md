# 智能桌面疲劳监测系统 - 项目实施规划

## 一、系统架构设计

### 1.1 整体架构
```
┌─────────────────────────────────────────────────────┐
│                   主控制模块                          │
│              (main_controller.py)                   │
└────────┬────────────────────────────────────────────┘
         │
    ┌────┴────┐
    │         │         │         │         │
┌───▼───┐ ┌──▼──┐ ┌───▼───┐ ┌───▼───┐ ┌───▼───┐
│摄像头  │ │检测  │ │分析   │ │提醒   │ │数据   │
│采集   │ │模块  │ │模块   │ │模块   │ │记录   │
│模块   │ │     │ │       │ │       │ │模块   │
└───────┘ └─────┘ └───────┘ └───────┘ └───────┘
```

### 1.2 核心模块划分

#### 模块1: 摄像头采集模块 (camera_module.py)
- 功能：实时视频流采集
- 技术：picamera2 / OpenCV VideoCapture
- 输出：视频帧 (640x480 或 320x240)

#### 模块2: 人脸检测与关键点提取 (face_detector.py)
- 功能：检测人脸、提取468个关键点
- 技术：MediaPipe Face Mesh
- 输出：人脸框坐标、关键点3D坐标

#### 模块3: 疲劳状态分析模块 (fatigue_analyzer.py)
**3.1 眼部分析**
- EAR (Eye Aspect Ratio) 计算
  - 公式：`EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)`
  - 阈值：EAR < 0.25 判定为闭眼
- PERCLOS 计算
  - 统计1分钟内闭眼时间占比
  - PERCLOS > 15% 判定为疲劳

**3.2 眨眼检测**
- 连续帧EAR变化检测
- 正常眨眼频率：15-20次/分钟
- 异常阈值：< 10次/分钟或 > 30次/分钟

**3.3 打瞌睡检测**
- 连续闭眼时长 > 2秒触发警报

#### 模块4: 距离监测模块 (distance_monitor.py)
- 功能：计算人脸到摄像头距离
- 方法1：基于人脸框大小
  - 公式：`distance = (known_face_width * focal_length) / face_box_width`
  - 需要校准焦距参数
- 方法2：基于眼距（更准确）
  - 使用MediaPipe关键点计算双眼间距
- 阈值：距离 < 50cm 触发提醒

#### 模块5: 坐姿监测模块 (posture_monitor.py)
- 功能：头部姿态估计（俯仰角pitch）
- 技术：PnP算法计算头部旋转矩阵
- 关键点选择：鼻尖、下巴、左眼角、右眼角、嘴角
- 阈值：
  - pitch > 30° (低头) 触发提醒
  - pitch < -15° (仰头) 触发提醒
  - 持续时间 > 30秒触发警报

#### 模块6: 多模态提醒模块 (alert_system.py)
**6.1 提醒等级设计**
- Level 1 (轻度): 屏幕弹窗提示
- Level 2 (中度): 弹窗 + LED闪烁
- Level 3 (重度): 弹窗 + LED + 语音播报

**6.2 提醒场景**
| 问题类型 | 触发条件 | 提醒等级 | 提醒内容 |
|---------|---------|---------|---------|
| 眨眼频率低 | < 10次/分钟持续3分钟 | Level 1 | "请注意眨眼，预防眼睛干涩" |
| 长时间闭眼 | 闭眼 > 2秒 | Level 2 | "您似乎很疲劳，建议休息" |
| 高PERCLOS | > 15% | Level 3 | "疲劳程度较高，请立即休息" |
| 距离过近 | < 50cm持续30秒 | Level 2 | "请保持合理用眼距离" |
| 低头过久 | pitch > 30°持续1分钟 | Level 2 | "请调整坐姿，抬头挺胸" |

**6.3 实现技术**
- 语音：pyttsx3 (离线) 或 gTTS (在线)
- LED：RPi.GPIO控制
- 弹窗：Tkinter Toplevel窗口

#### 模块7: 数据记录模块 (data_logger.py)
- 记录每日使用时长
- 记录提醒次数统计
- 生成健康报告
- 数据存储：SQLite 或 JSON文件

#### 模块8: 配置管理模块 (config.py)
- 存储所有阈值参数
- 用户偏好设置
- 校准数据

## 二、目录结构设计

```
Smart-Desktop-Fatigue-Monitoring-System/
├── README.md                   # 项目说明文档
├── requirements.txt            # 依赖库列表
├── config.yaml                 # 配置文件
├── main.py                     # 主程序入口
│
├── src/                        # 源代码目录
│   ├── __init__.py
│   ├── camera/                 # 摄像头模块
│   │   ├── __init__.py
│   │   └── camera_capture.py
│   │
│   ├── detection/              # 检测模块
│   │   ├── __init__.py
│   │   ├── face_detector.py   # 人脸检测
│   │   └── landmark_extractor.py  # 关键点提取
│   │
│   ├── analysis/               # 分析模块
│   │   ├── __init__.py
│   │   ├── fatigue_analyzer.py    # 疲劳分析
│   │   ├── distance_monitor.py    # 距离监测
│   │   └── posture_monitor.py     # 坐姿监测
│   │
│   ├── alert/                  # 提醒模块
│   │   ├── __init__.py
│   │   ├── alert_manager.py       # 提醒管理器
│   │   ├── voice_alert.py         # 语音提醒
│   │   ├── led_alert.py           # LED提醒
│   │   └── gui_alert.py           # GUI弹窗
│   │
│   ├── utils/                  # 工具模块
│   │   ├── __init__.py
│   │   ├── config_loader.py       # 配置加载
│   │   ├── data_logger.py         # 数据记录
│   │   └── metrics.py             # 性能指标
│   │
│   └── gui/                    # 图形界面
│       ├── __init__.py
│       └── main_window.py         # 主窗口
│
├── tests/                      # 测试代码
│   ├── test_fatigue.py
│   ├── test_distance.py
│   └── test_posture.py
│
├── data/                       # 数据目录
│   ├── logs/                   # 日志文件
│   ├── calibration/            # 校准数据
│   └── reports/                # 健康报告
│
├── models/                     # 模型文件（如果需要）
│
├── docs/                       # 文档目录
│   ├── API.md
│   ├── 安装指南.md
│   └── 使用手册.md
│
└── scripts/                    # 脚本目录
    ├── calibrate_camera.py     # 摄像头校准
    ├── test_performance.py     # 性能测试
    └── install_dependencies.sh # 依赖安装脚本
```

## 三、开发计划（分阶段实施）

### 阶段1: 环境搭建与基础框架（Week 1）
- [ ] 任务1.1: 树莓派环境配置
  - 安装Raspberry Pi OS
  - 配置Python 3.7+
  - 安装OpenCV、MediaPipe等依赖
- [ ] 任务1.2: 创建项目目录结构
- [ ] 任务1.3: 实现摄像头采集模块
  - 测试摄像头正常工作
  - 实现帧率控制
- [ ] 任务1.4: 集成MediaPipe Face Mesh
  - 实现人脸检测
  - 绘制关键点验证

**验收标准**: 能够实时显示摄像头画面并标注人脸关键点，帧率≥15 FPS

### 阶段2: 疲劳检测功能实现（Week 2-3）
- [ ] 任务2.1: 实现EAR计算
  - 选择眼部关键点（MediaPipe: 33, 133, 159, 145等）
  - 计算左右眼EAR值
- [ ] 任务2.2: 实现眨眼检测
  - EAR阈值判定
  - 眨眼计数器
- [ ] 任务2.3: 实现PERCLOS计算
  - 滑动窗口统计（60秒）
  - 疲劳状态判定
- [ ] 任务2.4: 长时间闭眼检测
  - 连续帧计数
  - 触发警报逻辑
- [ ] 任务2.5: 单元测试与参数调优
  - 测试不同光照条件
  - 测试不同人脸角度

**验收标准**: 疲劳检测准确率≥85%，误报率≤1次/小时

### 阶段3: 距离与坐姿监测（Week 4）
- [ ] 任务3.1: 摄像头焦距校准
  - 测量已知距离下的人脸框大小
  - 计算焦距参数
- [ ] 任务3.2: 实现距离计算
  - 基于人脸框宽度
  - 基于眼距（双眼间距）
- [ ] 任务3.3: 实现头部姿态估计
  - 选择6个关键点（鼻尖、下巴、眼角、嘴角）
  - solvePnP计算旋转向量
  - 提取pitch、yaw、roll角度
- [ ] 任务3.4: 坐姿判定逻辑
  - 低头/仰头阈值设定
  - 持续时间统计

**验收标准**: 距离和坐姿提醒准确率≥90%

### 阶段4: 多模态提醒系统（Week 5）
- [ ] 任务4.1: LED硬件接线与测试
  - GPIO引脚配置
  - LED闪烁控制
- [ ] 任务4.2: 语音提醒实现
  - pyttsx3离线语音
  - 提醒文本编写
- [ ] 任务4.3: GUI弹窗设计
  - Tkinter窗口设计
  - 样式美化
- [ ] 任务4.4: 提醒管理器
  - 分级提醒逻辑
  - 防止频繁提醒（冷却时间）
  - 提醒优先级队列

**验收标准**: 三种提醒方式均正常工作，提醒及时且不过于频繁

### 阶段5: 数据记录与GUI界面（Week 6）
- [ ] 任务5.1: 数据记录模块
  - SQLite数据库设计
  - 每日数据统计
  - 健康报告生成
- [ ] 任务5.2: 主界面设计
  - 实时监测画面
  - 状态指示器
  - 统计数据展示
- [ ] 任务5.3: 设置界面
  - 阈值参数调整
  - 提醒方式开关
  - 校准功能入口

**验收标准**: 界面友好，数据记录完整

### 阶段6: 性能优化与部署（Week 7）
- [ ] 任务6.1: 性能优化
  - 降低分辨率（320x240）
  - 跳帧处理（隔帧检测）
  - MediaPipe模型轻量化配置
  - 多线程优化（摄像头采集与处理分离）
- [ ] 任务6.2: 内存优化
  - 对象池复用
  - 及时释放资源
- [ ] 任务6.3: 开机自启动配置
  - systemd服务配置
  - 异常自动重启
- [ ] 任务6.4: 完整系统测试
  - 长时间运行测试（24小时）
  - 稳定性测试
  - 资源占用监控

**验收标准**: 树莓派上稳定运行≥15 FPS，CPU占用<70%

### 阶段7: 文档与答辩准备（Week 8）
- [ ] 任务7.1: 编写用户手册
- [ ] 任务7.2: 编写开发文档
- [ ] 任务7.3: 准备毕业答辩PPT
- [ ] 任务7.4: 录制演示视频
- [ ] 任务7.5: 撰写毕业论文

## 四、关键技术实现细节

### 4.1 EAR计算实现（伪代码）
```python
def calculate_ear(eye_landmarks):
    """
    eye_landmarks: 6个眼部关键点坐标
    返回: EAR值
    """
    # 计算垂直距离
    vertical_1 = euclidean_distance(eye_landmarks[1], eye_landmarks[5])
    vertical_2 = euclidean_distance(eye_landmarks[2], eye_landmarks[4])

    # 计算水平距离
    horizontal = euclidean_distance(eye_landmarks[0], eye_landmarks[3])

    # EAR公式
    ear = (vertical_1 + vertical_2) / (2.0 * horizontal)
    return ear
```

### 4.2 MediaPipe关键点索引（重要）
- **左眼**: 33, 160, 158, 133, 153, 144
- **右眼**: 362, 385, 387, 263, 373, 380
- **鼻尖**: 1
- **下巴**: 152
- **左眼角**: 33
- **右眼角**: 263
- **左嘴角**: 61
- **右嘴角**: 291

### 4.3 头部姿态估计实现
```python
# 3D模型点（标准人脸模型）
model_points = np.array([
    (0.0, 0.0, 0.0),          # 鼻尖
    (0.0, -330.0, -65.0),     # 下巴
    (-225.0, 170.0, -135.0),  # 左眼角
    (225.0, 170.0, -135.0),   # 右眼角
    (-150.0, -150.0, -125.0), # 左嘴角
    (150.0, -150.0, -125.0)   # 右嘴角
])

# 相机内参矩阵（需根据实际摄像头校准）
camera_matrix = np.array([
    [focal_length, 0, image_width/2],
    [0, focal_length, image_height/2],
    [0, 0, 1]
], dtype=np.float64)

# solvePnP求解
success, rotation_vector, translation_vector = cv2.solvePnP(
    model_points,
    image_points,
    camera_matrix,
    dist_coeffs
)

# 转换为旋转矩阵
rotation_matrix, _ = cv2.Rodrigues(rotation_vector)

# 提取欧拉角
pitch = math.atan2(rotation_matrix[2][1], rotation_matrix[2][2])
yaw = math.atan2(-rotation_matrix[2][0],
                  math.sqrt(rotation_matrix[2][1]**2 + rotation_matrix[2][2]**2))
roll = math.atan2(rotation_matrix[1][0], rotation_matrix[0][0])
```

### 4.4 性能优化策略
1. **降低分辨率**: 320x240足够人脸检测使用
2. **降低MediaPipe检测置信度**: `min_detection_confidence=0.5`
3. **跳帧处理**: 每2-3帧执行一次完整检测
4. **ROI裁剪**: 只处理人脸区域
5. **多线程**: 摄像头读取与处理分离
6. **禁用不必要功能**: MediaPipe的iris、attention等

## 五、依赖库清单

```txt
# requirements.txt
opencv-python==4.8.1.78
mediapipe==0.10.8
numpy==1.24.3
picamera2==0.3.12
RPi.GPIO==0.7.1
pyttsx3==2.90
PyYAML==6.0.1
```

## 六、风险与对策

| 风险 | 可能性 | 影响 | 对策 |
|------|-------|------|------|
| 树莓派性能不足 | 中 | 高 | 降低分辨率、优化算法、使用轻量级模型 |
| 光照影响检测准确率 | 高 | 中 | 添加光照补偿、自适应阈值 |
| 多人脸干扰 | 低 | 低 | 选择最大人脸或距离最近人脸 |
| MediaPipe在ARM架构兼容性 | 低 | 高 | 提前测试，准备备选方案（dlib） |
| 语音延迟影响用户体验 | 中 | 低 | 异步播放、缓存常用语音 |

## 七、评估指标

### 性能指标
- 帧率: ≥15 FPS
- CPU占用: <70%
- 内存占用: <500MB
- 启动时间: <10秒

### 功能指标
- 疲劳检测准确率: ≥85%
- 距离监测准确率: ≥90%
- 坐姿监测准确率: ≥90%
- 误报率: ≤1次/小时
- 漏报率: ≤5%

### 稳定性指标
- 连续运行时间: ≥24小时无崩溃
- 异常恢复时间: <5秒

## 八、后续扩展方向

1. **AI模型升级**: 使用深度学习模型提高准确率
2. **移动端APP**: 手机端查看健康报告
3. **云端同步**: 数据上传云端分析
4. **个性化提醒**: 根据用户习惯调整提醒策略
5. **多用户支持**: 人脸识别区分不同用户
6. **久坐提醒**: 增加久坐检测功能
7. **眼保健操引导**: 语音引导做眼保健操

---

**文档版本**: v1.0
**最后更新**: 2025-01-19
**作者**: Claude AI Assistant
