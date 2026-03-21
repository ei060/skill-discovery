"""
AI Roland 会话结束脚本
每次退出时自动执行：
1. 检查任务状态
2. 检查记忆完整性
3. 提示是否需要记录重要信息
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# 修复 Windows 编码
if sys.platform == 'win32':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

# 添加system目录到路径
system_dir = Path(__file__).parent.parent / "AI_Roland" / "system"
sys.path.insert(0, str(system_dir))

def check_task_state():
    """检查任务状态"""
    state_file = Path(__file__).parent.parent / "AI_Roland" / "current_task.json"
    if not state_file.exists():
        return None

    try:
        with open(state_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

def check_memory_integrity():
    """检查记忆系统完整性"""
    memory_dir = Path(__file__).parent.parent / "AI_Roland" / "记忆库"
    checks = {
        "强制规则目录": (memory_dir / "强制规则").exists(),
        "技能库目录": (memory_dir / "技能库").exists(),
        "日记目录": (memory_dir.parent / "日记").exists(),
    }
    return checks

def main():
    state = check_task_state()
    if not state:
        print("✓ 会话结束 - 无任务状态")
        return

    print("\n" + "="*50)
    print("  AI Roland 会话结束检查")
    print("="*50)

    # 显示活跃任务
    if state.get("active_tasks"):
        print(f"\n  ⚠ 进行中的任务:")
        for task in state["active_tasks"]:
            print(f"    - {task}")

    # 显示上下文笔记数量
    context_count = len(state.get("context_notes", []))
    if context_count > 0:
        print(f"\n  📝 上下文笔记: {context_count} 条")

    # 检查记忆系统
    memory_status = check_memory_integrity()
    all_ok = all(memory_status.values())
    if all_ok:
        print(f"\n  ✓ 记忆系统完整")
    else:
        print(f"\n  ⚠ 记忆系统检查:")
        for name, ok in memory_status.items():
            status = "✓" if ok else "✗"
            print(f"    {status} {name}")

    # 最后更新时间
    last_updated = state.get("last_updated", "")
    if last_updated:
        print(f"\n  最后更新: {last_updated}")

    print("="*50 + "\n")

if __name__ == "__main__":
    main()
