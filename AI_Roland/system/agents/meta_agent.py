#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI Roland Meta-Agent - 元Agent系统

功能：
1. 审查Agent表现
2. 优化记忆结构
3. 跨Agent知识传播
4. 生成改进建议
5. 自动化调度
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone, timedelta
from collections import defaultdict, Counter
import re

# 修复Windows编码
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

# 添加系统路径
system_path = Path(__file__).parent.parent
sys.path.insert(0, str(system_path))

from agents.agent_memory import AgentMemoryManager, get_agent_memory_manager
from homunculus_memory import HomunculusMemory


class MetaAgent:
    """元Agent：让所有Agent具备反思和自我优化能力"""

    def __init__(self, workspace=None):
        if workspace is None:
            workspace = Path(__file__).parent.parent.parent

        self.workspace = Path(workspace)
        self.memory_manager = get_agent_memory_manager()

        # 元数据存储
        self.meta_dir = self.workspace / "system" / "agents" / "meta"
        self.meta_dir.mkdir(parents=True, exist_ok=True)

        # 数据文件
        self.review_history_file = self.meta_dir / "review_history.json"
        self.optimization_log_file = self.meta_dir / "optimization_log.json"
        self.cross_learning_file = self.meta_dir / "cross_learning.json"

        # 初始化属性
        self.review_history = []
        self.optimization_log = []
        self.cross_learning = {}

        # 加载历史数据
        self.review_history = self._load_json(self.review_history_file, [])
        self.optimization_log = self._load_json(self.optimization_log_file, [])
        self.cross_learning = self._load_json(self.cross_learning_file, {})

        # Agent列表
        self.agents = ['architect', 'planner', 'engineer',
                      'code_reviewer', 'security_reviewer', 'doc_writer']

    def _load_json(self, path: Path, default=None):
        """安全加载JSON"""
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[WARN] 加载{path.name}失败: {e}")
        return default if default is not None else {}

    def _save_json(self, path: Path, data: Any):
        """安全保存JSON"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

    def daily_review(self) -> Dict:
        """每日反思：审查所有Agent的表现

        Returns:
            审查报告
        """
        print("\n" + "="*70)
        print("🤖 Meta-Agent: 每日Agent审查开始")
        print("="*70)

        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agents": {}
        }

        for agent_name in self.agents:
            agent_report = self._analyze_agent(agent_name)
            report["agents"][agent_name] = agent_report

            # 打印关键发现
            self._print_agent_summary(agent_name, agent_report)

        # 保存审查历史
        self.review_history.append(report)
        self._save_json(self.review_history_file, self.review_history)

        # 生成全局建议
        global_suggestions = self._generate_global_suggestions(report)
        report["global_suggestions"] = global_suggestions

        print("\n" + "="*70)
        print("✅ 每日审查完成")
        print("="*70)

        return report

    def _analyze_agent(self, agent_name: str) -> Dict:
        """分析单个Agent的表现"""
        memory = self.memory_manager.get_agent_memory(agent_name)

        # 基础统计
        prof_count = len(memory.professional_memory)
        pattern_count = len(memory.patterns)
        tasks_completed = memory.stats.get('tasks_completed', 0)

        # 成功任务分析
        successful_tasks = [
            m for m in memory.professional_memory
            if m.get('type') == 'successful_task'
        ]

        # 记忆质量分析
        quality_score = self._calculate_memory_quality(memory)

        # 学习速度（最近7天新增记忆）
        recent_memories = self._count_recent_memories(memory, days=7)

        # 识别优势
        strengths = self._identify_strengths(memory, successful_tasks)

        # 识别弱点
        weaknesses = self._identify_weaknesses(memory)

        # 生成建议
        suggestions = self._generate_agent_suggestions(
            agent_name, memory, strengths, weaknesses
        )

        return {
            "professional_memory_count": prof_count,
            "pattern_count": pattern_count,
            "tasks_completed": tasks_completed,
            "successful_tasks_count": len(successful_tasks),
            "quality_score": quality_score,
            "recent_learning_velocity": recent_memories,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "suggestions": suggestions,
            "last_active": memory.stats.get('last_active')
        }

    def _calculate_memory_quality(self, memory) -> Dict:
        """计算记忆质量分数"""
        total = len(memory.professional_memory)
        if total == 0:
            return {"score": 0, "details": "无记忆数据"}

        # 质量指标
        has_approach = sum(1 for m in memory.professional_memory
                          if m.get('type') == 'successful_task'
                          and m.get('approach'))

        has_lessons = sum(1 for m in memory.professional_memory
                         if m.get('type') == 'successful_task'
                         and m.get('lessons'))

        has_context = sum(1 for m in memory.professional_memory
                         if m.get('context'))

        # 计算分数 (0-100)
        score = 0
        if total > 0:
            score += (has_approach / total) * 40  # 40分：有方法
            score += (has_lessons / total) * 30   # 30分：有经验
            score += (has_context / total) * 30   # 30分：有上下文

        return {
            "score": round(score, 2),
            "details": {
                "tasks_with_approach": has_approach,
                "tasks_with_lessons": has_lessons,
                "memories_with_context": has_context,
                "total_memories": total
            }
        }

    def _count_recent_memories(self, memory, days=7) -> int:
        """计算最近N天新增的记忆"""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        count = 0

        for m in memory.professional_memory:
            try:
                timestamp = datetime.fromisoformat(m.get('timestamp', ''))
                if timestamp > cutoff:
                    count += 1
            except:
                pass

        return count

    def _identify_strengths(self, memory, successful_tasks) -> List[str]:
        """识别Agent的优势"""
        strengths = []

        # 任务完成率高
        if len(successful_tasks) >= 3:
            strengths.append(f"已完成{len(successful_tasks)}个任务，实战经验丰富")

        # 模式库丰富
        if len(memory.patterns) >= 5:
            strengths.append(f"模式库完善（{len(memory.patterns)}条模式）")

        # 最近活跃
        last_active = memory.stats.get('last_active')
        if last_active:
            try:
                last_active_date = datetime.fromisoformat(last_active)
                if (datetime.now(timezone.utc) - last_active_date).days <= 7:
                    strengths.append("最近一周有活动，学习活跃")
            except:
                pass

        # 记忆质量高
        quality = self._calculate_memory_quality(memory)
        if quality['score'] >= 70:
            strengths.append(f"记忆质量优秀（{quality['score']}/100）")

        return strengths

    def _identify_weaknesses(self, memory) -> List[str]:
        """识别Agent的弱点"""
        weaknesses = []

        # 任务完成少
        if memory.stats.get('tasks_completed', 0) == 0:
            weaknesses.append("尚未完成任务，缺乏实战经验")

        # 记忆少
        if len(memory.professional_memory) < 5:
            weaknesses.append(f"专业记忆较少（仅{len(memory.professional_memory)}条）")

        # 模式库少
        if len(memory.patterns) < 3:
            weaknesses.append(f"模式库需扩充（仅{len(memory.patterns)}条）")

        # 记忆质量低
        quality = self._calculate_memory_quality(memory)
        if quality['score'] < 50:
            weaknesses.append(f"记忆质量需提升（{quality['score']}/100）")
            if quality['details']['tasks_with_approach'] == 0:
                weaknesses.append("任务记录缺少approach字段")
            if quality['details']['tasks_with_lessons'] == 0:
                weaknesses.append("任务记录缺少lessons字段")

        # 长期未活跃
        last_active = memory.stats.get('last_active')
        if last_active:
            try:
                last_active_date = datetime.fromisoformat(last_active)
                days_inactive = (datetime.now(timezone.utc) - last_active_date).days
                if days_inactive > 30:
                    weaknesses.append(f"长期未活跃（{days_inactive}天）")
            except:
                pass

        return weaknesses

    def _generate_agent_suggestions(self, agent_name: str, memory,
                                   strengths: List, weaknesses: List) -> List[str]:
        """为特定Agent生成改进建议"""
        suggestions = []

        # 针对弱点提建议
        for weakness in weaknesses:
            if "实战经验" in weakness:
                suggestions.append(f"建议：为{agent_name}分配更多实际任务，积累经验")
            elif "专业记忆较少" in weakness:
                suggestions.append(f"建议：补充{agent_name}的专业领域知识")
            elif "模式库需扩充" in weakness:
                suggestions.append(f"建议：添加{agent_name}的常见模式和最佳实践")
            elif "approach字段" in weakness:
                suggestions.append(f"建议：完善任务记录，添加详细的approach描述")
            elif "lessons字段" in weakness:
                suggestions.append(f"建议：记录每次任务的经验教训")
            elif "长期未活跃" in weakness:
                suggestions.append(f"建议：在适合的场景下激活{agent_name}")

        # 基于Agent特性的专门建议
        agent_specific_suggestions = self._get_agent_specific_suggestions(agent_name)
        suggestions.extend(agent_specific_suggestions)

        return suggestions

    def _get_agent_specific_suggestions(self, agent_name: str) -> List[str]:
        """获取Agent特定的改进建议"""
        suggestions_map = {
            'architect': [
                "建议：补充云原生架构模式（Kubernetes、Service Mesh）",
                "建议：添加架构决策记录（ADR）模板",
                "建议：增加成本优化相关的架构考虑"
            ],
            'planner': [
                "建议：添加风险应对模板",
                "建议：补充敏捷估算技巧（Planning Poker）",
                "建议：增加干系人沟通策略"
            ],
            'engineer': [
                "建议：补充更多设计模式的应用案例",
                "建议：添加代码重构的Checklist",
                "建议：增加性能优化的实战经验"
            ],
            'code_reviewer': [
                "建议：补充Rust和Swift的审查模式",
                "建议：添加代码审查沟通技巧",
                "建议：增加自动化审查工具的使用经验"
            ],
            'security_reviewer': [
                "建议：补充DevSecOps实践经验",
                "建议：添加安全测试工具的使用指南",
                "建议：增加隐私保护（GDPR）相关经验"
            ],
            'doc_writer': [
                "建议：补充技术博客写作技巧",
                "建议：添加视频教程制作经验",
                "建议：增加API文档的交互式设计"
            ]
        }

        return suggestions_map.get(agent_name, [])

    def _print_agent_summary(self, agent_name: str, report: Dict):
        """打印Agent审查摘要"""
        print(f"\n📊 {agent_name.upper()}")
        print(f"   任务完成: {report['tasks_completed']}个")
        print(f"   专业记忆: {report['professional_memory_count']}条")
        print(f"   模式库: {report['pattern_count']}条")
        print(f"   质量分数: {report['quality_score']['score']}/100")
        print(f"   学习速度: +{report['recent_learning_velocity']}条/周")

        if report['strengths']:
            print(f"   ✅ 优势: {', '.join(report['strengths'][:2])}")

        if report['weaknesses']:
            print(f"   ⚠️  弱点: {', '.join(report['weaknesses'][:2])}")

    def _generate_global_suggestions(self, report: Dict) -> List[str]:
        """生成全局改进建议"""
        suggestions = []

        # 分析整体表现
        low_quality_agents = [
            name for name, data in report['agents'].items()
            if data['quality_score']['score'] < 50
        ]

        inactive_agents = [
            name for name, data in report['agents'].items()
            if data.get('last_active') is None
        ]

        if low_quality_agents:
            suggestions.append(
                f"需要提升记忆质量：{', '.join(low_quality_agents)}"
            )

        if inactive_agents:
            suggestions.append(
                f"需要激活使用：{', '.join(inactive_agents)}"
            )

        # 跨Agent学习建议
        suggestions.extend(self._identify_cross_learning_opportunities(report))

        return suggestions

    def _identify_cross_learning_opportunities(self, report: Dict) -> List[str]:
        """识别跨Agent学习机会"""
        opportunities = []

        # 找出表现最好的Agent
        best_agent = max(
            report['agents'].items(),
            key=lambda x: x[1]['quality_score']['score']
        )

        opportunities.append(
            f"建议：让{best_agent[0]}分享最佳实践（质量分数{best_agent[1]['quality_score']['score']}）"
        )

        # 检查是否有互补的Agent
        architect_data = report['agents'].get('architect', {})
        engineer_data = report['agents'].get('engineer', {})

        if architect_data.get('tasks_completed', 0) > engineer_data.get('tasks_completed', 0):
            opportunities.append(
                "建议：architect可以指导engineer进行系统设计"
            )

        return opportunities

    def weekly_optimization(self) -> Dict:
        """每周优化：优化所有Agent的记忆结构

        Returns:
            优化报告
        """
        print("\n" + "="*70)
        print("🔧 Meta-Agent: 每周记忆优化开始")
        print("="*70)

        optimization_report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "optimizations": {}
        }

        for agent_name in self.agents:
            print(f"\n🔍 优化 {agent_name}...")

            optimizations = self._optimize_agent_memory(agent_name)
            optimization_report["optimizations"][agent_name] = optimizations

            if optimizations:
                print(f"   ✅ 完成 {len(optimizations)}项优化")
            else:
                print(f"   ℹ️  无需优化")

        # 执行跨Agent知识传播
        print(f"\n🔄 执行跨Agent知识传播...")
        cross_learning_results = self.cross_agent_learning()
        optimization_report["cross_learning"] = cross_learning_results

        # 保存优化日志
        self.optimization_log.append(optimization_report)
        self._save_json(self.optimization_log_file, self.optimization_log)

        print("\n" + "="*70)
        print("✅ 每周优化完成")
        print("="*70)

        return optimization_report

    def _optimize_agent_memory(self, agent_name: str) -> List[Dict]:
        """优化单个Agent的记忆"""
        memory = self.memory_manager.get_agent_memory(agent_name)
        optimizations = []

        # 1. 删除重复记忆
        duplicates_removed = self._remove_duplicate_memories(memory)
        if duplicates_removed > 0:
            optimizations.append({
                "type": "remove_duplicates",
                "count": duplicates_removed
            })

        # 2. 合并相似记忆
        merged = self._merge_similar_memories(memory)
        if merged > 0:
            optimizations.append({
                "type": "merge_similar",
                "count": merged
            })

        # 3. 清理空字段
        cleaned = self._clean_empty_fields(memory)
        if cleaned > 0:
            optimizations.append({
                "type": "clean_empty_fields",
                "count": cleaned
            })

        # 4. 更新模式库（从成功任务中提取）
        patterns_extracted = self._extract_patterns_from_tasks(memory)
        if patterns_extracted > 0:
            optimizations.append({
                "type": "extract_patterns",
                "count": patterns_extracted
            })

        # 保存优化后的记忆
        if optimizations:
            self.memory_manager._save_agent_memory(agent_name)

        return optimizations

    def _remove_duplicate_memories(self, memory) -> int:
        """删除重复的记忆"""
        seen = set()
        to_remove = []

        for i, item in enumerate(memory.professional_memory):
            # 创建唯一标识
            content = item.get('content', '')
            item_type = item.get('type', '')
            key = f"{item_type}:{content}"

            if key in seen:
                to_remove.append(i)
            else:
                seen.add(key)

        # 从后往前删除，避免索引错位
        for i in reversed(to_remove):
            memory.professional_memory.pop(i)

        return len(to_remove)

    def _merge_similar_memories(self, memory) -> int:
        """合并相似的记忆"""
        # 简单实现：合并完全相同type和content开头
        merged_count = 0
        i = 0

        while i < len(memory.professional_memory) - 1:
            current = memory.professional_memory[i]
            next_item = memory.professional_memory[i + 1]

            # 检查是否相似
            current_content = current.get('content', '')
            next_content = next_item.get('content', '')

            if (current.get('type') == next_item.get('type') and
                current_content and next_content.startswith(current_content[:20])):
                # 合并：保留更完整的那个
                if len(next_content) > len(current_content):
                    memory.professional_memory.pop(i)
                else:
                    memory.professional_memory.pop(i + 1)
                merged_count += 1
            else:
                i += 1

        return merged_count

    def _clean_empty_fields(self, memory) -> int:
        """清理空字段"""
        cleaned = 0

        for item in memory.professional_memory:
            # 删除空字符串字段
            if item.get('approach') == '':
                del item['approach']
                cleaned += 1
            if item.get('lessons') == '':
                del item['lessons']
                cleaned += 1
            if item.get('context') == '':
                del item['context']
                cleaned += 1

        return cleaned

    def _extract_patterns_from_tasks(self, memory) -> int:
        """从成功任务中提取模式"""
        extracted = 0

        for item in memory.professional_memory:
            if item.get('type') == 'successful_task':
                # 检查是否已经有对应的模式
                task_desc = item.get('task', '')
                if not task_desc:
                    continue

                # 简单的启发式：从task中提取关键词作为模式
                # 例如："实现线程池" -> "线程池实现模式"
                for keyword in ['设计', '实现', '优化', '重构', '审查', '编写']:
                    if keyword in task_desc:
                        pattern_content = f"{keyword}模式"

                        # 检查是否已存在
                        exists = any(
                            p.get('content') == pattern_content
                            for p in memory.patterns
                        )

                        if not exists:
                            memory.add_pattern({
                                "content": pattern_content,
                                "source": f"任务: {task_desc[:50]}",
                                "timestamp": datetime.now(timezone.utc).isoformat()
                            })
                            extracted += 1
                            break

        return extracted

    def cross_agent_learning(self) -> Dict:
        """跨Agent知识传播

        Returns:
            传播结果
        """
        results = {
            "best_practices_shared": [],
            "patterns_propagated": []
        }

        # 1. 找出各Agent的最佳实践
        for agent_name in self.agents:
            memory = self.memory_manager.get_agent_memory(agent_name)

            # 找出质量最高的记忆
            best_memories = sorted(
                [m for m in memory.professional_memory if m.get('type')],
                key=lambda x: len(str(x)),
                reverse=True
            )[:3]

            for memory_item in best_memories:
                # 传播到共享记忆
                self.memory_manager.add_to_shared({
                    'type': 'best_practice',
                    'source_agent': agent_name,
                    'content': memory_item.get('content', '')[:200],
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })

                results["best_practices_shared"].append({
                    "from": agent_name,
                    "content": memory_item.get('content', '')[:50]
                })

        # 2. 传播常见模式
        pattern_frequency = Counter()

        for agent_name in self.agents:
            memory = self.memory_manager.get_agent_memory(agent_name)
            for pattern in memory.patterns:
                content = pattern.get('content', '')
                if content:
                    pattern_frequency[content] += 1

        # 找出高频模式（多个Agent都有）
        common_patterns = [
            (content, count)
            for content, count in pattern_frequency.items()
            if count >= 2
        ]

        for pattern_content, count in common_patterns:
            results["patterns_propagated"].append({
                "pattern": pattern_content,
                "frequency": count,
                "agents": count
            })

        # 保存跨学习记录
        self.cross_learning[str(datetime.now(timezone.utc).isoformat())] = results
        self._save_json(self.cross_learning_file, self.cross_learning)

        return results

    def get_status_report(self) -> Dict:
        """获取Meta-Agent的状态报告"""
        return {
            "agents_monitored": len(self.agents),
            "reviews_conducted": len(self.review_history),
            "optimizations_performed": len(self.optimization_log),
            "last_review": self.review_history[-1]['timestamp'] if self.review_history else None,
            "last_optimization": self.optimization_log[-1]['timestamp'] if self.optimization_log else None,
            "cross_learning_events": len(self.cross_learning)
        }


def get_meta_agent() -> MetaAgent:
    """获取Meta-Agent单例"""
    return MetaAgent()


# 命令行接口
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AI Roland Meta-Agent")
    parser.add_argument('--review', action='store_true', help='执行每日审查')
    parser.add_argument('--optimize', action='store_true', help='执行每周优化')
    parser.add_argument('--status', action='store_true', help='查看状态')
    parser.add_argument('--cross-learn', action='store_true', help='跨Agent学习')

    args = parser.parse_args()

    meta = get_meta_agent()

    if args.status:
        status = meta.get_status_report()
        print("\n📊 Meta-Agent 状态:")
        print(f"   监控Agent数: {status['agents_monitored']}")
        print(f"   审查次数: {status['reviews_conducted']}")
        print(f"   优化次数: {status['optimizations_performed']}")
        print(f"   跨学习事件: {status['cross_learning_events']}")
        if status['last_review']:
            print(f"   最近审查: {status['last_review']}")

    elif args.review:
        meta.daily_review()

    elif args.optimize:
        meta.weekly_optimization()

    elif args.cross_learn:
        results = meta.cross_agent_learning()
        print("\n🔄 跨Agent学习结果:")
        print(f"   分享最佳实践: {len(results['best_practices_shared'])}条")
        print(f"   传播常见模式: {len(results['patterns_propagated'])}条")

    else:
        parser.print_help()
