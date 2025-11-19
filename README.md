# 智能桌面疲劳监测与提醒系统

> 基于树莓派和计算机视觉的桌面健康监测系统 | 毕业设计项目

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-green.svg)](https://opencv.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-orange.svg)](https://mediapipe.dev/)
[![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi-red.svg)](https://www.raspberrypi.org/)

## 📖 项目简介

本项目是一个**智能桌面疲劳监测与提醒系统**，通过树莓派摄像头实时监测用户的面部状态和坐姿，识别疲劳、近距离用眼和不良坐姿等问题，并通过语音播报、LED灯闪烁和屏幕弹窗等方式进行提醒，帮助用户养成健康的用眼和坐姿习惯。

### 核心功能

- 🥱 **疲劳状态检测**: 基于EAR和PERCLOS指标，识别眨眼异常、打瞌睡等疲劳状态
- 📏 **距离监测**: 检测用户与屏幕距离，过近时及时提醒（阈值：50cm）
- 🧘 **坐姿监测**: 通过头部姿态估计，识别长时间低头等不良坐姿
- 🔔 **多模态提醒**: 语音播报、LED闪烁、屏幕弹窗三种提醒方式
- 📊 **数据记录**: 记录每日使用情况，生成健康报告

### 技术亮点

- ⚡ 高性能：树莓派4B上稳定运行 ≥15 FPS
- 🎯 高准确率：疲劳检测准确率 ≥85%，距离/坐姿检测 ≥90%
- 🪶 轻量化：基于MediaPipe，资源占用低
- 🔧 易部署：完整的配置和安装脚本

## 📚 文档导航

### 核心文档

| 文档 | 说明 | 适用人群 |
|------|------|---------|
| [项目主题.md](./项目主题.md) | 项目需求和目标 | 所有人 |
| [PROJECT_PLAN.md](./PROJECT_PLAN.md) | **完整实施规划** ⭐ | 开发者 |
| [TECH_COMPARISON.md](./TECH_COMPARISON.md) | 技术选型对比分析 | 开发者 |

### 快速链接

- **开始开发**: 请查看 [PROJECT_PLAN.md](./PROJECT_PLAN.md) 的"开发计划"部分
- **技术选型**: 查看 [TECH_COMPARISON.md](./TECH_COMPARISON.md)
- **常见问题**: 查看 [TECH_COMPARISON.md](./TECH_COMPARISON.md) 的FAQ部分

## 🚀 快速开始

### 前置要求

**硬件**:
- 树莓派 4B (4GB推荐) 或 3B+
- 树莓派摄像头模块 V2/V3
- LED灯×3、220Ω电阻×3
- MicroSD卡（≥32GB）

**软件**:
- Raspberry Pi OS (64-bit)
- Python 3.9+

### 开发路线图

根据 [PROJECT_PLAN.md](./PROJECT_PLAN.md)，项目分为7个阶段：

```
Week 1: 环境搭建与基础框架
  └─ 摄像头采集 + MediaPipe人脸检测

Week 2-3: 疲劳检测功能
  └─ EAR计算 + 眨眼检测 + PERCLOS

Week 4: 距离与坐姿监测
  └─ 距离计算 + 头部姿态估计

Week 5: 多模态提醒系统
  └─ LED + 语音 + GUI弹窗

Week 6: 数据记录与界面
  └─ SQLite + 主界面 + 设置界面

Week 7: 性能优化与部署
  └─ 帧率优化 + 开机自启

Week 8: 文档与答辩准备
  └─ 用户手册 + 毕业论文
```

### 安装依赖（快速命令）

```bash
# 更新系统
sudo apt-get update && sudo apt-get upgrade -y

# 安装系统依赖
sudo apt-get install -y python3-pip python3-opencv libatlas-base-dev espeak

# 安装Python库
pip3 install opencv-python mediapipe numpy picamera2 RPi.GPIO pyttsx3 PyYAML
```

详细安装指南请参考 [PROJECT_PLAN.md](./PROJECT_PLAN.md) 的"阶段1"部分。

## 🏗️ 项目架构

```
主控制器
    │
    ├─ 摄像头采集模块
    ├─ 检测模块 (MediaPipe)
    ├─ 分析模块
    │   ├─ 疲劳分析 (EAR/PERCLOS)
    │   ├─ 距离监测
    │   └─ 坐姿监测 (姿态估计)
    ├─ 提醒模块
    │   ├─ 语音播报
    │   ├─ LED闪烁
    │   └─ GUI弹窗
    └─ 数据记录模块
```

完整架构图见 [PROJECT_PLAN.md](./PROJECT_PLAN.md) 第一章。

## 📊 性能指标

| 指标 | 目标值 | 说明 |
|------|-------|------|
| 帧率 | ≥15 FPS | 树莓派4B实测可达20+ FPS |
| 疲劳检测准确率 | ≥85% | 基于EAR和PERCLOS |
| 距离/坐姿准确率 | ≥90% | 基于人脸框和姿态估计 |
| 误报率 | ≤1次/小时 | 通过阈值优化 |
| CPU占用 | <70% | 多线程优化后 |

## 🛠️ 技术栈

| 类别 | 技术 | 原因 |
|------|------|------|
| 人脸检测 | MediaPipe | 轻量高效，468个3D关键点 |
| 图像处理 | OpenCV | 行业标准 |
| 摄像头 | picamera2 | 树莓派官方库 |
| 语音播报 | pyttsx3 | 离线快速 |
| 硬件控制 | RPi.GPIO | LED灯控制 |
| GUI | Tkinter | 轻量，内置 |
| 数据库 | SQLite | 轻量，无需服务器 |

技术选型详细对比见 [TECH_COMPARISON.md](./TECH_COMPARISON.md)。

## 📖 关键算法

### 1. 眼睛纵横比 (EAR)

```
EAR = (||p2-p6|| + ||p3-p5||) / (2 × ||p1-p4||)
```

- EAR < 0.25 → 闭眼
- 用于检测眨眼和长时间闭眼

### 2. PERCLOS（闭眼时间百分比）

```
PERCLOS = (闭眼时间 / 总时间) × 100%
```

- PERCLOS > 15% → 疲劳状态

### 3. 距离估计

```
距离 = (真实人脸宽度 × 焦距) / 人脸框像素宽度
```

### 4. 头部姿态（欧拉角）

使用 `cv2.solvePnP` 计算俯仰角 (pitch):
- pitch > 30° → 低头
- pitch < -15° → 仰头

## 🎯 预期成果

- ✅ 完整的桌面健康监测系统
- ✅ 在树莓派上稳定运行（≥15 FPS）
- ✅ 疲劳检测准确率达到85%以上
- ✅ 距离和坐姿提醒准确率达到90%以上
- ✅ 误报率控制在每小时1次以内
- ✅ 良好的用户体验和实用价值

## 📅 开发时间线

预计总开发周期：**8周**

详细的每周任务清单和验收标准见 [PROJECT_PLAN.md](./PROJECT_PLAN.md) 第三章。

## 🤔 常见问题

### Q: 为什么选择MediaPipe而不是dlib？
**A**: MediaPipe在树莓派上性能更优（20+ FPS vs 5-8 FPS），模型更小，且提供3D关键点。详见 [TECH_COMPARISON.md](./TECH_COMPARISON.md) 第一章。

### Q: 需要购买哪些硬件？
**A**: 树莓派4B、摄像头模块、LED灯和电阻，总成本约885元。详见 [TECH_COMPARISON.md](./TECH_COMPARISON.md) 第八章。

### Q: 如何优化帧率？
**A**: 降低分辨率至320x240、跳帧处理、多线程优化等。详见 [PROJECT_PLAN.md](./PROJECT_PLAN.md) 的"性能优化"部分。

更多问题请查看 [TECH_COMPARISON.md](./TECH_COMPARISON.md) 的FAQ章节。

## 📝 开发建议

### 推荐开发流程

1. **先阅读文档** (30分钟)
   - 通读 [PROJECT_PLAN.md](./PROJECT_PLAN.md) 了解整体规划
   - 查看 [TECH_COMPARISON.md](./TECH_COMPARISON.md) 理解技术选型

2. **搭建环境** (2小时)
   - 按 PROJECT_PLAN.md 阶段1 配置树莓派
   - 测试摄像头和MediaPipe

3. **逐模块开发** (6周)
   - 严格按PROJECT_PLAN.md的7个阶段推进
   - 每个阶段完成后进行验收测试

4. **优化与测试** (1周)
   - 性能调优、长时间稳定性测试

5. **文档撰写** (1周)
   - 用户手册、毕业论文

### 开发注意事项

⚠️ **重要提示**:
- 每个阶段都有明确的验收标准，务必达标后再进入下一阶段
- 优先保证准确率，再优化性能
- 经常在真实场景下测试（不同光照、不同姿势）
- 及时记录遇到的问题和解决方案

## 📞 支持与反馈

如果在开发过程中遇到问题：

1. 先查阅 [TECH_COMPARISON.md](./TECH_COMPARISON.md) 的FAQ部分
2. 检查 [PROJECT_PLAN.md](./PROJECT_PLAN.md) 的相关章节
3. 搜索MediaPipe和OpenCV官方文档

## 📄 许可证

本项目仅用于学习和毕业设计，请勿用于商业用途。

---

## 🎓 关于此项目

这是一个毕业设计项目，旨在通过计算机视觉技术改善桌面工作者的健康状况。项目集成了人脸检测、姿态估计、疲劳分析等多项技术，是一个很好的计算机视觉综合实践项目。

**开发者**: 祝你毕业设计顺利！🎉

**文档生成时间**: 2025-01-19
**规划版本**: v1.0

---

## 📌 下一步行动

- [ ] 阅读 [PROJECT_PLAN.md](./PROJECT_PLAN.md) 全文（约30分钟）
- [ ] 准备硬件设备（参考 [TECH_COMPARISON.md](./TECH_COMPARISON.md) 成本预算）
- [ ] 配置树莓派开发环境（按 PROJECT_PLAN.md 阶段1执行）
- [ ] 创建项目目录结构（参考 PROJECT_PLAN.md 第二章）
- [ ] 开始第一个功能模块：摄像头采集

**祝开发顺利！如有问题随时沟通。**
