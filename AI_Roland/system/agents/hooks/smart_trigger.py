#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能触发Hook - 只在必要时咨询子Agent

避免每次工具调用都触发，只在真正需要时提供建议
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime, timezone

# 添加系统路径
system_path = Path(__file__).parent.parent
sys.path.insert(0, str(system_path))


def should_trigger(user_input: str) -> bool:
    """
    判断是否应该触发子Agent咨询

    只在以下情况触发：
    1. 用户输入超过15个字符（复杂任务）
    2. 包含特定关键词
    3. 用户明确要求帮助
    """

    # 简单任务不需要触发
    if len(user_input) < 10:
        return False

    # 触发关键词
    trigger_keywords = [
        '审查', 'review', '安全', '设计', '架构', '计划',
        '测试', '优化', '重构', '文档', 'bug', '问题',
        '帮助', '建议', '如何', '怎么', '最佳实践',
        '开发', 'api', '代码', '认证'
    ]

    # 检查是否包含触发关键词（不区分大小写）
    user_input_lower = user_input.lower()
    for keyword in trigger_keywords:
        if keyword.lower() in user_input_lower:
            return True

    # 输入很长，可能是复杂任务
    if len(user_input) > 50:
        return True

    return False


def main():
    """主函数"""

    # 从环境变量获取输入
    if 'CLAUDE_LAST_USER_MESSAGE' in os.environ:
        user_input = os.environ['CLAUDE_LAST_USER_MESSAGE']
    elif len(sys.argv) > 1:
        user_input = ' '.join(sys.argv[1:])
    else:
        # 没有输入，不触发
        sys.exit(0)

    # 判断是否需要触发
    if not should_trigger(user_input):
        sys.exit(0)

    try:
        from consult_agents import consult_agents

        # 获取建议（简洁格式）
        suggestion = consult_agents(user_input, format='simple')

        # 检查是否建议调用Agent
        if '建议调用' not in suggestion and '建议使用' not in suggestion:
            # 简单任务，不需要输出
            sys.exit(0)

        # 输出建议到stderr（这样不会干扰正常输出）
        print("\n" + "="*60, file=sys.stderr)
        print("🤖 子Agent建议", file=sys.stderr)
        print("="*60, file=sys.stderr)
        print(suggestion, file=sys.stderr)
        print("="*60 + "\n", file=sys.stderr)

        # 记录到日志
        log_file = Path(__file__).parent / 'smart_trigger.log'
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now(timezone.utc).isoformat()} | Triggered\n")

    except Exception as e:
        # 静默失败，不影响正常执行
        error_file = Path(__file__).parent / 'smart_trigger_errors.log'
        with open(error_file, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now(timezone.utc).isoformat()} | Error: {str(e)}\n")

    sys.exit(0)


if __name__ == "__main__":
    main()
