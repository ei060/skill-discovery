# AI Roland v2.0 CLI 命令参考

## 概述

AI Roland v2.0 提供完整的命令行工具集，用于管理记忆系统、本能进化和观察分析。

**创建日期**: 2026-03-15
**版本**: 1.0.0

---

## 快捷方式

### Windows
```bash
# 使用批处理快捷方式
roland <command> [args]

# 或直接使用 Python
python AI_Roland\system\roland_cli.py <command> [args]
```

### Linux/Mac
```bash
# 创建符号链接
ln -s AI_Roland/system/roland_cli.py /usr/local/bin/roland

# 或直接使用 Python
python AI_Roland/system/roland_cli.py <command> [args]
```

---

## 命令列表

### 1. memory - 查看记忆状态

显示完整的记忆系统状态报告。

```bash
roland memory
```

**输出示例**:
```
╔════════════════════════════════════════════════════════════╗
║            🧠 Homunculus Memory System                   ║
║        ECC v2.1 + AI Roland 记忆树整合                   ║
╚════════════════════════════════════════════════════════════╝

📊 当前项目: ClaudeWork (3694270db109)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌱 生命周期状态
  🌱 萌芽: 0 个
  🌿 绿叶: 2 个
  🍂 黄叶: 0 个
  🍁 枯叶: 0 个
  🪨 土壤: 0 份精华
```

---

### 2. instincts - 列出所有本能

列出系统中的所有本能，支持过滤。

```bash
roland instincts [--stage STAGE] [--scope SCOPE] [--json]
```

**选项**:
- `--stage`: 过滤生命周期阶段 (sprout|green|yellow|withered|soil)
- `--scope`: 过滤作用域 (project|global)
- `--json`: JSON 格式输出

**示例**:
```bash
# 列出所有绿叶期本能
roland instincts --stage green

# 列出所有全局本能
roland instincts --scope global

# JSON 格式输出
roland instincts --json
```

---

### 3. evolve - 进化指定本能

提升本能的置信度，可能触发生命周期阶段升级。

```bash
roland evolve <instinct_id> [--boost AMOUNT]
```

**选项**:
- `--boost`: 提升量 (默认: 0.1)

**示例**:
```bash
# 提升 0.1 置信度
roland evolve use-read-tool

# 提升 0.2 置信度
roland evolve use-read-tool --boost 0.2
```

**生命周期阶段**:
- 🌱 萌芽: 0.7 - 0.79
- 🌿 绿叶: 0.8 - 1.0
- 🍂 黄叶: 0.5 - 0.69
- 🍁 枯叶: 0.0 - 0.49

---

### 4. promote - 提升本能到全局

将高置信度的项目本能提升为全局本能。

```bash
roland promote <instinct_id>
```

**提升条件**:
- 置信度 >= 0.8 (Config.PROMOTE_CONFIDENCE_THRESHOLD)
- 当前作用域为 project

**示例**:
```bash
roland promote test-git-convention
```

---

### 5. search - 搜索本能

根据关键词搜索相关本能。

```bash
roland search <query> [--json]
```

**示例**:
```bash
# 搜索包含 "git" 的本能
roland search git

# 搜索包含 "read" 的本能
roland search read
```

---

### 6. observations - 查看观察记录

显示最近的观察记录。

```bash
roland observations [--limit N] [--json]
```

**选项**:
- `--limit`: 返回数量 (默认: 20)

**示例**:
```bash
# 查看最近 10 条观察
roland observations --limit 10

# JSON 格式输出
roland observations --json
```

---

### 7. decay - 执行置信度衰减

执行每日置信度衰减任务。

```bash
roland decay [--json]
```

**衰减规则**:
- P0 (核心): 不衰减
- P1 (重要): 每天衰减 0.004
- P2 (普通): 每天衰减 0.008

---

### 8. cleanup - 清理枯萎本能

将枯萎本能归档到土壤中。

```bash
roland cleanup [--json]
```

**归档条件**:
- 生命周期阶段为 withered
- 置信度 < 0.3

**提取精华**: 归档时会自动提取精华内容到土壤。

---

### 9. boost - 重要标记本能

大幅提升本能置信度并设置为 P0 优先级。

```bash
roland boost <instinct_id> [--amount AMOUNT]
```

**选项**:
- `--amount`: 提升量 (默认: 0.95)

**效果**:
- 置信度提升到 0.95 或更高
- 优先级设置为 P0 (永不衰减)

---

### 10. analyze - 触发观察分析

分析观察记录，检测模式并创建新本能。

```bash
roland analyze [--json]
```

**分析条件**:
- 至少 10 条观察记录

**检测模式**:
- 工具使用频率 (重复 5 次以上)
- 工具使用序列 (重复 3 次以上)

---

## 使用场景

### 场景 1: 查看系统状态
```bash
roland memory
```

### 场景 2: 搜索相关本能
```bash
roland search "git"
```

### 场景 3: 进化有用的本能
```bash
roland evolve use-read-tool --boost 0.15
```

### 场景 4: 提升成熟本能到全局
```bash
roland promote test-git-convention
```

### 场景 5: 查看观察记录
```bash
roland observations --limit 10
```

### 场景 6: 触发模式分析
```bash
roland analyze
```

---

## JSON 输出格式

所有命令都支持 `--json` 选项，输出 JSON 格式便于脚本处理。

**示例**:
```json
{
  "status": "success",
  "instinct_id": "test-git-convention",
  "old_confidence": 0.96,
  "new_confidence": 0.99,
  "old_stage": "green",
  "new_stage": "green",
  "boost": 0.1
}
```

---

## 集成到脚本

### Bash 脚本
```bash
#!/bin/bash
# 检查本能是否存在
result=$(roland search "git" --json)
count=$(echo "$result" | jq '. | length')

if [ "$count" -gt 0 ]; then
    echo "找到 $count 个相关本能"
fi
```

### Python 脚本
```python
import json
import subprocess

def evolve_instinct(instinct_id, boost=0.1):
    result = subprocess.run(
        ["python", "AI_Roland/system/roland_cli.py",
         "evolve", instinct_id, "--boost", str(boost)],
        capture_output=True, text=True
    )
    return json.loads(result.stdout)

# 使用
result = evolve_instinct("use-read-tool", 0.15)
print(f"新置信度: {result['new_confidence']}")
```

---

## 故障排除

### 命令不存在
确保已安装 Python 3.8+ 且在 PATH 中。

### 找不到本能
使用 `roland search <keyword>` 搜索，或 `roland instincts` 查看所有本能。

### 置信度不变
检查本能是否已达到最大值 (1.0)，或是否为 P0 优先级（不衰减）。

---

**创建者**: AI Roland v2.0
**基于**: ECC v2.1 Homunculus Memory System
**版本**: 1.0.0
