#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Agent 强制参与系统

为特定任务类型创建强制 agent 参与规则，确保关键任务由专业 agent 处理
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass


@dataclass
class EnforcementRule:
    """强制执行规则"""
    name: str
    description: str
    pattern: str  # 正则表达式模式
    required_agent: str
    priority: int  # 优先级 (1-10)
    auto_trigger: bool = True
    fallback_agents: List[str] = None  # 备选 agent

    def __post_init__(self):
        if self.fallback_agents is None:
            self.fallback_agents = []


class AgentEnforcer:
    """Agent 强制参与管理器"""

    def __init__(self):
        self.workspace = Path(__file__).parent.parent.parent

        # 定义强制规则
        self.rules = self._load_default_rules()

        # 执行历史
        self.enforcement_history: List[Dict] = []

    def _load_default_rules(self) -> List[EnforcementRule]:
        """加载默认的强制规则"""

        return [
            # 安全相关 - 最高优先级
            EnforcementRule(
                name="security_mandatory",
                description="所有安全相关任务必须由 security_reviewer 处理",
                pattern=r'(安全|security|漏洞|vulnerability|攻击|attack|注入|injection|xss|csrf|权限|permission|认证|auth|加密|encrypt)',
                required_agent="security-reviewer",
                priority=10,
                auto_trigger=True,
                fallback_agents=["code-reviewer"]
            ),

            # 测试相关 - TDD
            EnforcementRule(
                name="test_tdd_mandatory",
                description="编写测试任务必须使用 TDD 方法",
                pattern=r'(写.*测试|创建.*测试|test.*case|单元测试|集成测试|tdd|测试驱动)',
                required_agent="tdd-guide",
                priority=9,
                auto_trigger=True,
                fallback_agents=["code-reviewer"]
            ),

            # 架构设计 - 复杂系统
            EnforcementRule(
                name="architecture_mandatory",
                description="系统架构设计必须由 architect 处理",
                pattern=r'(系统.*架构|软件.*架构|架构.*设计|technical.*decision|设计模式|design.*pattern)',
                required_agent="architect",
                priority=8,
                auto_trigger=True,
                fallback_agents=["planner"]
            ),

            # 大规模重构
            EnforcementRule(
                name="refactor_mandatory",
                description="大规模重构需要 planner 规划",
                pattern=r'(重构|refactor).*系统|(重构|refactor).*模块|(重构|refactor).*架构',
                required_agent="planner",
                priority=8,
                auto_trigger=True,
                fallback_agents=["architect"]
            ),

            # Python 特定
            EnforcementRule(
                name="python_specific",
                description="Python 特定任务",
                pattern=r'python.*(代码|code|django|flask|fastapi|pep)',
                required_agent="python-reviewer",
                priority=6,
                auto_trigger=False,
                fallback_agents=["code-reviewer"]
            ),

            # Go 特定
            EnforcementRule(
                name="go_specific",
                description="Go 特定任务",
                pattern=r'(go|golang).*(代码|code|goroutine|channel)',
                required_agent="go-reviewer",
                priority=6,
                auto_trigger=False,
                fallback_agents=["code-reviewer"]
            ),

            # 文档相关
            EnforcementRule(
                name="documentation_mandatory",
                description="文档任务必须由 doc_writer 处理",
                pattern=r'(写|创建|更新).*文档|(write|create|update).*doc|readme|api.*文档|使用.*指南',
                required_agent="doc-writer",
                priority=5,
                auto_trigger=True,
                fallback_agents=["planner"]
            ),

            # E2E 测试
            EnforcementRule(
                name="e2e_mandatory",
                description="端到端测试",
                pattern=r'(e2e|端到端|end.*end|用户流程|user.*flow).*(测试|test)',
                required_agent="e2e-runner",
                priority=7,
                auto_trigger=True,
                fallback_agents=["tdd-guide"]
            ),

            # 代码审查
            EnforcementRule(
                name="code_review_mandatory",
                description="代码审查必须由 code_reviewer 处理",
                pattern=r'(审查|review|检查).*(代码|code)|(分析|analyze).*(代码|code)',
                required_agent="code-reviewer",
                priority=6,
                auto_trigger=False,
                fallback_agents=["python-reviewer", "go-reviewer"]
            ),
        ]

    def check_task(self, task: str, context: Dict = None) -> Optional[Dict]:
        """
        检查任务是否匹配强制规则

        Args:
            task: 任务描述
            context: 额外上下文

        Returns:
            如果匹配规则，返回规则信息；否则返回 None
        """
        context = context or {}

        # 按优先级排序规则
        sorted_rules = sorted(self.rules, key=lambda r: r.priority, reverse=True)

        for rule in sorted_rules:
            # 检查是否匹配模式
            if re.search(rule.pattern, task, re.IGNORECASE):
                # 记录强制执行
                self._record_enforcement(rule, task, context)

                return {
                    'rule_name': rule.name,
                    'required_agent': rule.required_agent,
                    'priority': rule.priority,
                    'description': rule.description,
                    'auto_trigger': rule.auto_trigger,
                    'fallback_agents': rule.fallback_agents,
                    'reason': f"任务匹配强制规则: {rule.description}"
                }

        return None

    def _record_enforcement(self, rule: EnforcementRule, task: str, context: Dict):
        """记录强制执行历史"""
        record = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'rule': rule.name,
            'required_agent': rule.required_agent,
            'task': task[:200],
            'context': context
        }
        self.enforcement_history.append(record)

        # 只保留最近 1000 条记录
        if len(self.enforcement_history) > 1000:
            self.enforcement_history = self.enforcement_history[-1000:]

    def should_force_agent(self, task: str, context: Dict = None) -> Tuple[bool, Optional[Dict]]:
        """
        判断是否应该强制使用特定 agent

        Args:
            task: 任务描述
            context: 额外上下文

        Returns:
            (是否强制, 强制规则信息)
        """
        rule_info = self.check_task(task, context)

        if rule_info and rule_info['auto_trigger']:
            return True, rule_info

        return False, rule_info

    def get_required_agent(self, task: str, context: Dict = None) -> Optional[str]:
        """
        获取任务要求的 agent

        Args:
            task: 任务描述
            context: 额外上下文

        Returns:
            要求的 agent 名称，如果没有要求则返回 None
        """
        rule_info = self.check_task(task, context)
        return rule_info['required_agent'] if rule_info else None

    def validate_agent_usage(
        self,
        task: str,
        selected_agent: str,
        context: Dict = None
    ) -> Tuple[bool, Optional[str]]:
        """
        验证使用的 agent 是否符合要求

        Args:
            task: 任务描述
            selected_agent: 选择的 agent
            context: 额外上下文

        Returns:
            (是否有效, 错误消息)
        """
        rule_info = self.check_task(task, context)

        if not rule_info:
            # 没有强制规则，任何 agent 都有效
            return True, None

        required = rule_info['required_agent']
        fallbacks = rule_info.get('fallback_agents', [])

        # 检查是否是要求的 agent
        if selected_agent == required:
            return True, None

        # 检查是否是备选 agent
        if selected_agent in fallbacks:
            return True, None

        # 不符合要求
        error_msg = (
            f"任务 '{task[:50]}...' 要求使用 {required} agent，"
            f"但选择了 {selected_agent}。"
        )

        if fallbacks:
            error_msg += f" 可接受的备选: {', '.join(fallbacks)}"

        return False, error_msg

    def suggest_correction(
        self,
        task: str,
        selected_agent: str,
        context: Dict = None
    ) -> Optional[str]:
        """
        建议如何修正 agent 选择

        Args:
            task: 任务描述
            selected_agent: 选择的 agent
            context: 额外上下文

        Returns:
            修正建议，如果不需要修正则返回 None
        """
        is_valid, error_msg = self.validate_agent_usage(task, selected_agent, context)

        if is_valid:
            return None

        rule_info = self.check_task(task, context)
        if rule_info:
            return (
                f"[强制规则] {rule_info['description']}\n"
                f"建议使用: {rule_info['required_agent']}\n"
                f"{error_msg}"
            )

        return error_msg

    def get_enforcement_stats(self) -> Dict:
        """获取强制执行统计"""
        if not self.enforcement_history:
            return {
                'total_enforcements': 0,
                'agent_counts': {},
                'rule_counts': {}
            }

        agent_counts = {}
        rule_counts = {}

        for record in self.enforcement_history:
            agent = record['required_agent']
            rule = record['rule']

            agent_counts[agent] = agent_counts.get(agent, 0) + 1
            rule_counts[rule] = rule_counts.get(rule, 0) + 1

        return {
            'total_enforcements': len(self.enforcement_history),
            'agent_counts': agent_counts,
            'rule_counts': rule_counts,
            'recent_enforcements': self.enforcement_history[-10:]
        }

    def add_custom_rule(
        self,
        name: str,
        pattern: str,
        required_agent: str,
        priority: int = 5,
        auto_trigger: bool = False,
        fallback_agents: List[str] = None
    ):
        """
        添加自定义规则

        Args:
            name: 规则名称
            pattern: 正则表达式模式
            required_agent: 要求的 agent
            priority: 优先级 (1-10)
            auto_trigger: 是否自动触发
            fallback_agents: 备选 agent 列表
        """
        rule = EnforcementRule(
            name=name,
            description=f"自定义规则: {name}",
            pattern=pattern,
            required_agent=required_agent,
            priority=priority,
            auto_trigger=auto_trigger,
            fallback_agents=fallback_agents or []
        )

        self.rules.append(rule)

    def remove_rule(self, rule_name: str) -> bool:
        """
        移除规则

        Args:
            rule_name: 规则名称

        Returns:
            是否成功移除
        """
        for i, rule in enumerate(self.rules):
            if rule.name == rule_name:
                self.rules.pop(i)
                return True
        return False

    def list_rules(self) -> List[Dict]:
        """列出所有规则"""
        return [
            {
                'name': rule.name,
                'description': rule.description,
                'required_agent': rule.required_agent,
                'priority': rule.priority,
                'auto_trigger': rule.auto_trigger,
                'fallback_agents': rule.fallback_agents
            }
            for rule in sorted(self.rules, key=lambda r: r.priority, reverse=True)
        ]


