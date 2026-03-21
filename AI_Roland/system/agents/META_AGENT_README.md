# Meta-Agent 系统

> 让6个Agent像主Agent一样具备反思和自我优化能力

## 📖 什么是Meta-Agent？

Meta-Agent（元Agent）是AI Roland系统中的"反思者"，负责监控、审查和优化其他6个专业Agent的表现。

### 核心能力

1. **每日审查** - 分析每个Agent的表现，识别优势和弱点
2. **每周优化** - 清理重复记忆、合并相似内容、提取模式
3. **跨Agent学习** - 传播最佳实践和常见模式
4. **生成建议** - 提供具体的改进方向

---

## 🚀 快速开始

### 方式1：命令行手动运行

```bash
# 查看Meta-Agent状态
cd AI_Roland/system/agents
python meta_agent.py --status

# 执行每日审查
python meta_agent.py --review

# 执行每周优化
python meta_agent.py --optimize

# 执行跨Agent学习
python meta_agent.py --cross-learn
```

### 方式2：Windows批处理

```bash
# 查看状态
meta_agent_schedule.bat status

# 执行每日审查
meta_agent_schedule.bat daily

# 执行每周优化
meta_agent_schedule.bat weekly
```

### 方式3：自动化调度（推荐）

```bash
# 启动自动调度器（后台运行）
python meta_agent_scheduler.py --start

# 手动触发一次任务
python meta_agent_scheduler.py --daily    # 每日审查
python meta_agent_scheduler.py --weekly   # 每周优化
python meta_agent_scheduler.py --cross    # 跨学习

# 停止调度器
python meta_agent_scheduler.py --stop
```

---

## 📊 审查报告示例

```
📊 ARCHITECT
   任务完成: 2个
   专业记忆: 12条
   模式库: 5条
   质量分数: 19.17/100
   学习速度: +12条/周
   ✅ 优势: 模式库完善（5条模式）, 最近一周有活动，学习活跃
   ⚠️  弱点: 记忆质量需提升（19.17/100）
```

### 质量分数说明

Meta-Agent会评估每个Agent的记忆质量（0-100分）：

- **tasks_with_approach**: 任务记录是否包含详细方法（40分）
- **tasks_with_lessons**: 任务记录是否包含经验教训（30分）
- **memories_with_context**: 记忆是否有上下文信息（30分）

**目标**：所有Agent质量分数 ≥ 70分

---

## 🔄 调度计划

自动化调度器默认配置：

| 时间 | 任务 | 描述 |
|------|------|------|
| 每天 09:00 | 每日审查 | 分析Agent表现，生成改进建议 |
| 每周一 03:00 | 每周优化 | 清理重复、合并相似、提取模式 |
| 每3天 | 跨Agent学习 | 传播最佳实践和常见模式 |

---

## 📂 文件结构

```
AI_Roland/system/agents/
├── meta_agent.py              # Meta-Agent核心
├── meta_agent_scheduler.py    # 自动化调度器
├── meta_agent_schedule.bat    # Windows批处理
└── meta/                      # 元数据存储
    ├── review_history.json    # 审查历史
    ├── optimization_log.json  # 优化日志
    └── cross_learning.json    # 跨学习记录
```

---

## 💡 使用建议

### 开发阶段
```bash
# 手动执行，观察效果
python meta_agent.py --review
python meta_agent.py --optimize
```

### 生产环境
```bash
# 启动自动调度，后台运行
python meta_agent_scheduler.py --start
```

### 定期检查
```bash
# 查看状态，了解系统健康度
python meta_agent.py --status
```

---

## 🎯 预期效果

### 短期（1周内）
- ✅ 识别所有Agent的弱点
- ✅ 清理重复和低质量记忆
- ✅ 生成针对性改进建议

### 中期（1个月内）
- ✅ 所有Agent质量分数 ≥ 70
- ✅ 建立跨Agent知识传播机制
- ✅ 形成持续优化的良性循环

### 长期（3个月+）
- ✅ Agent自主学习和进化
- ✅ 集体智慧和协作
- ✅ 接近"像人类一样思考"的目标

---

## 🔧 集成到主系统

### 方式1：Hook触发

在 `system/hooks/hook-post.bat` 中添加：

```bash
REM 会话结束时触发审查
python %AI_ROLAND_DIR%\system\agents\meta_agent.py --review
```

### 方式2：Daemon集成

修改 `system/daemon.py`，添加Meta-Agent监控：

```python
from agents.meta_agent_scheduler import MetaAgentScheduler

class Daemon:
    def __init__(self):
        # ...
        self.meta_scheduler = MetaAgentScheduler()

    def start(self):
        # ...
        self.meta_scheduler.start()
```

---

## 📈 监控指标

Meta-Agent维护的关键指标：

- **quality_score**: 记忆质量分数（目标 ≥ 70）
- **learning_velocity**: 学习速度（条/周）
- **tasks_completed**: 完成任务数
- **cross_learning_events**: 跨学习事件数

---

## 🐛 故障排查

### 问题1：导入错误

```
ModuleNotFoundError: No module named 'homunculus_memory'
```

**解决**：确保从正确的目录运行
```bash
cd AI_Roland/system/agents
python meta_agent.py --status
```

### 问题2：权限错误

**解决**：以管理员身份运行终端

### 问题3：调度器不执行

**解决**：检查系统时间，确保09:00和03:00已到

---

## 📚 相关文档

- [Agent记忆系统](./memory/README.md)
- [Homunculus记忆系统](../homunculus/)
- [Observer守护进程](../observer_daemon.py)
- [自我改进引擎](../self_improvement_engine.py)

---

**版本**: v1.0
**创建日期**: 2026-03-17
**状态**: ✅ 已测试并可用
