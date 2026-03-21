#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能 Agent 建议系统

自动分析任务类型并推荐最合适的 agent，减少手动调用的依赖
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timezone


class AgentSuggester:
    """智能 Agent 建议器"""

    def __init__(self):
        self.workspace = Path(__file__).parent.parent.parent

        # Agent 能力定义
        self.agent_capabilities = {
            'planner': {
                'name': 'planner',
                'description': '规划和设计专家',
                'model': 'opus',
                'keywords': [
                    '规划', '设计', '重构', '实现', '计划', '架构',
                    'plan', 'design', 'refactor', 'implement', 'architecture',
                    '分解', '步骤', '流程', '方案', '策略'
                ],
                'patterns': [
                    r'如何.*实现',
                    r'.*的(设计|架构|方案)',
                    r'(制定|创建).*计划',
                    r'(重构|优化).*系统',
                    r'任务.*分解'
                ],
                'priority': 10  # 优先级（高优先级先推荐）
            },

            'architect': {
                'name': 'architect',
                'description': '软件架构专家',
                'model': 'opus',
                'keywords': [
                    '架构', '系统设计', '可扩展', '技术决策', '设计模式',
                    'architecture', 'scalable', 'design pattern', 'technical decision',
                    '模块化', '耦合', '接口', '组件'
                ],
                'patterns': [
                    r'(系统|软件).*架构',
                    r'(技术|架构)决策',
                    r'设计.*模式',
                    r'(可扩展|扩展性)',
                    r'模块.*设计'
                ],
                'priority': 9
            },

            'code-reviewer': {
                'name': 'code-reviewer',
                'description': '代码审查专家',
                'model': 'sonnet',
                'keywords': [
                    '审查', 'review', '代码质量', 'bug', '优化',
                    'review', 'code quality', 'optimize', 'refactor',
                    '代码.*问题', '改进.*代码'
                ],
                'patterns': [
                    r'(审查|review).*代码',
                    r'代码.*质量',
                    r'(检查|分析).*代码',
                    r'(优化|改进).*实现',
                    r'代码.*建议'
                ],
                'priority': 8
            },

            'security-reviewer': {
                'name': 'security-reviewer',
                'description': '安全审查专家',
                'model': 'sonnet',
                'keywords': [
                    '安全', '漏洞', '攻击', '权限', '认证',
                    'security', 'vulnerability', 'attack', 'permission', 'auth',
                    '注入', 'xss', 'csrf', '加密'
                ],
                'patterns': [
                    r'(安全|security).*审查',
                    r'(检查|测试).*安全',
                    r'(漏洞|vulnerability)',
                    r'(权限|认证|授权)',
                    r'(注入|injection)'
                ],
                'priority': 10  # 安全相关优先级最高
            },

            'tdd-guide': {
                'name': 'tdd-guide',
                'description': '测试驱动开发专家',
                'model': 'sonnet',
                'keywords': [
                    '测试', 'test', 'tdd', '单元测试', '覆盖',
                    'test case', 'coverage', 'mock', 'fixture',
                    '测试.*驱动', '先写.*测试'
                ],
                'patterns': [
                    r'(写|创建).*测试',
                    r'tdd.*开发',
                    r'(单元|集成).*测试',
                    r'测试.*覆盖',
                    r'(mock|stub|fixture)'
                ],
                'priority': 7
            },

            'python-reviewer': {
                'name': 'python-reviewer',
                'description': 'Python 代码审查专家',
                'model': 'sonnet',
                'keywords': [
                    'python', 'py', 'django', 'flask', 'fastapi',
                    'pep', 'pythonic', 'python代码'
                ],
                'patterns': [
                    r'python.*代码',
                    r'(django|flask|fastapi)',
                    r'pep.*8'
                ],
                'priority': 6,
                'language_specific': True
            },

            'go-reviewer': {
                'name': 'go-reviewer',
                'description': 'Go 代码审查专家',
                'model': 'sonnet',
                'keywords': [
                    'go', 'golang', 'goroutine', 'channel',
                    'go代码', 'go语言'
                ],
                'patterns': [
                    r'go.*代码',
                    r'golang.*',
                    r'goroutine.*'
                ],
                'priority': 6,
                'language_specific': True
            },

            'doc-writer': {
                'name': 'doc-writer',
                'description': '文档写作专家',
                'model': 'sonnet',
                'keywords': [
                    '文档', 'doc', 'readme', '指南', '说明',
                    'documentation', 'guide', 'manual', 'tutorial',
                    'api文档', '使用说明'
                ],
                'patterns': [
                    r'(写|创建).*文档',
                    r'(更新|修改).*readme',
                    r'(使用|开发).*指南',
                    r'api.*文档'
                ],
                'priority': 5
            },

            'e2e-runner': {
                'name': 'e2e-runner',
                'description': '端到端测试专家',
                'model': 'sonnet',
                'keywords': [
                    'e2e', '端到端', '集成测试', '用户流程',
                    'end-to-end', 'integration test', 'user flow'
                ],
                'patterns': [
                    r'e2e.*测试',
                    r'(端到端|end.*end)',
                    r'(用户流程|user flow).*测试'
                ],
                'priority': 6
            }
        }

        # 统计信息
        self.stats = {
            'total_suggestions': 0,
            'agent_suggestion_counts': {},
            'last_suggestion_time': None
        }

    def analyze_task(self, task: str, context: Dict = None) -> List[Dict]:
        """
        分析任务并返回推荐的 agent 列表

        Args:
            task: 任务描述
            context: 额外上下文信息

        Returns:
            推荐的 agent 列表，按匹配度排序
        """
        self.stats['total_suggestions'] += 1

        task_lower = task.lower()
        context = context or {}

        scores = []

        # 计算每个 agent 的匹配分数
        for agent_name, agent_config in self.agent_capabilities.items():
            score = self._calculate_match_score(
                task_lower,
                agent_config,
                context
            )

            if score > 0:
                scores.append({
                    'agent': agent_name,
                    'score': score,
                    'description': agent_config['description'],
                    'model': agent_config['model'],
                    'reason': self._generate_reason(agent_config, task)
                })

        # 按分数排序
        scores.sort(key=lambda x: x['score'], reverse=True)

        # 更新统计
        if scores:
            top_agent = scores[0]['agent']
            self.stats['agent_suggestion_counts'][top_agent] = \
                self.stats['agent_suggestion_counts'].get(top_agent, 0) + 1

        self.stats['last_suggestion_time'] = datetime.now(timezone.utc).isoformat()

        return scores

    def _calculate_match_score(
        self,
        task_lower: str,
        agent_config: Dict,
        context: Dict
    ) -> float:
        """计算 agent 与任务的匹配分数"""

        score = 0.0

        # 1. 关键词匹配（每个关键词 10 分）
        keyword_matches = sum(
            1 for kw in agent_config['keywords']
            if kw.lower() in task_lower
        )
        score += keyword_matches * 10

        # 2. 模式匹配（每个匹配模式 20 分）
        pattern_matches = 0
        for pattern in agent_config.get('patterns', []):
            if re.search(pattern, task_lower, re.IGNORECASE):
                pattern_matches += 1
        score += pattern_matches * 20

        # 3. 优先级加权（优先级越高，加分越多）
        priority_bonus = agent_config.get('priority', 5) * 2
        score += priority_bonus

        # 4. 语言特定加分（如果上下文包含语言信息）
        if agent_config.get('language_specific'):
            language = context.get('language', '')
            if language and language.lower() in agent_config['name']:
                score += 30

        # 5. 文件类型匹配（如果上下文包含文件路径）
        file_extensions = context.get('file_extensions', [])
        if file_extensions:
            ext_bonus = self._check_file_extension_match(
                agent_config['name'],
                file_extensions
            )
            score += ext_bonus

        return score

    def _check_file_extension_match(
        self,
        agent_name: str,
        extensions: List[str]
    ) -> float:
        """检查文件扩展名与 agent 的匹配度"""

        extension_map = {
            'python-reviewer': ['.py'],
            'go-reviewer': ['.go'],
            'code-reviewer': ['.js', '.ts', '.py', '.go', '.java'],
            'security-reviewer': ['.py', '.js', '.php']  # 安全审查适用多种语言
        }

        agent_extensions = extension_map.get(agent_name, [])
        if any(ext in agent_extensions for ext in extensions):
            return 15  # 匹配加分

        return 0

    def _generate_reason(self, agent_config: Dict, task: str) -> str:
        """生成推荐理由"""

        reasons = []

        # 基于关键词的理由
        matched_keywords = [
            kw for kw in agent_config['keywords']
            if kw.lower() in task.lower()
        ]

        if matched_keywords:
            reasons.append(f"匹配关键词: {', '.join(matched_keywords[:3])}")

        # 基于模式的理由
        for pattern in agent_config.get('patterns', []):
            if re.search(pattern, task, re.IGNORECASE):
                reasons.append(f"匹配模式: {pattern[:30]}...")
                break

        # 基于优先级的理由
        priority = agent_config.get('priority', 5)
        if priority >= 9:
            reasons.append(f"高优先级任务类型")

        return " | ".join(reasons) if reasons else "综合评估推荐"

    def get_top_suggestion(self, task: str, context: Dict = None) -> Optional[Dict]:
        """
        获取最佳推荐（简化版）

        Args:
            task: 任务描述
            context: 额外上下文

        Returns:
            最佳推荐，如果没有合适的则返回 None
        """
        suggestions = self.analyze_task(task, context)

        if not suggestions:
            return None

        # 只返回分数最高的，且分数 >= 30 的推荐
        if suggestions[0]['score'] >= 30:
            return suggestions[0]

        return None

    def should_auto_trigger(self, task: str, context: Dict = None) -> Tuple[bool, Optional[Dict]]:
        """
        判断是否应该自动触发 agent

        Args:
            task: 任务描述
            context: 额外上下文

        Returns:
            (是否自动触发, 推荐的 agent)
        """
        suggestion = self.get_top_suggestion(task, context)

        if not suggestion:
            return False, None

        # 高优先级任务自动触发（分数 >= 50）
        if suggestion['score'] >= 50:
            return True, suggestion

        # 安全相关任务自动触发
        if suggestion['agent'] == 'security-reviewer':
            return True, suggestion

        # 规划任务自动触发
        if suggestion['agent'] == 'planner' and suggestion['score'] >= 40:
            return True, suggestion

        return False, suggestion

    def format_suggestion_message(self, suggestions: List[Dict]) -> str:
        """格式化建议消息"""

        if not suggestions:
            return "未找到合适的 agent，建议使用通用实现方式。"

        lines = [
            "\n[AI] 智能 Agent 建议\n",
            f"分析完成，找到 {len(suggestions)} 个合适的 agent:\n"
        ]

        for i, suggestion in enumerate(suggestions[:3], 1):  # 只显示前 3 个
            lines.append(f"{i}. {suggestion['agent']} "
                        f"(分数: {suggestion['score']})")
            lines.append(f"   - 描述: {suggestion['description']}")
            lines.append(f"   - 模型: {suggestion['model']}")
            lines.append(f"   - 理由: {suggestion['reason']}")
            lines.append("")

        # 如果第一个建议的分数很高，提示可以自动触发
        if suggestions[0]['score'] >= 50:
            lines.append(f"[提示] {suggestions[0]['agent']} 匹配度很高，"
                        f"建议优先使用！")

        return "\n".join(lines)

    def get_stats(self) -> Dict:
        """获取统计信息"""
        return self.stats.copy()

    def save_stats(self):
        """保存统计信息"""
        stats_file = self.workspace / 'system' / 'agents' / 'suggester_stats.json'

        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)