# 全局单例
_instance = None


def get_agent_enforcer() -> AgentEnforcer:
    """获取 Agent 强制管理器单例"""
    global _instance
    if _instance is None:
        _instance = AgentEnforcer()
    return _instance


# 命令行测试
if __name__ == "__main__":
    import sys

    enforcer = get_agent_enforcer()

    print("=" * 70)
    print("Agent 强制参与系统测试")
    print("=" * 70)

    # 测试用例
    test_cases = [
        ("检查 SQL 注入漏洞", "security-reviewer"),
        ("为 API 编写单元测试", "tdd-guide"),
        ("设计用户认证系统架构", "architect"),
        ("审查 Python 代码质量", "python-reviewer"),
        ("更新 README 文档", "doc-writer"),
        ("重构订单处理模块", "planner"),
        # 错误选择
        ("检查 SQL 注入漏洞", "code-reviewer"),
        ("为 API 编写单元测试", "code-reviewer"),
    ]

    print("\n[测试] 验证 agent 选择:\n")

    for task, agent in test_cases:
        is_valid, error_msg = enforcer.validate_agent_usage(task, agent)

        if is_valid:
            print(f"[OK] '{task[:40]}...' -> {agent}")
        else:
            print(f"[FAIL] '{task[:40]}...' -> {agent}")
            print(f"       {error_msg}")

    # 检查强制规则
    print("\n[测试] 检查任务是否需要强制 agent:\n")

    test_tasks = [
        "检查 XSS 漏洞",
        "编写集成测试",
        "设计微服务架构",
        "更新 API 文档"
    ]

    for task in test_tasks:
        should_force, rule_info = enforcer.should_force_agent(task)

        if should_force:
            print(f"[FORCE] '{task}'")
            print(f"         -> {rule_info['required_agent']} (自动触发)")
        elif rule_info:
            print(f"[SUGGEST] '{task}'")
            print(f"           -> {rule_info['required_agent']} (建议)")
        else:
            print(f"[NONE] '{task}'")
            print(f"        -> 无强制要求")

    # 统计信息
    print("\n[测试] 强制规则列表:\n")

    rules = enforcer.list_rules()
    for i, rule in enumerate(rules, 1):
        auto_mark = "[AUTO]" if rule['auto_trigger'] else ""
        print(f"{i}. {rule['name']} {auto_mark}")
        print(f"   Agent: {rule['required_agent']}")
        print(f"   优先级: {rule['priority']}")
        print(f"   描述: {rule['description']}")
        print()

    print("=" * 70)
