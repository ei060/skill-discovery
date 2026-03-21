# AI Roland Agent 协作系统 - 使用指南

**版本**: 2.0
**状态**: 验收测试中
**更新时间**: 2026-03-19

---

## 快速开始

### 方式 1：使用 Task Executor（推荐）

```python
# 1. 分析任务
from AI_Roland.system.task_executor import analyze_task

task = "检查 SQL 注入漏洞"
analysis = analyze_task(task)

# 2. 查看推荐结果
print(f"推荐 Agent: {analysis['recommended_agent']}")
print(f"置信度: {analysis['confidence']}%")
print(f"理由: {analysis['reason']}")

# 3. 如果置信度 >= 50%，自动触发
if analysis['auto_trigger']:
    # 直接调用推荐的 Agent
    Task(tool="Task", subagent_type=analysis['recommended_agent'], prompt=task)
```

### 方式 2：使用 Task tool 时自动记录

```python
# 记录执行（会自动记录到监控系统）
from AI_Roland.system.task_executor import execute_with_agent

result = execute_with_agent("检查 SQL 注入", agent_name="security-reviewer", record=True)
```

---

## 可用的 Agent

| Agent | 专长 | 触发条件 |
|-------|------|---------|
| **security-reviewer** | 安全审查 | 关键词：安全、漏洞、注入、xss、csrf |
| **tdd-guide** | 测试驱动开发 | 关键词：测试、tdd、单元测试 |
| **architect** | 系统架构 | 关键词：架构、设计、可扩展性 |
| **planner** | 规划设计 | 关键词：规划、设计、重构、计划 |
| **code-reviewer** | 代码审查 | 关键词：审查、review、代码质量 |
| **python-reviewer** | Python 代码 | 关键词：python、django、flask |
| **go-reviewer** | Go 代码 | 关键词：go、golang |
| **doc-writer** | 文档写作 | 关键词：文档、readme、指南 |
| **e2e-runner** | 端到端测试 | 关键词：e2e、端到端、用户流程 |

---

## 强制规则

以下任务类型**必须**使用指定的 Agent：

1. **安全相关** → security-reviewer（强制）
2. **测试相关** → tdd-guide（强制）
3. **架构相关** → architect（建议）
4. **文档相关** → doc-writer（建议）

---

## 验证方法

### 检查 Agent 是否真的被调用

```bash
# 查看最近的 hooks 日志
tail -20 D:/ClaudeWork/AI_Roland/system/agents/hooks/memory_injection.log

# 验证 hooks 是否工作
python D:/ClaudeWork/verify_hooks_working.py
```

### 检查 Agent 使用情况

```python
from AI_Roland.system.task_executor import get_task_executor

executor = get_task_executor()
summary = executor.monitor.get_activity_summary(days=7)

print(f"活跃 Agent: {summary['active_agents']}")
print(f"成功率: {summary['success_rate']}%")
```

---

## 故障排除

### 问题 1：Agent 推荐不准确

**解决**：检查强制规则

```python
enforcement = executor.enforcer.check_task("检查 SQL 注入")
if enforcement:
    print(f"强制规则: {enforcement['description']}")
    print(f"要求 Agent: {enforcement['required_agent']}")
```

### 问题 2：Hooks 未触发

**解决**：运行验证脚本

```bash
python D:/ClaudeWork/verify_hooks_working.py
```

### 问题 3：某些 Agent 从未被使用

**解决**：查看警报

```python
alerts = executor.monitor.check_and_alert()
for alert in alerts:
    if alert['type'] == 'never_used':
        print(f"未使用的 Agent: {alert['agents']}")
```

---

## 最佳实践

1. **优先使用高置信度推荐**（>= 80%）
2. **尊重强制规则**（安全、测试等）
3. **记录所有执行**（使用 execute_with_agent）
4. **定期检查活跃度**（使用 monitor.get_activity_summary）

---

**记住**：系统的目标是为每个任务找到最合适的 Agent，而不是跳过 Agent 直接执行。
