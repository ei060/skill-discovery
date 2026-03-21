#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI Roland 主动参与系统

让子Agent能够主动分析指令并提供建议
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import re

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

from agent_communication import get_collaboration_hub, AgentCapability, AgentMessage
from agent_memory import get_agent_memory_manager


class ActiveParticipationEngine:
    """主动参与引擎 - 让子Agent能够主动介入"""

    def __init__(self, workspace: Optional[Path] = None):
        if workspace is None:
            workspace = Path(__file__).parent.parent.parent

        self.workspace = Path(workspace)
        self.collab_hub = get_collaboration_hub()
        self.memory_mgr = get_agent_memory_manager()

        # 能力-关键词映射
        self.capability_keywords = {
            'code_reviewer': {
                'keywords': ['审查', 'review', '代码质量', 'bug', '安全', '优化', '重构'],
                'trigger_threshold': 2  # 匹配2个关键词就触发
            },
            'planner': {
                'keywords': ['计划', 'plan', '设计', '架构', '方案', '流程', '任务分解', '开发'],
                'trigger_threshold': 2
            },
            'architect': {
                'keywords': ['架构', '设计', '系统', '模块', '接口', 'api', '技术选型', '功能', '开发'],
                'trigger_threshold': 1  # 降低阈值，更容易触发
            },
            'security_reviewer': {
                'keywords': ['安全', '漏洞', '注入', 'XSS', 'CSRF', '加密', '认证'],
                'trigger_threshold': 1  # 安全问题优先级高
            },
            'tdd_guide': {
                'keywords': ['测试', 'test', 'TDD', '覆盖', '用例', '测试驱动'],
                'trigger_threshold': 2
            },
            'python_reviewer': {
                'keywords': ['python', 'django', 'flask', 'fastapi', 'pep8'],
                'trigger_threshold': 2
            },
            'database_reviewer': {
                'keywords': ['数据库', 'database', 'sql', '查询', '索引', '优化', 'migration'],
                'trigger_threshold': 2
            },
            'doc_writer': {
                'keywords': ['文档', 'documentation', 'readme', '说明', '注释'],
                'trigger_threshold': 2
            },
            'refactor_cleaner': {
                'keywords': ['清理', '删除', '未使用', 'dead code', '重构'],
                'trigger_threshold': 2
            },
            'e2e_runner': {
                'keywords': ['e2e', '端到端', '集成', '测试流程', '用户流程'],
                'trigger_threshold': 2
            }
        }

    def analyze_user_input(self, user_input: str) -> List[Dict]:
        """分析用户输入，返回应该参与的Agent列表"""

        results = []

        for agent_name, config in self.capability_keywords.items():
            # 计算关键词匹配分数
            matched_keywords = []
            for keyword in config['keywords']:
                if keyword.lower() in user_input.lower():
                    matched_keywords.append(keyword)

            match_count = len(matched_keywords)

            # 如果达到阈值，触发建议
            if match_count >= config['trigger_threshold']:
                # 获取Agent能力信息
                cap = self.collab_hub.capabilities.get(agent_name)
                if not cap:
                    continue

                # 计算优先级分数
                priority_score = self._calculate_priority_score(
                    agent_name,
                    matched_keywords,
                    user_input
                )

                results.append({
                    'agent_name': agent_name,
                    'agent_type': cap.agent_type,
                    'matched_keywords': matched_keywords,
                    'match_count': match_count,
                    'priority_score': priority_score,
                    'suggestion': self._generate_suggestion(agent_name, matched_keywords)
                })

        # 按优先级排序
        results.sort(key=lambda x: x['priority_score'], reverse=True)

        return results

    def _calculate_priority_score(
        self,
        agent_name: str,
        matched_keywords: List[str],
        user_input: str
    ) -> float:
        """计算优先级分数（0-100）"""

        score = 0.0

        # 基础分：关键词匹配数量
        score += len(matched_keywords) * 20

        # 加分：特殊关键词
        high_priority_keywords = ['安全', '漏洞', 'critical', 'urgent', '重要']
        if any(kw in user_input.lower() for kw in high_priority_keywords):
            score += 30

        # 加分：Agent历史成功率
        memory = self.memory_mgr.get_agent_memory(agent_name)
        success_rate = memory.stats.get('success_rate', 0.8)
        score += success_rate * 10

        # 加分：Agent最近活跃度
        if memory.stats.get('last_active'):
            last_active = memory.stats['last_active']
            # 如果最近活跃过，加分
            score += 10

        return min(score, 100)

    def _generate_suggestion(self, agent_name: str, matched_keywords: List[str]) -> str:
        """生成建议文本"""

        suggestions = {
            'code_reviewer': f"建议使用代码审查，发现潜在问题（检测到：{', '.join(matched_keywords)}）",
            'planner': f"建议先制定详细计划，避免遗漏（检测到：{', '.join(matched_keywords)}）",
            'architect': f"建议进行架构设计，确保可扩展性（检测到：{', '.join(matched_keywords)}）",
            'security_reviewer': f"⚠️ 安全警告！建议进行安全审查（检测到：{', '.join(matched_keywords)}）",
            'tdd_guide': f"建议采用TDD方法，先写测试（检测到：{', '.join(matched_keywords)}）",
            'python_reviewer': f"建议使用Python专家审查代码规范（检测到：{', '.join(matched_keywords)}）",
            'database_reviewer': f"建议审查数据库查询和设计（检测到：{', '.join(matched_keywords)}）",
            'doc_writer': f"建议更新文档，保持同步（检测到：{', '.join(matched_keywords)}）",
            'refactor_cleaner': f"建议清理代码，移除未使用部分（检测到：{', '.join(matched_keywords)}）",
            'e2e_runner': f"建议进行端到端测试验证（检测到：{', '.join(matched_keywords)}）"
        }

        return suggestions.get(agent_name, f"建议调用{agent_name}（检测到：{', '.join(matched_keywords)}）")

    def get_participation_report(self, user_input: str) -> Dict:
        """生成参与报告"""

        suggested_agents = self.analyze_user_input(user_input)

        return {
            'user_input': user_input,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'total_suggestions': len(suggested_agents),
            'suggestions': suggested_agents,
            'recommendations': self._generate_recommendations(suggested_agents)
        }

    def _generate_recommendations(self, suggested_agents: List[Dict]) -> Dict:
        """生成具体建议"""

        if not suggested_agents:
            return {
                'should_use_agents': False,
                'message': '这是一个简单的任务，主Agent可以直接处理'
            }

        # 检查是否有高优先级Agent
        high_priority = [a for a in suggested_agents if a['priority_score'] >= 70]

        if high_priority:
            return {
                'should_use_agents': True,
                'priority': 'high',
                'message': f'建议使用 {len(high_priority)} 个高优先级Agent',
                'agents': [a['agent_name'] for a in high_priority],
                'workflow': self._suggest_workflow(high_priority)
            }

        # 中等优先级
        medium_priority = [a for a in suggested_agents if a['priority_score'] >= 40]

        if medium_priority:
            return {
                'should_use_agents': True,
                'priority': 'medium',
                'message': f'可以使用 {len(medium_priority)} 个Agent辅助',
                'agents': [a['agent_name'] for a in medium_priority],
                'workflow': self._suggest_workflow(medium_priority)
            }

        return {
            'should_use_agents': True,
            'priority': 'low',
            'message': f'有 {len(suggested_agents)} 个Agent可以提供帮助',
            'agents': [a['agent_name'] for a in suggested_agents[:3]],
            'workflow': 'optional'
        }

    def _suggest_workflow(self, agents: List[Dict]) -> str:
        """建议工作流程"""

        agent_names = [a['agent_name'] for a in agents]

        # 特殊组合
        if 'planner' in agent_names and 'architect' in agent_names:
            return 'planner → architect → implementation → review'

        if 'tdd_guide' in agent_names and 'code_reviewer' in agent_names:
            return 'tdd_guide → implementation → code_reviewer'

        # 默认流程
        if len(agent_names) == 1:
            return f'use {agent_names[0]}'

        return ' → '.join(agent_names[:3])


