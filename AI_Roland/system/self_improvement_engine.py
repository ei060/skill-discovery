"""
AI Roland 自我迭代引擎
让工程师 Agent 能够自我学习、优化和进化
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import re

# 设置环境变量
os.environ['PYTHONIOENCODING'] = 'utf-8'


class SelfImprovementEngine:
    """自我迭代引擎 - 让 AI 持续进化"""

    def __init__(self, workspace: Path = None):
        if workspace is None:
            workspace = Path(__file__).parent.parent

        self.workspace = workspace
        self.system_dir = workspace / "system"

        # 数据存储路径
        self.data_dir = self.system_dir / "improvement_data"
        self.data_dir.mkdir(exist_ok=True)

        # 各类数据文件
        self.experience_file = self.data_dir / "experience_db.json"
        self.pattern_file = self.data_dir / "success_patterns.json"
        self.capability_file = self.data_dir / "capability_graph.json"
        self.optimization_file = self.data_dir / "optimizations.json"

        # 加载已有数据
        self.experiences = self._load_json(self.experience_file, [])
        self.patterns = self._load_json(self.pattern_file, {})
        self.capabilities = self._load_json(self.capability_file, {})
        self.optimizations = self._load_json(self.optimization_file, {})

        # 初始化能力图谱
        if not self.capabilities:
            self._init_capability_graph()

    def _load_json(self, path: Path, default=None):
        """安全加载 JSON"""
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return default if default is not None else {}

    def _save_json(self, path: Path, data: Any):
        """安全保存 JSON"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _init_capability_graph(self):
        """初始化能力图谱"""
        self.capabilities = {
            "nodes": {
                # 技能节点
                "skill-discovery": {"type": "skill", "efficiency": 0.8, "usage_count": 0},
                "browser-control": {"type": "skill", "efficiency": 0.7, "usage_count": 0},
                "smart-commit": {"type": "skill", "efficiency": 0.9, "usage_count": 0},
                "short-drama-script": {"type": "skill", "efficiency": 0.6, "usage_count": 0},
                "12306-booking": {"type": "skill", "efficiency": 0.5, "usage_count": 0},
                "second-brain": {"type": "skill", "efficiency": 0.8, "usage_count": 0},
                "ai-code-review": {"type": "skill", "efficiency": 0.7, "usage_count": 0},
                "daily-briefing": {"type": "skill", "efficiency": 0.9, "usage_count": 0},
                "ai-roland-secretary": {"type": "skill", "efficiency": 0.85, "usage_count": 0},
                # 能力节点
                "search": {"type": "capability", "sources": ["skill-discovery", "second-brain"]},
                "automation": {"type": "capability", "sources": ["browser-control", "12306-booking"]},
                "writing": {"type": "capability", "sources": ["short-drama-script", "smart-commit"]},
                "analysis": {"type": "capability", "sources": ["ai-code-review", "second-brain"]},
                "management": {"type": "capability", "sources": ["daily-briefing", "ai-roland-secretary"]}
            },
            "edges": [
                # 技能之间的关联
                {"from": "skill-discovery", "to": "browser-control", "strength": 0.6},
                {"from": "second-brain", "to": "skill-discovery", "strength": 0.5},
                {"from": "browser-control", "to": "12306-booking", "strength": 0.8},
                {"from": "smart-commit", "to": "ai-code-review", "strength": 0.7}
            ],
            "combinations": {
                # 发现的技能组合
                "search_automate": ["skill-discovery", "browser-control"],
                "analyze_improve": ["ai-code-review", "smart-commit"],
                "create_publish": ["short-drama-script", "smart-commit"]
            }
        }
        self._save_json(self.capability_file, self.capabilities)

    def record_experience(self, experience: Dict):
        """记录执行经验"""
        exp = {
            "id": self._generate_id(),
            "timestamp": datetime.now().isoformat(),
            "request": experience.get("request", ""),
            "intent": experience.get("intent", ""),
            "selected_skill": experience.get("skill", ""),
            "success": experience.get("success", True),
            "duration": experience.get("duration", 0),
            "outcome": experience.get("outcome", ""),
            "user_feedback": experience.get("feedback", ""),
            "lessons_learned": experience.get("lessons", [])
        }

        self.experiences.append(exp)
        self._save_json(self.experience_file, self.experiences)

        # 更新能力图谱
        self._update_capability_usage(exp["selected_skill"], exp["success"])

        # 提取模式
        self._extract_patterns()

        return exp["id"]

    def _generate_id(self) -> str:
        """生成唯一 ID"""
        import uuid
        return str(uuid.uuid4())[:8]

    def _update_capability_usage(self, skill: str, success: bool):
        """更新能力使用统计"""
        if skill in self.capabilities["nodes"]:
            node = self.capabilities["nodes"][skill]
            node["usage_count"] = node.get("usage_count", 0) + 1

            # 更新效率（成功率高则效率高）
            if "success_count" not in node:
                node["success_count"] = 0
            if success:
                node["success_count"] += 1

            total = node["usage_count"]
            successful = node["success_count"]
            node["efficiency"] = round(successful / total, 2) if total > 0 else 0.5

            self._save_json(self.capability_file, self.capabilities)

    def _extract_patterns(self):
        """从经验中提取成功模式"""
        if len(self.experiences) < 5:
            return

        # 按意图分组
        intent_groups = defaultdict(list)
        for exp in self.experiences:
            if exp["success"]:
                intent_groups[exp["intent"]].append(exp)

        # 提取每个意图的最佳实践
        for intent, exps in intent_groups.items():
            if len(exps) >= 2:
                # 找出最常用的技能
                skills = [e["selected_skill"] for e in exps]
                most_common = Counter(skills).most_common(1)[0]

                # 计算平均成功率
                success_rate = sum(1 for e in exps if e["success"]) / len(exps)

                self.patterns[intent] = {
                    "best_skill": most_common[0],
                    "confidence": most_common[1] / len(exps),
                    "success_rate": round(success_rate, 2),
                    "sample_size": len(exps),
                    "last_updated": datetime.now().isoformat()
                }

        self._save_json(self.pattern_file, self.patterns)

    def find_optimization_opportunities(self) -> List[Dict]:
        """主动发现优化机会"""
        opportunities = []

        # 1. 检查低效技能
        for name, node in self.capabilities["nodes"].items():
            if node.get("type") == "skill":
                if node["usage_count"] >= 5 and node["efficiency"] < 0.7:
                    opportunities.append({
                        "type": "low_efficiency",
                        "target": name,
                        "current_efficiency": node["efficiency"],
                        "suggestion": f"技能 {name} 的效率低于 70%，建议检查使用方式或寻找替代方案"
                    })

        # 2. 检查未使用的技能组合
        discovered_combos = set()
        for exp in self.experiences[-50:]:  # 最近50次执行
            skills_used = [exp["selected_skill"]]
            # 检查是否有其他技能也被使用过
            for other in self.experiences[-50:]:
                if (other["id"] != exp["id"] and
                    abs(datetime.fromisoformat(exp["timestamp"]) -
                        datetime.fromisoformat(other["timestamp"])).seconds < 300):
                    skills_used.append(other["selected_skill"])
            if len(skills_used) > 1:
                discovered_combos.add(tuple(sorted(set(skills_used))))

        # 3. 检查重复问题
        recent_issues = defaultdict(int)
        for exp in self.experiences[-100:]:
            if not exp["success"]:
                key = f"{exp['intent']}_{exp['selected_skill']}"
                recent_issues[key] += 1

        for issue, count in recent_issues.items():
            if count >= 3:
                intent, skill = issue.split("_")
                opportunities.append({
                    "type": "recurring_issue",
                    "intent": intent,
                    "skill": skill,
                    "occurrences": count,
                    "suggestion": f"意图 '{intent}' 使用技能 '{skill}' 反复失败，建议重新评估技能匹配"
                })

        # 4. 发现新的技能组合潜力
        intent_skills = defaultdict(set)
        for exp in self.experiences:
            intent_skills[exp["intent"]].add(exp["selected_skill"])

        for intent, skills in intent_skills.items():
            if len(skills) > 1:
                opportunities.append({
                    "type": "combination_potential",
                    "intent": intent,
                    "skills": list(skills),
                    "suggestion": f"意图 '{intent}' 可以使用多种技能，考虑建立技能组合策略"
                })

        return opportunities

    def suggest_optimization(self, request: str, intent: str, context: Dict = None) -> Optional[Dict]:
        """基于当前情况建议优化方案"""
        # 查找历史相似情况
        similar = self._find_similar_experiences(request, intent)

        if not similar:
            return None

        # 分析最佳实践
        successful = [s for s in similar if s["success"]]
        if not successful:
            return None

        # 找出最成功的方案
        best = max(successful, key=lambda x: x.get("success_rate", 0.5))

        return {
            "recommended_approach": best.get("selected_skill"),
            "confidence": best.get("success_rate", 0.5),
            "reasoning": f"基于 {len(similar)} 次相似经验",
            "expected_duration": best.get("avg_duration", "未知")
        }

    def _find_similar_experiences(self, request: str, intent: str, limit: int = 10) -> List[Dict]:
        """查找相似的历史经验"""
        keywords = self._extract_keywords(request)

        similar = []
        for exp in self.experiences[-200:]:  # 查看最近200次
            if exp["intent"] == intent:
                # 计算关键词重叠度
                exp_keywords = self._extract_keywords(exp["request"])
                overlap = len(set(keywords) & set(exp_keywords))
                if overlap > 0:
                    similar.append({
                        **exp,
                        "keyword_overlap": overlap
                    })

        # 按重叠度排序
        similar.sort(key=lambda x: x["keyword_overlap"], reverse=True)
        return similar[:limit]

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单分词
        words = re.findall(r'\w+', text.lower())
        # 过滤停用词
        stopwords = {'的', '是', '在', '有', '和', '我', '你', '他', '她', '它', 'help', 'please', 'the', 'a', 'an'}
        return [w for w in words if len(w) > 2 and w not in stopwords]

    def discover_new_combinations(self) -> List[Dict]:
        """发现新的技能组合机会"""
        combinations = []

        # 分析技能共现模式
        skill_pairs = defaultdict(int)
        skill_success = defaultdict(int)

        for i, exp1 in enumerate(self.experiences[-100:]):
            if not exp1["success"]:
                continue
            for exp2 in self.experiences[i+1:i+11]:  # 10次执行内的关联
                if exp2["success"]:
                    pair = tuple(sorted([exp1["selected_skill"], exp2["selected_skill"]]))
                    if exp1["selected_skill"] != exp2["selected_skill"]:
                        skill_pairs[pair] += 1
                        skill_success[pair] += 1

        # 找出高频组合
        for pair, count in skill_pairs.items():
            if count >= 3 and pair not in self.capabilities["combinations"].values():
                combinations.append({
                    "skills": list(pair),
                    "co_occurrence": count,
                    "success_rate": round(skill_success[pair] / (count * 2), 2),
                    "potential_use": self._infer_combination_use(list(pair))
                })

        return combinations

    def _infer_combination_use(self, skills: List[str]) -> str:
        """推断技能组合的用途"""
        # 基于技能描述推断组合用途
        descriptions = {
            "skill-discovery": "搜索工具",
            "browser-control": "浏览器操作",
            "smart-commit": "代码提交",
            "short-drama-script": "剧本创作",
            "12306-booking": "订票",
            "second-brain": "知识查询",
            "ai-code-review": "代码审查",
            "daily-briefing": "简报",
            "ai-roland-secretary": "任务管理"
        }

        uses = {
            ("skill-discovery", "browser-control"): "自动化搜索和测试工具",
            ("smart-commit", "ai-code-review"): "代码提交流程优化",
            ("short-drama-script", "browser-control"): "内容发布自动化",
            ("second-brain", "skill-discovery"): "智能工具推荐",
            ("daily-briefing", "ai-roland-secretary"): "任务管理自动化"
        }

        key = tuple(sorted(skills))
        return uses.get(key, "协同完成复杂任务")

    def generate_self_report(self) -> str:
        """生成自我迭代报告"""
        lines = []
        lines.append("=" * 60)
        lines.append("[自我迭代报告]")
        lines.append("=" * 60)
        lines.append("")

        # 统计数据
        total_exp = len(self.experiences)
        successful = sum(1 for e in self.experiences if e["success"])
        success_rate = round(successful / total_exp, 2) if total_exp > 0 else 0

        lines.append(f"[执行统计]")
        lines.append(f"  总经验数: {total_exp}")
        lines.append(f"  成功率: {success_rate:.1%}")
        lines.append(f"  已识别模式: {len(self.patterns)}")
        lines.append("")

        # 最常用的技能
        skill_usage = defaultdict(int)
        for exp in self.experiences:
            skill_usage[exp["selected_skill"]] += 1

        lines.append(f"[最常用技能]")
        for skill, count in Counter(skill_usage).most_common(5):
            lines.append(f"  {skill}: {count} 次")
        lines.append("")

        # 优化机会
        opportunities = self.find_optimization_opportunities()
        if opportunities:
            lines.append(f"[发现的优化机会] ({len(opportunities)})")
            for opp in opportunities[:5]:
                lines.append(f"  • {opp['suggestion']}")
            lines.append("")

        # 新组合
        combinations = self.discover_new_combinations()
        if combinations:
            lines.append(f"[新技能组合] ({len(combinations)})")
            for combo in combinations[:3]:
                lines.append(f"  • {' + '.join(combo['skills'])}")
                lines.append(f"    用途: {combo['potential_use']}")
            lines.append("")

        # 效率趋势
        lines.append("[效率趋势]")
        recent = self.experiences[-50:] if len(self.experiences) >= 50 else self.experiences
        if recent:
            recent_success = sum(1 for e in recent if e["success"])
            recent_rate = round(recent_success / len(recent), 2)
            lines.append(f"  近期成功率: {recent_rate:.1%}")
            lines.append(f"  趋势: {'↑ 提升' if recent_rate > success_rate else '↓ 下降' if recent_rate < success_rate else '→ 稳定'}")
        lines.append("")

        lines.append("=" * 60)

        return "\n".join(lines)

    def apply_optimization(self, optimization_id: str) -> bool:
        """应用优化建议"""
        opportunities = self.find_optimization_opportunities()

        for opp in opportunities:
            if str(hash(opp["suggestion"])) == optimization_id:
                # 记录优化应用
                if "optimizations_applied" not in self.optimizations:
                    self.optimizations["optimizations_applied"] = []

                self.optimizations["optimizations_applied"].append({
                    "id": optimization_id,
                    "type": opp["type"],
                    "applied_at": datetime.now().isoformat(),
                    "description": opp["suggestion"]
                })

                self._save_json(self.optimization_file, self.optimizations)
                return True

        return False

    def get_recommendation(self, context: Dict) -> Optional[Dict]:
        """基于上下文主动推荐解决方案"""
        request = context.get("request", "")
        intent = context.get("intent", "")

        # 1. 检查是否有成功模式
        if intent in self.patterns:
            pattern = self.patterns[intent]
            return {
                "type": "pattern_match",
                "confidence": pattern["confidence"],
                "suggestion": f"使用 {pattern['best_skill']} 技能",
                "success_rate": pattern["success_rate"],
                "reason": "历史上此意图的成功模式"
            }

        # 2. 检查技能组合
        combinations = self.discover_new_combinations()
        if combinations:
            best = max(combinations, key=lambda x: x["co_occurrence"])
            return {
                "type": "combination",
                "suggestion": f"组合使用 {' + '.join(best['skills'])}",
                "potential_use": best["potential_use"],
                "reason": "发现这些技能经常一起使用"
            }

        # 3. 基于能力图谱推荐
        if intent in self.capabilities["nodes"]:
            # 这是一个能力节点，推荐其源技能
            node = self.capabilities["nodes"][intent]
            if "sources" in node:
                sources = node["sources"]
                return {
                    "type": "capability_sources",
                    "suggestion": f"从以下技能中选择: {', '.join(sources)}",
                    "reason": f"{intent} 能力可以通过这些技能实现"
                }

        return None

    def learn_from_mistake(self, experience: Dict):
        """从失败中学习"""
        mistake = {
            "id": self._generate_id(),
            "timestamp": datetime.now().isoformat(),
            "request": experience.get("request", ""),
            "intent": experience.get("intent", ""),
            "failed_skill": experience.get("skill", ""),
            "error": experience.get("error", ""),
            "corrective_action": experience.get("correction", ""),
            "lesson": experience.get("lesson", "")
        }

        if "mistakes" not in self.optimizations:
            self.optimizations["mistakes"] = []

        self.optimizations["mistakes"].append(mistake)
        self._save_json(self.optimization_file, self.optimizations)

        # 更新模式：避免重复错误
        key = f"{mistake['intent']}_{mistake['failed_skill']}"
        if "avoid_patterns" not in self.patterns:
            self.patterns["avoid_patterns"] = {}

        self.patterns["avoid_patterns"][key] = {
            "reason": mistake["lesson"],
            "alternative": mistake.get("alternative_skill", ""),
            "occurrences": self.patterns["avoid_patterns"].get(key, {}).get("occurrences", 0) + 1
        }

        self._save_json(self.pattern_file, self.patterns)


def main():
    """测试自我迭代引擎"""
    import io
    if sys.platform == 'win32':
        try:
            if hasattr(sys.stdout, 'buffer') and sys.stdout.buffer:
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        except (ValueError, AttributeError):
            pass

    engine = SelfImprovementEngine()

    # 模拟一些经验
    sample_experiences = [
        {"request": "搜索 GitHub 工具", "intent": "search", "skill": "skill-discovery", "success": True, "duration": 5},
        {"request": "搜索 GitHub 工具", "intent": "search", "skill": "skill-discovery", "success": True, "duration": 4},
        {"request": "浏览器爬取", "intent": "automation", "skill": "browser-control", "success": True, "duration": 8},
        {"request": "浏览器爬取", "intent": "automation", "skill": "browser-control", "success": False, "duration": 15},
        {"request": "git commit", "intent": "write", "skill": "smart-commit", "success": True, "duration": 3},
    ]

    for exp in sample_experiences:
        engine.record_experience(exp)

    print(engine.generate_self_report())


if __name__ == "__main__":
    main()
