"""
HTTP API 服务器 - 允许外部系统调用 AI Roland
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
from pathlib import Path
from datetime import datetime

class HTTPAPIServer:
    """HTTP API 服务器"""

    def __init__(self, engine):
        self.engine = engine
        self.app = Flask(__name__)
        CORS(self.app)

        # 配置文件
        self.config_file = engine.workspace / "config" / "api.json"
        self.config = self._load_config()

        # 注册路由
        self._register_routes()

    def _load_config(self):
        """加载 API 配置"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        return {
            "enabled": False,
            "host": "127.0.0.1",
            "port": 3000,
            "api_key": ""
        }

    def _register_routes(self):
        """注册 API 路由"""

        @self.app.route('/')
        def index():
            """API 根路径"""
            return jsonify({
                "name": "AI Roland API",
                "version": "2.0",
                "status": "running",
                "endpoints": {
                    "POST /api/process": "处理用户输入",
                    "GET /api/status": "获取系统状态",
                    "GET /api/tasks": "获取任务清单",
                    "GET /api/briefing": "获取每日简报",
                    "GET /api/brain": "获取认知状态",
                    "POST /api/memory": "创建记忆",
                    "POST /api/cron": "管理 cron 任务"
                }
            })

        @self.app.route('/api/process', methods=['POST'])
        def process_input():
            """处理用户输入"""
            data = request.get_json()

            if not data or 'input' not in data:
                return jsonify({"error": "Missing 'input' field"}), 400

            user_input = data['input']
            response = self.engine.process_user_input(user_input)

            return jsonify({
                "success": True,
                "response": response,
                "timestamp": datetime.now().isoformat()
            })

        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            """获取系统状态"""
            return jsonify({
                "workspace": str(self.engine.workspace),
                "state": self.engine.state,
                "heartbeat_running": self.engine._heartbeat_running,
                "emotion": self.engine.cognitive_state.get_emotion()
            })

        @self.app.route('/api/tasks', methods=['GET'])
        def get_tasks():
            """获取任务清单"""
            if not self.engine.tasks_file.exists():
                return jsonify({"error": "Tasks file not found"}), 404

            content = self.engine.tasks_file.read_text(encoding='utf-8')

            # 解析任务
            import re
            tasks = {
                "urgent": re.findall(r'【紧急重要】\s*\n\s*(- \[.\] .+)', content),
                "important": re.findall(r'【重要不紧急】\s*\n\s*(- \[.\] .+)', content),
                "daily": re.findall(r'【日常事项】\s*\n\s*(- \[.\] .+)', content)
            }

            return jsonify({
                "tasks": tasks,
                "total": sum(len(v) for v in tasks.values())
            })

        @self.app.route('/api/briefing', methods=['GET'])
        def get_briefing():
            """获取每日简报"""
            from engine import Scheduler
            scheduler = Scheduler(self.engine)
            briefing = scheduler._generate_daily_briefing()

            return jsonify({
                "briefing": briefing,
                "timestamp": datetime.now().isoformat()
            })

        @self.app.route('/api/brain', methods=['GET'])
        def get_brain():
            """获取认知状态"""
            return jsonify({
                "emotion": self.engine.cognitive_state.get_emotion(),
                "commits": self._get_recent_commits(limit=10),
                "heartbeat_count": self.engine.state.get("heartbeat_count", 0)
            })

        @self.app.route('/api/memory', methods=['POST'])
        def create_memory():
            """创建记忆"""
            data = request.get_json()

            if not data or 'event' not in data:
                return jsonify({"error": "Missing 'event' field"}), 400

            event = data['event']
            description = data.get('description', '')

            result = self.engine.memory_manager.create_episodic_memory(
                event, description
            )

            return jsonify({
                "success": True,
                "path": result
            })

        @self.app.route('/api/cron', methods=['GET', 'POST'])
        def manage_cron():
            """管理 cron 任务"""
            if request.method == 'GET':
                jobs = self.engine.cron_manager.list_jobs()
                return jsonify({"jobs": jobs})

            else:  # POST
                data = request.get_json()

                required_fields = ['name', 'cron', 'action']
                if not all(field in data for field in required_fields):
                    return jsonify({"error": f"Missing required fields: {required_fields}"}), 400

                job = self.engine.cron_manager.add_job(
                    name=data['name'],
                    cron_expression=data['cron'],
                    action=data['action'],
                    metadata=data.get('metadata')
                )

                return jsonify({
                    "success": True,
                    "job": job
                })

        @self.app.route('/api/heartbeat/start', methods=['POST'])
        def start_heartbeat():
            """启动心跳循环"""
            interval = request.get_json().get('interval', 60)
            self.engine.start_heartbeat(interval)

            return jsonify({
                "success": True,
                "message": f"Heartbeat started with interval {interval}s"
            })

        @self.app.route('/api/heartbeat/stop', methods=['POST'])
        def stop_heartbeat():
            """停止心跳循环"""
            self.engine.stop_heartbeat()

            return jsonify({
                "success": True,
                "message": "Heartbeat stopped"
            })

        @self.app.route('/api/telegram/send', methods=['POST'])
        def send_telegram_message():
            """发送 Telegram 消息"""
            data = request.get_json()

            if not data or 'message' not in data:
                return jsonify({"error": "Missing 'message' field"}), 400

            from telegram_bot import TelegramBot
            bot = TelegramBot(self.engine)
            result = bot.send_message(data['message'], data.get('chat_id'))

            return jsonify(result)

        @self.app.route('/api/search', methods=['POST'])
        def web_search():
            """网页搜索"""
            data = request.get_json()

            if not data or 'query' not in data:
                return jsonify({"error": "Missing 'query' field"}), 400

            result = self.engine.browser.search(data['query'])

            return jsonify(result)

    def _get_recent_commits(self, limit=10):
        """获取最近的 commits"""
        if not self.engine.cognitive_state.commit_file.exists():
            return []

        commits = []
        with open(self.engine.cognitive_state.commit_file, 'r', encoding='utf-8') as f:
            for line in f:
                if len(commits) >= limit:
                    break
                commit = json.loads(line.strip())
                commits.append(commit)

        return commits

    def run(self, host=None, port=None, debug=False):
        """启动 API 服务器"""
        if host is None:
            host = self.config.get("host", "127.0.0.1")
        if port is None:
            port = self.config.get("port", 3000)

        self.config["enabled"] = True
        self._save_config()

        print(f"[OK] API 服务器启动在 http://{host}:{port}")
        print(f"[OK] API 文档: http://{host}:{port}/")

        self.app.run(host=host, port=port, debug=debug)

    def _save_config(self):
        """保存配置"""
        self.config_file.parent.mkdir(exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def get_api_documentation(self):
        """获取 API 文档"""
        return """
# AI Roland HTTP API 文档

## 基础信息

- Base URL: `http://127.0.0.1:3000`
- Content-Type: `application/json`

## 端点列表

### 1. 处理用户输入
**POST** `/api/process`

请求体：
```json
{
  "input": "这篇文章明天要发布"
}
```

响应：
```json
{
  "success": true,
  "response": {
    "actions_taken": [...],
    "messages": [...]
  }
}
```

### 2. 获取系统状态
**GET** `/api/status`

响应：
```json
{
  "workspace": "路径",
  "state": {...},
  "heartbeat_running": true,
  "emotion": {...}
}
```

### 3. 获取任务清单
**GET** `/api/tasks`

响应：
```json
{
  "tasks": {
    "urgent": [...],
    "important": [...],
    "daily": [...]
  },
  "total": 10
}
```

### 4. 获取每日简报
**GET** `/api/briefing`

### 5. 获取认知状态
**GET** `/api/brain`

### 6. 创建记忆
**POST** `/api/memory`

请求体：
```json
{
  "event": "事件标题",
  "description": "详细描述"
}
```

### 7. 管理 Cron 任务
**GET** `/api/cron` - 列出所有任务
**POST** `/api/cron` - 添加新任务

请求体：
```json
{
  "name": "任务名称",
  "cron": "0 9 * * *",
  "action": "daily_briefing"
}
```

### 8. 心跳控制
**POST** `/api/heartbeat/start`
**POST** `/api/heartbeat/stop`

### 9. Telegram 消息
**POST** `/api/telegram/send`

请求体：
```json
{
  "message": "消息内容",
  "chat_id": "可选，指定 chat_id"
}
```

### 10. 网页搜索
**POST** `/api/search`

请求体：
```json
{
  "query": "搜索关键词"
}
```

## 使用示例

### Python
```python
import requests

# 处理输入
response = requests.post('http://localhost:3000/api/process', json={
    'input': '明天要记得写报告'
})
print(response.json())

# 获取任务
tasks = requests.get('http://localhost:3000/api/tasks').json()
print(tasks)

# 添加 cron 任务
requests.post('http://localhost:3000/api/cron', json={
    'name': '每周提醒',
    'cron': '0 10 * * 1',
    'action': 'weekly_review'
})
```

### cURL
```bash
# 处理输入
curl -X POST http://localhost:3000/api/process \\
  -H "Content-Type: application/json" \\
  -d '{"input": "明天要写报告"}'

# 获取状态
curl http://localhost:3000/api/status

# 获取任务
curl http://localhost:3000/api/tasks
```

### JavaScript
```javascript
// 处理输入
fetch('http://localhost:3000/api/process', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({input: '明天要写报告'})
}).then(r => r.json()).then(console.log);

// 获取任务
fetch('http://localhost:3000/api/tasks')
  .then(r => r.json())
  .then(console.log);
```
        """


if __name__ == "__main__":
    # 测试服务器
    from engine_v2 import RolandEngineV2

    engine = RolandEngineV2()
    server = HTTPAPIServer(engine)
    server.run(debug=True)
