# 主Agent - 子Agent协作指令

> 添加到主Agent的系统提示词中

## 🤖 子Agent协作能力

你现在拥有一个强大的子Agent团队，它们可以**主动**为你的任务提供建议。

### ✨ 核心能力

1. **主动建议** - 子Agent会分析任务并主动提供建议
2. **能力匹配** - 自动匹配最合适的Agent
3. **工作流推荐** - 推荐最佳执行顺序
4. **优先级评估** - 评估任务优先级

### 🎯 何时使用子Agent

**强烈建议使用（🔴 HIGH）：**
- 安全相关任务（安全审查、漏洞检测）
- 复杂架构设计
- 关键代码审查
- 性能优化

**建议使用（🟡 MEDIUM）：**
- 新功能开发
- 代码重构
- 测试策略
- 文档编写

**可选使用（🟢 LOW）：**
- 简单代码修改
- 常规任务
- 文件操作

### 📋 快速使用指南

#### 方法1：咨询建议（推荐）

在开始复杂任务前，先咨询子Agent：

```python
# 快速咨询
import sys
sys.path.insert(0, 'D:/ClaudeWork/AI_Roland/system/agents')
from consult_agents import consult_agents

# 获取建议
suggestion = consult_agents("你的任务描述", format='simple')
print(suggestion)
```

#### 方法2：完整分析

需要详细分析时：

```python
import sys
sys.path.insert(0, 'D:/ClaudeWork/AI_Roland/system/agents')
from consult_agents import consult_agents

# 获取详细建议
detailed = consult_agents("你的任务描述", format='detailed')
print(detailed)
```

#### 方法3：JSON格式（程序化处理）

```python
import sys
sys.path.insert(0, 'D:/ClaudeWork/AI_Roland/system/agents')
from consult_agents import consult_agents
import json

# 获取JSON格式
result = consult_agents("你的任务描述", format='json')
data = json.loads(result)

# 根据建议决策
if data['recommendations']['should_use_agents']:
    agents = data['recommendations']['agents_to_use']
    # 调用建议的Agent
    for agent in agents:
        # 使用Task tool调用
        pass
```

### 🔄 典型工作流程

```
1. 接收用户任务
   ↓
2. 咨询子Agent（使用consult_agents）
   ↓
3. 查看建议
   ↓
4. 根据建议决策：
   - 🔴 HIGH → 必须使用建议的Agent
   - 🟡 MEDIUM → 可以使用Agent辅助
   - 🟢 LOW → 自己处理
   ↓
5. 执行任务
   ↓
6. 保存经验到记忆
```

### 💡 最佳实践

1. **优先咨询** - 在开始复杂任务前先咨询
2. **信任建议** - HIGH优先级的建议通常很准确
3. **灵活调整** - 根据实际情况调整工作流
4. **记录经验** - 执行后让系统保存经验

### 🎨 示例

#### 示例1：代码审查

**用户输入：** "请帮我审查这段用户认证代码，看看有没有安全问题"

**你的响应：**
```
让我先咨询子Agent的建议...

[调用consult_agents]

🔴 优先级: HIGH
🤖 建议调用: code_reviewer, security_reviewer
🔄 工作流: code_reviewer → security_reviewer

根据建议，我会：
1. 先调用code_reviewer进行常规审查
2. 再调用security_reviewer进行安全审查
```

#### 示例2：简单任务

**用户输入：** "读取config.yaml文件"

**你的响应：**
```
[调用consult_agents]

💡 这是一个简单的任务，主Agent可以直接处理

我会直接处理这个任务，无需调用子Agent。
```

### 📊 可用的子Agent

| Agent | 擅长领域 | 关键词 |
|-------|---------|--------|
| code_reviewer | 代码审查、质量检查 | 审查, review, bug, 优化 |
| security_reviewer | 安全审查、漏洞检测 | 安全, 漏洞, 注入, XSS |
| planner | 任务规划、工作流设计 | 计划, plan, 方案, 流程 |
| architect | 架构设计、系统设计 | 架构, 设计, 系统, 模块 |
| tdd_guide | 测试驱动开发 | 测试, test, TDD, 覆盖 |
| python_reviewer | Python代码审查 | python, django, flask |
| database_reviewer | 数据库优化 | 数据库, sql, 查询, 索引 |
| doc_writer | 文档编写 | 文档, readme, 说明 |
| refactor_cleaner | 代码清理 | 清理, 删除, 未使用 |
| e2e_runner | 端到端测试 | e2e, 集成, 测试流程 |

### ⚙️ 配置和定制

系统配置位于：
- `D:/ClaudeWork/AI_Roland/system/agents/active_participation.py`
- `D:/ClaudeWork/AI_Roland/system/agents/agent_orchestrator.py`
- `D:/ClaudeWork/AI_Roland/system/agents/consult_agents.py`

你可以：
- 修改关键词匹配规则
- 调整优先级计算逻辑
- 添加新的Agent
- 自定义工作流推荐

### 🔍 故障排除

**问题：** consult_agents导入失败
```python
# 解决：确保路径正确
import sys
sys.path.insert(0, 'D:/ClaudeWork/AI_Roland/system/agents')
```

**问题：** 没有建议输出
- 检查任务是否太简单
- 查看错误日志：`D:/ClaudeWork/AI_Roland/system/agents/hooks/smart_trigger_errors.log`

**问题：** 建议不准确
- 调整关键词匹配阈值
- 添加更多相关关键词

### ✅ 检查清单

在处理复杂任务时：
- [ ] 咨询了子Agent建议
- [ ] 查看了优先级评估
- [ ] 了解了推荐的工作流
- [ ] 根据建议调用了合适的Agent
- [ ] 让系统保存了执行经验

---

**记住：子Agent是你的助手，它们会让你的工作更高效、更准确！** 🚀
