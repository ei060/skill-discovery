#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI Roland 自动化记忆管理系统

在会话开始/结束时自动更新记忆文件：
- USER_MEMORY.md - 用户记忆档案
- 对话历史.md - 会话记录
- 任务清单.md - 任务统计
- 记忆库/ - 分类记忆存储
"""

import sys
import os
import re
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import hashlib

# 修复 Windows 编码
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

# 添加系统路径
system_path = Path(__file__).parent
sys.path.insert(0, str(system_path))

from homunculus_memory import HomunculusMemory
try:
    from agent_memory import get_agent_memory_manager
except ImportError:
    from agents.agent_memory import get_agent_memory_manager


class AutoMemoryManager:
    """自动化记忆管理器"""

    def __init__(self, workspace: Optional[Path] = None):
        if workspace is None:
            workspace = Path(__file__).parent.parent

        self.workspace = Path(workspace)

        # 文件路径
        self.user_memory_file = self.workspace / "USER_MEMORY.md"
        self.chat_history_file = self.workspace / "对话历史.md"
        self.tasks_file = self.workspace / "任务清单.md"

        # 记忆目录
        self.memory_dirs = {
            "episodic": self.workspace / "记忆库/情景记忆",
            "semantic": self.workspace / "记忆库/语义记忆",
            "professional": self.workspace / "记忆库/专业知识",
            "rules": self.workspace / "记忆库/强制规则"
        }

        # 确保目录存在
        for dir_path in self.memory_dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)

        # 记忆系统
        self.homunculus = HomunculusMemory(self.workspace)
        self.agent_memory = get_agent_memory_manager()

        # 状态跟踪
        self.last_update_hash = self._get_last_hash()

    def _get_last_hash(self) -> Dict[str, str]:
        """获取文件哈希，用于检测变化"""
        hashes = {}
        for file_path in [self.chat_history_file, self.tasks_file]:
            if file_path.exists():
                content = file_path.read_text(encoding='utf-8')
                hashes[str(file_path)] = hashlib.md5(content.encode()).hexdigest()
        return hashes

    def _file_changed(self, file_path: Path) -> bool:
        """检查文件是否变化"""
        if not file_path.exists():
            return False

        current_hash = self._get_last_hash()
        file_str = str(file_path)

        if file_str not in current_hash:
            return True

        new_content = file_path.read_text(encoding='utf-8')
        new_hash = hashlib.md5(new_content.encode()).hexdigest()

        return new_hash != current_hash.get(file_str, "")

    def on_session_start(self, session_id: str = None) -> Dict:
        """会话开始时调用"""
        if session_id is None:
            session_id = datetime.now().strftime("%Y-%m-%d %H:%M")

        result = {
            "session_id": session_id,
            "actions": []
        }

        # 1. 追加会话开始记录到对话历史
        self._append_session_start(session_id)
        result["actions"].append("appended_session_start")

        # 2. 创建每日日志
        self._ensure_daily_log(session_id)
        result["actions"].append("created_daily_log")

        # 3. 清理工作记忆（会话恢复）
        self.agent_memory.clear_all_working_memory()
        result["actions"].append("cleared_working_memory")

        return result

    def on_session_end(self, session_id: str, summary: str = "",
                       tasks_completed: List[str] = None) -> Dict:
        """会话结束时调用"""
        result = {
            "session_id": session_id,
            "actions": []
        }

        # 1. 更新对话历史中的会话记录
        self._update_session_record(session_id, summary, tasks_completed or [])
        result["actions"].append("updated_session_record")

        # 2. 分析会话内容，提取关键信息
        key_points = self._extract_key_points(session_id)
        if key_points:
            result["key_points"] = key_points

        # 3. 如果有重要任务完成，创建语义记忆
        if tasks_completed:
            for task in tasks_completed:
                self._create_semantic_memory(task, session_id)
            result["actions"].append(f"created_{len(tasks_completed)}_semantic_memories")

        # 4. 检查是否需要更新用户记忆
        if self._should_update_user_memory():
            self._update_user_memory_auto()
            result["actions"].append("updated_user_memory")

        # 5. 同步代理记忆到全局
        self.agent_memory.sync_to_global()
        result["actions"].append("synced_agent_memory")

        # 6. 更新哈希
        self.last_update_hash = self._get_last_hash()

        return result

    def _append_session_start(self, session_id: str):
        """追加会话开始记录"""
        content = ""
        if self.chat_history_file.exists():
            content = self.chat_history_file.read_text(encoding='utf-8')

        new_session = f"""
