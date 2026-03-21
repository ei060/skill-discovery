#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
初始化新Agent的独立记忆系统

为缺失记忆的高优先级Agent创建初始记忆文件
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime, timezone

# 添加系统路径
system_path = Path(__file__).parent
sys.path.insert(0, str(system_path))

from agent_memory import AgentMemoryManager, AgentMemory


# 新Agent配置（按优先级排序）
NEW_AGENTS_CONFIG = {
    # HIGH 优先级
    'python_reviewer': {
        'agent_type': 'language_reviewer',
        'priority': 'HIGH',
        'initial_patterns': [
            {
                'name': '类型注解检查',
                'description': '确保函数参数和返回值有类型注解',
                'example': 'def process_data(data: List[Dict]) -> Optional[Dict]:',
                'category': 'type_safety'
            },
            {
                'name': 'PEP8规范',
                'description': '遵循Python代码风格指南',
                'example': '使用flake8或black格式化代码',
                'category': 'style'
            },
            {
                'name': 'Django最佳实践',
                'description': 'Django项目结构和性能优化',
                'example': '使用select_related减少查询',
                'category': 'framework'
            },
            {
                'name': '异步编程陷阱',
                'description': 'async/await常见错误',
                'example': '避免在同步函数中直接调用async函数',
                'category': 'async'
            },
            {
                'name': 'Flask最佳实践',
                'description': 'Flask应用结构和蓝本',
                'example': '使用蓝本组织大型应用',
                'category': 'framework'
            }
        ],
        'preferences': {
            'strict_typing': True,
            'require_docstrings': True,
            'max_complexity': 10,
            'enforce_pep8': True
        }
    },

    'database_reviewer': {
        'agent_type': 'specialist',
        'priority': 'HIGH',
        'initial_patterns': [
            {
                'name': 'SQL查询优化',
                'description': '识别慢查询和优化建议',
                'example': '使用EXPLAIN ANALYZE分析查询计划',
                'category': 'performance'
            },
            {
                'name': '索引策略',
                'description': '何时创建索引以及索引类型选择',
                'example': '为WHERE和JOIN列创建B-tree索引',
                'category': 'design'
            },
            {
                'name': '事务处理',
                'description': '正确使用数据库事务',
                'example': '保持事务简短，避免长事务',
                'category': 'consistency'
            },
            {
                'name': 'ORM最佳实践',
                'description': 'SQLAlchemy/Django ORM使用规范',
                'example': '使用select_related和prefetch_related',
                'category': 'orm'
            },
            {
                'name': '分库分表',
                'description': '大规模数据库的拆分策略',
                'example': '按用户ID哈希分表',
                'category': 'scaling'
            }
        ],
        'preferences': {
            'require_indexes': True,
            'max_query_time': 1000,  # ms
            'enforce_transactions': True,
            'allow_n_plus_one': False
        }
    },

    # MEDIUM 优先级
    'tdd_guide': {
        'agent_type': 'testing',
        'priority': 'MEDIUM',
        'initial_patterns': [
            {
                'name': 'RED-GREEN-REFACTOR循环',
                'description': 'TDD核心开发流程',
                'example': '先写失败的测试，实现代码，再重构',
                'category': 'process'
            },
            {
                'name': '测试驱动步骤',
                'description': '如何从需求开始编写测试',
                'example': '先将需求转化为可测试的断言',
                'category': 'workflow'
            },
            {
                'name': '单元测试优先级',
                'description': '测试顺序和覆盖策略',
                'example': '先测试核心业务逻辑，再测试边界情况',
                'category': 'strategy'
            }
        ],
        'preferences': {
            'require_test_first': True,
            'min_coverage': 80,
            'enforce_red_green': True
        }
    },

    'e2e_runner': {
        'agent_type': 'testing',
        'priority': 'MEDIUM',
        'initial_patterns': [
            {
                'name': 'Page Object模式',
                'description': 'E2E测试的页面对象设计',
                'example': '将页面元素选择器封装在Page类中',
                'category': 'design'
            },
            {
                'name': '等待策略',
                'description': '处理异步加载的最佳实践',
                'example': '使用waitForSelector而非固定sleep',
                'category': 'stability'
            },
            {
                'name': '定位器稳定性',
                'description': '选择可靠的元素定位器',
                'example': '优先使用data-testid属性',
                'category': 'reliability'
            },
            {
                'name': '测试数据管理',
                'description': 'E2E测试的数据准备和清理',
                'example': '每个测试独立准备数据，测试后清理',
                'category': 'maintenance'
            }
        ],
        'preferences': {
            'use_page_objects': True,
            'default_timeout': 5000,
            'retry_failed': True,
            'cleanup_after_test': True
        }
    },

    'verification_before_completion': {
        'agent_type': 'quality',
        'priority': 'MEDIUM',
        'initial_patterns': [
            {
                'name': '安全检查',
                'description': '代码完成前的安全验证清单',
                'example': '检查SQL注入、XSS、CSRF等漏洞',
                'category': 'security'
            },
            {
                'name': '性能验证',
                'description': '确保代码满足性能要求',
                'example': '检查是否有N+1查询，是否需要缓存',
                'category': 'performance'
            },
            {
                'name': '测试覆盖',
                'description': '验证测试覆盖率',
                'example': '确保新代码有对应测试',
                'category': 'testing'
            },
            {
                'name': '文档完整性',
                'description': '检查文档是否完整',
                'example': 'API变更是否更新了文档',
                'category': 'documentation'
            }
        ],
        'preferences': {
            'require_security_check': True,
            'require_tests': True,
            'require_docs': True,
            'min_coverage': 80
        }
    },

    # LOW 优先级
    'go_reviewer': {
        'agent_type': 'language_reviewer',
        'priority': 'LOW',
        'initial_patterns': [
            {
                'name': 'Goroutine泄漏检测',
                'description': '识别可能导致goroutine泄漏的代码',
                'example': '确保带缓冲的channel能被正确关闭',
                'category': 'concurrency'
            },
            {
                'name': '错误处理最佳实践',
                'description': 'Go特有的错误处理模式',
                'example': '总是检查error返回值',
                'category': 'error_handling'
            },
            {
                'name': 'Context使用模式',
                'description': '正确使用context包',
                'example': '传递context到所有阻塞操作',
                'category': 'cancellation'
            },
            {
                'name': '接口设计原则',
                'description': 'Go接口设计最佳实践',
                'example': '接口应该在使用方定义',
                'category': 'design'
            }
        ],
        'preferences': {
            'check_goroutine_leaks': True,
            'enforce_error_handling': True,
            'require_context': True
        }
    },

    'kotlin_reviewer': {
        'agent_type': 'language_reviewer',
        'priority': 'LOW',
        'initial_patterns': [
            {
                'name': '空安全',
                'description': 'Kotlin空类型系统最佳实践',
                'example': '优先使用非空类型，谨慎使用??',
                'category': 'safety'
            },
            {
                'name': '协程使用',
                'description': 'Kotlin协程的正确使用',
                'example': '使用CoroutineScope管理协程生命周期',
                'category': 'concurrency'
            },
            {
                'name': 'Android最佳实践',
                'description': 'Android Kotlin开发规范',
                'example': '使用ViewModel和LiveData',
                'category': 'mobile'
            }
        ],
        'preferences': {
            'enforce_null_safety': True,
            'require_coroutine_scope': True
        }
    },

    'refactor_cleaner': {
        'agent_type': 'quality',
        'priority': 'LOW',
        'initial_patterns': [
            {
                'name': '死代码识别',
                'description': '如何识别未使用的代码',
                'example': '使用knip或prune工具',
                'category': 'detection'
            },
            {
                'name': '重构优先级',
                'description': '重构任务的顺序安排',
                'example': '先重构依赖少的模块',
                'category': 'strategy'
            },
            {
                'name': '安全重构',
                'description': '确保重构不破坏功能',
                'example': '重构前后都要运行测试',
                'category': 'safety'
            }
        ],
        'preferences': {
            'use_knip': True,
            'require_tests': True,
            'backup_before_refactor': True
        }
    }
}


