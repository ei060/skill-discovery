"""
AI Roland 记忆树训练工具
通过模拟搜索和重复使用来"培养"绿叶
"""

import sys
import os
import time
from pathlib import Path
from datetime import datetime

# 设置环境变量
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 添加system目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from memory_tree import MemoryTree


class MemoryTreeTrainer:
    """记忆树训练器 - 通过模拟使用培养绿叶"""

    # 常见搜索查询
    TRAINING_QUERIES = [
        "git commit",
        "搜索",
        "github",
        "用户偏好",
        "系统规则",
        "代码质量",
        "技能",
        "记忆管理",
        "短剧",
        "剧本",
        "创作",
        "浏览器",
        "自动化",
        "简报",
        "任务",
        "订票",
        "12306",
        "审查",
        "测试",
        "工具",
        "框架",
        "最佳实践"
    ]

    def __init__(self, workspace: Path = None):
        if workspace is None:
            workspace = Path(__file__).parent.parent

        self.workspace = workspace
        self.memory_tree = MemoryTree(workspace)

    def show_status(self):
        """显示当前状态"""
        print(self.memory_tree.get_status_report())

    def train_by_search(self, rounds: int = 5) -> dict:
        """
        通过搜索训练 - 模拟用户查询

        每次搜索命中会提升置信度 +0.03
        """
        print(f"\n🔍 搜索训练 ({rounds} 轮)")
        print("-" * 50)

        stats = {
            "total_searches": 0,
            "total_hits": 0,
            "confidence_gains": 0
        }

        for round_num in range(1, rounds + 1):
            print(f"\n[第 {round_num}/{rounds} 轮]")

            round_hits = 0
            round_gain = 0

            for query in self.TRAINING_QUERIES:
                results = self.memory_tree.search(query, top_k=3)

                stats["total_searches"] += 1

                if results:
                    round_hits += len(results)
                    for result in results:
                        old_conf = result["confidence"]
                        new_conf = min(1.0, old_conf + 0.03)
                        round_gain += (new_conf - old_conf)

                # 短暂延迟，避免过快
                time.sleep(0.01)

            stats["total_hits"] += round_hits
            stats["confidence_gains"] += round_gain

            print(f"  命中: {round_hits} 次")
            print(f"  置信度提升: {round_gain:.3f}")

        print(f"\n[搜索训练完成]")
        print(f"  总搜索: {stats['total_searches']}")
        print(f"  总命中: {stats['total_hits']}")
        print(f"  总提升: {stats['confidence_gains']:.3f}")

        return stats

    def train_by_usage(self, count: int = 10) -> dict:
        """
        通过使用训练 - 模拟调用知识

        每次使用会提升置信度 +0.08
        """
        print(f"\n⚡ 使用训练 ({count} 次)")
        print("-" * 50)

        # 获取活跃知识（非土壤状态）
        active_knowledge = [
            (kid, k) for kid, k in self.memory_tree.knowledge.items()
            if self.memory_tree.confidence[kid]["status"] != self.memory_tree.STATUS_SOIL
        ]

        if not active_knowledge:
            print("  [WARN] 没有可训练的知识")
            return {}

        # 选择最需要训练的知识（置信度较低的）
        sorted_knowledge = sorted(
            active_knowledge,
            key=lambda x: self.memory_tree.confidence[x[0]]["value"]
        )[:count]

        stats = {
            "total_uses": 0,
            "confidence_gains": 0
        }

        for kid, knowledge in sorted_knowledge:
            old_conf = self.memory_tree.confidence[kid]["value"]
            self.memory_tree.use_knowledge(kid)
            new_conf = self.memory_tree.confidence[kid]["value"]
            gain = new_conf - old_conf

            stats["total_uses"] += 1
            stats["confidence_gains"] += gain

            status = self.memory_tree._get_status_icon(
                self.memory_tree.confidence[kid]["status"]
            )
            print(f"  {status} {knowledge['key'][:30]} "
                  f"{old_conf:.2f} → {new_conf:.2f} (+{gain:.2f})")

        print(f"\n[使用训练完成]")
        print(f"  总使用: {stats['total_uses']}")
        print(f"  总提升: {stats['confidence_gains']:.3f}")

        return stats

    def train_by_marking(self, count: int = 3) -> dict:
        """
        通过标记重要训练 - 将知识设为 P0

        标记重要会直接设置置信度为 0.95
        """
        print(f"\n⭐ 标记重要训练 ({count} 条)")
        print("-" * 50)

        # 选择置信度最高但还未达到 P0 的知识
        candidates = []
        for kid, conf in self.memory_tree.confidence.items():
            if conf["status"] != self.memory_tree.STATUS_SOIL:
                knowledge = self.memory_tree.knowledge.get(kid)
                if knowledge:
                    candidates.append({
                        "id": kid,
                        "confidence": conf["value"],
                        "key": knowledge["key"]
                    })

        # 按置信度排序，选择最高的
        candidates.sort(key=lambda x: x["confidence"], reverse=True)
        selected = candidates[:count]

        stats = {
            "total_marked": 0,
            "before_avg": 0,
            "after_avg": 0
        }

        before_sum = sum(c["confidence"] for c in candidates)

        for item in selected:
            old_conf = item["confidence"]
            self.memory_tree.mark_important(item["id"])
            new_conf = self.memory_tree.confidence[item["id"]]["value"]

            print(f"  ⭐ {item['key'][:30]} "
                  f"{old_conf:.2f} → {new_conf:.2f}")
            stats["total_marked"] += 1

        after_sum = sum(
            self.memory_tree.confidence[c["id"]]["value"]
            for c in selected
        )

        stats["before_avg"] = before_sum / len(selected) if selected else 0
        stats["after_avg"] = after_sum / len(selected) if selected else 0

        print(f"\n[标记训练完成]")
        print(f"  标记数量: {stats['total_marked']}")
        print(f"  平均提升: {stats['before_avg']:.2f} → {stats['after_avg']:.2f}")

        return stats

    def full_training_session(self) -> dict:
        """完整训练会话"""
        print("=" * 60)
        print("🌳 AI Roland 记忆树训练会话")
        print("=" * 60)

        # 初始状态
        print("\n[初始状态]")
        self.show_status()

        initial_stats = self.memory_tree.stats.copy()

        # 训练阶段
        all_stats = {}

        # 1. 搜索训练（多轮）
        search_stats = self.train_by_search(rounds=3)
        all_stats["search"] = search_stats

        # 2. 使用训练
        usage_stats = self.train_by_usage(count=10)
        all_stats["usage"] = usage_stats

        # 3. 标记重要
        mark_stats = self.train_by_marking(count=3)
        all_stats["marking"] = mark_stats

        # 最终状态
        print("\n" + "=" * 60)
        print("[最终状态]")
        self.show_status()

        # 对比
        final_stats = self.memory_tree.stats

        print("\n" + "=" * 60)
        print("📊 训练效果")
        print("=" * 60)

        green_change = final_stats["green_leaves"] - initial_stats["green_leaves"]
        yellow_change = final_stats["yellow_leaves"] - initial_stats["yellow_leaves"]
        sprout_change = final_stats["sprouts"] - initial_stats["sprouts"]

        print(f"  🌱 萌芽: {initial_stats['sprouts']} → {final_stats['sprouts']} ({sprout_change:+d})")
        print(f"  🌿 绿叶: {initial_stats['green_leaves']} → {final_stats['green_leaves']} ({green_change:+d})")
        print(f"  🍂 黄叶: {initial_stats['yellow_leaves']} → {final_stats['yellow_leaves']} ({yellow_change:+d})")
        print(f"  🍁 枯叶: {initial_stats['withered_leaves']} → {final_stats['withered_leaves']}")

        if final_stats["total_leaves"] > 0:
            health_before = initial_stats["green_leaves"] / initial_stats["total_leaves"] if initial_stats["total_leaves"] > 0 else 0
            health_after = final_stats["green_leaves"] / final_stats["total_leaves"]
            print(f"\n  💚 健康度: {health_before:.1%} → {health_after:.1%}")

        return all_stats

    def simulate_days(self, days: int = 7):
        """
        模拟多天使用 - 包含衰减训练

        Args:
            days: 模拟天数
        """
        print(f"\n📅 模拟 {days} 天使用")
        print("-" * 50)

        for day in range(1, days + 1):
            print(f"\n[第 {day} 天]")

            # 每天进行搜索训练
            self.train_by_search(rounds=1)

            # 显示当前状态
            stats = self.memory_tree.stats
            print(f"  状态: 🌱{stats['sprouts']} 🌿{stats['green_leaves']} "
                  f"🍂{stats['yellow_leaves']} 🍁{stats['withered_leaves']}")

            # 执行衰减
            decay_result = self.memory_tree.decay_all()
            if decay_result["decayed"] > 0 or decay_result["withered"] > 0:
                print(f"  衰减: -{decay_result['decayed']} 片, "
                      f"{decay_result['withered']} 片枯萎")

            # 短暂延迟
            time.sleep(0.1)

        print(f"\n[模拟完成]")


def main():
    """主函数"""
    import io
    if sys.platform == 'win32':
        try:
            if hasattr(sys.stdout, 'buffer') and sys.stdout.buffer:
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        except (ValueError, AttributeError):
            pass

    trainer = MemoryTreeTrainer()

    # 运行完整训练会话
    stats = trainer.full_training_session()

    print("\n" + "=" * 60)
    print("✅ 训练会话完成!")
    print("=" * 60)
    print("\n💡 提示:")
    print("  - 绿叶越多，记忆树越健康")
    print("  - 定期使用能让知识保持常青")
    print("  - 不重要知识会自然衰减，这是正常的")
    print("  - 枯叶会被清理，精华会保存到土壤")


if __name__ == "__main__":
    main()