def get_active_participation_engine() -> ActiveParticipationEngine:
    """获取主动参与引擎单例"""
    # 每次都创建新实例，避免状态污染
    return ActiveParticipationEngine()


# 测试
if __name__ == "__main__":
    print("\n" + "="*70)
    print("AI Roland 主动参与系统测试")
    print("="*70)

    engine = get_active_participation_engine()

    # 测试1：代码审查场景
    print("\n1. 测试：代码审查场景")
    test_input_1 = "请帮我审查这段用户认证代码，看看有没有安全问题"
    report_1 = engine.get_participation_report(test_input_1)

    print(f"  输入: {test_input_1}")
    print(f"  建议数量: {report_1['total_suggestions']}")
    print(f"  推荐结果:")
    print(f"    是否使用Agent: {report_1['recommendations']['should_use_agents']}")
    print(f"    优先级: {report_1['recommendations'].get('priority', 'N/A')}")
    print(f"    消息: {report_1['recommendations']['message']}")
    if report_1['suggestions']:
        print(f"  详细建议:")
        for sug in report_1['suggestions'][:3]:
            print(f"    - {sug['agent_name']}: {sug['suggestion']}")

    # 测试2：新功能开发
    print("\n2. 测试：新功能开发场景")
    test_input_2 = "我要开发一个新的API接口，需要设计数据库schema和实现逻辑"
    report_2 = engine.get_participation_report(test_input_2)

    print(f"  输入: {test_input_2}")
    print(f"  建议数量: {report_2['total_suggestions']}")
    print(f"  推荐结果:")
    print(f"    是否使用Agent: {report_2['recommendations']['should_use_agents']}")
    print(f"    优先级: {report_2['recommendations'].get('priority', 'N/A')}")
    print(f"    消息: {report_2['recommendations']['message']}")
    if report_2['suggestions']:
        print(f"  详细建议:")
        for sug in report_2['suggestions'][:3]:
            print(f"    - {sug['agent_name']}: {sug['suggestion']}")

    # 测试3：简单任务
    print("\n3. 测试：简单任务场景")
    test_input_3 = "帮我读取一下config.yaml文件的内容"
    report_3 = engine.get_participation_report(test_input_3)

    print(f"  输入: {test_input_3}")
    print(f"  建议数量: {report_3['total_suggestions']}")
    print(f"  推荐结果:")
    print(f"    消息: {report_3['recommendations']['message']}")

    print("\n✓ 测试完成")
