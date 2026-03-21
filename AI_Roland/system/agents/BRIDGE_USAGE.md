# Agent 桥接层使用指南

## 🎯 核心功能

桥接层（AgentBridge）连接ECC的执行能力和AI Roland的记忆系统，让无记忆的ECC agent获得记忆和协作能力。

---

## 📚 快速开始

### 基本使用

```python
from agent_bridge import get_agent_bridge

# 获取桥接层
bridge = get_agent_bridge()

# 准备执行上下文（自动加载记忆）
exec_ctx = bridge.prepare_execution_context(
    agent_name="code-reviewer",  # ECC agent名称
    task="审查这段Python代码",
    context={"file": "auth.py"}
)

# 查看加载的内容
print(f"经验数: {len(exec_ctx['memory_context']['recent_experiences'])}")
print(f"模式数: {len(exec_ctx['memory_context']['best_practices'])}")
print(f"协作消息: {len(exec_ctx['collaboration_context'])}")
```

---

## 🔧 主要功能

### 1. 记忆增强执行

```python
# 使用记忆增强执行
result = bridge.execute_with_memory(
    agent_name="code-reviewer",
    task="审查这段Django代码的安全性"
)

# result['enhanced_task'] 已包含记忆上下文
# 可以直接用于调用ECC agent
```

**效果对比：**

```
原始任务:
"审查这段Django代码的安全性"

增强后:
"审查这段Django代码的安全性

## 相关经验（来自你的记忆）
1. SQL注入审查：检查参数化查询
2. XSS防护：验证输出转义
3. CSRF保护：确认token验证

## 最佳实践（来自你的记忆）
- **OWASP Top 10**: 检查常见安全漏洞
- **Django安全**: 使用django.contrib.auth
- **输入验证**: 验证所有用户输入
"
```

### 2. 经验分享

```python
# agent学到新东西后，分享给其他agent
bridge.share_experience(
    agent_name="code-reviewer",
    experience={
        "title": "Django N+1查询优化",
        "category": "performance",
        "content": "使用select_related和prefetch_related",
        "benefit": "查询次数从N+1减少到2次"
    }
)
# → 广播给13个其他agent
```

### 3. 协作请求

```python
# 遇到问题时，请求其他agent帮助
matched_agent = bridge.request_collaboration(
    from_agent="code-reviewer",
    subject="遇到数据库优化问题",
    problem={
        "issue": "慢查询，耗时2秒",
        "query": "SELECT * FROM users WHERE...",
        "context": "用户表100万行"
    },
    required_capabilities=["query_review"],
    required_expertise=["sql", "optimization"],
    priority=8
)

print(f"系统已匹配到: {matched_agent}")
# → database_reviewer
```

### 4. 响应协作

```python
# 响应其他agent的请求
bridge.respond_to_collaboration(
    agent_name="database_reviewer",
    msg_id="b12a4413-1fb5-42f7-8c61-118c0e6c7a0e",
    response={
        "solution": "使用select_related优化",
        "example": "User.objects.select_related('profile')",
        "expected_improvement": "从2秒降到100ms"
    }
)
```

---

## 📊 ECC → AI Roland 名称映射

桥接层自动转换agent名称：

| ECC Agent | AI Roland Agent |
|-----------|----------------|
| code-reviewer | code_reviewer |
| security-reviewer | security_reviewer |
| python-reviewer | python_reviewer |
| go-reviewer | go_reviewer |
| kotlin-reviewer | kotlin_reviewer |
| database-reviewer | database_reviewer |
| planner | planner |
| architect | architect |
| tdd-guide | tdd_guide |
| e2e-runner | e2e_runner |
| refactor-cleaner | refactor_cleaner |
| doc-updater | doc_writer |
| verification-before-completion | verification_before_completion |
| build-error-resolver | engineer |

---

## 💡 使用场景

### 场景1：代码审查

```python
# 你调用 code-reviewer
bridge = get_agent_bridge()

# 1. 准备上下文
exec_ctx = bridge.prepare_execution_context(
    "code-reviewer",
    "审查认证模块代码"
)

# 2. 调用ECC（增强后的任务）
# Task tool 使用 exec_ctx['enhanced_task']

# 3. 执行完成后保存经验
bridge.execute_with_memory(
    "code-reviewer",
    "审查认证模块代码",
    execution_callback=my_execution_function
)
```

### 场景2：遇到专业问题

```python
# python_reviewer遇到Django性能问题
if is_performance_issue:
    # 请求database_reviewer帮助
    matched = bridge.request_collaboration(
        "python-reviewer",
        "需要数据库优化建议",
        {"problem": "N+1查询", "table": "users"},
        required_expertise=["django", "optimization"]
    )

    if matched:
        print(f"已请求{matched}协助")
```

