#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Agent优先级评估工具

评估缺失记忆的Agent，决定是否需要创建记忆系统
"""

from pathlib import Path

# 8个缺失记忆的Agent
MISSING_AGENTS = {
    # 语言专用审查员（3个）
    'python_reviewer': {
        'category': 'language_reviewer',
        'priority': 'HIGH',
        'importance': 8,
        'reason': 'Python是最常用的语言，需要专业的审查模式',
        'suggested_patterns': ['类型注解检查', 'PEP8规范', 'Django/Flask最佳实践', '异步编程陷阱']
    },
    'go_reviewer': {
        'category': 'language_reviewer',
        'priority': 'MEDIUM',
        'importance': 6,
        'reason': 'Go用于微服务，需要并发和错误处理模式',
        'suggested_patterns': ['Goroutine泄漏检测', '错误处理最佳实践', 'Context使用模式', '接口设计原则']
    },
    'kotlin_reviewer': {
        'category': 'language_reviewer',
        'priority': 'LOW',
        'importance': 4,
        'reason': 'Kotlin使用场景较少，优先级较低',
        'suggested_patterns': ['空安全', '协程使用', 'Android最佳实践']
    },

    # 数据库审查员（1个）
    'database_reviewer': {
        'category': 'specialist',
        'priority': 'HIGH',
        'importance': 7,
        'reason': '数据库是应用核心，需要专业的优化模式',
        'suggested_patterns': ['SQL查询优化', '索引策略', '事务处理', 'ORM最佳实践', '分库分表']
    },

    # 测试相关（2个）
    'tdd_guide': {
        'category': 'testing',
        'priority': 'MEDIUM',
        'importance': 6,
        'reason': 'TDD是开发流程的一部分，但已有planner覆盖',
        'suggested_patterns': ['RED-GREEN-REFACTOR循环', '测试驱动步骤', '单元测试优先级']
    },
    'test_coverage': {
        'category': 'testing',
        'priority': 'LOW',
        'importance': 4,
        'reason': '测试覆盖率工具使用，不需要复杂记忆',
        'suggested_patterns': ['覆盖率阈值', '测试盲区识别']
    },
    'e2e_runner': {
        'category': 'testing',
        'priority': 'MEDIUM',
        'importance': 5,
        'reason': 'E2E测试需要Playwright/Selenium模式',
        'suggested_patterns': ['Page Object模式', '等待策略', '定位器稳定性', '测试数据管理']
    },

    # 代码清理（1个）
    'refactor_cleaner': {
        'category': 'quality',
        'priority': 'LOW',
        'importance': 3,
        'reason': '重构工具，主要使用knip等外部工具',
        'suggested_patterns': ['死代码识别', '重构优先级', '安全重构']
    },

    # 文档更新（1个）
    'doc_updater': {
        'category': 'documentation',
        'priority': 'LOW',
        'importance': 2,
        'reason': 'doc_writer已覆盖文档编写，无需重复',
        'suggested_patterns': ['文档同步策略', 'API文档生成']
    },

    # 完成前验证（1个）
    'verification_before_completion': {
        'category': 'quality',
        'priority': 'MEDIUM',
        'importance': 5,
        'reason': '完成前检查清单，保证代码质量',
        'suggested_patterns': ['安全检查', '性能验证', '测试覆盖', '文档完整性']
    }
}


def evaluate_priority():
    """评估Agent优先级"""

    print("\n" + "="*70)
    print("Agent优先级评估报告")
    print("="*70)

    # 按优先级分组
    high_priority = []
    medium_priority = []
    low_priority = []

    for agent_name, info in MISSING_AGENTS.items():
        item = {
            'name': agent_name,
            'category': info['category'],
            'importance': info['importance'],
            'reason': info['reason']
        }

        if info['priority'] == 'HIGH':
            high_priority.append(item)
        elif info['priority'] == 'MEDIUM':
            medium_priority.append(item)
        else:
            low_priority.append(item)

    # 打印结果
    print(f"\nHIGH PRIORITY (强烈建议创建): {len(high_priority)}个")
    print("-" * 70)
    for item in sorted(high_priority, key=lambda x: -x['importance']):
        print(f"  - {item['name']:<30} (重要性: {item['importance']}/10)")
        print(f"    原因: {item['reason']}")
        print(f"    类别: {item['category']}")

    print(f"\nMEDIUM PRIORITY (可选创建): {len(medium_priority)}个")
    print("-" * 70)
    for item in sorted(medium_priority, key=lambda x: -x['importance']):
        print(f"  - {item['name']:<30} (重要性: {item['importance']}/10)")
        print(f"    原因: {item['reason']}")

    print(f"\nLOW PRIORITY (暂不需要): {len(low_priority)}个")
    print("-" * 70)
    for item in sorted(low_priority, key=lambda x: -x['importance']):
        print(f"  - {item['name']:<30} (重要性: {item['importance']}/10)")
        print(f"    原因: {item['reason']}")

    # 建议
    print("\n" + "="*70)
    print("建议")
    print("="*70)
    print("""
1. 立即创建 HIGH PRIORITY Agent的记忆系统：
   - python_reviewer (Python最常用)
   - database_reviewer (数据库核心)

2. 按需创建 MEDIUM PRIORITY：
   - 当项目使用Go时创建 go_reviewer
   - 当需要E2E测试时创建 e2e_runner

3. 暂缓创建 LOW PRIORITY：
   - kotlin_reviewer (使用场景少)
   - refactor_cleaner (已有外部工具)
   - doc_updater (doc_writer已覆盖)
    """)

    return {
        'high': high_priority,
        'medium': medium_priority,
        'low': low_priority
    }


if __name__ == "__main__":
    result = evaluate_priority()