# 全局单例
_instance = None


def get_agent_suggester() -> AgentSuggester:
    """获取 Agent 建议器单例"""
    global _instance
    if _instance is None:
        _instance = AgentSuggester()
    return _instance


# 命令行测试
if __name__ == "__main__":
    import sys

    suggester = get_agent_suggester()

    # 测试用例
    test_tasks = [
        "设计一个用户认证系统的架构",
        "审查这段 Python 代码的安全性",
        "为 API 接口编写单元测试",
        "创建项目的 README 文档",
        "重构订单处理模块",
        "检查 SQL 注入漏洞"
    ]

    print("=" * 70)
    print("智能 Agent 建议系统测试")
    print("=" * 70)

    for task in test_tasks:
        print(f"\n[任务] {task}")
        print("-" * 70)

        suggestions = suggester.analyze_task(task)

        if suggestions:
            print(f"[OK] 找到 {len(suggestions)} 个推荐:")
            for i, sugg in enumerate(suggestions[:3], 1):
                print(f"  {i}. {sugg['agent']} (分数: {sugg['score']})")
                print(f"     {sugg['reason']}")

            # 检查是否应该自动触发
            should_auto, top_sugg = suggester.should_auto_trigger(task)
            if should_auto:
                print(f"  [AUTO] 建议自动触发: {top_sugg['agent']}")
        else:
            print("  [WARN] 未找到合适的 agent")

    print("\n" + "=" * 70)
    print("统计信息:")
    stats = suggester.get_stats()
    print(f"  总建议次数: {stats['total_suggestions']}")
    print(f"  Agent 推荐次数: {stats['agent_suggestion_counts']}")
    print("=" * 70)
