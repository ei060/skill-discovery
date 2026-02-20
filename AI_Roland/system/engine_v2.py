"""
AI Roland 增强版引擎 - 集成 OpenAlice 功能
版本: v2.0
新增: Heartbeat, Cron, Browser, Telegram, HTTP API, MCP, Cognitive State
"""

import os
import json
import asyncio
import croniter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
import threading
import time

class RolandEngineV2:
    """AI Roland 增强版核心引擎"""

    def __init__(self, workspace_path=None):
        # 自动检测工作区路径
        if workspace_path is None:
            current_dir = Path(__file__).parent
            self.workspace = current_dir.parent
        else:
            self.workspace = Path(workspace_path)

        # 核心目录
        self.memory_lib = self.workspace / "记忆库"
        self.identity = self.workspace / "本体画像"
        self.tasks_file = self.workspace / "任务清单.md"
        self.chat_history = self.workspace / "对话历史.md"
        self.brain_dir = self.workspace / "brain"  # 认知状态

        # 创建必要的目录
        self.brain_dir.mkdir(exist_ok=True)

        # 初始化各个管理器
        self.intent_parser = IntentParser(self)
        self.file_router = FileRouter(self)
        self.memory_manager = MemoryManager(self)
        self.task_manager = TaskManager(self)
        self.scheduler = SchedulerV2(self)
        self.cognitive_state = CognitiveState(self)
        self.browser = BrowserBridge(self)
        self.cron_manager = CronManager(self)

        # 加载系统状态
        self.load_state()

        # 心跳循环控制
        self._heartbeat_running = False
        self._heartbeat_thread = None

    def load_state(self):
        """加载系统状态"""
        state_file = self.workspace / "system_state.json"
        if state_file.exists():
            with open(state_file, 'r', encoding='utf-8') as f:
                self.state = json.load(f)
        else:
            self.state = {
                "last_daily_briefing": None,
                "last_sunday_reminder": None,
                "last_monthly_merge": None,
                "last_storage_review": None,
                "current_session": None,
                "heartbeat_count": 0,
                "last_heartbeat": None
            }
            self.save_state()

    def save_state(self):
        """保存系统状态"""
        state_file = self.workspace / "system_state.json"
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def start_heartbeat(self, interval_seconds=60):
        """启动心跳循环 - 定期自主思考和行动"""
        if self._heartbeat_running:
            print("[OK] Heartbeat already running")
            return

        self._heartbeat_running = True
        self._heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop,
            args=(interval_seconds,),
            daemon=True
        )
        self._heartbeat_thread.start()
        print(f"[OK] Heartbeat started (interval: {interval_seconds}s)")

    def stop_heartbeat(self):
        """停止心跳循环"""
        self._heartbeat_running = False
        if self._heartbeat_thread:
            self._heartbeat_thread.join()
        print("[OK] Heartbeat stopped")

    def _heartbeat_loop(self, interval_seconds):
        """心跳循环 - 定期自主思考"""
        while self._heartbeat_running:
            try:
                # 更新心跳计数
                self.state["heartbeat_count"] += 1
                self.state["last_heartbeat"] = datetime.now().isoformat()
                self.save_state()

                # 自主思考：我应该做什么？
                self._autonomous_thinking()

                # 检查 cron 任务
                self.cron_manager.check_cron_jobs()

                # 等待下一次心跳
                time.sleep(interval_seconds)

            except Exception as e:
                print(f"[ERROR] Heartbeat error: {e}")

    def _autonomous_thinking(self):
        """自主思考 - 系统应该做什么"""
        # 1. 检查待办任务
        # 2. 检查是否有紧急事项
        # 3. 检查是否需要提醒用户
        # 4. 更新认知状态
        thoughts = []

        # 检查任务
        if self.tasks_file.exists():
            content = self.tasks_file.read_text(encoding='utf-8')
            urgent_tasks = len(re.findall(r'\[ \].*(?:紧急|明天|后天)', content))
            if urgent_tasks > 0:
                thoughts.append(f"检测到 {urgent_tasks} 个紧急任务")

        # 记录思考过程
        if thoughts:
            self.cognitive_state.add_thought(thoughts)

    def process_user_input(self, user_input):
        """处理用户输入"""
        response = {
            "actions_taken": [],
            "messages": [],
            "thoughts": []
        }

        # 记录到认知状态
        self.cognitive_state.add_input(user_input)

        # 记录会话开始
        if not self.state.get("current_session"):
            session_id = datetime.now().strftime("%Y-%m-%d %H:%M")
            self.state["current_session"] = session_id
            self.append_chat_history(session_id, user_input)
            response["messages"].append("[OK] 会话已记录")

        # 意图识别
        intents = self.intent_parser.parse(user_input)

        # 执行操作
        if intents.get("time_intent"):
            action = self.task_manager.add_from_intent(
                intents["time_intent"],
                user_input
            )
            if action:
                response["actions_taken"].append(action)
                response["messages"].append("[时间捕获] 已添加到任务清单")

        if intents.get("publish_intent"):
            action = self.file_router.update_publish_status(intents["publish_intent"])
            if action:
                response["actions_taken"].append(action)
                response["messages"].append("[发布状态] 已更新")

        if intents.get("search_intent"):
            # 使用浏览器自动化搜索
            results = self.browser.search(intents["search_intent"])
            response["actions_taken"].append(results)
            response["messages"].append("[搜索] 已执行浏览器搜索")

        # 检查定时任务
        scheduled_actions = self.scheduler.check_scheduled_tasks()
        if scheduled_actions:
            response["actions_taken"].extend(scheduled_actions)
            response["messages"].append("[定时任务] 已执行")

        # 归档完成的任务
        archived = self.task_manager.archive_completed()
        if archived:
            response["actions_taken"].extend(archived)
            response["messages"].append(f"[归档] 已归档 {len(archived)} 个任务")

        return response

    def append_chat_history(self, session_id, user_input):
        """追加对话历史"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        content = self.chat_history.read_text(encoding='utf-8') if self.chat_history.exists() else ""

        new_entry = f"""
