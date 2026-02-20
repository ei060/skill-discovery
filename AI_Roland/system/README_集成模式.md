# AI Roland - Claude 集成版

## ✅ 已配置：按需激活

**特点**：
- ✅ 只在你调用时才工作
- ✅ 不占用 Windows 资源
- ✅ 随会话自动清理
- ✅ 无后台进程

---

## 🎯 使用方式

### 方式1：直接导入（推荐）

在 Claude 会话中：

```python
# 导入集成模块
import sys
sys.path.insert(0, 'D:/ClaudeWork/AI_Roland/system')
from claude_integration import *

# 使用
process_input("这篇文章明天要发布")
add_task("下周要完成报告", "urgent")
generate_briefing()
```

### 方式2：快捷命令

```python
# 处理输入（自动识别意图）
from claude_integration import process_input
result = process_input("明天要记得开会")

# 添加任务
from claude_integration import add_task
add_task("写项目报告", "important")

# 查看状态
from claude_integration import get_status
status = get_status()

# 生成简报
from claude_integration import generate_briefing
briefing = generate_briefing()
```

---

## 📊 可用功能

| 函数 | 说明 | 资源占用 |
|------|------|----------|
| `process_input(text)` | 处理输入，自动识别意图 | 极低 |
| `get_status()` | 获取系统状态 | 极低 |
| `get_tasks()` | 获取任务清单 | 极低 |
| `add_task(task, category)` | 添加任务 | 极低 |
| `create_memory(event, desc)` | 创建记忆 | 极低 |
| `generate_briefing()` | 生成每日简报 | 极低 |
| `cleanup()` | 清理资源 | 无 |

---

## 💡 使用示例

### 示例1：时间意图捕获

```python
from claude_integration import process_input

# 这些都会自动识别并添加到任务清单
process_input("明天要发布文章")
process_input("下周要完成报告")
process_input("后天记得开会")
```

### 示例2：直接操作

```python
from claude_integration import add_task, get_tasks

# 添加任务
add_task("紧急任务1", "urgent")
add_task("重要任务2", "important")

# 查看所有任务
tasks = get_tasks()
print(tasks)
```

### 示例3：生成简报

```python
from claude_integration import generate_briefing

briefing = generate_briefing()
print(briefing)
```

---

## 🔒 权限与安全

### 只在 Claude 会话中运行

- ✅ 不创建后台进程
- ✅ 不修改系统配置
- ✅ 不设置开机自启
- ✅ 会话结束自动清理

### 资源使用

- **CPU**: 只在调用时使用，平时 0%
- **内存**: 只在调用时占用，会话结束释放
- **磁盘**: 只读写配置文件，不创建日志

---

## 📂 文件结构

```
AI_Roland/
├── system/
│   ├── claude_integration.py  # 集成模块 ✅
│   ├── engine.py              # 核心引擎
│   └── 启动守护进程.bat        # [不再使用]
├── system_state.json          # 系统状态
├── 任务清单.md               # 任务文件
└── 记忆库/                   # 记忆存储
```

---

## 🚀 快速开始

### 在 Claude 中使用

```
我需要使用 AI Roland 处理一个任务

> 请执行：from claude_integration import process_input; result = process_input("明天要发布文章")

AI Roland 会自动：
1. 识别时间意图
2. 添加到任务清单
3. 返回处理结果
```

### 常用命令

```
# 处理输入
process_input("你的文本")

# 添加任务
add_task("任务描述", "urgent")

# 生成简报
generate_briefing()

# 查看状态
get_status()

# 查看任务
get_tasks()
```

---

## ⚙️ 配置说明

### 任务分类

- `urgent`: 【紧急重要】
- `important`: 【重要不紧急】
- `daily`: 【日常事项】

### 意图自动识别

系统会自动识别：
- 时间关键词：明天、后天、下周等
- 发布关键词：已发布、发布了等
- 搜索关键词：搜索、查一下等

---

## 🎉 总结

✅ **轻量集成**
- 不占用 Windows 资源
- 只在需要时工作
- 随会话自动清理

✅ **简单易用**
- 导入即用
- 几个函数搞定所有操作
- 无需配置

✅ **功能完整**
- 时间意图捕获
- 任务自动管理
- 状态持久化

---

**版本**: v2.0 (Claude 集成版)
**模式**: 按需激活
**资源占用**: 极低
**安全**: 不影响 Windows 主机
