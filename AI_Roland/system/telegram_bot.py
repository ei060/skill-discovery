"""
Telegram 机器人集成 - 通过手机管理 AI Roland
"""

import json
from pathlib import Path
from typing import Optional

class TelegramBot:
    """Telegram 机器人 - 允许通过 Telegram 与 AI Roland 交互"""

    def __init__(self, engine):
        self.engine = engine
        self.config_file = engine.workspace / "config" / "telegram.json"
        self.config = self._load_config()

    def _load_config(self):
        """加载 Telegram 配置"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        # 默认配置
        return {
            "enabled": False,
            "bot_token": "",
            "allowed_chat_ids": [],
            "commands": {
                "/status": "查看系统状态",
                "/tasks": "查看任务清单",
                "/briefing": "获取每日简报",
                "/brain": "查看认知状态",
                "/help": "显示帮助"
            }
        }

    def setup(self, bot_token: str, chat_ids: list):
        """设置 Telegram 机器人

        使用方法:
        1. 在 Telegram 中找 @BotFather
        2. 创建新机器人，获取 token
        3. 用你的账号跟机器人说话，获取 chat_id
        4. 调用此方法设置
        """
        self.config["bot_token"] = bot_token
        self.config["allowed_chat_ids"] = chat_ids
        self.config["enabled"] = True
        self._save_config()

        return {
            "status": "configured",
            "bot_token": bot_token[:10] + "...",
            "chat_ids": chat_ids
        }

    def send_message(self, message: str, chat_id: Optional[str] = None):
        """发送消息到 Telegram

        如果未指定 chat_id，发送到所有允许的 chat
        """
        if not self.config.get("enabled"):
            return {"error": "Telegram bot not enabled"}

        try:
            import requests

            # 如果指定了 chat_id，只发送到该 chat
            # 否则发送到所有允许的 chat
            target_ids = [chat_id] if chat_id else self.config.get("allowed_chat_ids", [])

            results = []
            for target_id in target_ids:
                url = f"https://api.telegram.org/bot{self.config['bot_token']}/sendMessage"
                data = {
                    "chat_id": target_id,
                    "text": message,
                    "parse_mode": "Markdown"
                }

                response = requests.post(url, json=data)
                results.append(response.json())

            return {"status": "sent", "results": results}

        except Exception as e:
            return {"error": str(e)}

    def send_daily_briefing(self):
        """发送每日简报到 Telegram"""
        from engine import Scheduler
        scheduler = Scheduler(self.engine)
        briefing = scheduler._generate_daily_briefing()

        return self.send_message(briefing)

    def send_task_reminder(self, task_text: str):
        """发送任务提醒"""
        message = f"""
🔔 任务提醒

{task_text}

---
AI Roland 自动提醒
        """
        return self.send_message(message)

    def _save_config(self):
        """保存配置"""
        self.config_file.parent.mkdir(exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def get_setup_instructions(self):
        """获取设置说明"""
        return """
📱 Telegram Bot 设置指南

1. 创建机器人
   - 在 Telegram 中搜索 @BotFather
   - 发送 /newbot
   - 按提示设置机器人名称
   - 获取 bot token（格式：123456:ABC-DEF...）

2. 获取 Chat ID
   - 与你的机器人发送一条消息
   - 访问：https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   - 找到 "chat":{"id":123456} 中的数字

3. 配置 AI Roland
   ```python
   bot.setup(
       bot_token="你的bot token",
       chat_ids=[123456]  # 可以添加多个
   )
   ```

4. 测试
   ```python
   bot.send_message("测试消息")
   ```

可用命令：
- /status - 查看系统状态
- /tasks - 查看任务清单
- /briefing - 获取每日简报
- /brain - 查看认知状态
- /help - 显示帮助
        """
