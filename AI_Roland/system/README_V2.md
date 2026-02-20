# AI Roland 增强版 v2.0 - 完整功能文档

> 集成 OpenAlice 所有功能，打造最强三层记忆架构自动化系统

---

## ✨ 核心升级

### v1.0 → v2.0 新增功能

| 功能 | 说明 | 状态 |
|------|------|------|
| **Heartbeat 循环** | 让系统定期自主思考和行动 | ✅ 已实现 |
| **Cron 任务** | 灵活的定时任务调度 | ✅ 已实现 |
| **认知状态** | 持久化"大脑"，记录情绪、思考、决策 | ✅ 已实现 |
| **Commit 系统** | 像 git 一样记录重要决策 | ✅ 已实现 |
| **浏览器自动化** | 自动搜索和浏览网页 | ✅ 已实现 |
| **Telegram 集成** | 通过手机管理 AI Roland | ✅ 已实现 |
| **HTTP API** | RESTful API 接口 | ✅ 已实现 |
| **MCP 服务器** | 暴露工具给外部系统 | ✅ 已实现 |

---

## 📁 系统架构

```
AI_Roland/
├── system/                      # 自动化引擎
│   ├── engine_v2.py            # 增强版核心引擎
│   ├── telegram_bot.py         # Telegram 机器人
│   ├── http_api.py             # HTTP API 服务器
│   ├── mcp_server.py           # MCP 服务器
│   ├── cli_v2.py               # 增强版 CLI
│   ├── start_all.bat           # 一键启动所有服务
│   └── README_V2.md            # 本文档
├── brain/                       # 认知状态目录
│   ├── memory.jsonl            # 记忆日志
│   ├── emotion.json            # 情绪状态
│   └── commits.jsonl           # Commit 历史
├── config/                      # 配置文件
│   ├── telegram.json           # Telegram 配置
│   ├── api.json                # API 配置
│   └── mcp.json                # MCP 配置
└── cron_jobs.json               # Cron 任务配置
```

---

## 🚀 快速启动

### 方式1：一键启动所有服务

双击运行：
```
AI_Roland/system/start_all.bat
```

这会启动：
- ✅ Heartbeat 循环（30秒间隔）
- ✅ HTTP API 服务器（端口 3000）
- ✅ MCP 服务器（端口 3010）

### 方式2：分别启动各个服务

```bash
# 启动引擎（带心跳）
cd AI_Roland/system
python engine_v2.py

# 启动 HTTP API
python http_api.py

# 启动 MCP 服务器
python mcp_server.py

# 启动 CLI
python cli_v2.py
```

---

## 💡 核心功能详解

### 1. Heartbeat 循环 - 自主思考

让 AI Roland 像人一样，定期自主思考应该做什么。

**使用示例**：
```python
from engine_v2 import RolandEngineV2

engine = RolandEngineV2()
engine.start_heartbeat(interval_seconds=30)

# 系统现在会每30秒自主思考一次：
# - 检查待办任务
# - 检查紧急事项
# - 更新认知状态
# - 执行 cron 任务
```

**通过 API 控制**：
```bash
# 启动心跳
curl -X POST http://localhost:3000/api/heartbeat/start \\
  -H "Content-Type: application/json" \\
  -d '{"interval": 60}'

# 停止心跳
curl -X POST http://localhost:3000/api/heartbeat/stop
```

---

### 2. Cron 任务 - 灵活调度

使用标准 cron 表达式设置定时任务。

**添加 Cron 任务**：
```python
# 每天早上9点生成简报
engine.cron_manager.add_job(
    name="每日简报",
    cron_expression="0 9 * * *",
    action="daily_briefing"
)

# 每周日早上10点提醒数据维护
engine.cron_manager.add_job(
    name="周日提醒",
    cron_expression="0 10 * * 0",
    action="sunday_reminder"
)

# 每2小时备份一次
engine.cron_manager.add_job(
    name="定期备份",
    cron_expression="0 */2 * * *",
    action="backup"
)
```

**通过 API 添加**：
```bash
curl -X POST http://localhost:3000/api/cron \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "每周回顾",
    "cron": "0 20 * * 5",
    "action": "weekly_review"
  }'
```

**Cron 表达式格式**：
```
* * * * *
│ │ │ │ │
│ │ │ │ └─── 星期几 (0-6, 0=周日)
│ │ │ └───── 月份 (1-12)
│ │ └─────── 日期 (1-31)
│ └───────── 小时 (0-23)
└─────────── 分钟 (0-59)

示例：
"0 9 * * *"      # 每天早上9点
"0 */2 * * *"    # 每2小时
"0 0 * * 0"      # 每周日午夜
"30 8 * * 1-5"   # 工作日早上8:30
```

---

### 3. 认知状态 - AI Roland 的"大脑"

持久化记录系统的思考、情绪和决策。

