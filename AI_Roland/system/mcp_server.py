"""
MCP (Model Context Protocol) 服务器 - 暴露 AI Roland 能力给外部
"""

from typing import Any, Optional
import json
from pathlib import Path

class MCPServer:
    """MCP 服务器 - 允许外部系统通过 MCP 协议调用 AI Roland"""

    def __init__(self, engine):
        self.engine = engine
        self.config_file = engine.workspace / "config" / "mcp.json"
        self.config = self._load_config()

        # 注册的工具
        self.tools = self._register_tools()

    def _load_config(self):
        """加载 MCP 配置"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        return {
            "enabled": False,
            "port": 3010,
            "server_name": "ai-roland"
        }

    def _register_tools(self):
        """注册 MCP 工具"""

        return {
            "roland_process_input": {
                "name": "roland_process_input",
                "description": "处理用户输入，AI Roland 会自动识别意图并执行相应操作",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "input": {
                            "type": "string",
                            "description": "用户输入的文本"
                        }
                    },
                    "required": ["input"]
                }
            },

            "roland_get_status": {
                "name": "roland_get_status",
                "description": "获取 AI Roland 系统状态",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },

            "roland_get_tasks": {
                "name": "roland_get_tasks",
                "description": "获取任务清单",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "enum": ["all", "urgent", "important", "daily"],
                            "description": "任务分类，默认为 all"
                        }
                    }
                }
            },

            "roland_add_task": {
                "name": "roland_add_task",
                "description": "添加新任务到任务清单",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "task": {
                            "type": "string",
                            "description": "任务描述"
                        },
                        "category": {
                            "type": "string",
                            "enum": ["urgent", "important", "daily"],
                            "description": "任务分类"
                        }
                    },
                    "required": ["task", "category"]
                }
            },

            "roland_create_memory": {
                "name": "roland_create_memory",
                "description": "创建情景记忆",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "event": {
                            "type": "string",
                            "description": "事件标题"
                        },
                        "description": {
                            "type": "string",
                            "description": "事件详细描述"
                        }
                    },
                    "required": ["event", "description"]
                }
            },

            "roland_get_brain_state": {
                "name": "roland_get_brain_state",
                "description": "获取 AI Roland 认知状态（情绪、记忆等）",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },

            "roland_commit": {
                "name": "roland_commit",
                "description": "创建一个 commit（像 git 一样记录重要决策）",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Commit 消息"
                        },
                        "metadata": {
                            "type": "object",
                            "description": "额外的元数据"
                        }
                    },
                    "required": ["message"]
                }
            },

            "roland_add_cron_job": {
                "name": "roland_add_cron_job",
                "description": "添加定时任务（cron 格式）",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "任务名称"
                        },
                        "cron": {
                            "type": "string",
                            "description": "Cron 表达式，如 '0 9 * * *' 表示每天早上9点"
                        },
                        "action": {
                            "type": "string",
                            "description": "要执行的动作"
                        }
                    },
                    "required": ["name", "cron", "action"]
                }
            },

            "roland_web_search": {
                "name": "roland_web_search",
                "description": "使用浏览器搜索网页",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "搜索关键词"
                        }
                    },
                    "required": ["query"]
                }
            },

            "roland_send_telegram": {
                "name": "roland_send_telegram",
                "description": "发送消息到 Telegram",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "要发送的消息"
                        }
                    },
                    "required": ["message"]
                }
            },

            "roland_start_heartbeat": {
                "name": "roland_start_heartbeat",
                "description": "启动心跳循环（让 AI Roland 定期自主思考）",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "interval": {
                            "type": "number",
                            "description": "心跳间隔（秒），默认 60"
                        }
                    }
                }
            },

            "roland_stop_heartbeat": {
                "name": "roland_stop_heartbeat",
                "description": "停止心跳循环",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        }

    def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """调用工具"""

        if tool_name not in self.tools:
            return {
                "error": f"Unknown tool: {tool_name}",
                "available_tools": list(self.tools.keys())
            }

        try:
            # 路由到具体的处理函数
            if tool_name == "roland_process_input":
                return self._process_input(arguments)
            elif tool_name == "roland_get_status":
                return self._get_status()
            elif tool_name == "roland_get_tasks":
                return self._get_tasks(arguments)
            elif tool_name == "roland_add_task":
                return self._add_task(arguments)
            elif tool_name == "roland_create_memory":
                return self._create_memory(arguments)
            elif tool_name == "roland_get_brain_state":
                return self._get_brain_state()
            elif tool_name == "roland_commit":
                return self._commit(arguments)
            elif tool_name == "roland_add_cron_job":
                return self._add_cron_job(arguments)
            elif tool_name == "roland_web_search":
                return self._web_search(arguments)
            elif tool_name == "roland_send_telegram":
                return self._send_telegram(arguments)
            elif tool_name == "roland_start_heartbeat":
                return self._start_heartbeat(arguments)
            elif tool_name == "roland_stop_heartbeat":
                return self._stop_heartbeat()

        except Exception as e:
            return {
                "error": str(e),
                "tool": tool_name
            }

    def _process_input(self, args):
        """处理用户输入"""
        user_input = args.get("input")
        response = self.engine.process_user_input(user_input)
        return {
            "success": True,
            "response": response
        }

    def _get_status(self):
        """获取系统状态"""
        return {
            "workspace": str(self.engine.workspace),
            "state": self.engine.state,
            "heartbeat_running": self.engine._heartbeat_running
        }

    def _get_tasks(self, args):
        """获取任务清单"""
        category = args.get("category", "all")

        if not self.engine.tasks_file.exists():
            return {"error": "Tasks file not found"}

        content = self.engine.tasks_file.read_text(encoding='utf-8')

        import re
        all_tasks = {
            "urgent": re.findall(r'【紧急重要】\s*\n\s*(- \[.\] .+)', content),
            "important": re.findall(r'【重要不紧急】\s*\n\s*(- \[.\] .+)', content),
            "daily": re.findall(r'【日常事项】\s*\n\s*(- \[.\] .+)', content)
        }

        if category == "all":
            return all_tasks
        else:
            return {category: all_tasks.get(category, [])}

    def _add_task(self, args):
        """添加任务"""
        task = args.get("task")
        category = args.get("category")

        category_map = {
            "urgent": "【紧急重要】",
            "important": "【重要不紧急】",
            "daily": "【日常事项】"
        }

        # 添加到任务文件
        if not self.engine.tasks_file.exists():
            return {"error": "Tasks file not found"}

        content = self.engine.tasks_file.read_text(encoding='utf-8')
        category_header = category_map[category]

        # 找到对应分类
        category_pos = content.find(category_header)
        if category_pos == -1:
            return {"error": f"Category {category} not found"}

        # 插入任务
        insert_pos = content.find("\n", category_pos) + 1
        new_task = f"- [ ] {task}\n"

        new_content = content[:insert_pos] + new_task + content[insert_pos:]

        with open(self.engine.tasks_file, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return {"success": True, "task": task}

    def _create_memory(self, args):
        """创建记忆"""
        event = args.get("event")
        description = args.get("description", "")

        result = self.engine.memory_manager.create_episodic_memory(event, description)

        return {
            "success": True,
            "path": result
        }

    def _get_brain_state(self):
        """获取认知状态"""
        return {
            "emotion": self.engine.cognitive_state.get_emotion(),
            "heartbeat_count": self.engine.state.get("heartbeat_count", 0),
            "last_heartbeat": self.engine.state.get("last_heartbeat")
        }

    def _commit(self, args):
        """创建 commit"""
        message = args.get("message")
        metadata = args.get("metadata", {})

        timestamp = self.engine.cognitive_state.commit(message, metadata)

        return {
            "success": True,
            "timestamp": timestamp,
            "message": message
        }

    def _add_cron_job(self, args):
        """添加 cron 任务"""
        name = args.get("name")
        cron = args.get("cron")
        action = args.get("action")

        job = self.engine.cron_manager.add_job(name, cron, action)

        return {
            "success": True,
            "job": job
        }

    def _web_search(self, args):
        """网页搜索"""
        query = args.get("query")
        result = self.engine.browser.search(query)

        return result

    def _send_telegram(self, args):
        """发送 Telegram 消息"""
        from telegram_bot import TelegramBot

        bot = TelegramBot(self.engine)
        message = args.get("message")
        result = bot.send_message(message)

        return result

    def _start_heartbeat(self, args):
        """启动心跳"""
        interval = args.get("interval", 60)
        self.engine.start_heartbeat(interval)

        return {
            "success": True,
            "interval": interval
        }

    def _stop_heartbeat(self):
        """停止心跳"""
        self.engine.stop_heartbeat()

        return {
            "success": True
        }

    def get_manifest(self):
        """获取 MCP 服务器清单"""
        return {
            "name": self.config.get("server_name", "ai-roland"),
            "version": "2.0",
            "description": "AI Roland - 三层记忆架构自动化系统",
            "tools": list(self.tools.values())
        }

    def get_mcp_config(self):
        """获取 MCP 配置（用于 Claude Desktop 等）"""
        return f"""
# Claude Desktop MCP 配置

将以下配置添加到 Claude Desktop 的配置文件中：

**macOS**: ~/Library/Application Support/Claude/claude_desktop_config.json
**Windows**: %APPDATA%\\Claude\\claude_desktop_config.json

```json
{{
  "mcpServers": {{
    "ai-roland": {{
      "command": "python",
      "args": ["{Path(__file__).parent.absolute()}/mcp_server.py"],
      "env": {{
        "ROLAND_WORKSPACE": "{self.engine.workspace.absolute()}"
      }}
    }}
  }}
}}
```

配置完成后，重启 Claude Desktop，AI Roland 的工具就会出现在可用工具列表中。

**可用工具**：
{chr(10).join(f'- {name}' for name in self.tools.keys())}
"""


if __name__ == "__main__":
    from engine_v2 import RolandEngineV2

    engine = RolandEngineV2()
    server = MCPServer(engine)

    print("="*60)
    print("AI Roland MCP Server")
    print("="*60)
    print()
    print("可用工具:")
    for tool_name in server.tools.keys():
        print(f"  - {tool_name}")
    print()
    print("获取配置说明:")
    print("  python mcp_server.py --help")
    print()