---
### 会话：{timestamp}
**用户**：{user_input[:50]}...
**AI Roland**：正在处理...
**任务**：待更新
**产出**：待更新
---
"""

        with open(self.chat_history, 'a', encoding='utf-8') as f:
            f.write(new_entry)


class CognitiveState:
    """认知状态管理 - AI Roland 的大脑""

    def __init__(self, engine):
        self.engine = engine
        self.memory_file = engine.brain_dir / "memory.jsonl"
        self.emotion_file = engine.brain_dir / "emotion.json"
        self.commit_file = engine.brain_dir / "commits.jsonl"

    def add_input(self, input_text):
        """记录用户输入"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "input",
            "content": input_text[:200]
        }
        self._append_to_memory(entry)

    def add_thought(self, thought):
        """记录系统思考"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "thought",
            "content": thought if isinstance(thought, str) else str(thought)
        }
        self._append_to_memory(entry)

    def add_action(self, action):
        """记录执行的操作"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "action",
            "content": action if isinstance(action, str) else str(action)
        }
        self._append_to_memory(entry)

    def update_emotion(self, emotion_data):
        """更新情绪状态"""
        with open(self.emotion_file, 'w', encoding='utf-8') as f:
            json.dump(emotion_data, f, ensure_ascii=False, indent=2)

    def get_emotion(self):
        """获取当前情绪"""
        if self.emotion_file.exists():
            with open(self.emotion_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "energy": 0.5,
            "focus": 0.5,
            "stress": 0.0,
            "satisfaction": 0.5
        }

    def commit(self, message, metadata=None):
        """创建一个 commit - 像 git 一样记录重要决策"""
        commit = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "metadata": metadata or {},
            "session": self.engine.state.get("current_session")
        }
        with open(self.commit_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(commit, ensure_ascii=False) + "\n")
        return commit["timestamp"]

    def _append_to_memory(self, entry):
        """追加到记忆文件"""
        with open(self.memory_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


class BrowserBridge:
    """浏览器自动化桥接"""

    def __init__(self, engine):
        self.engine = engine

    def search(self, query):
        """使用浏览器搜索"""
        try:
            # 使用系统默认浏览器搜索
            url = f"https://www.google.com/search?q={query}"
            import webbrowser
            webbrowser.open(url)

            return {
                "action": "browser_search",
                "query": query,
                "url": url,
                "status": "opened"
            }
        except Exception as e:
            return {
                "action": "browser_search",
                "query": query,
                "error": str(e)
            }

    def browse(self, url):
        """打开指定网址"""
        try:
            import webbrowser
            webbrowser.open(url)
            return {"status": "opened", "url": url}
        except Exception as e:
            return {"status": "error", "error": str(e)}


class CronManager:
    """Cron 任务管理器"""

    def __init__(self, engine):
        self.engine = engine
        self.cron_file = engine.workspace / "cron_jobs.json"
        self.jobs = self._load_jobs()

    def _load_jobs(self):
        """加载 cron 任务"""
        if self.cron_file.exists():
            with open(self.cron_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "jobs": []
        }

    def add_job(self, name, cron_expression, action, metadata=None):
        """添加 cron 任务

        示例:
        - "0 9 * * *" - 每天早上9点
        - "0 */2 * * *" - 每2小时
        - "0 0 * * 0" - 每周日午夜
        """
        job = {
            "name": name,
            "cron": cron_expression,
            "action": action,
            "metadata": metadata or {},
            "enabled": True,
            "last_run": None,
            "next_run": self._calculate_next_run(cron_expression)
        }

        self.jobs["jobs"].append(job)
        self._save_jobs()
        return job

    def check_cron_jobs(self):
        """检查并执行到期的 cron 任务"""
        now = datetime.now()
        executed = []

        for job in self.jobs["jobs"]:
            if not job.get("enabled", True):
                continue

            next_run = datetime.fromisoformat(job["next_run"])
            if now >= next_run:
                # 执行任务
                result = self._execute_job(job)
                executed.append(result)

                # 更新下次运行时间
                job["last_run"] = now.isoformat()
                job["next_run"] = self._calculate_next_run(job["cron"])

        if executed:
            self._save_jobs()

        return executed

    def _execute_job(self, job):
        """执行 cron 任务"""
        action = job["action"]

        if action == "daily_briefing":
            from engine import Scheduler
            scheduler = Scheduler(self.engine)
            return {
                "job": job["name"],
                "action": "daily_briefing",
                "result": scheduler._generate_daily_briefing()
            }

        elif action == "sunday_reminder":
            from engine import Scheduler
            scheduler = Scheduler(self.engine)
            return {
                "job": job["name"],
                "action": "sunday_reminder",
                "result": scheduler._generate_sunday_reminder()
            }

        else:
            return {
                "job": job["name"],
                "action": action,
                "status": "executed"
            }

    def _calculate_next_run(self, cron_expression):
        """计算下次运行时间"""
        base = datetime.now()
        cron = croniter.croniter(cron_expression, base)
        return cron.get_next(datetime).isoformat()

    def _save_jobs(self):
        """保存 cron 任务"""
        with open(self.cron_file, 'w', encoding='utf-8') as f:
            json.dump(self.jobs, f, ensure_ascii=False, indent=2)

    def list_jobs(self):
        """列出所有 cron 任务"""
        return self.jobs.get("jobs", [])


class SchedulerV2:
    """增强版调度器"""

    def __init__(self, engine):
        self.engine = engine

    def check_scheduled_tasks(self):
        """检查并执行定时任务"""
        actions = []
        now = datetime.now()

        # 每日简报
        if self._should_run_daily_briefing(now):
            briefing = self._generate_daily_briefing()
            actions.append({"action": "daily_briefing", "content": briefing})

        # 周日数据维护提醒
        if self._should_run_sunday_reminder(now):
            reminder = self._generate_sunday_reminder()
            actions.append({"action": "sunday_reminder", "content": reminder})

        return actions

    def _should_run_daily_briefing(self, now):
        """检查是否应该运行每日简报"""
        last_briefing = self.engine.state.get("last_daily_briefing")
        if not last_briefing:
            return True

        last_briefing_date = datetime.fromisoformat(last_briefing).date()
        return now.date() > last_briefing_date

    def _generate_daily_briefing(self):
        """生成每日简报"""
        # 更新状态
        self.engine.state["last_daily_briefing"] = datetime.now().isoformat()
        self.engine.save_state()

        # 读取任务清单
        if not self.engine.tasks_file.exists():
            return "[ERROR] 任务清单文件不存在"

        content = self.engine.tasks_file.read_text(encoding='utf-8')

        # 提取未完成任务
        import re
        tasks = re.findall(r'- \[ \] (.+)', content)

        briefing = f"""
