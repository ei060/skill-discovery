#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Agent 活跃度监控系统

跟踪所有 agent 的参与情况，确保所有 agent 都有参与机会
"""

import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
from collections import defaultdict, Counter
import threading


class AgentActivityMonitor:
    """Agent 活跃度监控器"""

    def __init__(self, workspace: Optional[Path] = None):
        if workspace is None:
            workspace = Path(__file__).parent.parent.parent

        self.workspace = Path(workspace)
        self.monitor_dir = self.workspace / "system" / "agents" / "monitor"
        self.monitor_dir.mkdir(parents=True, exist_ok=True)

        # 数据文件
        self.activity_file = self.monitor_dir / "activity_log.json"
        self.stats_file = self.monitor_dir / "activity_stats.json"
        self.alerts_file = self.monitor_dir / "alerts.json"

        # 所有已注册的 agent
        self.all_agents = [
            'planner', 'architect', 'engineer',
            'code_reviewer', 'security_reviewer', 'doc_writer',
            'tdd_guide', 'e2e_runner', 'refactor_cleaner',
            'python_reviewer', 'go_reviewer', 'kotlin_reviewer',
            'database_reviewer'
        ]

        # 活动记录
        self.activity_log: List[Dict] = []
        self.stats: Dict = {}

        # 线程锁
        self._lock = threading.Lock()

        # 加载历史数据
        self._load_data()

    def _load_data(self):
        """加载历史数据"""
        # 加载活动日志
        if self.activity_file.exists():
            try:
                with open(self.activity_file, 'r', encoding='utf-8') as f:
                    self.activity_log = json.load(f)
            except Exception as e:
                print(f"[WARN] 加载活动日志失败: {e}")
                self.activity_log = []

        # 加载统计信息
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    self.stats = json.load(f)
            except Exception as e:
                print(f"[WARN] 加载统计信息失败: {e}")
                self.stats = {}

    def _save_data(self):
        """保存数据"""
        with self._lock:
            # 保存活动日志（只保留最近 1000 条）
            log_to_save = self.activity_log[-1000:] if len(self.activity_log) > 1000 else self.activity_log
            with open(self.activity_file, 'w', encoding='utf-8') as f:
                json.dump(log_to_save, f, indent=2, ensure_ascii=False, default=str)

            # 保存统计信息
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False, default=str)

    def record_activity(
        self,
        agent_name: str,
        task_type: str,
        task_description: str,
        success: bool = True,
        duration_seconds: float = 0,
        triggered_by: str = "manual"
    ):
        """
        记录 agent 活动

        Args:
            agent_name: Agent 名称
            task_type: 任务类型
            task_description: 任务描述
            success: 是否成功
            duration_seconds: 执行时长（秒）
            triggered_by: 触发方式 (manual/auto/suggested)
        """
        with self._lock:
            activity = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'agent': agent_name,
                'task_type': task_type,
                'task_description': task_description[:200],  # 限制长度
                'success': success,
                'duration_seconds': duration_seconds,
                'triggered_by': triggered_by
            }

            self.activity_log.append(activity)

            # 更新统计
            self._update_stats(agent_name, activity)

            # 保存数据
            self._save_data()

    def _update_stats(self, agent_name: str, activity: Dict):
        """更新统计信息"""

        # 初始化 agent 统计
        if agent_name not in self.stats:
            self.stats[agent_name] = {
                'total_tasks': 0,
                'successful_tasks': 0,
                'failed_tasks': 0,
                'total_duration': 0,
                'first_activity': activity['timestamp'],
                'last_activity': activity['timestamp'],
                'task_types': Counter(),
                'trigger_methods': Counter()
            }

        # 更新统计
        stats = self.stats[agent_name]
        stats['total_tasks'] += 1
        stats['last_activity'] = activity['timestamp']

        if activity['success']:
            stats['successful_tasks'] += 1
        else:
            stats['failed_tasks'] += 1

        stats['total_duration'] += activity['duration_seconds']
        stats['task_types'][activity['task_type']] += 1
        stats['trigger_methods'][activity['triggered_by']] += 1

        # 转换 Counter 为普通 dict
        stats['task_types'] = dict(stats['task_types'])
        stats['trigger_methods'] = dict(stats['trigger_methods'])

    def get_agent_stats(self, agent_name: str) -> Optional[Dict]:
        """获取单个 agent 的统计信息"""
        return self.stats.get(agent_name)

    def get_all_agent_stats(self) -> Dict:
        """获取所有 agent 的统计信息"""

        all_stats = {}

        for agent_name in self.all_agents:
            if agent_name in self.stats:
                all_stats[agent_name] = self.stats[agent_name]
            else:
                # 从未参与过的 agent
                all_stats[agent_name] = {
                    'total_tasks': 0,
                    'successful_tasks': 0,
                    'failed_tasks': 0,
                    'total_duration': 0,
                    'first_activity': None,
                    'last_activity': None,
                    'task_types': {},
                    'trigger_methods': {},
                    'never_used': True
                }

        return all_stats

    def get_inactive_agents(self, days: int = 7) -> List[str]:
        """
        获取不活跃的 agent 列表

        Args:
            days: 不活跃天数阈值

        Returns:
            不活跃的 agent 名称列表
        """
        inactive = []
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        for agent_name in self.all_agents:
            stats = self.stats.get(agent_name)

            if not stats:
                # 从未使用过
                inactive.append(agent_name)
            else:
                # 检查最后活动时间
                last_activity_str = stats.get('last_activity')
                if last_activity_str:
                    try:
                        last_activity = datetime.fromisoformat(last_activity_str)
                        if last_activity < cutoff:
                            inactive.append(agent_name)
                    except:
                        inactive.append(agent_name)
                else:
                    inactive.append(agent_name)

        return inactive

    def get_activity_summary(self, days: int = 7) -> Dict:
        """
        获取活动摘要

        Args:
            days: 统计最近 N 天的数据

        Returns:
            活动摘要
        """
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        # 筛选最近的活动
        recent_activities = [
            act for act in self.activity_log
            if datetime.fromisoformat(act['timestamp']) > cutoff
        ]

        # 统计
        agent_counts = Counter(act['agent'] for act in recent_activities)
        task_type_counts = Counter(act['task_type'] for act in recent_activities)
        success_rate = sum(1 for act in recent_activities if act['success']) / len(recent_activities) if recent_activities else 0

        return {
            'period_days': days,
            'total_activities': len(recent_activities),
            'agent_counts': dict(agent_counts),
            'task_type_counts': dict(task_type_counts),
            'success_rate': round(success_rate * 100, 2),
            'active_agents': len(agent_counts),
            'inactive_agents': len(self.all_agents) - len(agent_counts)
        }

    def check_and_alert(self) -> List[Dict]:
        """
        检查并生成警报

        Returns:
            警报列表
        """
        alerts = []

        # 1. 检查从未使用的 agent
        never_used = [agent for agent in self.all_agents if agent not in self.stats]
        if never_used:
            alerts.append({
                'type': 'never_used',
                'severity': 'warning',
                'message': f"以下 {len(never_used)} 个 agent 从未使用: {', '.join(never_used)}",
                'agents': never_used,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })

        # 2. 检查长期不活跃的 agent（超过 14 天）
        inactive_14d = self.get_inactive_agents(days=14)
        if inactive_14d:
            alerts.append({
                'type': 'inactive_14d',
                'severity': 'warning',
                'message': f"以下 {len(inactive_14d)} 个 agent 超过 14 天未使用: {', '.join(inactive_14d)}",
                'agents': inactive_14d,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })

        # 3. 检查活跃度不均衡
        recent_summary = self.get_activity_summary(days=7)
        active_ratio = recent_summary['active_agents'] / len(self.all_agents)

        if active_ratio < 0.5:  # 少于 50% 的 agent 在使用
            alerts.append({
                'type': 'imbalance',
                'severity': 'info',
                'message': f"Agent 活跃度不均衡，最近 7 天只有 {recent_summary['active_agents']}/{len(self.all_agents)} 个 agent 被使用",
                'active_ratio': active_ratio,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })

        # 4. 检查失败率
        if recent_summary['total_activities'] > 0:
            failure_rate = 100 - recent_summary['success_rate']
            if failure_rate > 30:  # 失败率超过 30%
                alerts.append({
                    'type': 'high_failure_rate',
                    'severity': 'warning',
                    'message': f"最近任务失败率过高: {failure_rate:.1f}%",
                    'failure_rate': failure_rate,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })

        # 保存警报
        if alerts:
            with open(self.alerts_file, 'w', encoding='utf-8') as f:
                json.dump(alerts, f, indent=2, ensure_ascii=False, default=str)

        return alerts

    def get_recommendations(self) -> List[str]:
        """
        生成改进建议

        Returns:
            建议列表
        """
        recommendations = []

        # 检查不活跃的 agent
        inactive = self.get_inactive_agents(days=7)
        if inactive:
            recommendations.append(
                f"建议：为以下 agent 分配任务以提高活跃度: {', '.join(inactive[:5])}"
            )

        # 检查自动触发比例
        recent_activities = [
            act for act in self.activity_log
            if datetime.fromisoformat(act['timestamp']) > datetime.now(timezone.utc) - timedelta(days=7)
        ]

        if recent_activities:
            auto_triggered = sum(1 for act in recent_activities if act.get('triggered_by') == 'auto')
            auto_ratio = auto_triggered / len(recent_activities)

            if auto_ratio < 0.3:  # 自动触发少于 30%
                recommendations.append(
                    f"建议：增加自动触发机制的使用（当前自动触发率: {auto_ratio*100:.1f}%）"
                )

        # 检查成功率
        summary = self.get_activity_summary(days=7)
        if summary['total_activities'] > 0 and summary['success_rate'] < 70:
            recommendations.append(
                f"警告：任务成功率较低 ({summary['success_rate']:.1f}%)，建议检查 agent 配置或任务分配"
            )

        return recommendations

    def generate_report(self) -> str:
        """生成活动报告"""
        lines = []
        lines.append("=" * 70)
        lines.append("Agent 活跃度监控报告")
        lines.append("=" * 70)

        # 整体统计
        summary = self.get_activity_summary(days=7)
        lines.append(f"\n[最近 7 天统计]")
        lines.append(f"  总活动数: {summary['total_activities']}")
        lines.append(f"  活跃 Agent: {summary['active_agents']}/{len(self.all_agents)}")
        lines.append(f"  不活跃 Agent: {summary['inactive_agents']}")
        lines.append(f"  成功率: {summary['success_rate']}%")

        # 各 Agent 统计
        lines.append(f"\n[各 Agent 统计]")
        all_stats = self.get_all_agent_stats()

        for agent_name in sorted(all_stats.keys()):
            stats = all_stats[agent_name]
            if stats.get('never_used'):
                lines.append(f"  {agent_name}: 从未使用")
            else:
                lines.append(
                    f"  {agent_name}: {stats['total_tasks']} 次任务, "
                    f"成功率 {stats['successful_tasks']/stats['total_tasks']*100:.1f}%"
                )

        # 警报
        alerts = self.check_and_alert()
        if alerts:
            lines.append(f"\n[警报] ({len(alerts)} 条)")
            for alert in alerts:
                lines.append(f"  [{alert['severity'].upper()}] {alert['message']}")

        # 建议
        recommendations = self.get_recommendations()
        if recommendations:
            lines.append(f"\n[建议]")
            for rec in recommendations:
                lines.append(f"  - {rec}")

        lines.append("\n" + "=" * 70)

        return "\n".join(lines)


# 全局单例
_instance = None
_lock = threading.Lock()


def get_activity_monitor() -> AgentActivityMonitor:
    """获取活动监控器单例"""
    global _instance
    with _lock:
        if _instance is None:
            _instance = AgentActivityMonitor()
    return _instance


# 命令行测试
if __name__ == "__main__":
    import sys

    monitor = get_activity_monitor()

    print("\n[测试] 记录一些模拟活动...\n")

    # 模拟活动记录
    test_activities = [
        ('planner', 'code_review', '审查认证代码', True, 120, 'manual'),
        ('code_reviewer', 'code_review', '审查 API 代码', True, 90, 'suggested'),
        ('security_reviewer', 'security_check', '检查 SQL 注入', True, 60, 'auto'),
        ('doc_writer', 'documentation', '编写 README', True, 180, 'manual'),
        ('planner', 'architecture', '设计系统架构', True, 300, 'suggested'),
    ]

    for agent, task_type, desc, success, duration, triggered in test_activities:
        monitor.record_activity(agent, task_type, desc, success, duration, triggered)

    print("[OK] 模拟活动记录完成\n")

    # 生成报告
    report = monitor.generate_report()
    print(report)
