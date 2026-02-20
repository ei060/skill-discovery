# Hooks 系统

让 AI 能够感知工作环境并在特定事件发生时自动触发脚本。

## 可用的事件

| 事件名 | 触发时机 | 用途 |
|--------|---------|------|
| `user_prompt_submit` | 用户提交问题时 | 获取当前状态、同步任务 |
| `assistant_response` | AI 回复后 | 记录日志、更新状态 |
| `tool_call` | AI 调用工具时 | 同步工作区、验证权限 |
| `session_start` | 会话开始时 | 初始化环境、加载配置 |
| `session_end` | 会话结束时 | 保存状态、清理临时文件 |

## 配置文件

编辑 `config/hooks.yaml` 来自定义 Hooks：

```yaml
user_prompt_submit:
  - "echo '[Hook] 用户提问: $(date)'"
  - "python ../system/update_status.py"

assistant_response:
  - "echo '[Hook] AI 回复完成'"
```

## 使用示例

### 1. 在 Python 中使用

```python
from system.hooks_manager import HooksManager

hooks = HooksManager()

# 触发事件
result = hooks.trigger_user_prompt_submit("测试问题")
print(result)
```

### 2. 实用的 Hook 场景

**自动同步 Git 状态**：
```yaml
user_prompt_submit:
  - "git status --short"
  - "git rev-parse --abbrev-ref HEAD"
```

**记录工作节奏**：
```yaml
assistant_response:
  - "echo '$(date)' >> ../logs/work_rhythm.log"
```

**自动更新任务清单**：
```yaml
session_end:
  - "python ../system/task_utils.py"
  - "python ../system/archive_completed_tasks.py"
```

## 日志

所有 Hooks 的执行日志保存在 `logs/hooks.log`

## 测试

```bash
cd AI_Roland/system
python hooks_manager.py
```