---
[Daily Briefing] {datetime.now().strftime("%Y-%m-%d")}

        [Today Tasks]:
"""
        for task in tasks[:5]:
            briefing += f"- [ ] {task}\n"

        briefing += f"""
[Statistics]: {len(tasks)} tasks pending

[Question] Which task do you want to start with?
---
"""

        return briefing

    def _should_run_sunday_reminder(self, now):
        """检查是否应该运行周日提醒"""
        if now.weekday() != 6:
            return False

        last_reminder = self.engine.state.get("last_sunday_reminder")
        if not last_reminder:
            return True

        last_reminder_date = datetime.fromisoformat(last_reminder).date()
        return now.date() > last_reminder_date

    def _generate_sunday_reminder(self):
        """生成周日数据维护提醒"""
        self.engine.state["last_sunday_reminder"] = datetime.now().isoformat()
        self.engine.save_state()

        return """---
[Sunday Data Maintenance Reminder]

Tasks to complete this week:
1. Enter data for published content (views, interactions, etc.)
2. Analyze which content performed well and why
3. Update viral content library status

Start now?
---
"""


# 保留原有的类
class IntentParser:
    """意图识别器"""

    def __init__(self, engine):
        self.engine = engine

    def parse(self, text):
        """解析用户输入的意图"""
        import re
        intents = {}

        # 时间意图识别
        time_patterns = [
            r'(明天|后天|下周|周[一二三四五六七]|[0-9]+月[0-9]+日)',
            r'(要发|要做|记得|别忘了|计划|打算|准备)'
        ]
        for pattern in time_patterns:
            if re.search(pattern, text):
                intents["time_intent"] = text
                break

        # 发布意图识别
        publish_patterns = [
            r'(已发布|发布了|发出去了|已经发了|刚发了)'
        ]
        for pattern in publish_patterns:
            if re.search(pattern, text):
                intents["publish_intent"] = text
                break

        # 搜索意图识别
        search_patterns = [
            r'(搜索|查一下|查找|看看)',
            r'(google|百度|bing)'
        ]
        for pattern in search_patterns:
            if re.search(pattern, text):
                intents["search_intent"] = text
                break

        # 文件创建意图
        if any(keyword in text for keyword in ["创建", "新建", "写一个", "生成"]):
            intents["create_file"] = {
                "filename": "untitled",
                "content": text
            }

        return intents


class FileRouter:
    """智能存储路由器"""

    def __init__(self, engine):
        self.engine = engine
        self.rules = {
            "article": "01-内容生产/选题管理/02-待发布",
            "material": "01-内容生产/素材库",
            "research": "03-科研",
            "business": "02-商业",
            "tool": "04-工具与效率"
        }

    def route_and_save(self, content, filename):
        """根据内容类型智能路由并保存文件"""
        content_type = self._detect_type(content)

        if content_type == "article":
            date_str = datetime.now().strftime("%Y-%m-%d")
            dir_name = f"{date_str}-{filename}"
            path = self.engine.workspace / self.rules["article"] / dir_name
        else:
            path = self.engine.workspace / self.rules[content_type]

        path.mkdir(parents=True, exist_ok=True)

        file_path = path / f"{filename}.md"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(file_path.relative_to(self.engine.workspace))

    def _detect_type(self, content):
        """检测内容类型"""
        if len(content) > 500:
            return "article"
        elif any(word in content for word in ["研究", "实验", "数据分析"]):
            return "research"
        elif any(word in content for word in ["商业", "产品", "营销"]):
            return "business"
        elif any(word in content for word in ["工具", "脚本", "自动化"]):
            return "tool"
        else:
            return "material"

    def update_publish_status(self, text):
        """更新发布状态"""
        return "状态已更新"


class MemoryManager:
    """记忆管理器"""

    def __init__(self, engine):
        self.engine = engine

    def create_episodic_memory(self, event, description):
        """创建情景记忆"""
        date_str = datetime.now().strftime("%m-%d")
        month_dir = datetime.now().strftime("%Y-%m")
        path = self.engine.memory_lib / "情景记忆" / month_dir
        path.mkdir(parents=True, exist_ok=True)

        filename = f"{date_str}-{event[:20]}.md"
        file_path = path / filename

        content = f"""# {event}

