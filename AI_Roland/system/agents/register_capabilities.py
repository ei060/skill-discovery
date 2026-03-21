#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Agent能力注册脚本

为所有Agent注册专业能力和协作信息
"""

import sys
import os
from pathlib import Path

# 添加系统路径
system_path = Path(__file__).parent
sys.path.insert(0, str(system_path))

from agent_communication import (
    CollaborationHub,
    AgentCapability,
    get_collaboration_hub
)


# 所有Agent的能力配置
AGENT_CAPABILITIES = {
    # 原有的6个Agent
    'architect': {
        'agent_type': 'design',
        'expertise': [
            'system_architecture', 'microservices', 'api_design',
            'database_design', 'scalability', 'design_patterns'
        ],
        'capabilities': [
            'architecture_review', 'tech_stack_selection', 'system_design',
            'component_design', 'api_design', 'data_modeling'
        ],
        'skill_level': 90
    },

    'planner': {
        'agent_type': 'planning',
        'expertise': [
            'project_planning', 'task_breakdown', 'risk_assessment',
            'dependency_analysis', 'resource_planning'
        ],
        'capabilities': [
            'create_plan', 'estimate_effort', 'identify_risks',
            'define_milestones', 'task_prioritization'
        ],
        'skill_level': 88
    },

    'code_reviewer': {
        'agent_type': 'review',
        'expertise': [
            'code_quality', 'best_practices', 'clean_code',
            'refactoring', 'design_patterns'
        ],
        'capabilities': [
            'code_review', 'quality_assessment', 'bug_detection',
            'performance_review', 'maintainability_check'
        ],
        'skill_level': 85
    },

    'security_reviewer': {
        'agent_type': 'security',
        'expertise': [
            'owasp_top10', 'sql_injection', 'xss_prevention',
            'authentication', 'authorization', 'cryptography'
        ],
        'capabilities': [
            'security_audit', 'vulnerability_scan', 'penetration_testing',
            'security_review', 'compliance_check'
        ],
        'skill_level': 92
    },

    'doc_writer': {
        'agent_type': 'documentation',
        'expertise': [
            'technical_writing', 'api_docs', 'user_guides',
            'readme', 'architecture_docs'
        ],
        'capabilities': [
            'write_docs', 'review_docs', 'doc_structure',
            'api_documentation', 'tutorials'
        ],
        'skill_level': 82
    },

    'engineer': {
        'agent_type': 'implementation',
        'expertise': [
            'programming', 'debugging', 'testing',
            'optimization', 'deployment'
        ],
        'capabilities': [
            'implement_feature', 'fix_bug', 'optimize_code',
            'write_tests', 'code_refactoring'
        ],
        'skill_level': 87
    },

    # 新增的8个Agent
    'python_reviewer': {
        'agent_type': 'language_reviewer',
        'expertise': [
            'python', 'django', 'flask', 'asyncio',
            'type_hints', 'pep8', 'pytest'
        ],
        'capabilities': [
            'python_review', 'django_review', 'flask_review',
            'async_review', 'type_check', 'pep8_check'
        ],
        'skill_level': 85
    },

    'database_reviewer': {
        'agent_type': 'specialist',
        'expertise': [
            'sql', 'postgresql', 'mysql', 'mongodb',
            'query_optimization', 'indexing', 'schema_design'
        ],
        'capabilities': [
            'query_review', 'index_optimization', 'schema_review',
            'performance_tuning', 'migration_plan'
        ],
        'skill_level': 90
    },

    'tdd_guide': {
        'agent_type': 'testing',
        'expertise': [
            'tdd', 'unit_testing', 'test_design',
            'red_green_refactor', 'coverage'
        ],
        'capabilities': [
            'tdd_guidance', 'test_design', 'coverage_analysis',
            'test_refactoring', 'testing_strategy'
        ],
        'skill_level': 80
    },

    'e2e_runner': {
        'agent_type': 'testing',
        'expertise': [
            'playwright', 'selenium', 'cypress',
            'page_object', 'test_automation', 'browser_testing'
        ],
        'capabilities': [
            'e2e_test_design', 'test_automation', 'page_object_model',
            'test_stability', 'browser_automation'
        ],
        'skill_level': 78
    },

    'verification_before_completion': {
        'agent_type': 'quality',
        'expertise': [
            'quality_assurance', 'checklist', 'verification',
            'security_check', 'performance_check'
        ],
        'capabilities': [
            'pre_completion_check', 'security_verification',
            'performance_check', 'documentation_check'
        ],
        'skill_level': 83
    },

    'go_reviewer': {
        'agent_type': 'language_reviewer',
        'expertise': [
            'go', 'golang', 'goroutines', 'channels',
            'context', 'error_handling', 'interfaces'
        ],
        'capabilities': [
            'go_review', 'concurrency_review', 'error_handling_check',
            'interface_design', 'goroutine_leak_detection'
        ],
        'skill_level': 82
    },

    'kotlin_reviewer': {
        'agent_type': 'language_reviewer',
        'expertise': [
            'kotlin', 'android', 'coroutines',
            'null_safety', 'jetpack_compose'
        ],
        'capabilities': [
            'kotlin_review', 'android_review', 'coroutine_review',
            'null_safety_check', 'compose_review'
        ],
        'skill_level': 75
    },

    'refactor_cleaner': {
        'agent_type': 'quality',
        'expertise': [
            'refactoring', 'dead_code', 'code_cleanup',
            'knip', 'dependency_analysis'
        ],
        'capabilities': [
            'dead_code_detection', 'refactor_plan',
            'dependency_cleanup', 'code_simplification'
        ],
        'skill_level': 76
    }
}


def register_all_agents():
    """注册所有Agent的能力"""

    print("\n" + "="*70)
    print("Agent能力注册")
    print("="*70)

    hub = get_collaboration_hub()

    registered = 0
    for agent_name, config in AGENT_CAPABILITIES.items():
        capability = AgentCapability(
            agent_name=agent_name,
            agent_type=config['agent_type'],
            expertise=config['expertise'],
            capabilities=config['capabilities'],
            skill_level=config['skill_level'],
            availability=1.0,  # 初始都是可用的
            current_load=0,
            max_capacity=10
        )

        hub.register_capability(capability)
        registered += 1

    print(f"\n✓ 成功注册 {registered} 个Agent")

    # 显示统计
    print("\n" + "="*70)
    print("能力注册表")
    print("="*70)

    stats = hub.get_statistics()

    print(f"\n注册的Agent ({stats['registered_agents']}个):")
    print(f"{'Agent':<30} {'类型':<20} {'技能':<10} {'能力数':<10}")
    print("-" * 70)

    for agent_name, agent_stat in stats['agent_stats'].items():
        cap = hub.capabilities[agent_name]
        print(f"{agent_name:<30} {agent_stat['type']:<20} "
              f"{agent_stat['skill_level']:<10} {len(cap.capabilities):<10}")

    return hub


def demonstrate_collaboration(hub):
    """演示协作功能"""

    print("\n" + "="*70)
    print("协作演示")
    print("="*70)

    # 场景1：code_reviewer遇到数据库问题，请求帮助
    print("\n场景1：code_reviewer遇到数据库问题")
    print("-" * 40)

    from agent_communication import AgentMessage

    help_request = AgentMessage(
        from_agent="code_reviewer",
        subject="需要数据库优化建议",
        content={
            "problem": "发现慢查询",
            "query": "SELECT * FROM users WHERE email = ?",
            "context": "用户表有100万行，查询耗时2秒",
            "expected": "希望优化到100ms以内"
        },
        required_capabilities=["query_review"],
        required_expertise=["sql", "optimization"],
        priority=8
    )

    if hub.send_message(help_request):
        print("✓ 协作请求已发送")

        # 查看匹配结果
        print(f"  → 系统自动匹配到: {help_request.to_agent}")
        print(f"  → 消息ID: {help_request.msg_id}")

    # 场景2：python_reviewer分享新经验
    print("\n场景2：python_reviewer分享异步编程经验")
    print("-" * 40)

    experience = {
        "title": "asyncio性能优化技巧",
        "category": "async_programming",
        "content": "使用asyncio.gather()并行执行多个协程，性能提升3倍",
        "example": """
