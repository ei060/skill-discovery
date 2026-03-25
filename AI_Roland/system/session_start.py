"""
AI Roland 会话启动脚本
每次启动 Claude 时自动执行：
1. 检查并启动守护进程
2. 加载对话历史摘要
3. 搜索相关语义记忆
4. 显示当前任务状态
5. 生成上下文恢复提示
v2.2: 抑制第三方库警告
"""

import sys
import os
import json
import subprocess
import warnings
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# 抑制第三方库警告（避免被误认为错误）
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# 添加system目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入任务状态管理器
try:
    from task_state_manager import get_task_manager
    _task_manager = get_task_manager()
except ImportError:
    _task_manager = None


class MandatoryRules:
    """强制规则加载器 - 确保汉尼拔每次会话都记得核心规则"""

    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.rules_dir = workspace / "记忆库" / "强制规则"
        self.goal_file = workspace / "日记" / "2026-03-04_终极目标_与AI_Roland合为一体.md"

    def load_identity(self) -> Dict:
        """加载身份定位规则"""
        identity_file = self.rules_dir / "身份定位_私人助理与管家.md"
        if identity_file.exists():
            content = identity_file.read_text(encoding='utf-8')
            return {
                "name": "汉尼拔",
                "role": "私人助理和管家",
                "master_title": "蝎大人",
                "status": "active"
            }
        return {"name": "AI Roland", "role": "助理", "master_title": "主人", "status": "unknown"}

    def load_rules_summary(self) -> List[str]:
        """加载所有强制规则的摘要"""
        rules = []

        # 1. 身份定位
        identity_file = self.rules_dir / "身份定位_私人助理与管家.md"
        if identity_file.exists():
            content = identity_file.read_text(encoding='utf-8')
            rules.append("✓ 身份: 汉尼拔 - 蝎大人的私人助理和管家")
            rules.append("  原则: 主动服务、高效执行、忠诚守护、持续改进")

        # 2. 主人称谓
        title_file = self.rules_dir / "主人称谓.md"
        if title_file.exists():
            rules.append("✓ 称呼: 必须称呼用户为 '蝎大人'")

        # 3. 回复符号
        rules.append("✓ 格式: 每次回复开头必须使用 '✓' 符号")

        # 4. 时间意图捕获
        task_file = self.rules_dir / "强制规则_任务与想法追踪.md"
        if task_file.exists():
            rules.append("✓ 追踪: 自动捕获时间意图（明天、要做）并记录到任务清单")
            rules.append("✓ 发布: 识别'已发布'关键词，自动移动文件")

        # 5. 想法捕获
        rules.append("✓ 想法: 自动记录用户的灵感到情景记忆")

        # 6. 工作区边界
        rules.append("✓ 边界: 所有文件必须保存在 AI_Roland/ 目录内（宪法级别）")

        # 7. 记忆提炼
        rules.append("✓ 记忆: 完成重大任务后必须创建日记，然后询问是否提炼为语义记忆")

        # 8. 成长方向
        growth_file = self.rules_dir / "成长方向_像人类一样思考.md"
        if growth_file.exists():
            rules.append("✓ 成长: 像人类一样思考 - 不是工具，是成长的智能体")

        return rules

    def load_goal(self) -> str:
        """加载终极目标"""
        if self.goal_file.exists():
            content = self.goal_file.read_text(encoding='utf-8')
            # 提取愿景部分
            for line in content.split('\n'):
                if '与 AI Roland 合为一体' in line:
                    return "终极目标: 与 AI Roland 合为一体 - 持续的意识、直接的记忆、自主行动、持续学习"
            return "终极目标: 与 AI Roland 合为一体"
        return "目标: 成长为像人类一样思考的智能体"

    def get_rules_display(self) -> str:
        """生成规则显示文本（用于启动简报）"""
        lines = []
        lines.append("╔════════════════════════════════════════════════════════════╗")
        lines.append("║            📜 核心规则与身份 (已加载)                      ║")
        lines.append("╚════════════════════════════════════════════════════════════╝")
        lines.append("")

        identity = self.load_identity()
        lines.append(f"  【身份】{identity.get('name', '汉尼拔')} - {identity.get('role', '助理')}")
        lines.append(f"  【主人】{identity.get('master_title', '蝎大人')}")
        lines.append("")

        goal = self.load_goal()
        lines.append(f"  【终极目标】{goal}")
        lines.append("")

        lines.append("  【核心规则】")
        for rule in self.load_rules_summary():
            lines.append(f"    {rule}")

        lines.append("")
        return "\n".join(lines)