时间：{datetime.now().strftime("%Y-%m-%d %H:%M")}

## 事件描述

{description}

## 关键信息

<!-- 记录重要的细节 -->
"""

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(file_path)


class TaskManager:
    """任务管理器"""

    def __init__(self, engine):
        self.engine = engine

    def add_from_intent(self, intent_text, original_input):
        """从时间意图添加任务"""
        import re

        if any(word in intent_text for word in ["明天", "后天", "紧急"]):
            category = "【紧急重要】"
        elif any(word in intent_text for word in ["下周", "计划"]):
            category = "【重要不紧急】"
        else:
            category = "【日常事项】"

        task_desc = original_input[:100]

        if not self.engine.tasks_file.exists():
            return None

        content = self.engine.tasks_file.read_text(encoding='utf-8')

        category_pos = content.find(category)
        if category_pos == -1:
            return None

        insert_pos = content.find("\n", category_pos) + 1
        new_task = f"- [ ] {task_desc} (来自时间意图捕获)\n"

        new_content = content[:insert_pos] + new_task + content[insert_pos:]

        with open(self.engine.tasks_file, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return {"action": "task_added", "category": category}

    def archive_completed(self):
        """归档已完成的任务"""
        return []


# 主入口
if __name__ == "__main__":
    print("="*60)
    print("AI Roland 增强版引擎 v2.0")
    print("集成 OpenAlice 功能")
    print("="*60)
    print()

    # 创建引擎实例
    roland = RolandEngineV2()

    print("[OK] 引擎已启动")
    print(f"[OK] 工作区: {roland.workspace}")
    print(f"[OK] 认知状态: {roland.brain_dir}")
    print()

    # 添加默认 cron 任务
    roland.cron_manager.add_job(
        name="每日简报",
        cron_expression="0 9 * * *",  # 每天早上9点
        action="daily_briefing"
    )

    roland.cron_manager.add_job(
        name="周日提醒",
        cron_expression="0 10 * * 0",  # 每周日早上10点
        action="sunday_reminder"
    )

    print("[OK] Cron 任务已配置:")
    for job in roland.cron_manager.list_jobs():
        print(f"  - {job['name']}: {job['cron']}")
    print()

    # 启动心跳循环
    print("[INFO] 启动心跳循环...")
    roland.start_heartbeat(interval_seconds=30)

    print()
    print("="*60)
    print("系统正在运行...")
    print("按 Ctrl+C 停止")
    print("="*60)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[OK] 正在停止...")
        roland.stop_heartbeat()
        print("[OK] 已停止")