def init_agent_memory(agent_name: str, config: dict, manager: AgentMemoryManager):
    """初始化单个agent的记忆"""

    print(f"\n{'='*60}")
    print(f"初始化 {agent_name} ({config['priority']} 优先级)")
    print(f"{'='*60}")

    # 获取或创建agent记忆
    memory = manager.get_agent_memory(agent_name)

    # 添加初始模式
    for pattern in config.get('initial_patterns', []):
        memory.add_pattern({
            **pattern,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'agent': agent_name
        })
        print(f"  ✓ 添加模式: {pattern['name']}")

    # 设置偏好
    for key, value in config.get('preferences', {}).items():
        memory.preferences[key] = value
    print(f"  ✓ 设置偏好: {len(memory.preferences)} 项")

    # 保存
    manager._save_agent_memory(agent_name)

    # 统计
    summary = memory.get_summary()
    print(f"\n  📊 {agent_name} 记忆统计:")
    print(f"     - 模式库: {summary['patterns_count']} 项")
    print(f"     - 偏好设置: {len(memory.preferences)} 项")
    print(f"     - 专业记忆: {summary['professional_memory_count']} 项")
    print(f"     - 工作记忆: {summary['working_memory_count']} 项")


def main():
    """主函数"""

    print("\n" + "="*60)
    print("Agent 独立记忆系统初始化")
    print("="*60)

    # 创建记忆管理器
    manager = AgentMemoryManager()

    # 按优先级分组
    priority_order = ['HIGH', 'MEDIUM', 'LOW']
    agents_by_priority = {}

    for agent_name, config in NEW_AGENTS_CONFIG.items():
        priority = config['priority']
        if priority not in agents_by_priority:
            agents_by_priority[priority] = []
        agents_by_priority[priority].append((agent_name, config))

    # 按优先级初始化
    total = 0
    for priority in priority_order:
        if priority not in agents_by_priority:
            continue

        print(f"\n{'='*60}")
        print(f"处理 {priority} 优先级 Agent")
        print(f"{'='*60}")

        for agent_name, config in agents_by_priority[priority]:
            try:
                init_agent_memory(agent_name, config, manager)
                total += 1
            except Exception as e:
                print(f"  ❌ 初始化失败 {agent_name}: {e}")

    # 最终报告
    print(f"\n{'='*60}")
    print("初始化完成")
    print(f"{'='*60}")
    print(f"总计: {total} 个 Agent")
    print(f"位置: {manager.memory_dir}")
    print()

    # 系统状态
    status = manager.get_status_report()
    print(f"当前系统状态:")
    print(f"  总 Agent 数: {status['total_agents']}")
    print(f"  共享记忆: {status['shared_memory_count']} 项")
    print()

    # 列出所有agent
    print(f"所有 Agent 记忆:")
    for agent_name in sorted(status['agents'].keys()):
        info = status['agents'][agent_name]
        print(f"  - {agent_name:25} | 模式:{info['patterns_count']:3} | "
              f"专业:{info['professional_memory_count']:4} | "
              f"任务:{info['tasks_completed']:3}")


if __name__ == "__main__":
    main()
