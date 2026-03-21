"""
AI Roland 工程师 Agent v3.0
负责技能选择、执行和技术实现
集成自我迭代引擎 + 记忆树系统 (Memory-Like-A-Tree)
持续学习和优化，让记忆像树一样自然生长
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import re
import time

# 设置环境变量
os.environ['PYTHONIOENCODING'] = 'utf-8'


class EngineerAgent:
    """工程师 Agent v3.0 - 技能选择、执行和自我进化 + 记忆树"""

    def __init__(self):
        self.system_dir = Path(__file__).parent
        self.workspace = self.system_dir.parent
        self.name = "工程师"
        self.version = "3.0.0"

        # 导入技能匹配器
        from skills_matcher import SkillsMatcher
        self.skill_matcher = SkillsMatcher()

        # 导入自我迭代引擎
        from self_improvement_engine import SelfImprovementEngine
        self.improvement_engine = SelfImprovementEngine(self.workspace)

        # 导入记忆树系统 (新增)
        from memory_tree import MemoryTree
        self.memory_tree = MemoryTree(self.workspace)

        # 技能执行历史
        self.execution_history = []

        # 当前任务状态
        self.current_task = None
        self.task_start_time = None

    def analyze_request(self, user_request: str) -> Dict:
        """分析用户需求（增强版：先搜索记忆树）"""
        # 🌳 Step 1: 先搜索记忆树中的相关知识
        memory_results = self.memory_tree.search(user_request, top_k=3)

        # 提取关键词
        keywords = self._extract_keywords(user_request)

        # 识别意图类型
        intent = self._classify_intent(user_request)

        # 匹配技能
        matched_skills = self.skill_matcher.match_skills(user_request)

        # 检查历史模式（从旧系统，会逐步迁移到记忆树）
        pattern_match = self._check_historical_patterns(user_request, intent)

        # 主动推荐
        recommendation = self.improvement_engine.get_recommendation({
            "request": user_request,
            "intent": intent
        })

        return {
            "request": user_request,
            "keywords": keywords,
            "intent": intent,
            "matched_skills": matched_skills,
            "has_skill": len(matched_skills) > 0,
            "pattern_match": pattern_match,
            "recommendation": recommendation,
            "memory_hits": memory_results  # 新增：记忆命中
        }

    def _check_historical_patterns(self, request: str, intent: str) -> Optional[Dict]:
        """检查历史成功模式（优先从记忆树查询）"""
        # 先从记忆树搜索
        tree_results = self.memory_tree.search(intent, top_k=5)

        if tree_results:
            best = tree_results[0]
            return {
                "skill": best["knowledge"].get("key", ""),
                "confidence": best["confidence"],
                "success_rate": best["confidence"],  # 记忆树中置信度即成功率
                "source": "memory_tree"
            }

        # 回退到旧系统
        patterns = self.improvement_engine.patterns
        if intent in patterns:
            pattern = patterns[intent]
            if pattern["confidence"] > 0.7:
                return {
                    "skill": pattern["best_skill"],
                    "confidence": pattern["confidence"],
                    "success_rate": pattern["success_rate"],
                    "source": "legacy"
                }
        return None

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        keywords = []
        text_lower = text.lower()

        tech_keywords = [
            "git", "commit", "push", "pull", "merge",
            "代码", "审查", "review", "test", "测试",
            "浏览器", "爬虫", "自动化", "playwright",
            "搜索", "github", "reddit", "工具",
            "短剧", "剧本", "创作",
            "简报", "今日", "任务", "记忆",
            "订票", "12306", "火车票"
        ]

        for kw in tech_keywords:
            if kw in text_lower:
                keywords.append(kw)

        return keywords

    def _classify_intent(self, text: str) -> str:
        """分类意图"""
        intent_patterns = {
            "search": r"(搜索|查找|发现|find|search|github)",
            "write": r"(写|创作|生成|create|write|compose)",
            "automate": r"(自动|批处理|脚本|script|automation)",
            "query": r"(查询|检索|回忆|query|search|recall)",
            "review": r"(审查|检查|review|audit)",
            "commit": r"(提交|commit|git|push)",
            "browse": r"(浏览器|网页|browser|web|爬取)",
            "booking": r"(订票|12306|火车票|ticket|booking)",
            "briefing": r"(简报|今日|日程|daily|briefing|today)"
        }

        text_lower = text.lower()
        for intent, pattern in intent_patterns.items():
            if re.search(pattern, text_lower):
                return intent

        return "general"

    def select_skill(self, analysis: Dict) -> Optional[Dict]:
        """选择最佳技能（增强版：结合记忆树和历史经验）"""
        # 优先使用历史成功模式
        if analysis.get("pattern_match"):
            pattern = analysis["pattern_match"]
            skill_name = pattern["skill"]
            skill_info = self.skill_matcher.skill_keywords.get(skill_name, {})
            return {
                "name": skill_name,
                "description": skill_info.get("description", ""),
                "score": pattern["confidence"] * 10,
                "matched_keywords": [],
                "source": pattern.get("source", "historical_pattern"),
                "expected_success_rate": pattern["success_rate"]
            }

        # 使用推荐
        if analysis.get("recommendation"):
            rec = analysis["recommendation"]
            if rec["type"] == "pattern_match":
                skill_name = rec["suggestion"].replace("使用 ", "").replace(" 技能", "")
                skill_info = self.skill_matcher.skill_keywords.get(skill_name, {})
                return {
                    "name": skill_name,
                    "description": skill_info.get("description", ""),
                    "score": rec["confidence"] * 10,
                    "matched_keywords": [],
                    "source": "recommendation",
                    "reason": rec["reason"]
                }

        # 默认匹配
        matched_skills = analysis.get("matched_skills", [])
        if matched_skills:
            best_skill = matched_skills[0]
            return {
                "name": best_skill["name"],
                "description": best_skill["description"],
                "score": best_skill["score"],
                "matched_keywords": best_skill["matched_keywords"],
                "source": "keyword_match"
            }

        return None

    def execute_with_skill(self, user_request: str, context: Dict = None) -> Dict:
        """使用技能执行任务（增强版：记录到记忆树）"""
        self.task_start_time = time.time()

        # 1. 分析需求（包含记忆树搜索）
        analysis = self.analyze_request(user_request)

        # 2. 选择技能
        selected_skill = self.select_skill(analysis)

        # 3. 生成执行计划
        execution_plan = self._generate_execution_plan(user_request, analysis, selected_skill)

        # 4. 检查优化建议
        optimization = self.improvement_engine.suggest_optimization(
            user_request, analysis["intent"], context
        )

        # 5. 记录当前任务
        self.current_task = {
            "request": user_request,
            "analysis": analysis,
            "selected_skill": selected_skill,
            "plan": execution_plan,
            "optimization": optimization
        }

        # 6. 如果记忆有命中，标记为已使用（提升置信度）
        for memory_hit in analysis.get("memory_hits", []):
            self.memory_tree.use_knowledge(memory_hit["knowledge_id"])

        return {
            "analysis": analysis,
            "selected_skill": selected_skill,
            "execution_plan": execution_plan,
            "optimization": optimization,
            "recommendations": self._get_active_recommendations(),
            "memory_hits": analysis.get("memory_hits", []),
            "ready": True
        }

    def _get_active_recommendations(self) -> List[str]:
        """获取当前活跃的推荐"""
        recommendations = []

        # 检查优化机会
        opportunities = self.improvement_engine.find_optimization_opportunities()
        if opportunities:
            recommendations.append({
                "type": "optimization",
                "message": f"发现 {len(opportunities)} 个优化机会",
                "top_priority": opportunities[0]["suggestion"] if opportunities else None
            })

        # 检查新组合
        combinations = self.improvement_engine.discover_new_combinations()
        if combinations:
            best = max(combinations, key=lambda x: x["co_occurrence"])
            recommendations.append({
                "type": "combination",
                "message": f"发现技能组合: {' + '.join(best['skills'])}",
                "potential_use": best["potential_use"]
            })

        # 🌳 检查记忆树状态
        tree_stats = self.memory_tree.stats
        if tree_stats["withered_leaves"] > 3:
            recommendations.append({
                "type": "memory_cleanup",
                "message": f"记忆树有 {tree_stats['withered_leaves']} 片枯叶，建议清理"
            })

        return recommendations

    def complete_task(self, success: bool, outcome: str = "", feedback: str = "", lessons: List[str] = None, save_to_tree: bool = True):
        """
        完成任务并记录经验

        Args:
            success: 任务是否成功
            outcome: 结果描述
            feedback: 用户反馈
            lessons: 经验教训列表
            save_to_tree: 是否保存到记忆树（默认True）
        """
        if not self.current_task:
            return

        duration = time.time() - self.task_start_time if self.task_start_time else 0

        # 记录到自我迭代引擎（旧系统，逐步迁移）
        experience = {
            "request": self.current_task["request"],
            "intent": self.current_task["analysis"]["intent"],
            "skill": self.current_task["selected_skill"]["name"] if self.current_task["selected_skill"] else "",
            "success": success,
            "duration": round(duration, 2),
            "outcome": outcome,
            "feedback": feedback,
            "lessons": lessons or []
        }

        if success:
            self.improvement_engine.record_experience(experience)
        else:
            # 从失败中学习
            self.improvement_engine.learn_from_mistake({
                **experience,
                "error": outcome,
                "lesson": lessons[0] if lessons else "需要进一步分析"
            })

        # 🌳 记录到记忆树
        if save_to_tree:
            self._save_to_memory_tree(experience, lessons)

        # 清除当前任务
        self.current_task = None
        self.task_start_time = None

    def _save_to_memory_tree(self, experience: Dict, lessons: List[str] = None):
        """将任务经验保存到记忆树"""
        # 构建知识内容
        content = f"""