# 错误做法（串行）
results = []
for task in tasks:
    result = await task
    results.append(result)

# 正确做法（并行）
results = await asyncio.gather(*tasks)
        """,
        "benefit": "性能提升3倍",
        "applicability": ["django", "fastapi", "aiohttp"]
    }

    sent_count = hub.broadcast_experience("python_reviewer", experience)
    print(f"✓ 经验已广播给 {sent_count} 个Agent")

    # 查看待处理消息
    print("\n当前待处理的协作请求:")
    print("-" * 40)

    for agent_name in ["database_reviewer", "python_reviewer", "go_reviewer"]:
        pending = hub.get_pending_messages(agent_name)
        if pending:
            print(f"\n{agent_name} 有 {len(pending)} 条待处理:")
            for msg in pending[:3]:  # 只显示前3条
                print(f"  - {msg.subject} (来自{msg.from_agent}, 优先级{msg.priority})")


def main():
    """主函数"""

    # 注册所有Agent
    hub = register_all_agents()

    # 演示协作
    demonstrate_collaboration(hub)

    # 最终统计
    print("\n" + "="*70)
    print("最终统计")
    print("="*70)

    stats = hub.get_statistics()
    print(f"\n注册Agent数: {stats['registered_agents']}")
    print(f"消息总数: {stats['total_messages']}")
    print(f"消息类型分布: {stats['by_type']}")
    print(f"匹配器统计: 平均匹配分数 {stats['matcher_stats'].get('avg_score', 0):.2f}")

    print("\n✓ Agent协作系统已就绪！")
    print("\n使用方法:")
    print("  from agent_communication import get_collaboration_hub, AgentMessage")
    print("  hub = get_collaboration_hub()")
    print("  hub.send_message(your_message)")


if __name__ == "__main__":
    main()