---
### 会话：{session_id}
**用户**：会话开始
**AI Roland**：系统已启动，等待用户输入...
**任务**：待记录
**产出**：待更新
---
"""

        with open(self.chat_history_file, 'a', encoding='utf-8') as f:
            f.write(new_session)

    def _update_session_record(self, session_id: str, summary: str,
                               tasks_completed: List[str]):
        """更新会话记录"""
        if not self.chat_history_file.exists():
            return

        content = self.chat_history_file.read_text(encoding='utf-8')

        # 找到对应会话的记录
        pattern = rf"(---\n### 会话：{re.escape(session_id)}.*?---)"
        match = re.search(pattern, content, re.DOTALL)

        if match:
            old_block = match.group(1)

            # 更新任务和产出
            task_str = "、".join(tasks_completed) if tasks_completed else "见日志"
            output_str = summary[:100] if summary else "见日志"

            new_block = old_block.replace("**任务**：待记录", f"**任务**：{task_str}")
            new_block = new_block.replace("**任务**：待更新", f"**任务**：{task_str}")
            new_block = new_block.replace("**产出**：待更新", f"**产出**：{output_str}")
            new_block = new_block.replace("**产出**：待记录", f"**产出**：{output_str}")

            content = content.replace(old_block, new_block)

            with open(self.chat_history_file, 'w', encoding='utf-8') as f:
                f.write(content)

    def _ensure_daily_log(self, session_id: str):
        """确保每日日志存在"""
        try:
            now = datetime.strptime(session_id, "%Y-%m-%d %H:%M")
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M")

            log_dir = self.workspace / "日志"
            log_dir.mkdir(exist_ok=True)
            log_file = log_dir / f"{date_str}.md"

            if not log_file.exists():
                # 创建新日志
                template = f"""# {date_str} 每日记录

## 🌅 晨间简报
- 待补充

## 💬 会话记录

### 会话 {time_str}
会话开始，等待用户输入...

## 📝 今日记录
- 待补充

## 📊 统计
- 会话次数: 1
- 完成任务: 待统计

## 💡 想法捕获
- 待补充
"""
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.write(template)
            else:
                # 追加新会话记录
                content = log_file.read_text(encoding='utf-8')
                new_entry = f"\n### 会话 {time_str}\n会话开始，等待用户输入...\n"

                # 在 "今日记录" 之前插入
                if "## 📝 今日记录" in content:
                    content = content.replace(
                        "## 📝 今日记录",
                        new_entry + "\n---\n\n## 📝 今日记录"
                    )
                    with open(log_file, 'w', encoding='utf-8') as f:
                        f.write(content)
        except Exception as e:
            print(f"[WARN] 创建每日日志失败: {e}")

    def _extract_key_points(self, session_id: str) -> List[str]:
        """从会话中提取关键点"""
        # 这里可以使用 AI 来分析对话内容
        # 简化版本：基于关键词提取
        return []

    def _create_semantic_memory(self, task: str, session_id: str):
        """创建语义记忆"""
        # 生成文件名
        date_str = datetime.now().strftime("%Y-%m-%d")
        safe_title = re.sub(r'[^\w\s-]', '', task)[:30]
        filename = f"{date_str}_{safe_title}.md"

        content = f"""# {task}

**时间**: {session_id}
**类型**: 任务完成