请求: {experience.get('request', '')}
意图: {experience.get('intent', '')}
使用技能: {experience.get('skill', '')}
结果: {'✅ 成功' if experience.get('success') else '❌ 失败'}
耗时: {experience.get('duration', 0)} 秒
        """.strip()

        if lessons:
            content += "\n经验教训:\n" + "\n".join(f"  • {l}" for l in lessons)

        if experience.get('outcome'):
            content += f"\n详细结果: {experience['outcome']}"

        # 根据结果决定优先级
        if experience.get('success'):
            priority = self.memory_tree.PRIORITY_P1  # 成功经验较重要
        else:
            priority = self.memory_tree.PRIORITY_P2  # 失败经验一般

        # 添加到记忆树
        key = f"{experience.get('intent', 'task')}:{experience.get('skill', 'general')}"
        knowledge_id = self.memory_tree.add_knowledge(
            key=key[:50],  # 限制标题长度
            content=content,
            priority=priority,
            category="task_experience",
            tags=[experience.get('intent', ''), experience.get('skill', '')]
        )

        return knowledge_id

    def remember(self, key: str, content: str, priority: str = "P2", tags: List[str] = None) -> str:
        """
        直接添加知识到记忆树

        Args:
            key: 知识键名
            content: 知识内容
            priority: 优先级 (P0/P1/P2)
            tags: 标签列表

        Returns:
            知识ID
        """
        # 映射优先级字符串到类常量
        priority_map = {
            "P0": self.memory_tree.PRIORITY_P0,
            "P1": self.memory_tree.PRIORITY_P1,
            "P2": self.memory_tree.PRIORITY_P2
        }

        return self.memory_tree.add_knowledge(
            key=key,
            content=content,
            priority=priority_map.get(priority, self.memory_tree.PRIORITY_P2),
            tags=tags or []
        )

    def recall(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        从记忆树召回知识

        Args:
            query: 搜索查询
            top_k: 返回数量

        Returns:
            匹配的知识列表
        """
        return self.memory_tree.search(query, top_k=top_k)

    def mark_important(self, knowledge_id: str) -> bool:
        """标记知识为重要"""
        return self.memory_tree.mark_important(knowledge_id)

    def decay_memory(self) -> Dict[str, int]:
        """执行记忆衰减（每日任务）"""
        return self.memory_tree.decay_all()

    def cleanup_memory(self) -> Dict[str, Any]:
        """清理枯叶（每日任务）"""
        return self.memory_tree.cleanup_withered()

    def _generate_execution_plan(self, request: str, analysis: Dict, skill: Optional[Dict]) -> Dict:
        """生成执行计划（增强版：结合历史最优和记忆树）"""
        if not skill:
            return {
                "method": "general",
                "steps": [
                    "使用通用实现方式",
                    "直接执行任务",
                    "验证结果"
                ],
                "estimated_duration": "未知"
            }

        skill_name = skill["name"]

        # 从历史获取预计耗时
        estimated_duration = self._get_estimated_duration(skill_name, analysis["intent"])

        # 根据技能类型生成执行计划
        plans = {
            "skill-discovery": {
                "method": "search_and_discover",
                "steps": [
                    "搜索 GitHub/Reddit",
                    "过滤和排序结果",
                    "返回推荐列表"
                ],
                "estimated_duration": estimated_duration
            },
            "browser-control": {
                "method": "browser_automation",
                "steps": [
                    "启动浏览器",
                    "导航到目标页面",
                    "执行操作（点击/填写/截图）",
                    "提取数据"
                ],
                "estimated_duration": estimated_duration
            },
            "smart-commit": {
                "method": "git_commit",
                "steps": [
                    "分析 git diff",
                    "生成 commit message",
                    "执行提交"
                ],
                "estimated_duration": estimated_duration
            },
            "short-drama-script": {
                "method": "creative_writing",
                "steps": [
                    "收集创作要求",
                    "选择题材模板",
                    "生成分集大纲",
                    "编写具体剧本"
                ],
                "estimated_duration": estimated_duration
            },
            "12306-booking": {
                "method": "booking",
                "steps": [
                    "登录 12306",
                    "查询车票",
                    "选择车次",
                    "提交订单"
                ],
                "estimated_duration": estimated_duration
            }
        }

        return plans.get(skill_name, {
            "method": "standard",
            "steps": [
                f"使用 {skill_name} 技能",
                "执行具体操作",
                "返回结果"
            ],
            "estimated_duration": estimated_duration
        })

    def _get_estimated_duration(self, skill: str, intent: str) -> str:
        """从历史获取预计耗时"""
        # 查找相似的历史记录
        similar = [
            e for e in self.improvement_engine.experiences[-50:]
            if e["selected_skill"] == skill and e["intent"] == intent
        ]

        if similar and len(similar) >= 3:
            avg_duration = sum(e["duration"] for e in similar) / len(similar)
            if avg_duration < 5:
                return "< 5 秒"
            elif avg_duration < 30:
                return "~15 秒"
            elif avg_duration < 120:
                return "~1 分钟"
            else:
                return "> 2 分钟"

        return "未知"

    def format_response(self, execution_result: Dict) -> str:
        """格式化响应（增强版：包含记忆树信息）"""
        lines = []
        lines.append(f"[{self.name}] 收到任务: {execution_result['analysis']['request']}")

        # 显示记忆命中
        memory_hits = execution_result.get("memory_hits", [])
        if memory_hits:
            lines.append(f"\n[🌳 记忆召回] 找到 {len(memory_hits)} 条相关记忆")
            for hit in memory_hits[:2]:
                status = self.memory_tree._get_status_icon(hit["status"])
                lines.append(f"  {status} {hit['knowledge']['key'][:40]} (置信度: {hit['confidence']:.2f})")
            lines.append("")

        # 显示来源
        selected_skill = execution_result.get("selected_skill")
        if selected_skill:
            source = selected_skill.get("source", "keyword_match")
            source_text = {
                "keyword_match": "关键词匹配",
                "historical_pattern": "历史经验",
                "recommendation": "智能推荐",
                "memory_tree": "🌳 记忆树"
            }.get(source, source)

            lines.append(f"[{self.name}] 已选择技能: {selected_skill['name']}")
            lines.append(f"选择依据: {source_text}")

            if selected_skill.get("expected_success_rate"):
                lines.append(f"预期成功率: {selected_skill['expected_success_rate']:.0%}")

        # 显示优化建议
        if execution_result.get("optimization"):
            opt = execution_result["optimization"]
            lines.append("")
            lines.append("[💡 智能建议]")
            lines.append(f"  {opt.get('recommended_approach', '基于历史经验')}")
            lines.append(f"  置信度: {opt.get('confidence', 0):.0%}")

        lines.append("")
        lines.append("[执行计划]")
        plan = execution_result["execution_plan"]
        for i, step in enumerate(plan["steps"], 1):
            lines.append(f"  {i}. {step}")

        if plan.get("estimated_duration") and plan["estimated_duration"] != "未知":
            lines.append(f"\n  ⏱️ 预计耗时: {plan['estimated_duration']}")

        # 显示推荐
        recommendations = execution_result.get("recommendations", [])
        if recommendations:
            lines.append("")
            lines.append("[🔔 发现的优化机会]")
            for rec in recommendations[:2]:
                if rec["type"] == "optimization":
                    lines.append(f"  • {rec.get('top_priority', rec['message'])}")
                elif rec["type"] == "combination":
                    lines.append(f"  • {rec['message']}")
                    lines.append(f"    用途: {rec['potential_use']}")
                elif rec["type"] == "memory_cleanup":
                    lines.append(f"  🌳 {rec['message']}")

        return "\n".join(lines)

    def get_status(self) -> Dict:
        """获取工程师状态（增强版：包含记忆树）"""
        tree_stats = self.memory_tree.stats

        base_status = {
            "name": self.name,
            "version": self.version,
            "available_skills": len(self.skill_matcher.skill_keywords),
            "execution_count": len(self.execution_history),
            "recent_intents": self._get_recent_intents(),
            "improvement_data": {
                "total_experiences": len(self.improvement_engine.experiences),
                "success_patterns": len(self.improvement_engine.patterns),
                "capability_nodes": len(self.improvement_engine.capabilities.get("nodes", {})),
                "optimization_opportunities": len(self.improvement_engine.find_optimization_opportunities())
            },
            # 新增：记忆树状态
            "memory_tree": {
                "total_leaves": tree_stats["total_leaves"],
                "sprouts": tree_stats["sprouts"],
                "green_leaves": tree_stats["green_leaves"],
                "yellow_leaves": tree_stats["yellow_leaves"],
                "withered_leaves": tree_stats["withered_leaves"],
                "soil_count": tree_stats["soil_count"],
                "health_ratio": round(tree_stats["green_leaves"] / tree_stats["total_leaves"], 2) if tree_stats["total_leaves"] > 0 else 0
            }
        }

        return base_status

    def _get_recent_intents(self) -> List[str]:
        """获取最近的意图类型"""
        if not self.improvement_engine.experiences:
            return []

        recent = self.improvement_engine.experiences[-5:]
        return [e["intent"] for e in recent]

    def generate_self_report(self) -> str:
        """生成自我迭代报告（包含记忆树）"""
        lines = []
        lines.append("=" * 60)
        lines.append("🌳 AI Roland 自我迭代报告")
        lines.append("=" * 60)
        lines.append("")

        # 自我迭代引擎报告
        lines.append(self.improvement_engine.generate_self_report())

        # 记忆树报告
        lines.append("")
        lines.append(self.memory_tree.get_status_report())

        return "\n".join(lines)

    def discover_improvements(self) -> List[Dict]:
        """主动发现改进机会"""
        return self.improvement_engine.find_optimization_opportunities()

    def get_capability_graph(self) -> Dict:
        """获取能力图谱"""
        return self.improvement_engine.capabilities

    def learn(self, lesson: str, priority: str = "P1"):
        """
        主动学习 - 记录新的经验教训到记忆树

        Args:
            lesson: 经验教训内容
            priority: 优先级 (P0/P1/P2)
        """
        # 同时记录到旧系统和新系统
        if "lessons_learned" not in self.improvement_engine.optimizations:
            self.improvement_engine.optimizations["lessons_learned"] = []

        self.improvement_engine.optimizations["lessons_learned"].append({
            "timestamp": self._get_timestamp(),
            "lesson": lesson
        })

        # 保存到旧系统
        self.improvement_engine._save_json(
            self.improvement_engine.optimization_file,
            self.improvement_engine.optimizations
        )

        # 🌳 同时保存到记忆树
        self.remember(
            key=f"经验教训: {lesson[:30]}",
            content=lesson,
            priority=priority,
            tags=["lesson", "manual"]
        )

    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def suggest_alternatives(self, current_skill: str, intent: str) -> List[Dict]:
        """建议替代技能方案"""
        alternatives = []

        # 从能力图谱查找
        for name, node in self.improvement_engine.capabilities["nodes"].items():
            if node.get("type") == "skill" and name != current_skill:
                # 检查是否可以处理相同意图
                skill_keywords = self.skill_matcher.skill_keywords.get(name, {}).get("keywords", [])
                if any(kw in intent.lower() for kw in skill_keywords):
                    alternatives.append({
                        "skill": name,
                        "efficiency": node.get("efficiency", 0.5),
                        "reason": f"可以处理 '{intent}' 类型的任务"
                    })

        # 按效率排序
        alternatives.sort(key=lambda x: x["efficiency"], reverse=True)
        return alternatives[:3]


