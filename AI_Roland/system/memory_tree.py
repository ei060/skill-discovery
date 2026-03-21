"""
AI Roland 记忆树系统 (Memory-Like-A-Tree)
基于 https://github.com/loryoncloud/memory-like-a-tree
让记忆像树一样自然生长、新陈代谢
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import re

# 设置环境变量
os.environ['PYTHONIOENCODING'] = 'utf-8'


class MemoryTree:
    """
    记忆树系统 - 让 AI 的记忆像树一样生长

    生命周期:
    🌱 萌芽 (0.7) → 🌿 绿叶 (≥0.8) → 🍂 黄叶 (0.5-0.8) → 🍁 枯叶 (<0.3) → 🪨 土壤 (0)
                      ↑                                              ↓
                      └──────────── 精华回流，滋养新知识 ──────────────┘
    """

    # 状态定义
    STATUS_SPROUT = "sprout"      # 🌱 萌芽
    STATUS_GREEN = "green"        # 🌿 绿叶
    STATUS_YELLOW = "yellow"      # 🍂 黄叶
    STATUS_WITHERED = "withered"  # 🍁 枯叶
    STATUS_SOIL = "soil"          # 🪨 土壤

    # 置信度阈值
    CONFIDENCE_SPROUT = 0.7
    CONFIDENCE_GREEN = 0.8
    CONFIDENCE_YELLOW_LOW = 0.5
    CONFIDENCE_WITHERED = 0.3
    CONFIDENCE_SOIL = 0.0

    # 优先级定义
    PRIORITY_P0 = "P0"  # 核心知识，永不衰减
    PRIORITY_P1 = "P1"  # 重要知识，缓慢衰减
    PRIORITY_P2 = "P2"  # 普通知识，正常衰减

    # 置信度变化值
    BOOST_SEARCH = 0.03      # 被搜索命中
    BOOST_USE = 0.08        # 被引用使用
    BOOST_IMPORTANT = 0.95   # 人工确认重要

    DECAY_P2_DAILY = 0.008   # P2 每天衰减
    DECAY_P1_DAILY = 0.004   # P1 每天衰减
    DECAY_P0_DAILY = 0.0     # P0 不衰减

    def __init__(self, workspace: Path = None):
        if workspace is None:
            workspace = Path(__file__).parent.parent

        self.workspace = workspace
        self.system_dir = workspace / "system"

        # 数据目录
        self.data_dir = self.system_dir / "memory_tree"
        self.data_dir.mkdir(exist_ok=True)

        # 数据文件
        self.knowledge_file = self.data_dir / "knowledge_db.json"
        self.confidence_file = self.data_dir / "confidence_db.json"
        self.soil_file = self.data_dir / "soil_db.json"  # 归档的精华

        # 加载数据
        self.knowledge = self._load_json(self.knowledge_file, {})
        self.confidence = self._load_json(self.confidence_file, {})
        self.soil = self._load_json(self.soil_file, {})

        # 统计数据
        self.stats = {
            "total_leaves": 0,
            "sprouts": 0,
            "green_leaves": 0,
            "yellow_leaves": 0,
            "withered_leaves": 0,
            "soil_count": len(self.soil)
        }

        self._update_stats()

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

    def add_knowledge(self, key: str, content: str, priority: str = None,
                     category: str = "general", tags: List[str] = None) -> str:
        """
        添加新知识（萌芽）

        Args:
            key: 知识键名
            content: 知识内容
            priority: 优先级 (P0/P1/P2)
            category: 分类
            tags: 标签列表

        Returns:
            知识ID
        """
        if priority is None:
            priority = self.PRIORITY_P2
        import uuid
        knowledge_id = str(uuid.uuid4())[:8]

        timestamp = datetime.now().isoformat()

        self.knowledge[knowledge_id] = {
            "id": knowledge_id,
            "key": key,
            "content": content,
            "priority": priority,
            "category": category,
            "tags": tags or [],
            "created_at": timestamp,
            "last_accessed": timestamp,
            "access_count": 0,
            "parent_soil_id": None  # 如果是从土壤复苏的，记录来源
        }

        # 新知识以萌芽状态开始
        self.confidence[knowledge_id] = {
            "value": self.CONFIDENCE_SPROUT,
            "status": self.STATUS_SPROUT,
            "last_updated": timestamp,
            "history": [
                {"action": "create", "value": self.CONFIDENCE_SPROUT, "timestamp": timestamp}
            ]
        }

        self._save_json(self.knowledge_file, self.knowledge)
        self._save_json(self.confidence_file, self.confidence)
        self._update_stats()

        return knowledge_id

    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        搜索知识（每次搜索命中会提升置信度）

        Args:
            query: 搜索关键词
            top_k: 返回结果数量

        Returns:
            匹配的知识列表
        """
        results = []
        query_lower = query.lower()

        for kid, knowledge in self.knowledge.items():
            # 跳过已归档的知识
            if self.confidence[kid]["status"] == self.STATUS_SOIL:
                continue

            # 计算匹配分数
            score = 0

            # 标题匹配
            if query_lower in knowledge["key"].lower():
                score += 10

            # 内容匹配
            if query_lower in knowledge["content"].lower():
                score += 5

            # 标签匹配
            for tag in knowledge.get("tags", []):
                if query_lower in tag.lower():
                    score += 3

            if score > 0:
                # 获取置信度加成
                confidence = self.confidence[kid]["value"]
                score = score * (1 + confidence)

                results.append({
                    "knowledge_id": kid,
                    "score": score,
                    "confidence": confidence,
                    "status": self.confidence[kid]["status"],
                    "knowledge": knowledge
                })

        # 按分数排序
        results.sort(key=lambda x: x["score"], reverse=True)

        # 提升命中知识的置信度
        for result in results[:top_k]:
            self._boost_confidence(result["knowledge_id"], self.BOOST_SEARCH, "search")
            # 更新访问记录
            self.knowledge[result["knowledge_id"]]["last_accessed"] = datetime.now().isoformat()
            self.knowledge[result["knowledge_id"]]["access_count"] += 1

        self._save_json(self.knowledge_file, self.knowledge)
        self._save_json(self.confidence_file, self.confidence)

        return results[:top_k]

    def use_knowledge(self, knowledge_id: str) -> bool:
        """
        使用知识（大幅提升置信度）

        Args:
            knowledge_id: 知识ID

        Returns:
            是否成功
        """
        if knowledge_id not in self.knowledge:
            return False

        if self.confidence[knowledge_id]["status"] == self.STATUS_SOIL:
            return False

        self._boost_confidence(knowledge_id, self.BOOST_USE, "use")
        self.knowledge[knowledge_id]["last_accessed"] = datetime.now().isoformat()
        self.knowledge[knowledge_id]["access_count"] += 1

        self._save_json(self.knowledge_file, self.knowledge)
        self._save_json(self.confidence_file, self.confidence)
        self._update_stats()

        return True

    def mark_important(self, knowledge_id: str) -> bool:
        """
        标记为重要（提升到高置信度）

        Args:
            knowledge_id: 知识ID

        Returns:
            是否成功
        """
        if knowledge_id not in self.knowledge:
            return False

        self._boost_confidence(knowledge_id, self.BOOST_IMPORTANT, "manual")
        self.knowledge[knowledge_id]["priority"] = self.PRIORITY_P0  # 提升为最高优先级

        self._save_json(self.knowledge_file, self.knowledge)
        self._save_json(self.confidence_file, self.confidence)
        self._update_stats()

        return True

    def _boost_confidence(self, knowledge_id: str, boost_amount: float, reason: str):
        """提升置信度"""
        current = self.confidence[knowledge_id]["value"]

        if boost_amount >= 1.0:
            # 直接设置
            new_value = boost_amount
        else:
            # 累加
            new_value = min(1.0, current + boost_amount)

        self._update_confidence(knowledge_id, new_value, reason)

    def _update_confidence(self, knowledge_id: str, new_value: float, reason: str):
        """更新置信度并同步状态"""
        old_status = self.confidence[knowledge_id]["status"]
        timestamp = datetime.now().isoformat()

        # 确定新状态
        if new_value >= self.CONFIDENCE_GREEN:
            new_status = self.STATUS_GREEN
        elif new_value >= self.CONFIDENCE_YELLOW_LOW:
            new_status = self.STATUS_YELLOW
        elif new_value > self.CONFIDENCE_WITHERED:
            new_status = self.STATUS_SPROUT
        else:
            new_status = self.STATUS_WITHERED

        # 更新置信度记录
        self.confidence[knowledge_id]["value"] = new_value
        self.confidence[knowledge_id]["status"] = new_status
        self.confidence[knowledge_id]["last_updated"] = timestamp
        self.confidence[knowledge_id]["history"].append({
            "action": reason,
            "old_value": self.confidence[knowledge_id]["value"],
            "new_value": new_value,
            "old_status": old_status,
            "new_status": new_status,
            "timestamp": timestamp
        })

    def decay_all(self) -> Dict[str, int]:
        """
        执行每日衰减

        Returns:
            衰减统计
        """
        stats = {
            "decayed": 0,
            "withered": 0,
            "protected": 0
        }

        now = datetime.now()
        timestamp = now.isoformat()

        for kid, conf in self.confidence.items():
            # 跳过已归档的
            if conf["status"] == self.STATUS_SOIL:
                continue

            knowledge = self.knowledge.get(kid)
            if not knowledge:
                continue

            # 根据优先级决定衰减量
            priority = knowledge.get("priority", self.PRIORITY_P2)

            if priority == self.PRIORITY_P0:
                # P0 不衰减
                stats["protected"] += 1
                continue

            decay_amount = self.DECAY_P2_DAILY if priority == self.PRIORITY_P2 else self.DECAY_P1_DAILY
            new_value = max(0, conf["value"] - decay_amount)

            if new_value != conf["value"]:
                old_status = conf["status"]
                self._update_confidence(kid, new_value, f"daily_decay_{priority}")

                if conf["status"] == self.STATUS_WITHERED and old_status != self.STATUS_WITHERED:
                    stats["withered"] += 1
                else:
                    stats["decayed"] += 1

        self._save_json(self.confidence_file, self.confidence)
        self._update_stats()

        return stats

    def cleanup_withered(self) -> Dict[str, any]:
        """
        清理枯叶（归档到土壤）

        Returns:
            清理统计
        """
        stats = {
            "archived": 0,
            "essence_extracted": 0
        }

        to_archive = []

        # 找出所有枯叶
        for kid, conf in self.confidence.items():
            if conf["status"] == self.STATUS_WITHERED:
                to_archive.append(kid)

        # 处理每片枯叶
        for kid in to_archive:
            knowledge = self.knowledge.get(kid)
            if not knowledge:
                continue

            # 提取精华
            essence = self._extract_essence(knowledge, kid)

            # 移到土壤
            soil_id = f"soil_{kid}"
            self.soil[soil_id] = {
                "id": soil_id,
                "original_id": kid,
                "essence": essence,
                "original_content": knowledge["content"],
                "archived_at": datetime.now().isoformat(),
                "access_count": knowledge.get("access_count", 0),
                "category": knowledge.get("category", "unknown")
            }

            # 从活跃知识中移除
            del self.knowledge[kid]
            self.confidence[kid]["status"] = self.STATUS_SOIL
            self.confidence[kid]["value"] = self.CONFIDENCE_SOIL

            stats["archived"] += 1
            if essence:
                stats["essence_extracted"] += 1

        self._save_json(self.knowledge_file, self.knowledge)
        self._save_json(self.confidence_file, self.confidence)
        self._save_json(self.soil_file, self.soil)
        self._update_stats()

        return stats

    def _extract_essence(self, knowledge: Dict, kid: str) -> str:
        """提取知识精华"""
        content = knowledge["content"]

        # 提取第一行作为标题
        lines = content.strip().split('\n')
        title = lines[0] if lines else ""

        # 提取关键信息
        key_points = []

        # 查找带标记的要点
        for line in lines:
            line = line.strip()
            if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                key_points.append(line)
            elif line.startswith('#'):
                key_points.append(line)

        # 构建精华
        if key_points:
            essence = f"{title}\n" + "\n".join(key_points[:5])  # 最多5个要点
        else:
            # 如果没有明显要点，取前100字
            essence = content[:100] + "..." if len(content) > 100 else content

        return essence

    def search_soil(self, query: str) -> List[Dict]:
        """搜索土壤中的归档知识"""
        results = []
        query_lower = query.lower()

        for soil_id, soil in self.soil.items():
            score = 0

            if query_lower in soil["essence"].lower():
                score += 5
            if query_lower in soil.get("category", "").lower():
                score += 2

            if score > 0:
                results.append({
                    "soil_id": soil_id,
                    "score": score,
                    "soil": soil
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def revive_from_soil(self, soil_id: str) -> Optional[str]:
        """从土壤中复苏知识"""
        if soil_id not in self.soil:
            return None

        soil = self.soil[soil_id]

        # 重新创建为萌芽
        new_id = self.add_knowledge(
            key=f"[复苏] {soil['essence'][:30]}",
            content=soil["original_content"],
            priority=self.PRIORITY_P1,  # 复苏的知识给予较高优先级
            category=soil.get("category", "revived"),
            tags=["revived", "from_soil"]
        )

        # 记录来源
        self.knowledge[new_id]["parent_soil_id"] = soil_id

        return new_id

    def _update_stats(self):
        """更新统计数据"""
        self.stats = {
            "total_leaves": len([k for k, v in self.confidence.items()
                               if v["status"] != self.STATUS_SOIL]),
            "sprouts": len([k for k, v in self.confidence.items()
                          if v["status"] == self.STATUS_SPROUT]),
            "green_leaves": len([k for k, v in self.confidence.items()
                              if v["status"] == self.STATUS_GREEN]),
            "yellow_leaves": len([k for k, v in self.confidence.items()
                               if v["status"] == self.STATUS_YELLOW]),
            "withered_leaves": len([k for k, v in self.confidence.items()
                                  if v["status"] == self.STATUS_WITHERED]),
            "soil_count": len(self.soil)
        }

    def get_status_report(self) -> str:
        """获取状态报告"""
        self._update_stats()

        lines = []
        lines.append("╔════════════════════════════════════════════════════════════╗")
        lines.append("║                    🌳 AI Roland 记忆树                     ║")
        lines.append("╚════════════════════════════════════════════════════════════╝")
        lines.append("")
        lines.append("📊 树的状态")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append(f"  🌱 萌芽: {self.stats['sprouts']} 片")
        lines.append(f"  🌿 绿叶: {self.stats['green_leaves']} 片")
        lines.append(f"  🍂 黄叶: {self.stats['yellow_leaves']} 片")
        lines.append(f"  🍁 枯叶: {self.stats['withered_leaves']} 片")
        lines.append(f"  🪨 土壤: {self.stats['soil_count']} 份精华")
        lines.append(f"  ─────────────────────────────────────")
        lines.append(f"  总计: {self.stats['total_leaves']} 片叶子")
        lines.append("")

        # 健康度
        if self.stats['total_leaves'] > 0:
            health_ratio = self.stats['green_leaves'] / self.stats['total_leaves']
            lines.append(f"💚 树的健康度: {health_ratio:.1%}")
            if health_ratio > 0.6:
                lines.append("   状态: 茂盛 🌳")
            elif health_ratio > 0.3:
                lines.append("   状态: 健康 🌿")
            else:
                lines.append("   状态: 需要关注 🍂")
        lines.append("")

        # 最近活动
        lines.append("🕐 最近活动")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # 获取最近访问的知识
        recent_accessed = sorted(
            [(k, v) for k, v in self.knowledge.items()],
            key=lambda x: x[1].get("last_accessed", ""),
            reverse=True
        )[:5]

        for kid, knowledge in recent_accessed:
            conf = self.confidence.get(kid, {})
            status_icon = self._get_status_icon(conf.get("status", ""))
            lines.append(f"  {status_icon} {knowledge['key'][:40]}")

        lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append(f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        return "\n".join(lines)

    def _get_status_icon(self, status: str) -> str:
        """获取状态图标"""
        icons = {
            self.STATUS_SPROUT: "🌱",
            self.STATUS_GREEN: "🌿",
            self.STATUS_YELLOW: "🍂",
            self.STATUS_WITHERED: "🍁",
            self.STATUS_SOIL: "🪨"
        }
        return icons.get(status, "📄")

    def import_from_experience_db(self) -> int:
        """从旧的经验数据库导入"""
        old_exp_file = self.system_dir / "improvement_data" / "experience_db.json"

        if not old_exp_file.exists():
            return 0

        try:
            old_experiences = self._load_json(old_exp_file, [])
            imported = 0

            for exp in old_experiences:
                # 跳过已导入的
                if any(k.get("original_exp_id") == exp.get("id")
                      for k in self.knowledge.values()):
                    continue

                # 转换为知识
                key = exp.get("request", "")[:50] or "未命名经验"
                content = f"""
请求: {exp.get('request', '')}
意图: {exp.get('intent', '')}
技能: {exp.get('selected_skill', '')}
结果: {'成功' if exp.get('success') else '失败'}
经验: {exp.get('lessons_learned', [])}
                """.strip()

                self.add_knowledge(
                    key=key,
                    content=content,
                    priority=self.PRIORITY_P1 if exp.get("success") else self.PRIORITY_P2,
                    category="experience",
                    tags=["imported", exp.get("intent", "")]
                )
                imported += 1

            return imported
        except Exception as e:
            print(f"[ERROR] 导入失败: {e}")
            return 0


def main():
    """测试记忆树系统"""
    import sys
    import io
    if sys.platform == 'win32':
        try:
            if hasattr(sys.stdout, 'buffer') and sys.stdout.buffer:
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        except (ValueError, AttributeError):
            pass

    tree = MemoryTree()

    print("=" * 60)
    print("🌳 AI Roland 记忆树系统 - 测试")
    print("=" * 60)
    print()

    # 添加一些测试知识
    print("📝 添加测试知识...")
    tree.add_knowledge(
        key="Git 提交规范",
        content="使用约定式提交: feat: 新功能, fix: 修复, docs: 文档",
        priority="P1",
        tags=["git", "development"]
    )

    tree.add_knowledge(
        key="用户偏好",
        content="用户喜欢简洁的回复，不要使用表情符号（除非特别要求）",
        priority="P0",
        tags=["preference", "communication"]
    )

    tree.add_knowledge(
        key="临时笔记",
        content="这是一个不太重要的临时笔记",
        priority="P2",
        tags=["temp"]
    )

    print("✅ 已添加 3 条知识\n")

    # 显示状态
    print(tree.get_status_report())
    print()

    # 测试搜索
    print("🔍 测试搜索 'git'...")
    results = tree.search("git")
    for r in results:
        status = tree._get_status_icon(r["status"])
        print(f"  {status} {r['knowledge']['key']} (置信度: {r['confidence']:.2f})")
    print()

    # 模拟衰减
    print("⏰ 模拟一天后的衰减...")
    decay_stats = tree.decay_all()
    print(f"  衰减: {decay_stats['decayed']} 条")
    print(f"  枯萎: {decay_stats['withered']} 条")
    print()

    print(tree.get_status_report())


if __name__ == "__main__":
    main()
