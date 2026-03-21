#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI Roland 任务执行器

统一的任务执行接口，自动选择合适的 Agent 并记录执行过程
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

# 添加系统路径
system_path = Path(__file__).parent
sys.path.insert(0, str(system_path))

from agents.auto_agent_suggester import get_agent_suggester
from agents.agent_activity_monitor import get_activity_monitor
from agents.agent_enforcer import get_agent_enforcer


class TaskExecutor:
    """任务执行器 - 统一的任务执行接口"""

    def __init__(self):
        self.suggester = get_agent_suggester()
        self.monitor = get_activity_monitor()
        self.enforcer = get_agent_enforcer()

    def analyze(self, task: str, context: Dict = None) -> Dict:
        """
        分析任务并推荐 Agent

        Args:
            task: 任务描述
            context: 额外上下文

        Returns:
            分析结果
        """
        context = context or {}

        # 1. 检查强制规则
        enforcement = self.enforcer.check_task(task, context)

        # 2. 获取智能建议
        suggestions = self.suggester.analyze_task(task, context)

        # 3. 确定最佳 Agent
        if enforcement:
            # 有强制规则，优先使用
            recommended = enforcement['required_agent']
            reason = enforcement['description']
            confidence = 100
            auto_trigger = enforcement.get('auto_trigger', False)
        elif suggestions:
            # 使用智能建议
            recommended = suggestions[0]['agent']
            reason = suggestions[0]['reason']
            confidence = min(int(suggestions[0]['score']), 99)
            auto_trigger = confidence >= 50
        else:
            # 无建议
            recommended = None
            reason = "未找到合适的 Agent"
            confidence = 0
            auto_trigger = False

        return {
            'task': task,
            'recommended_agent': recommended,
            'confidence': confidence,
            'reason': reason,
            'suggestions': suggestions[:3],
            'auto_trigger': auto_trigger,
            'enforcement': enforcement
        }

    def execute(self, task: str, agent_name: str = None,
                 context: Dict = None, record: bool = True) -> Dict:
        """
        执行任务（记录，不实际调用 Agent）

        注意：这个函数只负责记录和推荐，实际执行需要由调用者完成

        Args:
            task: 任务描述
            agent_name: 指定的 Agent（可选）
            context: 额外上下文
            record: 是否记录到监控系统

        Returns:
            执行结果
        """
        context = context or {}

        # 分析任务
        analysis = self.analyze(task, context)

        # 确定使用的 Agent
        if agent_name:
            selected = agent_name
            # 验证是否合规
            is_valid, error = self.enforcer.validate_agent_usage(
                task, selected, context
            )
            if not is_valid:
                return {
                    'success': False,
                    'error': error,
                    'recommendation': f"建议使用: {analysis['recommended_agent']}"
                }
        else:
            selected = analysis['recommended_agent']
            if not selected:
                return {
                    'success': False,
                    'error': '未找到合适的 Agent'
                }

        # 记录活动
        if record:
            self.monitor.record_activity(
                agent_name=selected,
                task_type=analysis.get('enforcement', {}).get('rule_name', 'general'),
                task_description=task,
                success=True,  # 记录时假设成功
                triggered_by='auto' if analysis['auto_trigger'] else 'manual'
            )

        return {
            'success': True,
            'agent': selected,
            'task': task,
            'confidence': analysis['confidence'],
            'reason': analysis['reason'],
            'analysis': analysis,
            'next_step': f"使用 Task tool 调用 {selected} agent"
        }

    def get_status(self) -> Dict:
        """获取系统状态"""
        activity_summary = self.monitor.get_activity_summary(days=7)
        suggester_stats = self.suggester.get_stats()

        return {
            'monitor': activity_summary,
            'suggester': suggester_stats,
            'last_update': activity_summary.get('period_days', 0)
        }

    def get_report(self) -> str:
        """生成系统报告"""
        lines = []
        lines.append("=" * 70)
        lines.append("AI Roland Agent 协作系统状态")
        lines.append("=" * 70)

        # 活跃度监控
        summary = self.monitor.get_activity_summary(days=7)
        lines.append(f"\n最近 7 天活动:")
        lines.append(f"  总活动数: {summary['total_activities']}")
        lines.append(f"  活跃 Agent: {summary['active_agents']}")
        lines.append(f"  成功率: {summary['success_rate']}%")

        # 警报
        alerts = self.monitor.check_and_alert()
        if alerts:
            lines.append(f"\n警报 ({len(alerts)} 条):")
            for alert in alerts:
                lines.append(f"  [{alert['severity']}] {alert['message']}")
        else:
            lines.append(f"\n警报: 无")

        # 建议
        recommendations = self.monitor.get_recommendations()
        if recommendations:
            lines.append(f"\n建议:")
            for rec in recommendations[:3]:
                lines.append(f"  - {rec}")

        lines.append("\n" + "=" * 70)

        return "\n".join(lines)


# 全局单例
_instance = None


def get_task_executor() -> TaskExecutor:
    """获取任务执行器单例"""
    global _instance
    if _instance is None:
        _instance = TaskExecutor()
    return _instance


# 便捷函数
def analyze_task(task: str, context: Dict = None) -> Dict:
    """分析任务并推荐 Agent"""
    executor = get_task_executor()
    return executor.analyze(task, context)


def execute_with_agent(task: str, agent: str = None,
                       context: Dict = None) -> Dict:
    """执行任务（记录）"""
    executor = get_task_executor()
    return executor.execute(task, agent, context)


def get_system_status() -> Dict:
    """获取系统状态"""
    executor = get_task_executor()
    return executor.get_status()


def get_system_report() -> str:
    """获取系统报告"""
    executor = get_task_executor()
    return executor.get_report()


if __name__ == "__main__":
    # 测试
    print("=" * 70)
    print("AI Roland 任务执行器测试")
    print("=" * 70)

    executor = get_task_executor()

    # 测试任务分析
    test_tasks = [
        "检查 SQL 注入漏洞",
        "编写单元测试",
        "设计系统架构"
    ]

    for task in test_tasks:
        print(f"\n任务: {task}")
        print("-" * 70)

        result = executor.analyze(task)
        print(f"推荐 Agent: {result['recommended_agent']}")
        print(f"置信度: {result['confidence']}%")
        print(f"理由: {result['reason']}")
        print(f"自动触发: {result['auto_trigger']}")

    # 系统报告
    print("\n" + executor.get_report())