def main():
    """测试工程师 Agent v3.0"""
    import io
    if sys.platform == 'win32':
        try:
            if hasattr(sys.stdout, 'buffer') and sys.stdout.buffer:
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        except (ValueError, AttributeError):
            pass

    engineer = EngineerAgent()

    print("=" * 60)
    print(f"[{engineer.name}] Agent v3.0 测试 - 记忆树版本")
    print("=" * 60)
    print()

    # 显示状态
    status = engineer.get_status()
    print(f"版本: {status['version']}")
    print(f"可用技能: {status['available_skills']} 个")
    print(f"历史经验: {status['improvement_data']['total_experiences']} 次")
    print(f"记忆树叶: {status['memory_tree']['total_leaves']} 片")
    print(f"树健康度: {status['memory_tree']['health_ratio']:.0%}")
    print()

    # 测试几个请求
    test_requests = [
        "帮我搜索 GitHub 上的工具",
        "生成 git commit",
        "写一个短剧剧本"
    ]

    for request in test_requests:
        print("-" * 60)
        result = engineer.execute_with_skill(request)
        print(engineer.format_response(result))

        # 模拟完成任务
        engineer.complete_task(success=True, outcome="任务完成成功")
        print()

    # 显示自我报告
    print("=" * 60)
    print(engineer.generate_self_report())


if __name__ == "__main__":
    main()
