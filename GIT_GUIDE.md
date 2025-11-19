# Git 命令使用指南

> 专为本项目定制的Git操作手册，适合Git初学者

## 📚 目录

- [基础概念](#基础概念)
- [常用命令速查](#常用命令速查)
- [日常开发流程](#日常开发流程)
- [分支管理](#分支管理)
- [提交规范](#提交规范)
- [常见问题解决](#常见问题解决)
- [实用技巧](#实用技巧)

---

## 基础概念

### Git的三个区域

```
工作区 (Working Directory)
    ↓ git add
暂存区 (Staging Area)
    ↓ git commit
本地仓库 (Local Repository)
    ↓ git push
远程仓库 (Remote Repository)
```

### 重要术语

| 术语 | 说明 | 示例 |
|------|------|------|
| **工作区** | 你直接编辑文件的地方 | 你的项目文件夹 |
| **暂存区** | 准备提交的文件列表 | `git add` 后的文件 |
| **仓库** | Git存储历史记录的地方 | `.git` 文件夹 |
| **分支** | 独立的开发线 | `main`, `claude/review-project-plan-xxx` |
| **提交** | 代码的一个快照 | 每次 `git commit` |
| **远程** | 托管在服务器上的仓库 | GitHub上的仓库 |

---

## 常用命令速查

### 1. 查看状态

```bash
# 查看当前状态（最常用！）
git status

# 查看简洁状态
git status -s

# 查看当前分支
git branch

# 查看所有分支（包括远程）
git branch -a
```

### 2. 查看历史

```bash
# 查看提交历史
git log

# 查看简洁历史（推荐）
git log --oneline

# 查看最近5次提交
git log --oneline -5

# 查看图形化历史
git log --oneline --graph --all

# 查看某个文件的修改历史
git log --follow README.md
```

### 3. 查看修改

```bash
# 查看工作区的修改（未add的）
git diff

# 查看暂存区的修改（已add但未commit的）
git diff --staged

# 查看某个文件的修改
git diff README.md

# 查看两次提交之间的差异
git diff commit1 commit2
```

### 4. 添加文件到暂存区

```bash
# 添加单个文件
git add README.md

# 添加多个文件
git add file1.py file2.py

# 添加所有修改过的文件
git add .

# 添加src目录下所有文件
git add src/

# 交互式添加（高级）
git add -p
```

### 5. 提交更改

```bash
# 提交暂存区的文件
git commit -m "提交信息"

# 提交并显示详细信息
git commit -v

# 修改最后一次提交（谨慎使用！）
git commit --amend

# 跳过暂存区，直接提交所有已跟踪的修改文件
git add . && git commit -m "提交信息"
```

**推荐的提交方式（多行提交信息）**:
```bash
git commit -m "$(cat <<'EOF'
简短的标题（50字以内）

详细描述：
- 修改了什么功能
- 为什么要这样修改
- 有什么影响
EOF
)"
```

### 6. 推送到远程

```bash
# 推送当前分支到远程（第一次需要-u）
git push -u origin 分支名

# 之后推送可以简写
git push

# 推送所有分支
git push --all

# 强制推送（危险！谨慎使用）
git push --force
```

### 7. 拉取远程更新

```bash
# 拉取并合并远程分支
git pull origin 分支名

# 仅拉取不合并
git fetch origin

# 拉取所有远程分支
git fetch --all
```

### 8. 撤销操作

```bash
# 撤销工作区的修改（危险！无法恢复）
git checkout -- 文件名

# 从暂存区移除文件（但保留工作区修改）
git reset HEAD 文件名

# 撤销最后一次提交（保留修改在工作区）
git reset --soft HEAD~1

# 撤销最后一次提交（修改也丢弃，危险！）
git reset --hard HEAD~1
```

---

## 日常开发流程

### 🔄 标准开发流程

#### 第一天：开始新任务

```bash
# 1. 查看当前状态
git status

# 2. 确认在正确的分支上
git branch
# 应该显示：* claude/review-project-plan-01HbXoRc4U8EzYeKMA6bxPxz

# 3. 拉取最新代码（如果有协作者）
git pull origin claude/review-project-plan-01HbXoRc4U8EzYeKMA6bxPxz

# 4. 开始编码...
```

#### 每次修改后：保存进度

```bash
# 1. 查看修改了哪些文件
git status

# 2. 查看具体修改内容
git diff

# 3. 添加要提交的文件
git add src/camera/camera_capture.py src/detection/face_detector.py

# 4. 再次确认要提交的内容
git status

# 5. 提交更改
git commit -m "实现摄像头采集模块

- 添加 camera_capture.py，实现实时视频流采集
- 集成 picamera2 库
- 支持分辨率配置（320x240 / 640x480）
- 添加帧率控制功能
"

# 6. 推送到远程（保存到GitHub）
git push
```

#### 一天工作结束

```bash
# 1. 确保所有改动都已提交
git status
# 应该显示：nothing to commit, working tree clean

# 2. 推送到远程
git push

# 3. 查看今天的工作成果
git log --oneline --since="1 day ago"
```

### 📋 快速操作模板

**添加新功能**:
```bash
# 一行命令完成：添加 → 提交 → 推送
git add . && git commit -m "添加疲劳检测功能" && git push
```

**批量操作**:
```bash
# 创建多个文件后，一次性提交
git add src/analysis/*.py && \
git commit -m "添加分析模块

- fatigue_analyzer.py: 疲劳分析
- distance_monitor.py: 距离监测
- posture_monitor.py: 坐姿监测
" && \
git push
```

---

## 分支管理

### 当前项目分支说明

本项目使用的分支：
- `main`: 主分支（稳定版本）
- `claude/review-project-plan-01HbXoRc4U8EzYeKMA6bxPxz`: 当前开发分支 ⭐

### 分支操作命令

```bash
# 查看所有分支
git branch -a

# 查看当前分支
git branch

# 切换分支（本项目不需要频繁切换）
git checkout 分支名

# 切换到main分支查看
git checkout main

# 切换回开发分支
git checkout claude/review-project-plan-01HbXoRc4U8EzYeKMA6bxPxz
```

### ⚠️ 重要提醒

在本项目中，你应该：
- ✅ 始终在 `claude/review-project-plan-01HbXoRc4U8EzYeKMA6bxPxz` 分支上开发
- ✅ 定期推送到这个分支
- ❌ 不要直接推送到 `main` 分支
- ❌ 不要自己创建新分支（除非有特殊需求）

---

## 提交规范

### 提交信息格式

**基本格式**:
```
简短标题（不超过50个字符）

详细描述（可选）：
- 做了什么
- 为什么这样做
- 有什么影响
```

### 提交信息示例

**✅ 好的提交信息**:
```bash
git commit -m "实现EAR计算和眨眼检测功能

- 添加 calculate_ear() 函数计算眼睛纵横比
- 实现眨眼检测逻辑，阈值设为0.25
- 添加眨眼计数器，统计每分钟眨眼次数
- 通过测试：正常光照下准确率达到90%
"
```

**❌ 不好的提交信息**:
```bash
git commit -m "更新"
git commit -m "修改bug"
git commit -m "完成"
```

### 提交类型前缀（可选）

```bash
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式调整
refactor: 重构代码
test: 添加测试
chore: 构建/工具变动
```

**示例**:
```bash
git commit -m "feat: 添加语音播报功能"
git commit -m "fix: 修复摄像头初始化失败的问题"
git commit -m "docs: 更新安装指南"
```

---

## 常见问题解决

### 问题1: 忘记添加文件就提交了

```bash
# 添加遗漏的文件
git add forgotten_file.py

# 修改最后一次提交（将新文件追加进去）
git commit --amend --no-edit

# 如果已经push了，需要强制推送（谨慎！）
git push --force
```

### 问题2: 提交信息写错了

```bash
# 修改最后一次提交的信息
git commit --amend

# 会打开编辑器，修改后保存退出

# 如果已经push了，需要强制推送
git push --force
```

### 问题3: 不小心修改了不想改的文件

```bash
# 查看修改内容
git diff filename

# 撤销修改（危险！修改会丢失）
git checkout -- filename

# 撤销所有未暂存的修改
git checkout -- .
```

### 问题4: 添加到暂存区但不想提交了

```bash
# 从暂存区移除（但保留修改）
git reset HEAD filename

# 移除所有暂存的文件
git reset HEAD .
```

### 问题5: 提交后发现有严重错误

```bash
# 撤销最后一次提交，保留修改
git reset --soft HEAD~1

# 修改代码...

# 重新提交
git add .
git commit -m "修正后的提交"
```

### 问题6: 查看某次提交的详细内容

```bash
# 查看最近一次提交
git show

# 查看指定提交（提交hash可从git log获取）
git show 9224a72

# 查看某次提交修改了哪些文件
git show --name-only 9224a72
```

### 问题7: 误删了文件想恢复

```bash
# 从最后一次提交恢复文件
git checkout HEAD -- filename

# 从暂存区恢复
git checkout -- filename
```

### 问题8: push被拒绝

```bash
# 错误信息：rejected because the remote contains work...

# 原因：远程有新提交，本地没有
# 解决：先拉取再推送
git pull origin claude/review-project-plan-01HbXoRc4U8EzYeKMA6bxPxz
git push
```

### 问题9: 想查看之前的代码版本

```bash
# 查看提交历史，找到目标提交的hash
git log --oneline

# 临时切换到历史版本查看
git checkout 提交hash

# 查看完毕，返回最新版本
git checkout claude/review-project-plan-01HbXoRc4U8EzYeKMA6bxPxz
```

### 问题10: 冲突解决

```bash
# 如果pull时出现冲突
git pull origin claude/review-project-plan-01HbXoRc4U8EzYeKMA6bxPxz

# Git会提示哪些文件有冲突
# 1. 打开冲突文件，查找类似这样的标记：
# <<<<<<< HEAD
# 你的修改
# =======
# 别人的修改
# >>>>>>> 远程分支

# 2. 手动编辑，删除标记，保留正确的代码

# 3. 标记为已解决
git add 冲突文件

# 4. 完成合并
git commit -m "解决合并冲突"

# 5. 推送
git push
```

---

## 实用技巧

### 技巧1: 查看图形化历史

```bash
# 美观的提交历史图
git log --oneline --graph --all --decorate

# 可以设置别名简化命令
git config --global alias.lg "log --oneline --graph --all --decorate"

# 之后只需输入
git lg
```

### 技巧2: 暂存工作进度（临时保存）

```bash
# 临时保存当前工作区（不提交）
git stash

# 切换分支或做其他事情...

# 恢复之前的工作
git stash pop

# 查看所有暂存的工作
git stash list

# 删除暂存
git stash drop
```

### 技巧3: 只提交部分修改

```bash
# 交互式添加（可以选择提交文件的部分内容）
git add -p filename

# Git会询问每一块修改是否要添加
# y = 添加这块
# n = 不添加
# s = 拆分成更小的块
# q = 退出
```

### 技巧4: 查找谁改了某行代码

```bash
# 查看每行代码的作者和提交时间
git blame filename

# 查看特定行范围
git blame -L 10,20 filename
```

### 技巧5: 搜索提交历史

```bash
# 搜索提交信息包含"摄像头"的提交
git log --grep="摄像头"

# 搜索修改了某个字符串的提交
git log -S "calculate_ear"

# 搜索某个文件的历史
git log -- src/camera/camera_capture.py
```

### 技巧6: 设置常用别名

```bash
# 设置简短命令
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.lg "log --oneline --graph"

# 之后可以使用
git st      # 代替 git status
git co main # 代替 git checkout main
git lg      # 代替 git log --oneline --graph
```

### 技巧7: 忽略文件

创建或编辑 `.gitignore` 文件：

```bash
# 本项目推荐的 .gitignore 内容
# Python
__pycache__/
*.py[cod]
*.so
*.egg
*.egg-info/
dist/
build/

# 虚拟环境
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# 项目特定
data/logs/*.log
*.db
*.sqlite

# 系统文件
.DS_Store
Thumbs.db

# 临时文件
*.tmp
temp/
```

### 技巧8: 查看配置

```bash
# 查看所有配置
git config --list

# 查看用户名和邮箱
git config user.name
git config user.email

# 设置用户名和邮箱
git config --global user.name "你的名字"
git config --global user.email "your.email@example.com"
```

---

## 🚀 快速参考卡片

### 每天必用命令

```bash
git status          # 查看状态（用得最多！）
git add .           # 添加所有修改
git commit -m "xxx" # 提交
git push            # 推送到远程
git log --oneline   # 查看历史
git diff            # 查看修改
```

### 本项目专用工作流

```bash
# 【开始工作】
git status
git pull

# 【编码中...】
# 编辑文件...

# 【提交更改】
git status
git add .
git commit -m "描述你的修改"
git push

# 【查看成果】
git log --oneline -5
```

### 救命命令（出问题时）

```bash
# 撤销工作区修改（未add）
git checkout -- 文件名

# 撤销暂存（已add但未commit）
git reset HEAD 文件名

# 撤销提交（已commit但未push）
git reset --soft HEAD~1

# 查看帮助
git --help
git 命令 --help
```

---

## 📖 推荐学习资源

### 在线教程
- [Git官方教程](https://git-scm.com/book/zh/v2)（中文版）
- [廖雪峰Git教程](https://www.liaoxuefeng.com/wiki/896043488029600)
- [GitHub Git速查表](https://training.github.com/downloads/zh_CN/github-git-cheat-sheet/)

### 可视化工具
- **GitKraken**: 图形化Git客户端
- **Sourcetree**: 免费的Git GUI工具
- **VS Code内置Git**: 如果你用VS Code，内置的Git功能很强大

### 练习网站
- [Learn Git Branching](https://learngitbranching.js.org/?locale=zh_CN)（互动式学习）

---

## ❓ 常见疑问

### Q1: 什么时候应该commit？
**A**:
- 完成一个小功能后
- 修复一个bug后
- 每天工作结束前
- 原则：小步快跑，频繁提交

### Q2: 什么时候应该push？
**A**:
- 每次commit后（如果网络允许）
- 至少每天结束前push一次
- 原则：及时备份，防止代码丢失

### Q3: commit和push有什么区别？
**A**:
- **commit**: 保存到本地仓库（还在你的电脑上）
- **push**: 上传到远程仓库（GitHub），别人能看到

### Q4: 我可以撤销已经push的提交吗？
**A**:
- 技术上可以，但需要 `git push --force`
- ⚠️ 危险操作！可能影响其他人
- 如果只有你一个人开发，相对安全

### Q5: .gitignore不生效怎么办？
**A**:
```bash
# 1. 先从git中移除缓存
git rm -r --cached .

# 2. 重新添加所有文件
git add .

# 3. 提交
git commit -m "更新.gitignore"
```

---

## 💡 最佳实践

### ✅ 应该做的

1. **经常commit**: 小步快跑，每个功能点提交一次
2. **写清楚commit message**: 方便将来查找和理解
3. **提交前检查**: `git status` 和 `git diff` 确认修改
4. **及时push**: 每天至少push一次，防止代码丢失
5. **工作前pull**: 确保使用最新代码（如果有协作）

### ❌ 不应该做的

1. **提交大量无关文件**: 使用 `.gitignore` 排除
2. **提交敏感信息**: 密码、密钥等不要提交
3. **空提交信息**: `git commit -m ""`
4. **长期不提交**: 一次性提交几百行代码
5. **随意使用 `--force`**: 除非你知道自己在做什么

---

## 🎯 本项目专用检查清单

每次提交前，检查以下几点：

- [ ] 代码可以正常运行
- [ ] 没有语法错误
- [ ] 已测试新功能
- [ ] 已添加必要的注释
- [ ] 提交信息描述清楚
- [ ] 没有提交敏感信息
- [ ] 没有提交IDE配置文件（.vscode, .idea等）

---

**最后提醒**:
- 🎓 Git是开发必备技能，值得花时间学习
- 💪 不要怕犯错，Git几乎可以恢复任何错误操作
- 📝 多练习，很快就能熟练掌握

**祝你使用愉快！有问题随时查阅本文档。**

---

*文档版本: v1.0*
*最后更新: 2025-01-19*
*适用项目: Smart-Desktop-Fatigue-Monitoring-System*
