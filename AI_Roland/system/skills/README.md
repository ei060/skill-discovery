# Skills 插件系统

可扩展的 AI 能力，通过 `/skill-name` 调用自定义功能。

## 内置 Skills

### /commit
智能生成 Git commit message

```
/commit
/commit feat=add-user-auth
/commit type=fix message=修复登录bug
```

### /briefing
生成每日简报

```
/briefing
/briefing date=today
```

## 创建自定义 Skill

### 方法 1：使用 Python API

```python
from system.skills_manager import SkillsManager

manager = SkillsManager()
manager.create_skill(
    "my_skill",
    description="我的自定义 Skill",
    prompt_template="# Skill 模板\n\nInput: {input}\n\nOutput: ..."
)
```

### 方法 2：手动创建

在 `system/skills/` 下创建目录：

```
system/skills/my_skill/
├── skill.yaml      # 配置文件
└── prompt.md       # 提示词模板
```

**skill.yaml 示例**：
```yaml
name: my_skill
description: 技能描述
version: 1.0.0
enabled: true
parameters:
  - name: param1
    description: 参数说明
    required: true
examples:
  - "/my_skill arg1"
  - "/my_skill param1=value1"
```

**prompt.md 示例**：
```markdown
# Skill 名称

你是 XXX 助手。

## 任务
{purpose}

## 输入
- 参数1: {param1}
- 参数2: {param2}

## 要求
1. ...
2. ...

## 输出
...
```

## Skill 模板变量

在 `prompt.md` 中可以使用变量：
- `{input}` - 用户输入
- `{purpose}` - 目的说明
- 自定义参数名

## 调用 Skills

### 在对话中
```
用户: /briefing
AI: [生成简报]
```

### 在代码中
```python
result = manager.execute_skill("briefing", date="today")
print(result)
```

## 列出所有 Skills
```bash
cd AI_Roland/system
python skills_manager.py
```