**记录思考**：
```python
# 记录用户输入
engine.cognitive_state.add_input("用户说：明天要写报告")

# 记录系统思考
engine.cognitive_state.add_thought("检测到3个紧急任务需要关注")

# 记录执行的操作
engine.cognitive_state.add_action("已添加任务到清单")
```

**情绪状态**：
```python
# 更新情绪
engine.cognitive_state.update_emotion({
    "energy": 0.8,      # 能量值
    "focus": 0.9,       # 专注度
    "stress": 0.2,      # 压力值
    "satisfaction": 0.7 # 满意度
})

# 获取当前情绪
emotion = engine.cognitive_state.get_emotion()
print(emotion)
# {'energy': 0.8, 'focus': 0.9, 'stress': 0.2, 'satisfaction': 0.7}
```

**Commit 系统**：
```python
# 记录重要决策
timestamp = engine.cognitive_state.commit(
    message="决定将所有文章迁移到新的存储结构",
    metadata={
        "reason": "提高检索效率",
        "impact": "影响100+个文件"
    }
)

# 查看 commit 历史
with open(engine.brain_dir / "commits.jsonl", 'r') as f:
    for line in f:
        commit = json.loads(line)
        print(f"{commit['timestamp']}: {commit['message']}")
```

---

### 4. 浏览器自动化 - 自动搜索

让 AI Roland 自动使用浏览器搜索信息。

**使用示例**：
```python
# 搜索网页
result = engine.browser.search("Python 自动化最新进展")
# 自动打开浏览器并显示搜索结果

# 打开指定网页
result = engine.browser.browse("https://github.com/TraderAlice/OpenAlice")
```

**通过 API 调用**：
```bash
curl -X POST http://localhost:3000/api/search \\
  -H "Content-Type: application/json" \\
  -d '{"query": "AI agents 2024"}'
```

---

### 5. Telegram 集成 - 手机管理

通过 Telegram 随时随地管理 AI Roland。

**设置步骤**：

1. **创建 Telegram 机器人**
   ```
   在 Telegram 中搜索 @BotFather
   发送 /newbot
   按提示设置机器人
   获取 bot token
   ```

2. **获取 Chat ID**
   ```
   与你的机器人发送一条消息
   访问：https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   找到 chat_id
   ```

3. **配置 AI Roland**
   ```python
   from telegram_bot import TelegramBot

   bot = TelegramBot(engine)
   bot.setup(
       bot_token="你的bot token",
       chat_ids=[123456]
   )
   ```

**可用命令**：
```
/status    # 查看系统状态
/tasks     # 查看任务清单
/briefing  # 获取每日简报
/brain     # 查看认知状态
/help      # 显示帮助
```

**发送消息到 Telegram**：
```python
# 发送每日简报
bot.send_daily_briefing()

# 发送任务提醒
bot.send_task_reminder("下午3点开会")

# 发送自定义消息
bot.send_message("系统运行正常")
```

**通过 API 发送**：
```bash
curl -X POST http://localhost:3000/api/telegram/send \\
  -H "Content-Type: application/json" \\
  -d '{"message": "你好 from AI Roland"}'
```

---

### 6. HTTP API - RESTful 接口

完整的 RESTful API，让任何系统都能调用 AI Roland。

**启动 API 服务器**：
```python
from http_api import HTTPAPIServer
from engine_v2 import RolandEngineV2

engine = RolandEngineV2()
server = HTTPAPIServer(engine)
server.run(host="127.0.0.1", port=3000)
```

**主要端点**：

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/process` | POST | 处理用户输入 |
| `/api/status` | GET | 获取系统状态 |
| `/api/tasks` | GET | 获取任务清单 |
| `/api/briefing` | GET | 获取每日简报 |
| `/api/brain` | GET | 获取认知状态 |
| `/api/memory` | POST | 创建记忆 |
| `/api/cron` | GET/POST | 管理 cron 任务 |
| `/api/heartbeat/start` | POST | 启动心跳 |
| `/api/heartbeat/stop` | POST | 停止心跳 |
| `/api/telegram/send` | POST | 发送 Telegram 消息 |
| `/api/search` | POST | 网页搜索 |

**使用示例**：

Python:
```python
import requests

# 处理输入
response = requests.post('http://localhost:3000/api/process', json={
    'input': '明天要写报告'
})
print(response.json())

# 获取任务
tasks = requests.get('http://localhost:3000/api/tasks').json()
print(tasks)
```

JavaScript:
```javascript
// 处理输入
fetch('http://localhost:3000/api/process', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({input: '明天要写报告'})
}).then(r => r.json()).then(console.log);
```

cURL:
```bash
curl -X POST http://localhost:3000/api/process \\
  -H "Content-Type: application/json" \\
  -d '{"input": "明天要写报告"}'
