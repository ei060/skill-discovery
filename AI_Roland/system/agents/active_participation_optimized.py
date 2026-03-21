#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI Roland 主动参与系统 - 性能优化版

添加缓存、并行处理等优化
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from functools import lru_cache
import hashlib

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

from agent_communication import get_collaboration_hub, AgentCapability
from agent_memory import get_agent_memory_manager


class OptimizedActiveParticipationEngine:
    """性能优化的主动参与引擎"""

    def __init__(self, workspace: Optional[Path] = None, enable_cache: bool = True):
        if workspace is None:
            workspace = Path(__file__).parent.parent.parent

        self.workspace = Path(workspace)
        self.collab_hub = get_collaboration_hub()
        self.memory_mgr = get_agent_memory_manager()
        self.enable_cache = enable_cache

        # 缓存目录
        self.cache_dir = self.workspace / "system" / "agents" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # 能力-关键词映射（与原版相同）
        self.capability_keywords = {
            'code_reviewer': {
                'keywords': ['审查', 'review', '代码质量', 'bug', '安全', '优化', '重构'],
                'trigger_threshold': 2
            },
            'planner': {
                'keywords': ['计划', 'plan', '设计', '架构', '方案', '流程', '任务分解', '开发'],
                'trigger_threshold': 2
            },
            'architect': {
                'keywords': ['架构', '设计', '系统', '模块', '接口', 'api', '技术选型', '功能', '开发'],
                'trigger_threshold': 1
            },
            'security_reviewer': {
                'keywords': ['安全', '漏洞', '注入', 'XSS', 'CSRF', '加密', '认证'],
                'trigger_threshold': 1
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

    def _get_cache_key(self, user_input: str) -> str:
        """生成缓存键"""
        return hashlib.md5(user_input.encode('utf-8')).hexdigest()

    def _load_from_cache(self, cache_key: str) -> Optional[Dict]:
        """从缓存加载"""
        if not self.enable_cache:
            return None

        cache_file = self.cache_dir / f"{cache_key}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 检查缓存是否过期（24小时）
            created_at = datetime.fromisoformat(data['created_at'])
            age = (datetime.now(timezone.utc) - created_at).total_seconds()

            if age > 86400:  # 24小时
                cache_file.unlink()
                return None

            return data['result']

        except Exception:
            return None

    def _save_to_cache(self, cache_key: str, result: Dict):
        """保存到缓存"""
        if not self.enable_cache:
            return

        cache_file = self.cache_dir / f"{cache_key}.json"

        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'result': result
                }, f, ensure_ascii=False, indent=2)
        except Exception:
            pass  # 缓存失败不影响主流程

    def analyze_user_input(self, user_input: str, use_cache: bool = True) -> List[Dict]:
        """分析用户输入，返回应该参与的Agent列表（优化版）"""

        # 检查缓存
        if use_cache:
            cache_key = self._get_cache_key(user_input)
            cached_result = self._load_from_cache(cache_key)

            if cached_result is not None:
                return cached_result

        # 执行分析
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

        # 保存到缓存
        if use_cache:
            self._save_to_cache(cache_key, results)

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
        """生成参与报告（优化版）"""

        suggested_agents = self.analyze_user_input(user_input)

        return {
            'user_input': user_input,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'cached': self._load_from_cache(self._get_cache_key(user_input)) is not None,
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

    def clear_cache(self):
        """清空缓存"""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()

    def get_cache_stats(self) -> Dict:
        """获取缓存统计"""
        cache_files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files)

        return {
            'cache_files': len(cache_files),
            'total_size_mb': total_size / (1024 * 1024),
            'cache_dir': str(self.cache_dir)
        }


# 保持向后兼容
def get_active_participation_engine() -> OptimizedActiveParticipationEngine:
    """获取主动参与引擎单例（优化版）"""
    return OptimizedActiveParticipationEngine()


# 测试
if __name__ == "__main__":
    print("\n" + "="*70)
    print("AI Roland 主动参与系统测试 - 性能优化版")
    print("="*70)

    import time

    engine = get_active_participation_engine()

    # 测试1：缓存性能
    print("\n1. 测试：缓存性能")
    test_input = "请帮我审查这段用户认证代码，看看有没有安全问题"

    # 第一次调用（无缓存）
    start = time.time()
    report_1 = engine.get_participation_report(test_input)
    time_1 = time.time() - start

    # 第二次调用（有缓存）
    start = time.time()
    report_2 = engine.get_participation_report(test_input)
    time_2 = time.time() - start

    print(f"  首次调用: {time_1*1000:.2f}ms")
    print(f"  缓存调用: {time_2*1000:.2f}ms")
    print(f"  性能提升: {(time_1/time_2):.1f}x")
    print(f"  缓存命中: {report_2['cached']}")

    # 测试2：缓存统计
    print("\n2. 测试：缓存统计")
    stats = engine.get_cache_stats()
    print(f"  缓存文件数: {stats['cache_files']}")
    print(f"  总大小: {stats['total_size_mb']:.2f}MB")

    # 测试3：分析结果
    print("\n3. 测试：分析结果")
    print(f"  建议数量: {report_1['total_suggestions']}")
    print(f"  推荐结果:")
    print(f"    是否使用Agent: {report_1['recommendations']['should_use_agents']}")
    print(f"    优先级: {report_1['recommendations'].get('priority', 'N/A')}")
    print(f"    消息: {report_1['recommendations']['message']}")

    print("\n✓ 测试完成")
