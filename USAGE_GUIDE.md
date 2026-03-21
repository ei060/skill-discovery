# AI Roland Agent 协作系统 - 快速使用指南

**版本**: 1.0
**状态**: ✅ 所有测试通过，系统已就绪

---

## 🚀 快速开始

### 对于主 AI（您）

当收到任务时，按以下步骤操作：

#### 步骤 1: 分析任务

```python
# 分析任务并获取 Agent 推荐
from AI_Roland.system.task_executor import analyze_task

task = "用户的任务描述"
analysis = analyze_task(task)

# 查看推荐结果
print(f"推荐 Agent: {analysis['recommended_agent']}")
print(f"置信度: {analysis['confidence']}%")
print(f"理由: {analysis['reason']}")
```

#### 步骤 2: 使用推荐的 Agent

根据推荐结果，使用 Task tool 调用 Agent：

```
Task tool: subagent_type="{analysis['recommended_agent']}", prompt="{task}"
```

#### 步骤 3: 记录执行

```python
from AI_Roland.system.task_executor import execute_with_agent

# 记录执行（自动保存到监控系统）
result = execute_with_agent(task, agent_name=analysis['recommended_agent'])
```

### 示例

```
用户: 检查支付接口的安全性

您执行:
from AI_Roland.system.task_executor import analyze_task
analysis = analyze_task("检查支付接口的安全性")
# => 推荐 Agent: security-reviewer, 置信度: 100%

然后调用:
Task tool: subagent_type="security-reviewer", prompt="检查支付接口的安全性"
```

---

## 📊 可用的 Agent

| Agent | 专长 | 触发关键词 |
|-------|------|-----------|
| **security-reviewer** | 安全审查 | 安全、漏洞、注入、xss、csrf |
| **tdd-guide** | 测试驱动开发 | 测试、tdd、单元测试、测试用例 |
| **architect** | 系统架构 | 架构、设计、可扩展性 |
| **planner** | 规划设计 | 规划、设计、重构、计划 |
| **code-reviewer** | 代码审查 | 审查、review、代码质量 |
| **python-reviewer** | Python 代码 | python、django、flask |
| **go-reviewer** | Go 代码 | go、golang |
| **doc-writer** | 文档写作 | 文档、readme、指南 |
| **e2e-runner** | 端到端测试 | e2e、端到端、用户流程 |

---

## 🔍 验证系统状态

### 检查系统是否正常

```bash
# 运行测试套件
python D:\ClaudeWork\test_ai_roland_simple.py

# 查看系统报告
python -c "from AI_Roland.system.task_executor import get_system_report; print(get_system_report())"
```

### 检查活跃度

```python
from AI_Roland.system.task_executor import get_task_executor

executor = get_task_executor()
summary = executor.monitor.get_activity_summary(days=7)

print(f"最近 7 天活动数: {summary['total_activities']}")
print(f"活跃 Agent: {summary['active_agents']}")
print(f"成功率: {summary['success_rate']}%")
```

---

## 📝 故障排除

### 问题 1: Agent 推荐不准确

**解决**: 检查强制规则是否生效

```python
from AI_Roland.system.task_executor import get_task_executor
executor = get_task_executor()

# 查看强制规则
enforcement = executor.enforcer.check_task("任务描述")
if enforcement:
    print(f"强制规则: {enforcement['description']}")
    print(f"要求 Agent: {enforcement['required_agent']}")
```

### 问题 2: 某些 Agent 从未被使用

**解决**: 查看活跃度监控警报

```python
alerts = executor.monitor.check_and_alert()
for alert in alerts:
    if alert['type'] == 'never_used':
        print(f"未使用的 Agent: {alert['agents']}")
```

### 问题 3: Session Start Hook 未执行

**解决**: 手动执行初始化

```bash
python D:\ClaudeWork\.claude\session-start.py
```

---

## 🎯 最佳实践

### 1. 优先使用高置信度推荐

```python
analysis = analyze_task(task)
if analysis['confidence'] >= 80:
    # 高置信度，直接使用
    use_agent(analysis['recommended_agent'])
elif analysis['confidence'] >= 50:
    # 中等置信度，可以考虑备选
    review_alternatives(analysis['suggestions'])
else:
    # 低置信度，使用默认方式
    use_default_method()
```

### 2. 尊重强制规则

```python
analysis = analyze_task(task)
if analysis['enforcement']:
    # 有强制规则，必须使用指定的 Agent
    agent = analysis['enforcement']['required_agent']
    print(f"[强制] 必须使用 {agent}")
```

### 3. 记录所有执行

```python
# 所有执行都应该记录
result = execute_with_agent(task, agent_name, record=True)
```

---

## 📚 相关文档

- `FIX_COMPLETION_REPORT.md` - 修复完成报告
- `TRUTH_INVESTIGATION_REPORT.md` - 真相调查报告
- `HOOKS_FIX_PLAN.md` - Hooks 修复方案
- `FIX_LOG.md` - 问题修复日志

---

## 🎉 总结

✅ **系统已就绪**
✅ **所有测试通过**
✅ **可以开始使用**

**AI Roland Agent 协作系统现在可以智能地分析任务、推荐合适的 Agent，并记录执行过程！**