```

---

### 7. MCP 服务器 - 暴露工具

通过 MCP (Model Context Protocol) 暴露 AI Roland 的能力给外部系统。

**可用工具**：

| 工具名 | 说明 |
|--------|------|
| `roland_process_input` | 处理用户输入 |
| `roland_get_status` | 获取系统状态 |
| `roland_get_tasks` | 获取任务清单 |
| `roland_add_task` | 添加新任务 |
| `roland_create_memory` | 创建情景记忆 |
| `roland_get_brain_state` | 获取认知状态 |
| `roland_commit` | 创建 commit |
| `roland_add_cron_job` | 添加 cron 任务 |
| `roland_web_search` | 网页搜索 |
| `roland_send_telegram` | 发送 Telegram 消息 |
| `roland_start_heartbeat` | 启动心跳 |
| `roland_stop_heartbeat` | 停止心跳 |

**配置 Claude Desktop**：

1. 打开 Claude Desktop 配置文件
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. 添加配置：
```json
{
  "mcpServers": {
    "ai-roland": {
      "command": "python",
      "args": ["D:/ClaudeWork/AI_Roland/system/mcp_server.py"],
      "env": {
        "ROLAND_WORKSPACE": "D:/ClaudeWork/AI_Roland"
      }
    }
  }
}
```

3. 重启 Claude Desktop

4. 在 Claude 中使用：
```
请使用 roland_process_input 工具处理输入："明天要写报告"
```

---

## 🎯 典型使用场景

### 场景1：个人助理模式

```python
# 启动引擎和心跳
engine = RolandEngineV2()
engine.start_heartbeat(interval_seconds=60)

# 设置 Telegram
bot = TelegramBot(engine)
bot.setup(bot_token="xxx", chat_ids=[123456])

# 添加定时任务
engine.cron_manager.add_job(
    name="晨间简报",
    cron_expression="0 8 * * *",
    action="daily_briefing"
)

# 现在你每天早上8点会收到 Telegram 简报
# 系统每分钟自主思考一次
# 随时通过 Telegram 管理任务
```

### 场景2：API 服务模式

```python
# 启动 API 服务器
engine = RolandEngineV2()
server = HTTPAPIServer(engine)
server.run(port=3000)

# 现在任何系统都可以通过 HTTP 调用
# Python、JavaScript、cURL 等
```

### 场景3：Claude 集成模式

```bash
# 配置 Claude Desktop MCP
# 在 Claude 中直接使用 AI Roland 的能力

# 示例对话：
用户：帮我添加一个任务，下周要完成项目报告
Claude：好的，我使用 roland_add_task 工具...
Claude：任务已添加到【重要不紧急】分类

用户：创建一个情景记忆，记录今天的学习内容
Claude：我使用 roland_create_memory 工具...
Claude：情景记忆已创建
```

---

## 📊 与 OpenAlice 功能对比

| 功能 | OpenAlice | AI Roland v2.0 |
|------|-----------|---------------|
| 文件驱动 | ✅ | ✅ |
| 推理驱动 | ✅ | ✅ |
| Heartbeat | ✅ | ✅ |
| Cron | ✅ | ✅ |
| 认知状态 | ✅ | ✅ |
| 浏览器集成 | ✅ | ✅ |
| Telegram | ✅ | ✅ |
| HTTP API | ✅ | ✅ |
| MCP | ✅ | ✅ |
| **三层记忆** | ❌ | ✅ 独有 |
| **中文优化** | ❌ | ✅ 独有 |
| **时间意图捕获** | ❌ | ✅ 独有 |

---

## 🔧 配置文件

### telegram.json
```json
{
  "enabled": true,
  "bot_token": "你的bot token",
  "allowed_chat_ids": [123456],
  "commands": {
    "/status": "查看系统状态",
    "/tasks": "查看任务清单"
  }
}
```

### api.json
```json
{
  "enabled": true,
  "host": "127.0.0.1",
  "port": 3000,
  "api_key": ""
}
```

### mcp.json
```json
{
  "enabled": true,
  "port": 3010,
  "server_name": "ai-roland"
}
```

### cron_jobs.json
```json
{
  "jobs": [
    {
      "name": "每日简报",
      "cron": "0 9 * * *",
      "action": "daily_briefing",
      "enabled": true
    }
  ]
}
```

---

## 🚀 下一步

1. **启动系统**
   ```bash
   cd AI_Roland/system
   python start_all.bat
   ```

2. **测试功能**
   - 访问 http://localhost:3000 查看 API 文档
   - 配置 Telegram 机器人
   - 配置 Claude Desktop MCP

3. **自定义扩展**
   - 添加新的 cron 任务
   - 创建自定义意图识别
   - 扩展认知状态

---

## 📝 开发路线图

- [ ] 添加更多浏览器自动化功能
- [ ] 支持更多消息平台（微信、Discord）
- [ ] 添加数据库支持（可选）
- [ ] 添加 Web UI
- [ ] 支持分布式部署
- [ ] 添加机器学习模型

---

**版本**: v2.0
**发布日期**: 2026-02-19
**状态**: ✅ 全部功能已实现并测试

---

## 🙏 致谢

本系统深受 [OpenAlice](https://github.com/TraderAlice/OpenAlice) 启发，感谢作者的开源贡献！
