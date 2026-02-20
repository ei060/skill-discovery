"""
AI Roland - Claude 集成版（轻量）
按需激活，不影响 Windows 主机
"""

import os
import json
from datetime import datetime
from pathlib import Path

class LazyRoland:
    """懒加载版 AI Roland - 只在需要时工作"""

    def __init__(self):
        self.system_dir = Path(__file__).parent
        self.workspace = self.system_dir.parent
        self._engine = None  # 延迟加载

    @property
    def engine(self):
        """延迟加载引擎"""
        if self._engine is None:
            from engine import RolandEngine
            self._engine = RolandEngine()
        return self._engine

    def process(self, user_input):
        """处理输入 - 只在调用时才工作"""
        response = self.engine.process_user_input(user_input)
        self.engine.save_state()  # 立即保存
        return response

    def get_status(self):
        """获取状态"""
        state_file = self.workspace / "system_state.json"
        if state_file.exists():
            with open(state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def get_tasks(self):
        """获取任务清单"""
        tasks_file = self.workspace / "任务清单.md"
        if tasks_file.exists():
            return tasks_file.read_text(encoding='utf-8')
        return ""

    def add_task(self, task, category="important"):
        """快速添加任务"""
        import re

        category_map = {
            "urgent": "【紧急重要】",
            "important": "【重要不紧急】",
            "daily": "【日常事项】"
        }

        tasks_file = self.workspace / "任务清单.md"
        if not tasks_file.exists():
            return {"error": "任务文件不存在"}

        content = tasks_file.read_text(encoding='utf-8')
        category_header = category_map.get(category, category_map["important"])

        # 找到分类位置
        pos = content.find(category_header)
        if pos == -1:
            return {"error": "分类不存在"}

        # 插入任务
        insert_pos = content.find("\n", pos) + 1
        new_task = f"- [ ] {task}\n"

        new_content = content[:insert_pos] + new_task + content[insert_pos:]

        with open(tasks_file, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return {"success": True, "task": task}

    def create_memory(self, event, description):
        """创建记忆"""
        return self.engine.memory_manager.create_episodic_memory(event, description)

    def generate_briefing(self):
        """生成简报"""
        from engine import Scheduler
        scheduler = Scheduler(self.engine)
        return scheduler._generate_daily_briefing()

    def cleanup(self):
        """清理（会话结束时）"""
        if self._engine is not None:
            self.engine.save_state()
            self._engine = None


# 全局单例
_roland = None

def get_roland():
    """获取 AI Roland 实例"""
    global _roland
    if _roland is None:
        _roland = LazyRoland()
    return _roland


# 便捷函数
def process_input(text):
    """处理输入"""
    return get_roland().process(text)

def get_status():
    """获取状态"""
    return get_roland().get_status()

def get_tasks():
    """获取任务"""
    return get_roland().get_tasks()

def add_task(task, category="important"):
    """添加任务"""
    return get_roland().add_task(task, category)

def create_memory(event, description):
    """创建记忆"""
    return get_roland().create_memory(event, description)

def generate_briefing():
    """生成简报"""
    return get_roland().generate_briefing()

def cleanup():
    """清理"""
    global _roland
    if _roland is not None:
        _roland.cleanup()
        _roland = None


# 导出接口
__all__ = [
    'process_input',
    'get_status',
    'get_tasks',
    'add_task',
    'create_memory',
    'generate_briefing',
    'cleanup'
]
