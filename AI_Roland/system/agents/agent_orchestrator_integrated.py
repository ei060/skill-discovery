#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Agent 协作系统集成版

整合智能建议、活跃度监控和强制参与功能
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 添加系统路径
system_path = Path(__file__).parent
sys.path.insert(0, str(system_path))

# 修复 Windows 编码
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

from auto_agent_suggester import AgentSuggester, get_agent_suggester
from agent_activity_monitor import AgentActivityMonitor, get_activity_monitor
from agent_enforcer import AgentEnforcer, get_agent_enforcer


class AgentOrchestrator:
    """
    Agent 编排器 - 整合所有 agent 管理功能

    功能：
    1. 智能建议 - 自动推荐合适的 agent
    2. 活跃度监控 - 跟踪 agent 使用情况
    3. 强制参与 - 确保关键任务由专业 agent 处理
    4. 自动触发 - 高匹配度任务自动调用 agent
    """

    def __init__(self):
        self.suggester = get_agent_suggester()
        self.monitor = get_activity_monitor()
        self.enforcer = get_agent_enforcer()

    def analyze_task(
        self,
        task: str,
        context: Dict = None
    ) -> Dict:
        """
        全面分析任务，返回最佳 agent 建议

        Args:
            task: 任务描述
            context: 额外上下文

        Returns:
            分析结果
        """
        context = context or {}

        # 1. 检查强制规则
        enforcement_result = self.enforcer.check_task(task, context)

        # 2. 获取智能建议
        suggestions = self.suggester.analyze_task(task, context)

        # 3. 检查是否应该自动触发
        should_auto, auto_rule = self.enforcer.should_force_agent(task, context)

        # 4. 整合建议
        if enforcement_result:
            # 有强制规则，优先使用
            recommended_agent = enforcement_result['required_agent']
            reason = enforcement_result['reason']
            confidence = 100  # 强制规则置信度最高
        elif suggestions:
            # 使用智能建议
            recommended_agent = suggestions[0]['agent']
            reason = suggestions[0]['reason']
            confidence = min(suggestions[0]['score'], 99)  # 最高 99
        else:
            # 无建议
            recommended_agent = None
            reason = "未找到合适的 agent"
            confidence = 0

        return {
            'task': task,
            'recommended_agent': recommended_agent,
            'confidence': confidence,
            'reason': reason,
            'enforcement': enforcement_result,
            'suggestions': suggestions[:3],  # 返回前 3 个建议
            'should_auto_trigger': should_auto,
            'auto_rule': auto_rule
        }

    def execute_with_agent(
        self,
        task: str,
        agent_name: str = None,
        context: Dict = None,
        auto_trigger: bool = False
    ) -> Dict:
        """
        使用指定 agent 执行任务（推荐）

        Args:
            task: 任务描述
            agent_name: 指定的 agent（如果为 None，则自动选择）
            context: 额外上下文
            auto_trigger: 是否自动触发

        Returns:
            执行计划
        """
        context = context or {}

        # 1. 分析任务
        analysis = self.analyze_task(task, context)

        # 2. 确定使用的 agent
        if agent_name:
            # 用户指定了 agent
            selected_agent = agent_name

            # 验证是否合规
            is_valid, error_msg = self.enforcer.validate_agent_usage(
                task, selected_agent, context
            )

            if not is_valid:
                return {
                    'success': False,
                    'error': error_msg,
                    'analysis': analysis,
                    'recommendation': f"建议使用: {analysis['recommended_agent']}"
                }
        else:
            # 自动选择 agent
            selected_agent = analysis['recommended_agent']

            if not selected_agent:
                return {
                    'success': False,
                    'error': '未找到合适的 agent',
                    'analysis': analysis
                }

        # 3. 记录活动
        self.monitor.record_activity(
            agent_name=selected_agent,
            task_type=analysis.get('enforcement', {}).get('rule_name', 'general'),
            task_description=task,
            triggered_by='auto' if auto_trigger else 'manual'
        )

        # 4. 返回执行计划
        return {
            'success': True,
            'agent': selected_agent,
            'task': task,
            'confidence': analysis['confidence'],
            'reason': analysis['reason'],
            'should_auto_trigger': analysis['should_auto_trigger'],
            'next_step': f"使用 Task tool 调用 {selected_agent} agent",
            'analysis': analysis
        }

    def get_system_report(self) -> str:
        """生成系统报告"""
        lines = []
        lines.append("=" * 70)
        lines.append("Agent 协作系统报告")
        lines.append("=" * 70)

        # 1. 活跃度监控报告
        lines.append("\n[活跃度监控]")
        activity_summary = self.monitor.get_activity_summary(days=7)
        lines.append(f"  最近 7 天活动数: {activity_summary['total_activities']}")
        lines.append(f"  活跃 Agent: {activity_summary['active_agents']}")
        lines.append(f"  不活跃 Agent: {activity_summary['inactive_agents']}")
        lines.append(f"  成功率: {activity_summary['success_rate']}%")

        # 2. 智能建议统计
        lines.append("\n[智能建议]")
        suggester_stats = self.suggester.get_stats()
        lines.append(f"  总建议次数: {suggester_stats['total_suggestions']}")
        lines.append(f"  Agent 建议分布:")
        for agent, count in suggester_stats['agent_suggestion_counts'].items():
            lines.append(f"    - {agent}: {count} 次")

        # 3. 强制规则统计
        lines.append("\n[强制规则]")
        enforcement_stats = self.enforcer.get_enforcement_stats()
        lines.append(f"  总强制次数: {enforcement_stats['total_enforcements']}")
        lines.append(f"  Agent 强制分布:")
        for agent, count in enforcement_stats['agent_counts'].items():
            lines.append(f"    - {agent}: {count} 次")

        # 4. 警报和建议
        lines.append("\n[警报和建议]")
        alerts = self.monitor.check_and_alert()
        if alerts:
            for alert in alerts:
                lines.append(f"  [{alert['severity'].upper()}] {alert['message']}")
        else:
            lines.append("  无警报")

        recommendations = self.monitor.get_recommendations()
        if recommendations:
            lines.append("\n  改进建议:")
            for rec in recommendations[:3]:
                lines.append(f"    - {rec}")

        lines.append("\n" + "=" * 70)

        return "\n".join(lines)

    def get_integrated_suggestion(self, task: str, context: Dict = None) -> str:
        """
        获取集成的建议消息（用于显示给用户）

        Args:
            task: 任务描述
            context: 额外上下文

        Returns:
            格式化的建议消息
        """
        analysis = self.analyze_task(task, context)

        lines = []
        lines.append("\n[AI] Agent 协作系统分析\n")
        lines.append(f"任务: {task[:100]}...\n")

        # 强制规则
        if analysis['enforcement']:
            lines.append(f"[强制规则] {analysis['enforcement']['description']}")
            lines.append(f"要求 Agent: {analysis['enforcement']['required_agent']}")
            if analysis['enforcement']['auto_trigger']:
                lines.append(f"[自动触发] 此任务将自动使用 {analysis['enforcement']['required_agent']}\n")
            else:
                lines.append("")

        # 推荐建议
        if analysis['recommended_agent']:
            lines.append(f"[推荐] {analysis['recommended_agent']}")
            lines.append(f"置信度: {analysis['confidence']}%")
            lines.append(f"理由: {analysis['reason']}\n")

        # 备选建议
        if len(analysis['suggestions']) > 1:
            lines.append("[备选方案]")
            for i, sugg in enumerate(analysis['suggestions'][1:3], 2):
                lines.append(f"  {i}. {sugg['agent']} (分数: {sugg['score']})")
            lines.append("")

        # 下一步
        if analysis['recommended_agent']:
            lines.append(f"[下一步] 使用以下命令:")
            lines.append(f'  Task tool: subagent_type="{analysis["recommended_agent"]}", prompt="{task[:50]}..."')

        return "\n".join(lines)


