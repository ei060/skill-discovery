"""
AI Roland 自动化引擎 - 让三层记忆架构自动运行
版本: v1.0
"""

import os
import re
from datetime import datetime, timedelta
from pathlib import Path
import json

# 📋 导入任务状态管理器 (TodoWrite 持久化)
from task_state_manager import get_task_manager


class TodoWriteManager:
    """TodoWrite 任务列表管理器"""

    def __init__(self):
        self.task_manager = get_task_manager()

    def update_todos(self, todos: list) -> bool:
        """
        更新 TodoWrite 任务列表

        Args:
            todos: 任务列表，格式为 Claude Code TaskList 输出

        Returns:
            是否保存成功
        """
        return self.task_manager.save_todos(todos)

    def get_todos(self) -> list:
        """
        获取保存的 TodoWrite 任务列表

        Returns:
            任务列表
        """
        return self.task_manager.load_todos()

    def get_todos_render(self) -> str:
        """
        获取 TodoWrite 任务列表的渲染文本

        Returns:
            格式化的任务列表文本
        """
        todos = self.get_todos()
        if not todos:
            return "当前无待办任务"

        lines = ["## 待办任务列表\n"]
        for todo in todos:
            status_emoji = {
                "pending": "⏳",
                "in_progress": "🔄",
                "completed": "✅"
            }.get(todo.get("status", "pending"), "⏳")

            lines.append(f"{status_emoji} **{todo.get('subject', '未知任务')}**")
            if todo.get("description"):
                lines.append(f"   {todo['description']}")
            if todo.get("status") == "in_progress" and todo.get("activeForm"):
                lines.append(f"   正在: {todo['activeForm']}")
            lines.append("")

        return "\n".join(lines)


class RolandEngine:
    """AI Roland 核心引擎"""

    def __init__(self, workspace_path=None):
        # 自动检测工作区路径
        if workspace_path is None:
            # 从当前脚本位置推导
            current_dir = Path(__file__).parent
            # system 目录的上一级就是 AI_Roland
            self.workspace = current_dir.parent
        else:
            self.workspace = Path(workspace_path)

        self.memory_lib = self.workspace / "记忆库"
        self.identity = self.workspace / "本体画像"
        self.tasks_file = self.workspace / "任务清单.md"
        self.chat_history = self.workspace / "对话历史.md"

        # 初始化各个管理器
        self.intent_parser = IntentParser(self)
        self.file_router = FileRouter(self)
        self.memory_manager = MemoryManager(self)
        self.task_manager = TaskManager(self)
        self.scheduler = Scheduler(self)
        self.todo_manager = TodoWriteManager()  # 📋 TodoWrite 管理器

        # 加载系统状态
        self.load_state()

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
                "current_session": None
            }
            self.save_state()

    def save_state(self):
        """保存系统状态"""
        state_file = self.workspace / "system_state.json"
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    # 📋 TodoWrite 任务列表相关方法

    def update_todos(self, todos: list) -> bool:
        """
        更新 TodoWrite 任务列表（持久化）

        Args:
            todos: 任务列表，格式为 Claude Code TaskList 输出

        Returns:
            是否保存成功
        """
        return self.todo_manager.update_todos(todos)

    def get_todos_render(self) -> str:
        """
        获取 TodoWrite 任务列表的渲染文本

        Returns:
            格式化的任务列表文本
        """
        return self.todo_manager.get_todos_render()

    def get_todos(self) -> list:
        """
        获取 TodoWrite 任务列表（原始格式）

        Returns:
            任务列表
        """
        return self.todo_manager.get_todos()

    def process_user_input(self, user_input):
        """
        处理用户输入 - 这是主要的入口点
        自动识别意图并执行相应操作
        """
        response = {
            "actions_taken": [],
            "messages": []
        }

        # 1. 记录会话开始
        if not self.state.get("current_session"):
            session_id = datetime.now().strftime("%Y-%m-%d %H:%M")
            self.state["current_session"] = session_id
            self.append_chat_history(session_id, user_input)
            response["messages"].append("✓ 会话已记录")

        # 2. 意图识别
        intents = self.intent_parser.parse(user_input)

        # 3. 执行相应的自动化操作

        # 时间意图捕获
        if intents.get("time_intent"):
            action = self.task_manager.add_from_intent(
                intents["time_intent"],
                user_input
            )
            if action:
                response["actions_taken"].append(action)
                response["messages"].append("⏰ 已添加到任务清单")

        # 发布状态更新
        if intents.get("publish_intent"):
            action = self.file_router.update_publish_status(intents["publish_intent"])
            if action:
                response["actions_taken"].append(action)
                response["messages"].append("📤 已更新发布状态")

        # 文件创建意图
        if intents.get("create_file"):
            action = self.file_router.route_and_save(
                intents["create_file"]["content"],
                intents["create_file"]["filename"]
            )
            if action:
                response["actions_taken"].append(action)
                response["messages"].append(f"📁 文件已保存到: {action}")

        # 4. 检查定时任务
        scheduled_actions = self.scheduler.check_scheduled_tasks()
        if scheduled_actions:
            response["actions_taken"].extend(scheduled_actions)
            response["messages"].append("📅 已执行定时任务")

        # 5. 检查任务归档
        archived = self.task_manager.archive_completed()
        if archived:
            response["actions_taken"].extend(archived)
            response["messages"].append(f"📦 已归档 {len(archived)} 个完成的任务")

        return response

    def append_chat_history(self, session_id, user_input):
        """追加对话历史"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        # 检查是否已有今天的会话记录
        content = self.chat_history.read_text(encoding='utf-8') if self.chat_history.exists() else ""

        # 追加新会话记录
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

    def end_session(self, summary):
        """结束会话"""
        if self.state.get("current_session"):
            # 更新会话记录
            self.append_chat_history(self.state["current_session"], summary)
            self.state["current_session"] = None
            self.save_state()


class IntentParser:
    """意图识别器"""

    def __init__(self, engine):
        self.engine = engine

    def parse(self, text):
        """解析用户输入的意图"""
        intents = {}

        # 时间意图识别
        time_patterns = [
            r'(明天|后天|下周|下周|周[一二三四五六七]|[0-9]+月[0-9]+日)',
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
        # 简单的内容类型识别
        content_type = self._detect_type(content)

        # 构建路径
        if content_type == "article":
            date_str = datetime.now().strftime("%Y-%m-%d")
            dir_name = f"{date_str}-{filename}"
            path = self.engine.workspace / self.rules["article"] / dir_name
        else:
            path = self.engine.workspace / self.rules[content_type]

        # 创建目录并保存
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
        # 这里简化实现，实际需要从文本中提取文章路径
        # 移动文件从 02-待发布 到 03-已发布
        return "状态已更新"


class MemoryManager:
    """记忆管理器 - 三层记忆提炼"""

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

    def distill_semantic_memory(self, episodic_path):
        """从情景记忆提炼语义记忆"""
        # 读取情景记忆
        # 识别模式
        # 创建或更新语义记忆
        pass

    def create_forced_rule(self, rule, domain):
        """创建强制规则"""
        filename = f"强制规则_{domain}.md"
        path = self.engine.memory_lib / "强制规则" / filename

        content = f"""# 强制规则：{domain}

