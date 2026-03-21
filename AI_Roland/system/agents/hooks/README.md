# Agent Hook 自动化使用指南

## 🎯 功能说明

这个hook系统让ECC agent在执行时自动使用AI Roland的记忆系统。

---

## 📁 文件结构

```
AI_Roland/system/agents/hooks/
├── inject_memory.py          # Python: 注入记忆核心
├── inject_memory.bat         # Windows: 注入记忆脚本
├── save_memory.py            # Python: 保存经验核心
├── save_memory.bat           # Windows: 保存经验脚本
├── enhance_agent.py          # Python: Agent文件增强
└── README.md                 # 本文档
```

---

## ⚙️ 安装步骤

### 1. 修改 settings.json

在 `C:\Users\DELL\.claude\settings.json` 中添加hook配置：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Task",
        "hooks": [
          {
            "type": "command",
            "command": "python D:/ClaudeWork/AI_Roland/system/agents/hooks/inject_memory.py"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Task",
        "hooks": [
          {
            "type": "command",
            "command": "python D:/ClaudeWork/AI_Roland/system/agents/hooks/save_memory.py"
          }
        ]
      }
    ]
  }
}
```

### 2. 修改ECC Agent配置

在每个ECC agent的.md文件中添加记忆读取指令。

在 `~/.claude/agents/code-reviewer.md` 开头添加：

```markdown
---
name: code-reviewer
description: Expert code review specialist
tools: ["Read", "Grep", "Glob", "Bash"]
model: sonnet
memory_context: true
---
```

---

## 🔄 执行流程

```
你的指令
    ↓
[PreToolUse Hook]
    ↓
inject_memory.py 执行
    ├─ 识别agent名称
    ├─ 加载AI Roland记忆
    ├─ 格式化为提示词
    └─ 写入临时文件
    ↓
ECC Agent执行（带记忆上下文）
    ↓
返回结果
    ↓
[PostToolUse Hook]
    ↓
save_memory.py 执行
    ├─ 提取执行结果
    ├─ 保存到记忆
    └─ 清理临时文件
```

---

## 📊 工作原理

### PreToolUse 阶段

```python
# inject_memory.py 的工作流程

1. 检测是否是Task tool调用
2. 提取agent名称（如 code-reviewer）
3. 调用 agent_bridge.py
4. 加载对应agent的记忆：
   - 最近5条专业经验
   - 最近5条最佳实践
   - 偏好设置
   - 待处理协作消息
5. 格式化为提示词
6. 写入临时文件
7. 设置环境变量 CLAUDE_AGENT_MEMORY_FILE
```

### PostToolUse 阶段

```python
# save_memory.py 的工作流程

1. 检测是否是Task tool执行完成
2. 提取agent名称和执行结果
3. 调用 agent_memory.py
4. 保存新经验到记忆：
   - 任务内容
   - 执行结果摘要
   - 时间戳
5. 清理临时文件
```

---

## 🔍 验证是否工作

### 方法1：检查日志文件

```bash
# 查看记忆注入日志
cat AI_Roland/system/agents/hooks/memory_injection.log

# 应该看到类似的输出：
# 2026-03-17T16:00:00.123456 | Agent: code-reviewer | Memory: 719 chars | File: /tmp/agent_memory_code-reviewer_xxx.md
```

### 方法2：检查记忆文件

```bash
# 查看agent记忆是否增长
python -c "from AI_Roland.system.agents.agent_memory import get_agent_memory_manager; \
mgr = get_agent_memory_manager(); \
mem = mgr.get_agent_memory('code_reviewer'); \
print(f'Professional memory: {len(mem.professional_memory)} items')"
```

### 方法3：检查临时文件

```bash
# 在Windows上检查临时目录
dir %TEMP%\agent_memory_*.md
```

---

## 💡 使用示例

### 正常调用

```python
# 你的代码
Task(
    subagent_type="code-reviewer",
    prompt="审查这段代码"
)

# hook自动：
# 1. 加载code_reviewer的记忆
# 2. 注入到执行上下文
# 3. agent使用记忆增强执行
# 4. 保存新经验
```

### 手动禁用hook

如果某次不想使用记忆：

```python
# 设置环境变量禁用
import os
os.environ('DISABLE_MEMORY_HOOK') = '1'

Task(...)
```

---

## 🐛 故障排除

### 问题1：Hook没有执行

**检查：**
1. settings.json配置是否正确
2. 路径是否正确（使用正斜杠 /）
3. Python是否在PATH中

**调试：**
```bash
# 手动测试hook
python AI_Roland/system/agents/hooks/inject_memory.py Task
```

### 问题2：记忆没有被加载

**检查：**
1. agent名称映射是否正确
2. 记忆文件是否存在
3. 查看memory_errors.log

**调试：**
```bash
# 查看错误日志
cat AI_Roland/system/agents/hooks/memory_errors.log
```

### 问题3：临时文件没有被清理

**手动清理：**
```bash
# Windows
del %TEMP%\agent_memory_*.md

# Linux/Mac
rm /tmp/agent_memory_*.md
```

---

## 📈 性能影响

- **注入记忆**: +50-200ms（加载记忆+写入临时文件）
- **保存经验**: +50-100ms（保存到文件）
- **总开销**: +100-300ms

这个开销是可接受的，因为：
1. 只在Task tool调用时发生
2. 记忆增强会提升执行质量
3. 经验积累会让后续执行更快更好

---

## 🔧 高级配置

### 调整记忆数量

编辑 `agent_bridge.py`:

```python
# 默认加载5条，改为10条
recent_professional = memory.professional_memory[-10:]
relevant_patterns = memory.patterns[-10:]
```

### 添加agent映射

编辑 `inject_memory.py`:

```python
mapping = {
    'your-agent': 'your_roland_agent',
    # ... 其他映射
}
```

### 禁用特定agent的记忆

在hook中添加：

```python
SKIP_AGENTS = ['test-agent', 'debug-agent']
if agent_name in SKIP_AGENTS:
    sys.exit(0)
```

---

## ✅ 检查清单

使用前确认：

- [ ] settings.json已配置hook
- [ ] agent_bridge.py可以运行
- [ ] agent_communication.py可以运行
- [ ] 权限：可以读写临时目录
- [ ] 权限：可以修改ECC agent文件

---

## 📞 支持

如遇问题：

1. 查看日志文件（memory_injection.log, memory_save.log, memory_errors.log）
2. 手动测试hook脚本
3. 检查Python环境和依赖

---

**蝎大人，hook系统已就绪！配置好后，ECC agent就会自动使用记忆了。** 🎉