### 场景3：分享学到的东西

```python
# security_reviewer发现新的防护模式
bridge.share_experience(
    "security-reviewer",
    {
        "title": "JWT token最佳实践",
        "category": "security",
        "content": "使用短过期期+refresh token",
        "code_example": "expires=15min, refresh=7days",
        "benefit": "降低token泄露风险"
    }
)

# → 13个agent都会学到这个经验
```

---

## 🔄 执行流程

```
用户指令: "审查这段代码"
    ↓
判断需要: code-reviewer
    ↓
获取桥接层: bridge = get_agent_bridge()
    ↓
准备上下文: exec_ctx = bridge.prepare_execution_context(...)
    ↓
加载记忆:
  - 最近5条专业经验
  - 最近5条最佳实践
  - 偏好设置
  - 待处理的协作消息
    ↓
格式化提示词: memory_prompt = bridge.format_memory_prompt(exec_ctx)
    ↓
增强任务: enhanced_task = task + memory_prompt
    ↓
调用ECC: Task tool → code-reviewer with enhanced_task
    ↓
执行结果: result
    ↓
保存经验: bridge._save_experience(..., result)
    ↓
返回结果
```

---

## 📈 系统统计

```python
# 获取系统统计
stats = bridge.get_system_stats()

print(f"执行次数: {stats['bridge']['total_executions']}")
print(f"记忆命中: {stats['bridge']['memory_hits']}")
print(f"经验保存: {stats['bridge']['experiences_saved']}")
print(f"协作触发: {stats['bridge']['collaborations_triggered']}")

print(f"\n记忆系统:")
print(f"  Agent数: {stats['memory_system']['total_agents']}")
print(f"  共享记忆: {stats['memory_system']['shared_memory_count']}")

print(f"\n协作系统:")
print(f"  消息数: {stats['collaboration_system']['total_messages']}")
print(f"  匹配分数: {stats['collaboration_system']['matcher_stats']['avg_score']:.2f}")
```

---

## 🎨 集成示例

### 在Claude Code中使用

```python
# 当你判断需要使用code-reviewer时
from agent_bridge import get_agent_bridge

bridge = get_agent_bridge()

# 增强任务
result = bridge.execute_with_memory(
    "code-reviewer",
    "审查用户认证代码"
)

# 使用增强后的任务调用ECC
Task(
    subagent_type="code-reviewer",
    prompt=result['enhanced_task']  # 包含记忆上下文
)
```

---

## ⚙️ 配置选项

### 调整记忆加载量

编辑 `agent_bridge.py`:

```python
# 默认加载最近5条经验
recent_professional = memory.professional_memory[-5:]  # 改为你需要的数量

# 默认加载最近5条模式
relevant_patterns = memory.patterns[-5:]  # 改为你需要的数量
```

### 调整协作消息数量

```python
# 默认只取前3条待处理消息
for msg in pending_messages[:3]:  # 改为[:5]获取更多
```

---

## 🔍 故障排除

### Q: 为什么没有加载记忆？

A: 检查：
1. agent名称是否正确映射
2. 记忆文件是否存在
3. 记忆文件是否有数据

```python
# 检查映射
roland_name = bridge.map_ecc_to_roland("code-reviewer")
print(f"映射后: {roland_name}")

# 检查记忆
from agent_memory import get_agent_memory_manager
mgr = get_agent_memory_manager()
memory = mgr.get_agent_memory(roland_name)
print(f"经验数: {len(memory.professional_memory)}")
```

### Q: 协作消息没有被处理？

A: 协作消息只是提示，需要agent主动响应：

```python
# 检查待处理消息
pending = bridge.collab_hub.get_pending_messages("code_reviewer")
for msg in pending:
    print(f"来自: {msg.from_agent}, 主题: {msg.subject}")

# 响应消息
bridge.respond_to_collaboration("code_reviewer", msg.msg_id, {...})
```

---

## 📝 注意事项

1. **记忆不是指令** - 记忆是参考信息，不是必须遵守的规则
2. **协作是可选的** - agent可以选择忽略或延迟响应协作请求
3. **经验要筛选** - 只保存有价值的经验，避免记忆过载
4. **定期清理** - 系统会自动限制记忆数量，但也可以手动清理

---

## 🔗 相关文件

- `agent_bridge.py` - 桥接层实现
- `agent_communication.py` - 协作通信协议
- `agent_memory.py` - 记忆管理系统
- `COLLABORATION_GUIDE.md` - 协作系统指南
