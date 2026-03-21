#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ECC Agent增强工具

为ECC agent添加记忆读取能力，修改.md文件以支持记忆注入
"""

import os
import sys
import re
from pathlib import Path
import shutil
from datetime import datetime, timezone

def inject_memory_to_agent_file(agent_file: Path, memory_file: Path) -> bool:
    """将记忆内容注入到agent文件中"""

    if not agent_file.exists() or not memory_file.exists():
        return False

    try:
        # 读取原始agent文件
        content = agent_file.read_text(encoding='utf-8')

        # 读取记忆内容
        memory_content = memory_file.read_text(encoding='utf-8')

        # 在YAML frontmatter后注入记忆
        # 查找frontmatter结束位置
        frontmatter_end = content.find('\n---\n', 4)
        if frontmatter_end == -1:
            frontmatter_end = content.find('\n---', 4)

        if frontmatter_end == -1:
            return False

        # 构建增强内容
        inject_marker = "\n\n## 🧠 Memory Context (Auto-loaded)\n"
        enhanced_content = (
            content[:frontmatter_end + 4] +  # 包含---
            inject_marker +
            memory_content +
            "\n\n## Original Instructions\n" +
            content[frontmatter_end + 4:]
        )

        # 备份原文件
        backup_file = agent_file.with_suffix('.md.backup')
        shutil.copy2(agent_file, backup_file)

        # 写入增强内容
        agent_file.write_text(enhanced_content, encoding='utf-8')

        return True

    except Exception as e:
        print(f"[ERROR] Failed to inject memory: {e}", file=sys.stderr)
        return False

def restore_agent_file(agent_file: Path) -> bool:
    """恢复agent文件到原始状态"""

    backup_file = agent_file.with_suffix('.md.backup')

    if not backup_file.exists():
        return False

    try:
        shutil.copy2(backup_file, agent_file)
        backup_file.unlink()
        return True
    except Exception as e:
        print(f"[ERROR] Failed to restore: {e}", file=sys.stderr)
        return False

def main():
    """主函数"""

    # 从环境变量获取文件路径
    agent_file = os.environ.get('CLAUDE_AGENT_FILE')
    memory_file = os.environ.get('CLAUDE_AGENT_MEMORY_FILE')

    if not agent_file or not memory_file:
        print("[INFO] No agent or memory file specified", file=sys.stderr)
        sys.exit(0)

    agent_path = Path(agent_file)
    memory_path = Path(memory_file)

    # 注入记忆
    if inject_memory_to_agent_file(agent_path, memory_path):
        print(f"[SUCCESS] Memory injected to {agent_path.name}", file=sys.stderr)
        sys.exit(0)
    else:
        print(f"[FAILED] Could not inject memory", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
