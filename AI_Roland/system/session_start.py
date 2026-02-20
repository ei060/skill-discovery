"""
AI Roland 会话启动脚本
每次启动 Claude 时自动执行：
1. 检查并启动守护进程
2. 加载对话历史摘要
3. 显示当前任务状态
4. 生成今日简报
"""

import sys
import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# 添加system目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class SessionStarter:
    """会话启动器"""

    def __init__(self):
        self.system_dir = Path(__file__).parent
        self.workspace = self.system_dir.parent
        self.daemon_status_file = self.workspace / "daemon_status.json"
        self.system_state_file = self.workspace / "system_state.json"
        self.chat_history_file = self.workspace / "对话历史.md"
        self.tasks_file = self.workspace / "任务清单.md"

    def check_and_start_daemon(self) -> bool:
        """检查并启动守护进程"""
        if self.daemon_status_file.exists():
            with open(self.daemon_status_file, 'r', encoding='utf-8') as f:
                status = json.load(f)

            if status.get("status") == "running":
                pid = status.get("pid")
                # 检查进程是否还在运行
                try:
                    import psutil
                    if psutil.pid_exists(pid):
                        return False  # 已在运行，无需启动
                except ImportError:
                    pass

        # 启动守护进程
        try:
            daemon_script = self.system_dir / "daemon.py"
            subprocess.Popen(
                [sys.executable, str(daemon_script)],
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            return True
        except Exception as e:
            print(f"启动守护进程失败: {e}")
            return False

    def load_chat_history(self, limit: int = 5) -> List[Dict]:
        """加载最近的对话历史"""
        if not self.chat_history_file.exists():
            return []

        content = self.chat_history_file.read_text(encoding='utf-8')

        # 解析会话记录
        import re
        sessions = re.findall(
            r'### 会话：(.+?)\n\*\*用户\*\*：(.+?)\n\*\*AI Roland\*\*：(.+?)\n\*\*任务\*\*：(.+?)\n\*\*产出\*\*：(.*?)(?=---|\Z)',
            content,
            re.DOTALL
        )

        recent_sessions = []
        for session in sessions[-limit:]:
            recent_sessions.append({
                "date": session[0].strip(),
                "user": session[1].strip(),
                "ai": session[2].strip(),
                "task": session[3].strip(),
                "output": session[4].strip()
            })

        return recent_sessions

    def load_tasks(self) -> Dict:
        """加载当前任务"""
        if not self.tasks_file.exists():
            return {"total": 0, "urgent": [], "important": [], "daily": []}

        content = self.tasks_file.read_text(encoding='utf-8')

        import re
        urgent_tasks = re.findall(r'## 【紧急重要】.*?(?=##|\Z)', content, re.DOTALL)
        important_tasks = re.findall(r'## 【重要不紧急】.*?(?=##|\Z)', content, re.DOTALL)
        daily_tasks = re.findall(r'## 【日常事项】.*?(?=##|\Z)', content, re.DOTALL)

        def extract_tasks(section_text):
            if not section_text:
                return []
            return re.findall(r'- \[ \]\s*(.+)', section_text[0] if isinstance(section_text, list) else section_text)

        return {
            "total": len(re.findall(r'- \[ \]', content)),
            "urgent": extract_tasks(urgent_tasks),
            "important": extract_tasks(important_tasks),
            "daily": extract_tasks(daily_tasks)
        }

    def generate_briefing(self) -> str:
        """生成会话简报"""
        lines = []
        lines.append("=" * 60)
        lines.append("[AI Roland] 会话启动")
        lines.append("=" * 60)
        lines.append("")

        # 1. 守护进程状态
        lines.append("[系统状态]")
        lines.append("-" * 60)
        if self.daemon_status_file.exists():
            with open(self.daemon_status_file, 'r', encoding='utf-8') as f:
                status = json.load(f)
            daemon_status = "[OK] 运行中" if status.get("status") == "running" else "[WARN] 已停止"
            lines.append(f"  守护进程: {daemon_status}")
        else:
            lines.append("  守护进程: [WARN] 未启动")
        lines.append("")

        # 2. 最近对话历史
        history = self.load_chat_history(limit=3)
        if history:
            lines.append("[最近对话]")
            lines.append("-" * 60)
            for i, session in enumerate(history, 1):
                lines.append(f"  {i}. [{session['date']}]")
                lines.append(f"     用户: {session['user'][:50]}...")
                lines.append(f"     任务: {session['task'][:50]}...")
            lines.append("")

        # 3. 当前任务
        tasks = self.load_tasks()
        if tasks["total"] > 0:
            lines.append("[当前任务]")
            lines.append("-" * 60)
            lines.append(f"  总计: {tasks['total']} 个待办任务")
            lines.append("")

            if tasks["urgent"]:
                lines.append("  [紧急重要]")
                for task in tasks["urgent"][:3]:
                    lines.append(f"  - {task}")
                if len(tasks["urgent"]) > 3:
                    lines.append(f"  ... 还有 {len(tasks['urgent']) - 3} 个")
                lines.append("")

            if tasks["important"]:
                lines.append("  [重要不紧急]")
                for task in tasks["important"][:2]:
                    lines.append(f"  - {task}")
                lines.append("")
        else:
            lines.append("[当前任务]")
            lines.append("-" * 60)
            lines.append("  [OK] 没有待办任务")
            lines.append("")

        lines.append("=" * 60)
        lines.append("")

        return "\n".join(lines)

    def start_session(self) -> Dict:
        """启动会话"""
        result = {
            "daemon_started": False,
            "briefing": "",
            "status": {}
        }

        # 1. 检查并启动守护进程
        result["daemon_started"] = self.check_and_start_daemon()

        # 2. 生成简报
        result["briefing"] = self.generate_briefing()

        # 3. 加载状态
        if self.system_state_file.exists():
            with open(self.system_state_file, 'r', encoding='utf-8') as f:
                result["status"] = json.load(f)

        # 4. 记录新会话
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.append_session_start(now)

        return result

    def append_session_start(self, session_time: str):
        """在对话历史中追加新会话开始记录"""
        content = ""
        if self.chat_history_file.exists():
            content = self.chat_history_file.read_text(encoding='utf-8')

        new_session = f"""
---
### 会话：{session_time}
**用户**：会话开始
**AI Roland**：系统已启动，等待用户输入...
**任务**：待记录
**产出**：待更新
---
"""

        self.chat_history_file.write_text(content + new_session, encoding='utf-8')


def main():
    """主函数"""
    starter = SessionStarter()
    result = starter.start_session()

    # 打印简报
    print(result["briefing"])

    if result["daemon_started"]:
        print("[OK] 守护进程已自动启动")
    else:
        print("[INFO] 守护进程已在运行")

    return result


if __name__ == "__main__":
    main()