## 描述
{task}

## 关键点
- 待补充

## 经验总结
- 待补充

## 相关文件
- 对话历史.md
"""

        output_file = self.memory_dirs["semantic"] / filename
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

    def _should_update_user_memory(self) -> bool:
        """检查是否需要更新用户记忆"""
        # 简化版本：每次会话结束都检查
        return True

    def _update_user_memory_auto(self):
        """自动更新用户记忆"""
        if not self.user_memory_file.exists():
            return

        # 读取当前用户记忆
        content = self.user_memory_file.read_text(encoding='utf-8')

        # 更新"最后活跃"字段
        now = datetime.now().isoformat()

        if "## 系统使用特征" in content:
            # 更新最后会话时间
            pattern = r"(\*\*最后会话\*\*：.*?\n)"
            replacement = f"**最后会话**：{now}\n"

            if "**最后会话**：" in content:
                content = re.sub(pattern, replacement, content)
            else:
                # 添加最后会话时间
                section = re.search(r"## 系统使用特征\n(.*?)(?=\n##|\n*$)", content, re.DOTALL)
                if section:
                    section_content = section.group(1)
                    updated_section = section_content + f"\n**最后会话**：{now}\n"
                    content = content.replace(section_content, updated_section)

            with open(self.user_memory_file, 'w', encoding='utf-8') as f:
                f.write(content)

    def get_memory_status(self) -> Dict:
        """获取记忆系统状态"""
        status = {
            "user_memory_exists": self.user_memory_file.exists(),
            "chat_history_exists": self.chat_history_file.exists(),
            "tasks_file_exists": self.tasks_file.exists(),
            "memory_dirs": {},
            "conversation_count": 0,
            "semantic_memories": 0,
            "last_update": datetime.now(timezone.utc).isoformat()
        }

        # 统计记忆目录
        for name, dir_path in self.memory_dirs.items():
            if dir_path.exists():
                md_files = list(dir_path.glob("*.md"))
                status["memory_dirs"][name] = len(md_files)
                if name == "semantic":
                    status["semantic_memories"] = len(md_files)

        # 统计会话数量
        if self.chat_history_file.exists():
            content = self.chat_history_file.read_text(encoding='utf-8')
            sessions = re.findall(r'### 会话：', content)
            status["conversation_count"] = len(sessions)

        return status


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(description="AI Roland 自动化记忆管理")
    parser.add_argument("action", choices=["start", "end", "status", "update"],
                       help="操作类型")
    parser.add_argument("--session", help="会话ID")
    parser.add_argument("--summary", help="会话摘要")
    parser.add_argument("--tasks", help="完成的任务列表（逗号分隔）")

    args = parser.parse_args()

    manager = AutoMemoryManager()

    if args.action == "start":
        result = manager.on_session_start(args.session)
        print(f"会话开始: {result['session_id']}")
        print(f"操作: {', '.join(result['actions'])}")

    elif args.action == "end":
        tasks = args.tasks.split(",") if args.tasks else []
        result = manager.on_session_end(args.session, args.summary or "", tasks)
        print(f"会话结束: {result['session_id']}")
        print(f"操作: {', '.join(result['actions'])}")

    elif args.action == "status":
        status = manager.get_memory_status()
        print("=== 记忆系统状态 ===")
        print(f"用户记忆: {'✓' if status['user_memory_exists'] else '✗'}")
        print(f"对话历史: {'✓' if status['chat_history_exists'] else '✗'}")
        print(f"任务清单: {'✓' if status['tasks_file_exists'] else '✗'}")
        print(f"会话数量: {status['conversation_count']}")
        print(f"语义记忆: {status['semantic_memories']} 条")
        print(f"记忆目录:")
        for name, count in status['memory_dirs'].items():
            print(f"  - {name}: {count} 条")

    elif args.action == "update":
        manager._update_user_memory_auto()
        print("用户记忆已更新")


if __name__ == "__main__":
    main()
