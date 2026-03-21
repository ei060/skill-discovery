# Agent 协作协议使用指南

## 📚 快速开始

### 1. 基本使用

```python
from agent_communication import get_collaboration_hub, AgentMessage, MessageType

# 获取协作中心
hub = get_collaboration_hub()

# 发送协作请求
message = AgentMessage(
    from_agent="python_reviewer",
    subject="需要Django优化建议",
    content={
        "problem": "N+1查询问题",
        "context": "用户列表页加载慢"
    },
    required_capabilities=["query_review"],
    required_expertise=["django", "optimization"],
    priority=8
)

hub.send_message(message)
# → 系统自动匹配到最合适的Agent（如database_reviewer）
```

### 2. 查看待处理消息

```python
# 获取我的待处理消息
my_messages = hub.get_pending_messages("database_reviewer")

for msg in my_messages:
    print(f"来自: {msg.from_agent}")
    print(f"主题: {msg.subject}")
    print(f"内容: {msg.content}")
    print(f"优先级: {msg.priority}")
```

### 3. 响应消息

```python
# 响应协作请求
hub.respond_to_message(
    msg_id=message.msg_id,
    response_from="database_reviewer",
    response_content={
        "solution": "使用select_related和prefetch_related",
        "example": "User.objects.select_related('profile').all()",
        "expected_improvement": "查询次数从N+1减少到2次"
    }
)
```

### 4. 分享经验

```python
# Agent学到新东西后，分享给其他Agent
experience = {
    "title": "asyncio性能优化技巧",
    "category": "async_programming",
    "content": "使用asyncio.gather()并行执行协程",
    "example": "results = await asyncio.gather(*tasks)",
    "benefit": "性能提升3倍"
}

sent_count = hub.broadcast_experience("python_reviewer", experience)
print(f"经验已分享给 {sent_count} 个Agent")
```

---

## 🎯 消息类型

| 类型 | 说明 | 使用场景 |
|------|------|----------|
| `help_request` | 请求帮助 | 遇到无法解决的问题 |
| `query` | 查询信息 | 询问其他Agent的专业知识 |
| `share_experience` | 分享经验 | 学到新东西，主动分享 |
| `task_delegation` | 任务委托 | 委托任务给更合适的Agent |
| `provide_answer` | 提供答案 | 响应请求 |
| `broadcast` | 广播消息 | 通知所有Agent |

---

## 🔧 能力配置

每个Agent注册时需提供：

```python
AgentCapability(
    agent_name="python_reviewer",
    agent_type="language_reviewer",
    expertise=["python", "django", "flask"],      # 专业领域
    capabilities=["code_review", "type_check"],   # 能力清单
    skill_level=85,                                # 技能水平(0-100)
    availability=1.0,                              # 可用性(0.0-1.0)
    max_capacity=10                                # 最大并发任务数
)
```

---

## 📊 匹配算法

系统自动选择最合适的Agent响应请求：

1. **能力匹配** (50%) - 检查是否能处理请求
2. **专业领域匹配** (30%) - 评估专业相关性
3. **技能水平** (10%) - 优先选择技能更高的Agent
4. **可用性** (10%) - 考虑当前负载

```python
# 匹配分数示例
database_reviewer匹配"SQL优化"请求: 0.92
python_reviewer匹配"SQL优化"请求: 0.35  # 可能不会被选中
```

---

## 💡 使用场景

### 场景1：跨领域协作

```
python_reviewer遇到Django查询性能问题
    ↓
发送help_request，要求：query_review + django
    ↓
系统匹配到database_reviewer
    ↓
database_reviewer提供优化方案
```

### 场景2：经验传播

```
security_reviewer发现新的XSS防护模式
    ↓
broadcast_experience分享给所有Agent
    ↓
13个Agent接收到经验
    ↓
存入各自的专业记忆
```

### 场景3：任务委托

```
code_reviewer发现需要重构的代码
    ↓
但重构是refactor_cleaner的专业
    ↓
委托任务给refactor_cleaner
    ↓
完成后返回结果
```

---

## 📈 系统统计

```python
stats = hub.get_statistics()

print(f"注册Agent数: {stats['registered_agents']}")
print(f"消息总数: {stats['total_messages']}")
print(f"消息类型分布: {stats['by_type']}")
print(f"平均匹配分数: {stats['matcher_stats']['avg_score']}")
```

---

## 🔄 与记忆系统集成

协作消息会自动同步到记忆系统：

```python
# 1. 发送消息 → 记录到共享记忆
# 2. 完成协作 → 添加到专业记忆
# 3. 分享经验 → 传播到所有相关Agent
```

---

## ⚙️ 高级功能

### 注册消息处理器

```python
def handle_help_request(message: AgentMessage):
    print(f"收到协作请求: {message.subject}")
    # 自定义处理逻辑

hub.register_handler(MessageType.HELP_REQUEST.value, handle_help_request)
hub.start_background_processor()
```

### 查看对话历史

```python
# 查看两个Agent之间的所有对话
conversation = hub.get_conversation("python_reviewer", "database_reviewer")

for msg in conversation:
    print(f"{msg.from_agent}: {msg.subject}")
```

### 更新Agent状态

```python
# 更新可用性
hub.update_capability("python_reviewer", availability=0.5)

# 更新负载
hub.update_capability("python_reviewer", current_load=5)

# 记录完成任务
hub.update_capability("python_reviewer", tasks_completed=10)
```

---

## 📝 注意事项

1. **不要阻塞** - 消息处理是异步的，不要在处理器中执行耗时操作
2. **及时响应** - 收到请求后应尽快响应，避免过期
3. **合理优先级** - 紧急问题使用高优先级(8-10)，一般问题使用中优先级(4-7)
4. **明确需求** - 在required_capabilities和required_expertise中明确说明需求
5. **分享价值** - 只分享有价值的经验，避免信息过载

---

## 🔗 相关文件

- `agent_communication.py` - 核心通信协议实现
- `register_capabilities.py` - Agent能力注册脚本
- `capabilities.json` - 能力注册表
- `messages.json` - 消息历史记录

---

## 🆘 常见问题

**Q: 如何确保消息被正确处理？**
A: 查看消息状态，`DELIVERED`表示已送达，`COMPLETED`表示已完成。

**Q: 如果没有合适的Agent怎么办？**
A: 系统返回None，可以尝试放宽要求或人工介入。

**Q: 消息会丢失吗？**
A: 不会，所有消息都保存在messages.json中，最多保留1000条。

**Q: 如何提高匹配成功率？**
A: 在required_capabilities和required_expertise中提供更多关键词，但不要过于严格。
