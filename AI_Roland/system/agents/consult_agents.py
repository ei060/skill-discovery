#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
主Agent快速咨询工具

让主Agent能够快速获取子Agent的建议
"""

import sys
import os
import json
from pathlib import Path

# 添加系统路径
system_path = Path(__file__).parent
sys.path.insert(0, str(system_path))

def consult_agents(user_input: str, format: str = 'simple') -> str:
    """
    快速咨询子Agent

    Args:
        user_input: 用户输入
        format: 输出格式 (simple, detailed, json)

    Returns:
        子Agent的建议
    """

    try:
        from agent_orchestrator import get_agent_orchestrator

        orchestrator = get_agent_orchestrator()

        if format == 'json':
            result = orchestrator.consult_sub_agents(user_input)
            return json.dumps(result, ensure_ascii=False, indent=2)
        elif format == 'detailed':
            result = orchestrator.consult_sub_agents(user_input)
            return result['consultation_result']
        else:  # simple
            # 获取行动计划
            plan = orchestrator.generate_action_plan(user_input)

            if plan['action'] == 'handle_directly':
                return f"💡 {plan['reason']}"

            # 简洁格式
            priority_emoji = {
                'high': '🔴',
                'medium': '🟡',
                'low': '🟢'
            }

            priority = plan.get('priority', 'low')
            agents = plan.get('agents_to_use', [])

            lines = []
            lines.append(f"{priority_emoji.get(priority, '⚪')} 优先级: {priority.upper()}")
            lines.append(f"🤖 建议调用: {', '.join(agents)}")

            if 'workflow' in plan and plan['workflow'] != 'optional':
                lines.append(f"🔄 工作流: {plan['workflow']}")

            return '\n'.join(lines)

    except Exception as e:
        return f"⚠️ 咨询失败: {str(e)}"


if __name__ == "__main__":
    # 从命令行参数获取输入
    if len(sys.argv) > 1:
        user_input = ' '.join(sys.argv[1:])
    else:
        # 从标准输入读取（安全地）
        from system.sys_utils import safe_read_stdin
        stdin_data = safe_read_stdin()
        user_input = stdin_data.strip() if stdin_data else ""

    if not user_input:
        print("❌ 请提供输入")
        sys.exit(1)

    # 检查格式参数
    format = 'simple'
    if '--format=json' in sys.argv or '-f json' in sys.argv:
        format = 'json'
    elif '--format=detailed' in sys.argv or '-f detailed' in sys.argv:
        format = 'detailed'

    # 输出建议
    result = consult_agents(user_input, format)
    print(result)
