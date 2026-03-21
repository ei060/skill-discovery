"""
AI Roland 历史数据迁移工具
将旧的经验数据迁移到记忆树系统
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# 设置环境变量
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 添加system目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from memory_tree import MemoryTree


class DataMigrator:
    """数据迁移器 - 旧系统到记忆树"""

    def __init__(self, workspace: Path = None):
        if workspace is None:
            workspace = Path(__file__).parent.parent

        self.workspace = workspace
        self.system_dir = workspace / "system"
        self.data_dir = self.system_dir / "improvement_data"

        # 初始化记忆树
        self.memory_tree = MemoryTree(workspace)

        # 迁移记录
        self.migration_log = []

    def migrate_experiences(self) -> int:
        """迁移经验数据库"""
        experience_file = self.data_dir / "experience_db.json"

        if not experience_file.exists():
            print(f"[SKIP] 经验数据库不存在: {experience_file}")
            return 0

        with open(experience_file, 'r', encoding='utf-8') as f:
            experiences = json.load(f)

        print(f"[INFO] 找到 {len(experiences)} 条经验记录")

        migrated = 0
        skipped = 0

        for exp in experiences:
            try:
                # 跳过已迁移的
                if self._is_already_migrated(exp.get("id", "")):
                    skipped += 1
                    continue

                # 构建知识内容
                content = self._format_experience(exp)

                # 根据成功率和使用次数决定优先级
                if exp.get("success", False):
                    # 成功且被多次引用的设为 P0
                    if exp.get("access_count", 0) >= 3:
                        priority = self.memory_tree.PRIORITY_P0
                    else:
                        priority = self.memory_tree.PRIORITY_P1
                else:
                    priority = self.memory_tree.PRIORITY_P2

                # 添加到记忆树
                kid = self.memory_tree.add_knowledge(
                    key=f"[迁移] {exp.get('request', exp.get('intent', 'task'))[:40]}",
                    content=content,
                    priority=priority,
                    category="migrated_experience",
                    tags=[exp.get("intent", ""), "migrated", exp.get("selected_skill", "")]
                )

                migrated += 1

                # 每10条显示进度
                if migrated % 10 == 0:
                    print(f"[PROGRESS] 已迁移 {migrated}/{len(experiences)}...")

            except Exception as e:
                print(f"[ERROR] 迁移失败: {e}")
                continue

        print(f"[OK] 经验迁移完成: {migrated} 条成功, {skipped} 条跳过")
        self.migration_log.append({
            "type": "experiences",
            "migrated": migrated,
            "skipped": skipped
        })

        return migrated

    def _is_already_migrated(self, exp_id: str) -> bool:
        """检查是否已迁移"""
        for kid, knowledge in self.memory_tree.knowledge.items():
            if knowledge.get("original_exp_id") == exp_id:
                return True
        return False

    def _format_experience(self, exp: dict) -> str:
        """格式化经验为知识内容"""
        lines = []
        lines.append(f"请求: {exp.get('request', 'N/A')}")
        lines.append(f"意图: {exp.get('intent', 'N/A')}")
        lines.append(f"技能: {exp.get('selected_skill', 'N/A')}")
        lines.append(f"结果: {'✅ 成功' if exp.get('success') else '❌ 失败'}")
        lines.append(f"耗时: {exp.get('duration', 0)} 秒")
        lines.append(f"时间: {exp.get('timestamp', 'N/A')}")

        if exp.get("outcome"):
            lines.append(f"结果: {exp['outcome']}")

        if exp.get("user_feedback"):
            lines.append(f"反馈: {exp['user_feedback']}")

        lessons = exp.get("lessons_learned", [])
        if lessons:
            lines.append("经验教训:")
            for lesson in lessons:
                lines.append(f"  • {lesson}")

        return "\n".join(lines)

    def migrate_patterns(self) -> int:
        """迁移成功模式"""
        pattern_file = self.data_dir / "success_patterns.json"

        if not pattern_file.exists():
            print(f"[SKIP] 成功模式文件不存在: {pattern_file}")
            return 0

        with open(pattern_file, 'r', encoding='utf-8') as f:
            patterns = json.load(f)

        print(f"[INFO] 找到 {len(patterns)} 个成功模式")

        migrated = 0

        for intent, pattern in patterns.items():
            try:
                content = f"""