# 全局单例
_instance = None


def get_agent_orchestrator() -> AgentOrchestrator:
    """获取 Agent 编排器单例"""
    global _instance
    if _instance is None:
        _instance = AgentOrchestrator()
    return _instance


# 命令行测试
if __name__ == "__main__":
    orchestrator = get_agent_orchestrator()

    print("=" * 70)
    print("Agent 协作系统集成测试")
    print("=" * 70)

    # 测试任务
    test_tasks = [
        "检查用户认证系统的 SQL 注入漏洞",
        "为支付 API 编写单元测试",
        "设计微服务架构",
        "审查 Python Django 代码质量",
        "更新项目 README 文档",
        "重构订单处理模块"
    ]

    print("\n[测试] 分析任务并获取建议:\n")

    for task in test_tasks:
        print(f"\n任务: {task}")
        print("-" * 70)

        # 分析任务
        analysis = orchestrator.analyze_task(task)

        print(f"推荐 Agent: {analysis['recommended_agent']}")
        print(f"置信度: {analysis['confidence']}%")
        print(f"理由: {analysis['reason']}")
        print(f"自动触发: {'是' if analysis['should_auto_trigger'] else '否'}")

        # 获取集成建议
        suggestion = orchestrator.get_integrated_suggestion(task)
        print(f"\n{suggestion}")

    # 系统报告
    print("\n" + "=" * 70)
    print("系统报告")
    print("=" * 70)

    report = orchestrator.get_system_report()
    print(report)
