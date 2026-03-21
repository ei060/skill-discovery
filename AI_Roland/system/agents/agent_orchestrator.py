#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI Roland Agent 编排器

让主Agent能够接收子Agent的主动建议
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

# 修复Windows编码
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

# 添加系统路径
system_path = Path(__file__).parent
sys.path.insert(0, str(system_path))

from active_participation import get_active_participation_engine


class AgentOrchestrator:
    """Agent编排器 - 协调主Agent和子Agent的协作"""

    def __init__(self):
        self.participation_engine = get_active_participation_engine()

    def consult_sub_agents(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """咨询子Agent，获取建议"""

        # 获取参与报告
        report = self.participation_engine.get_participation_report(user_input)

        # 格式化输出给主Agent
        output = {
            'user_input': user_input,
            'timestamp': report['timestamp'],
            'consultation_result': self._format_for_main_agent(report)
        }

        return output

    def _format_for_main_agent(self, report: Dict) -> str:
        """格式化建议为主Agent可读的格式"""

        lines = []
        lines.append("=" * 60)
        lines.append("🤖 子Agent主动建议")
        lines.append("=" * 60)
        lines.append("")

        # 总体建议
        rec = report['recommendations']

        if not rec['should_use_agents']:
            lines.append(f"💡 {rec['message']}")
            lines.append("")
            lines.append("→ 主Agent可以直接处理此任务")
            return "\n".join(lines)

        # 有建议的情况
        priority_emoji = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }

        priority = rec.get('priority', 'low')
        lines.append(f"{priority_emoji.get(priority, '⚪')} 优先级: {priority.upper()}")
        lines.append(f"💡 {rec['message']}")

        if 'agents' in rec:
            lines.append(f"📋 建议调用: {', '.join(rec['agents'])}")

        if 'workflow' in rec and rec['workflow'] != 'optional':
            lines.append(f"🔄 工作流: {rec['workflow']}")

        lines.append("")
        lines.append("-" * 60)
        lines.append("详细建议:")
        lines.append("")

        for sug in report['suggestions'][:5]:
            agent_emoji = self._get_agent_emoji(sug['agent_name'])
            lines.append(f"{agent_emoji} **{sug['agent_name']}**")
            lines.append(f"   {sug['suggestion']}")
            lines.append(f"   匹配关键词: {', '.join(sug['matched_keywords'])}")
            lines.append(f"   优先级分数: {sug['priority_score']:.1f}/100")
            lines.append("")

        lines.append("=" * 60)

        return "\n".join(lines)

    def _get_agent_emoji(self, agent_name: str) -> str:
        """获取Agent对应的emoji"""

        emoji_map = {
            'code_reviewer': '👁️',
            'planner': '📋',
            'architect': '🏗️',
            'security_reviewer': '🔒',
            'tdd_guide': '✅',
            'python_reviewer': '🐍',
            'database_reviewer': '🗄️',
            'doc_writer': '📝',
            'refactor_cleaner': '🧹',
            'e2e_runner': '🎭'
        }

        return emoji_map.get(agent_name, '🤖')

    def generate_action_plan(self, user_input: str) -> Dict:
        """生成行动计划"""

        report = self.participation_engine.get_participation_report(user_input)
        rec = report['recommendations']

        if not rec['should_use_agents']:
            return {
                'action': 'handle_directly',
                'reason': rec['message'],
                'agents_to_use': []
            }

        return {
            'action': 'delegate_to_agents',
            'reason': rec['message'],
            'priority': rec.get('priority', 'low'),
            'agents_to_use': rec.get('agents', []),
            'workflow': rec.get('workflow', 'sequential'),
            'suggestions': report['suggestions']
        }


def get_agent_orchestrator() -> AgentOrchestrator:
    """获取编排器单例"""
    return AgentOrchestrator()


# CLI接口 - 供主Agent调用
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Agent编排器')
    parser.add_argument('input', help='用户输入')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                       help='输出格式')

    args = parser.parse_args()

    orchestrator = get_agent_orchestrator()

    if args.format == 'json':
        result = orchestrator.consult_sub_agents(args.input)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        result = orchestrator.consult_sub_agents(args.input)
        print(result['consultation_result'])

        # 也输出行动计划
        plan = orchestrator.generate_action_plan(args.input)
        print("\n📋 建议行动计划:")
        print(json.dumps(plan, ensure_ascii=False, indent=2))