成功模式: {intent}
最佳技能: {pattern.get('best_skill', 'N/A')}
置信度: {pattern.get('confidence', 0):.2%}
成功率: {pattern.get('success_rate', 0):.2%}
样本量: {pattern.get('sample_size', 0)} 次
最后更新: {pattern.get('last_updated', 'N/A')}
                """.strip()

                # 成功模式设为 P0（核心知识）
                self.memory_tree.add_knowledge(
                    key=f"[模式] {intent}最佳实践",
                    content=content,
                    priority=self.memory_tree.PRIORITY_P0,
                    category="success_pattern",
                    tags=[intent, "pattern", "best_practice"]
                )

                migrated += 1

            except Exception as e:
                print(f"[ERROR] 模式迁移失败: {e}")
                continue

        print(f"[OK] 模式迁移完成: {migrated} 个")
        self.migration_log.append({
            "type": "patterns",
            "migrated": migrated
        })

        return migrated

    def migrate_optimizations(self) -> int:
        """迁移优化记录"""
        opt_file = self.data_dir / "optimizations.json"

        if not opt_file.exists():
            print(f"[SKIP] 优化记录文件不存在: {opt_file}")
            return 0

        with open(opt_file, 'r', encoding='utf-8') as f:
            optimizations = json.load(f)

        migrated = 0

        # 迁移经验教训
        lessons = optimizations.get("lessons_learned", [])
        if lessons:
            print(f"[INFO] 找到 {len(lessons)} 条经验教训")

            for lesson in lessons[-50:]:  # 最近50条
                try:
                    self.memory_tree.add_knowledge(
                        key=f"[教训] {lesson.get('lesson', '')[:30]}",
                        content=lesson.get('lesson', ''),
                        priority=self.memory_tree.PRIORITY_P1,
                        category="lesson",
                        tags=["lesson", "optimization"]
                    )
                    migrated += 1
                except Exception as e:
                    print(f"[ERROR] 教训迁移失败: {e}")

        # 迁移错误记录
        mistakes = optimizations.get("mistakes", [])
        if mistakes:
            print(f"[INFO] 找到 {len(mistakes)} 条错误记录")

            for mistake in mistakes[-20:]:  # 最近20条
                try:
                    content = f"""
错误: {mistake.get('error', 'N/A')}
意图: {mistake.get('intent', 'N/A')}
失败技能: {mistake.get('failed_skill', 'N/A')}
教训: {mistake.get('lesson', 'N/A')}
                    """.strip()

                    self.memory_tree.add_knowledge(
                        key=f"[错误] {mistake.get('intent', '')[:30]}",
                        content=content,
                        priority=self.memory_tree.PRIORITY_P2,
                        category="mistake",
                        tags=["mistake", "error", mistake.get("intent", "")]
                    )
                    migrated += 1
                except Exception as e:
                    print(f"[ERROR] 错误迁移失败: {e}")

        print(f"[OK] 优化记录迁移完成: {migrated} 条")
        self.migration_log.append({
            "type": "optimizations",
            "migrated": migrated
        })

        return migrated

    def import_important_knowledge(self) -> int:
        """导入重要的用户偏好知识"""
        important_knowledge = [
            {
                "key": "用户沟通偏好",
                "content": """
• 用户喜欢简洁的回复
• 不要过度使用表情符号（除非特别要求）
• 代码质量优先于代码数量
• 不需要过度工程化
• 直接解决问题，不要绕圈子
• 遇到不确定时主动询问
                """.strip(),
                "priority": "P0",
                "tags": ["preference", "communication"]
            },
            {
                "key": "系统边界规则",
                "content": """