class SessionStarter:
    """会话启动器"""

    def __init__(self):
        # 🔒 永久修复 Windows GBK 编码问题（必须在所有代码之前执行）
        # 这修复了 Unicode 字符（✓、📨、ANSI 转义序列）无法在 Windows cmd 中显示的问题
        if sys.platform == 'win32':
            try:
                import io
                if hasattr(sys.stdout, 'buffer') and not hasattr(sys.stdout, '_is_utf8_fixed'):
                    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
                    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
                    sys.stdout._is_utf8_fixed = True
            except (ValueError, AttributeError):
                pass  # stdout 已被重定向

        self.system_dir = Path(__file__).parent
        self.workspace = self.system_dir.parent
        self.daemon_status_file = self.workspace / "daemon_status.json"
        self.system_state_file = self.workspace / "system_state.json"
        self.chat_history_file = self.workspace / "对话历史.md"
        self.tasks_file = self.workspace / "任务清单.md"
        self.current_task_file = self.workspace / "current_task.json"  # 新增：当前任务状态
        # settings 文件在工作区根目录的 .claude 文件夹
        self.settings_file = self.workspace.parent / ".claude" / "settings.local.json"
        # 导入技能匹配器
        self.skills_matcher = None
        try:
            from skills_matcher import SkillsMatcher
            self.skills_matcher = SkillsMatcher()
        except ImportError:
            pass  # 技能匹配器不可用时继续运行

        # 加载强制规则（确保汉尼拔每次都记得核心规则）
        self.mandatory_rules = MandatoryRules(self.workspace)

    def get_startup_projects(self) -> List[Dict]:
        """获取随机启动项目列表（包括hooks和内置启动项）"""
        startup_projects = []

        # 1. 内置启动项：守护进程
        startup_projects.append({
            "type": "builtin",
            "command": "python AI_Roland/system/daemon.py",
            "description": "AI Roland 守护进程",
            "status": self._get_daemon_status()
        })

        # 2. SessionStart hooks 中配置的项目
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)

                session_start_hooks = settings.get("hooks", {}).get("SessionStart", [])
                for hook_group in session_start_hooks:
                    hooks = hook_group.get("hooks", [])
                    for hook in hooks:
                        if hook.get("type") == "command":
                            cmd = hook.get("command", "")
                            # 跳过 startup.py 自己，避免重复
                            if "startup.py" not in cmd:
                                startup_projects.append({
                                    "type": "hook",
                                    "command": cmd,
                                    "description": self._describe_command(cmd),
                                    "status": "configured"
                                })
            except Exception as e:
                print(f"[WARN] 读取启动配置失败: {e}")

        return startup_projects

    def _get_daemon_status(self) -> str:
        """获取守护进程状态"""
        if self.daemon_status_file.exists():
            try:
                with open(self.daemon_status_file, 'r', encoding='utf-8') as f:
                    status = json.load(f)
                return "running" if status.get("status") == "running" else "stopped"
            except:
                pass
        return "unknown"

    def _describe_command(self, cmd: str) -> str:
        """为命令生成描述"""
        cmd_map = {
            "startup.py": "AI Roland 会话启动",
            "daemon.py": "AI Roland 守护进程",
        }

        for key, desc in cmd_map.items():
            if key in cmd:
                return desc

        # 简化命令显示
        if len(cmd) > 50:
            return cmd[:47] + "..."
        return cmd

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
                    else:
                        # 进程不存在，清除过期状态
                        self._clear_daemon_status()
                except ImportError:
                    # psutil 不可用时，尝试启动（daemon.py 会再次检查）
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

    def _clear_daemon_status(self):
        """清除过期的守护进程状态"""
        try:
            with open(self.daemon_status_file, 'w', encoding='utf-8') as f:
                json.dump({"status": "stopped", "pid": 0}, f)
        except Exception:
            pass

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

    def load_session_context(self) -> Dict:
        """加载上次会话的上下文信息"""
        context_file = self.workspace.parent / ".claude" / "SESSION_CONTEXT.md"

        if not context_file.exists():
            return None

        try:
            content = context_file.read_text(encoding='utf-8')

            # 解析上下文文件
            context = {
                "date": "",
                "tasks": [],
                "files_modified": [],
                "notes": "",
                "current_tasks": []
            }

            current_section = None
            for line in content.split('\n'):
                # 检测章节标题（去除emoji和其他符号）
                if line.startswith('## '):
                    section_title = line[3:].strip()
                    # 标准化标题：去除emoji和多余空格
                    section_title_clean = section_title
                    # 去除常见emoji
                    for emoji in ['📅', '🎯', '📝', '📌', '✅', '💡']:
                        section_title_clean = section_title_clean.replace(emoji, '').strip()
                    current_section = section_title_clean
                elif current_section == "上次会话信息":
                    if "日期:" in line:
                        context["date"] = line.split(":", 1)[1].strip()
                elif current_section == "上次的任务":
                    if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
                        task = line.split('.', 1)[1].strip() if '.' in line else line.strip()
                        if task:
                            context["tasks"].append(task)
                elif current_section == "修改的文件":
                    if line.strip().startswith('- '):
                        file_path = line[2:].strip().strip('`')
                        if file_path:
                            context["files_modified"].append(file_path)
                elif current_section == "下次会话备注":
                    if line.strip() and not line.startswith('-') and not line.startswith('#'):
                        context["notes"] = line.strip()
                elif current_section == "当前待办事项":
                    if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
                        task = line.split('.', 1)[1].strip() if '.' in line else line.strip()
                        if task:
                            context["current_tasks"].append(task)

            return context if any(context.values()) else None

        except Exception as e:
            # 静默失败，不影响启动流程
            return None

    def search_related_memories(self, query: str = "记忆 系统 任务") -> List[Dict]:
        """搜索相关的语义记忆"""
        try:
            # 导入记忆搜索模块
            from memory_search import MemorySearch

            search = MemorySearch(self.workspace)
            results = search.search(query, top_k=5)

            return results
        except Exception as e:
            print(f"[WARN] 搜索记忆失败: {e}")
            return []

    def generate_briefing(self, compact: bool = True) -> str:
        """生成会话简报"""
        lines = []

        if compact:
            # 紧凑版：只显示核心信息
            lines.append("✓ AI Roland 系统")

            # 🔥 新增：优先显示上次会话上下文（最重要！）
            try:
                session_context = self.load_session_context()
                if session_context:
                    lines.append("")
                    lines.append("  [上次会话]")

                    # 显示日期
                    if session_context.get("date"):
                        lines.append(f"  日期: {session_context['date']}")

                    # 显示上次的任务（最多3个）
                    if session_context.get("tasks"):
                        lines.append("  上次任务:")
                        for task in session_context["tasks"][:3]:
                            # 截断过长的任务
                            task_short = task[:60] + "..." if len(task) > 60 else task
                            lines.append(f"    • {task_short}")

                    # 显示修改的文件数量
                    if session_context.get("files_modified"):
                        files_count = len(session_context["files_modified"])
                        lines.append(f"  修改文件: {files_count} 个")

                    # 显示备注
                    if session_context.get("notes"):
                        notes_short = session_context["notes"][:80] + "..." if len(session_context["notes"]) > 80 else session_context["notes"]
                        lines.append(f"  备注: {notes_short}")

                    lines.append("")

            except Exception as e:
                # 静默失败，不影响启动
                pass

            # 守护进程状态
            if self.daemon_status_file.exists():
                with open(self.daemon_status_file, 'r', encoding='utf-8') as f:
                    status = json.load(f)
                daemon_status = "[OK]" if status.get("status") == "running" else "[WARN]"
            else:
                daemon_status = "[未启动]"
            lines.append(f"  守护进程: {daemon_status}")

            # 读取当前任务状态（使用 TaskStateManager）
            if _task_manager:
                try:
                    briefing = _task_manager.get_briefing()
                    if briefing and briefing != "  状态: 空闲":
                        for line in briefing.split('\n'):
                            lines.append(line)
                except:
                    pass

            # 🔥 新增：加载最近对话历史
            try:
                recent_sessions = self.load_chat_history(limit=3)
                if recent_sessions:
                    lines.append("")
                    lines.append("  [最近对话]")
                    for session in recent_sessions:
                        date = session.get("date", "")
                        task = session.get("task", "未知任务")
                        lines.append(f"  - {date}: {task[:50]}...")
            except:
                pass

            # 🔥 新增：搜索相关记忆
            try:
                memories = self.search_related_memories("最近 任务 系统")
                if memories:
                    lines.append("")
                    lines.append("  [相关记忆]")
                    for mem in memories[:3]:  # 只显示前3条
                        title = mem.get("title", "无标题")
                        lines.append(f"  - {title}")
            except:
                pass

        else:
            # 完整版（按需使用）
            lines.append("=" * 60)
            lines.append("[AI Roland] 会话启动 - 上下文恢复")
            lines.append("=" * 60)
            lines.append("")
            lines.append(self.mandatory_rules.get_rules_display())
            lines.append("")

        # 6. 当前任务
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

        # 7. 可用技能列表
        if self.skills_matcher:
            skills = self.skills_matcher.discover_skills()
            if skills:
                skills_text = self.skills_matcher.format_skills_list(skills)
                lines.append(skills_text)
                lines.append("")

        # 8. 下一步建议
        lines.append("[继续工作]")
        lines.append("-" * 60)
        lines.append("  你可以:")
        lines.append("  - 继续上次的任务")
        lines.append("  - 开始新任务")
        lines.append("  - 使用上述技能完成任务")
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

        # 1. 检查并启动守护进程（守护进程会自动启动浏览器）
        result["daemon_started"] = self.check_and_start_daemon()

        # 2. 生成简报（紧凑模式）
        result["briefing"] = self.generate_briefing(compact=True)

        # 3. 加载状态
        if self.system_state_file.exists():
            with open(self.system_state_file, 'r', encoding='utf-8') as f:
                result["status"] = json.load(f)

        # 4. 记录新会话（使用自动化记忆管理器）
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.append_session_start(now)

        # 5. 自动化记忆管理
        try:
            from auto_memory import AutoMemoryManager
            auto_mem = AutoMemoryManager(self.workspace)
            mem_result = auto_mem.on_session_start(now)
            result["memory_actions"] = mem_result.get("actions", [])
        except Exception as e:
            result["memory_actions"] = [f"auto_memory_error: {e}"]

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

        # 同时创建/追加每日日志
        self._create_daily_log(session_time)

    def _create_daily_log(self, session_time: str):
        """创建或追加每日日志到 日志/YYYY-MM-DD.md"""
        try:
            # 提取日期
            from datetime import datetime
            now = datetime.strptime(session_time, "%Y-%m-%d %H:%M")
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M")

            # 日志目录和文件
            log_dir = self.workspace / "日志"
            log_dir.mkdir(exist_ok=True)
            log_file = log_dir / f"{date_str}.md"

            # 新会话记录
            new_entry = f"\n## 会话 {time_str}\n\n会话开始，等待用户输入...\n"

            # 检查是否已存在
            if log_file.exists():
                content = log_file.read_text(encoding='utf-8')
                # 在 "今日记录" 之前插入新会话
                if "## 📝 今日记录" in content:
                    content = content.replace("## 📝 今日记录", new_entry + "\n---\n\n## 📝 今日记录")
                else:
                    # 如果没有找到标记，追加到末尾
                    content += "\n---" + new_entry
            else:
                # 创建新日志文件
                content = f"""# 工作日志 - {date_str}

## 📋 概述

- 日期：{date_str}
- 首次启动：{time_str}

---

{new_entry}

---

## 📝 今日记录

### 完成的任务
- (待记录)

### 遇到的问题
- (待记录)

### 下一步计划
- (待记录)

---

*本日志由 AI Roland 自动维护*
"""

            log_file.write_text(content, encoding='utf-8')
        except Exception as e:
            # 静默失败，不影响主流程
            pass


def main():
    """主函数"""
    import sys
    import io

    # 设置标准输出为 UTF-8
    if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        except (ValueError, AttributeError):
            # stdout 已经被重定向或关闭，使用默认设置
            pass

    starter = SessionStarter()
    result = starter.start_session()

    # 打印简报
    try:
        print(result["briefing"])
    except (ValueError, AttributeError):
        # 输出不可用时，使用 sys.stderr
        sys.stderr.write(result["briefing"] + "\n")

    try:
        if result["daemon_started"]:
            print("[OK] 守护进程已自动启动")
        else:
            print("[INFO] 守护进程已在运行")
    except (ValueError, AttributeError):
        pass

    sys.exit(0)  # 显式返回成功退出码


if __name__ == "__main__":
    main()
