"""
AI Roland 任务状态管理器
用于跨会话保存和恢复任务状态
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class TaskStateManager:
    """任务状态管理器"""

    def __init__(self, workspace: Path = None):
        if workspace is None:
            workspace = Path(__file__).parent.parent
        self.workspace = workspace
        self.state_file = workspace / "current_task.json"

    def load_state(self) -> Dict:
        """加载当前任务状态"""
        if not self.state_file.exists():
            return {
                "session_id": "",
                "last_updated": "",
                "active_tasks": [],
                "completed_tasks": [],
                "context_notes": [],
                "next_session_focus": "等待指示"
            }
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return self._get_empty_state()

    def _get_empty_state(self) -> Dict:
        """返回空状态"""
        return {
            "session_id": "",
            "last_updated": "",
            "active_tasks": [],
            "completed_tasks": [],
            "context_notes": [],
            "next_session_focus": "等待指示"
        }

    def save_state(self, state: Dict) -> bool:
        """保存任务状态"""
        try:
            state["last_updated"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"[ERR] 保存状态失败: {e}")
            return False

    def add_active_task(self, task: str) -> bool:
        """添加进行中的任务"""
        state = self.load_state()
        if task not in state["active_tasks"]:
            state["active_tasks"].append(task)
        return self.save_state(state)

    def complete_task(self, task: str) -> bool:
        """完成任务"""
        state = self.load_state()
        if task in state["active_tasks"]:
            state["active_tasks"].remove(task)
        if task not in state["completed_tasks"]:
            state["completed_tasks"].append(task)
        return self.save_state(state)

    def set_focus(self, focus: str) -> bool:
        """设置下次会话的重点"""
        state = self.load_state()
        state["next_session_focus"] = focus
        return self.save_state(state)

    def add_context_note(self, note: str) -> bool:
        """添加上下文笔记（重要信息）"""
        state = self.load_state()
        if note not in state["context_notes"]:
            state["context_notes"].append(note)
            # 只保留最近 10 条
            if len(state["context_notes"]) > 10:
                state["context_notes"] = state["context_notes"][-10:]
        return self.save_state(state)

    def clear_active_tasks(self) -> bool:
        """清空所有进行中的任务"""
        state = self.load_state()
        state["active_tasks"] = []
        return self.save_state(state)

    def get_briefing(self) -> str:
        """获取状态摘要（用于启动时显示）"""
        state = self.load_state()
        lines = []

        if state["active_tasks"]:
            lines.append(f"  进行中: {', '.join(state['active_tasks'][:2])}")

        focus = state.get("next_session_focus", "")
        if focus and focus != "等待指示":
            lines.append(f"  继续: {focus[:40]}")

        if state["context_notes"]:
            # 显示最重要的笔记
            important = [n for n in state["context_notes"] if "API" in n or "Key" in n or "配置" in n]
            if important:
                lines.append(f"  重要: {important[0][:35]}")

        return "\n".join(lines) if lines else "  状态: 空闲"


    def save_todos(self, todos: list) -> bool:
        """保存 TodoWrite 任务列表到状态文件"""
        try:
            state = self.load_state()
            state["todos"] = todos
            state["last_todo_update"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            return self.save_state(state)
        except Exception as e:
            print(f"[ERR] 保存 TodoWrite 状态失败: {e}")
            return False

    def load_todos(self) -> list:
        """从状态文件加载 TodoWrite 任务列表"""
        try:
            state = self.load_state()
            return state.get("todos", [])
        except Exception as e:
            print(f"[WARN] 加载 TodoWrite 状态失败: {e}")
            return []


# 单例实例
_task_manager: Optional[TaskStateManager] = None


def get_task_manager() -> TaskStateManager:
    """获取任务状态管理器单例"""
    global _task_manager
    if _task_manager is None:
        _task_manager = TaskStateManager()
    return _task_manager


if __name__ == "__main__":
    # 测试
    manager = get_task_manager()
    manager.add_active_task("测试任务")
    manager.set_focus("继续开发 Skill 安全检查")
    manager.add_context_note("YouTube API Key 已配置")
    print(manager.get_briefing())