• 所有文件必须保存在 AI_Roland/ 目录内
• 不要将文件保存到工作区外
• 如果用户要求外部路径，建议正确的内部路径
• 只读操作可以访问外部文件
                """.strip(),
                "priority": "P0",
                "tags": ["rule", "boundary", "workspace"]
            },
            {
                "key": "代码质量原则",
                "content": """
• 直接修改问题代码，不要添加兼容性补丁
• 保持代码简洁，只实现当前需求
• 不在原有代码上加 if 分支"修复"问题
• 不过度抽象，不创建"以防万一"的功能
• 优先简单方案
                """.strip(),
                "priority": "P1",
                "tags": ["rule", "code_quality"]
            },
            {
                "key": "记忆管理原则",
                "content": """
• 每次会话结束时记录上下文使用情况
• 复杂任务拆分成多个会话
• 完成重大项目后必须创建记录
• 时间意图自动捕获（明天、下周等词汇）
• 发布状态自动更新
                """.strip(),
                "priority": "P1",
                "tags": ["rule", "memory", "workflow"]
            },
            {
                "key": "技能使用指南",
                "content": """
skill-discovery: 搜索发现工具
browser-control: 浏览器自动化
12306-booking: 火车票订票
smart-commit: Git提交
ai-code-review: 代码审查
short-drama-script: 短剧创作
daily-briefing: 每日简报
second-brain: 知识检索
ai-roland-secretary: 执行系统
                """.strip(),
                "priority": "P1",
                "tags": ["skill", "reference"]
            }
        ]

        migrated = 0
        for item in important_knowledge:
            try:
                # 映射优先级
                priority_map = {
                    "P0": self.memory_tree.PRIORITY_P0,
                    "P1": self.memory_tree.PRIORITY_P1,
                    "P2": self.memory_tree.PRIORITY_P2
                }

                self.memory_tree.add_knowledge(
                    key=item["key"],
                    content=item["content"],
                    priority=priority_map.get(item["priority"], self.memory_tree.PRIORITY_P2),
                    category="important_knowledge",
                    tags=item["tags"]
                )
                migrated += 1
            except Exception as e:
                print(f"[ERROR] 导入知识失败 ({item['key']}): {e}")

        print(f"[OK] 重要知识导入完成: {migrated} 条")
        self.migration_log.append({
            "type": "important_knowledge",
            "migrated": migrated
        })

        return migrated

    def save_migration_report(self):
        """保存迁移报告"""
        report_file = self.workspace / "记忆库" / f"迁移报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)

        report = {
            "migration_time": datetime.now().isoformat(),
            "log": self.migration_log,
            "tree_state_after": self.memory_tree.stats
        }

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"[OK] 迁移报告已保存: {report_file}")

    def run_full_migration(self):
        """执行完整迁移"""
        print("=" * 60)
        print("🔄 AI Roland 数据迁移工具")
        print("=" * 60)
        print()

        # 1. 导入重要知识
        print("[1/4] 导入重要知识...")
        self.import_important_knowledge()
        print()

        # 2. 迁移经验数据库
        print("[2/4] 迁移经验数据库...")
        self.migrate_experiences()
        print()

        # 3. 迁移成功模式
        print("[3/4] 迁移成功模式...")
        self.migrate_patterns()
        print()

        # 4. 迁移优化记录
        print("[4/4] 迁移优化记录...")
        self.migrate_optimizations()
        print()

        # 保存报告
        print("=" * 60)
        print("📊 迁移完成!")
        print("=" * 60)
        print()

        # 显示记忆树状态
        print(self.memory_tree.get_status_report())
        print()

        self.save_migration_report()


def main():
    """主函数"""
    import io
    if sys.platform == 'win32':
        try:
            if hasattr(sys.stdout, 'buffer') and sys.stdout.buffer:
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        except (ValueError, AttributeError):
            pass

    migrator = DataMigrator()
    migrator.run_full_migration()


if __name__ == "__main__":
    main()
