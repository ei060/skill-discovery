#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动 Agent 触发器

当任务分析的置信度 >= 80% 时，自动建议使用推荐的 Agent
"""

import sys
from pathlib import Path

# 添加系统路径
system_path = Path(__file__).parent / "system"
sys.path.insert(0, str(system_path))

from task_executor import get_task_executor

def auto_analyze_and_suggest(task: str) -> dict:
    """
    自动分析任务并给出明确的调用建议

    Args:
        task: 任务描述

    Returns:
        包含调用建议的字典
    """
    executor = get_task_executor()
    analysis = executor.analyze(task)

    # 构建建议
    suggestion = {
        'task': task,
        'recommended_agent': analysis['recommended_agent'],
        'confidence': analysis['confidence'],
        'reason': analysis['reason'],
        'should_auto_trigger': analysis['auto_trigger'],
        'enforcement': analysis['enforcement'],
        'call_instruction': None
    }

    # 生成调用指令
    if analysis['recommended_agent']:
        suggestion['call_instruction'] = {
            'tool': 'Task',
            'subagent_type': analysis['recommended_agent'],
            'prompt': task,
            'confidence': analysis['confidence'],
            'reason': analysis['reason']
        }

    return suggestion

def print_suggestion(suggestion: dict):
    """打印建议"""
    print("\n" + "=" * 70)
    print("Agent 自动推荐")
    print("=" * 70)

    print(f"\n任务: {suggestion['task']}")

    if suggestion['recommended_agent']:
        print(f"\n推荐 Agent: {suggestion['recommended_agent']}")
        print(f"置信度: {suggestion['confidence']}%")
        print(f"理由: {suggestion['reason']}")

        if suggestion['enforcement']:
            print(f"强制规则: {suggestion['enforcement']['description']}")

        if suggestion['should_auto_trigger']:
            print(f"\n[OK] 置信度 >= 50%，建议立即使用")
        else:
            print(f"\n[WARN] 置信度 < 50%，可以手动考虑")

        if suggestion['call_instruction']:
            print(f"\n调用指令:")
            print(f"  Task(")
            print(f"    subagent_type=\"{suggestion['call_instruction']['subagent_type']}\",")
            print(f"    prompt=\"{suggestion['call_instruction']['prompt']}\"")
            print(f"  )")
    else:
        print("\n未找到合适的 Agent")

    print("\n" + "=" * 70)

def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python auto_agent_trigger.py \"任务描述\"")
        print("\n示例:")
        print("  python auto_agent_trigger.py \"检查 SQL 注入\"")
        print("  python auto_agent_trigger.py \"编写单元测试\"")
        sys.exit(1)

    task = " ".join(sys.argv[1:])

    # 分析任务
    suggestion = auto_analyze_and_suggest(task)

    # 打印建议
    print_suggestion(suggestion)

    # 返回建议
    return 0 if suggestion['should_auto_trigger'] else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"[ERROR] 分析失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