> 创建时间：{datetime.now().strftime("%Y-%m-%d")}

## 规则内容

{rule}

## 违反后果

<!-- 描述违反此规则的后果 -->

## 适用场景

<!-- 描述此规则适用的场景 -->
"""

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(path)


class TaskManager:
    """任务管理器"""

    def __init__(self, engine):
        self.engine = engine

    def add_from_intent(self, intent_text, original_input):
        """从时间意图添加任务"""
        # 识别紧急程度
        if any(word in intent_text for word in ["明天", "后天", "紧急"]):
            category = "【紧急重要】"
        elif any(word in intent_text for word in ["下周", "计划"]):
            category = "【重要不紧急】"
        else:
            category = "【日常事项】"

        # 提取任务描述
        task_desc = original_input[:100]

        # 添加到任务清单
        content = self.engine.tasks_file.read_text(encoding='utf-8')

        # 找到对应分类的位置
        category_pos = content.find(category)
        if category_pos == -1:
            return None

        # 插入新任务
        insert_pos = content.find("\n", category_pos) + 1
        new_task = f"- [ ] {task_desc} (来自时间意图捕获)\n"

        new_content = content[:insert_pos] + new_task + content[insert_pos:]

        with open(self.engine.tasks_file, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return {"action": "task_added", "category": category}

    def archive_completed(self):
        """归档已完成的任务"""
        # 读取任务清单
        # 找到已完成的任务
        # 移动到归档文件
        return []


class Scheduler:
    """定时任务调度器"""

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
        content = self.engine.tasks_file.read_text(encoding='utf-8')

        # 提取未完成任务
        tasks = re.findall(r'- \[ \] (.+)', content)

        briefing = f"""
---
🌅 晨间简报 | {datetime.now().strftime("%Y-%m-%d")}

📋 今日待办：
"""
        for task in tasks[:5]:  # 最多显示5个
            briefing += f"- [ ] {task}\n"

        briefing += f"""
📊 统计：共 {len(tasks)} 项待办

❓ 你想从哪个任务开始？
---
"""

        return briefing

    def _should_run_sunday_reminder(self, now):
        """检查是否应该运行周日提醒"""
        if now.weekday() != 6:  # 6 = Sunday
            return False

        last_reminder = self.engine.state.get("last_sunday_reminder")
        if not last_reminder:
            return True

        last_reminder_date = datetime.fromisoformat(last_reminder).date()
        return now.date() > last_reminder_date

    def _generate_sunday_reminder(self):
        """生成周日数据维护提醒"""
        # 更新状态
        self.engine.state["last_sunday_reminder"] = datetime.now().isoformat()
        self.engine.save_state()

        return """
---
📊 周日数据维护提醒

本周需要完成：
1. 录入本周发布内容的数据（阅读量、互动量等）
2. 分析哪些内容表现好，为什么
3. 更新爆款递归库状态

是否现在开始？
---
"""


# 主入口
if __name__ == "__main__":
    # 创建引擎实例
    roland = RolandEngine()

    # 示例：处理用户输入
    test_input = "这篇文章明天要发布"
    result = roland.process_user_input(test_input)

    print("✓ AI Roland 自动化引擎已启动")
    print(f"执行的操作: {result['actions_taken']}")
    print(f"消息: {result['messages']}")
