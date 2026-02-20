"""
AI Roland 命令行界面 - 与自动化引擎交互
"""

import sys
import os

# 添加system目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import RolandEngine

class RolandCLI:
    """命令行交互界面"""

    def __init__(self):
        self.engine = RolandEngine()
        self.running = False

    def start(self):
        """启动CLI"""
        print("=" * 60)
        print("✓ AI Roland 自动化引擎已启动")
        print("=" * 60)
        print()
        print("可用命令：")
        print("  /help      - 显示帮助")
        print("  /status    - 查看系统状态")
        print("  /tasks     - 查看任务清单")
        print("  /briefing  - 生成每日简报")
        print("  /memory    - 查看记忆统计")
        print("  /quit      - 退出")
        print()
        print("或者直接输入你的想法，系统会自动识别意图...")
        print()

        self.running = True

        while self.running:
            try:
                user_input = input(">>> ").strip()

                if not user_input:
                    continue

                # 处理命令
                if user_input.startswith("/"):
                    self.handle_command(user_input)
                else:
                    # 处理普通输入
                    response = self.engine.process_user_input(user_input)
                    self.display_response(response)

            except KeyboardInterrupt:
                print("\n\n✓ 会话已结束")
                self.engine.end_session("用户主动退出")
                break
            except Exception as e:
                print(f"❌ 错误: {e}")

    def handle_command(self, command):
        """处理命令"""
        cmd = command.lower()

        if cmd == "/help":
            self.show_help()
        elif cmd == "/status":
            self.show_status()
        elif cmd == "/tasks":
            self.show_tasks()
        elif cmd == "/briefing":
            self.show_briefing()
        elif cmd == "/memory":
            self.show_memory_stats()
        elif cmd == "/quit":
            self.quit()
        else:
            print(f"❌ 未知命令: {command}")
            print("输入 /help 查看可用命令")

    def display_response(self, response):
        """显示系统响应"""
        print()

        # 显示消息
        for msg in response.get("messages", []):
            print(f"  {msg}")

        # 显示执行的操作
        actions = response.get("actions_taken", [])
        if actions:
            print("\n  执行的操作:")
            for action in actions:
                print(f"    • {action}")

        print()

    def show_help(self):
        """显示帮助"""
        print("""
📖 AI Roland 帮助
===================

自动化功能：
  • 时间意图自动捕获 - 说"明天"、"下周"等会自动添加到任务清单
  • 发布状态自动更新 - 说"已发布"会自动移动文件
  • 智能存储路由 - 创建文件会自动分类到正确位置
  • 每日简报 - 自动生成今日待办
  • 周日提醒 - 自动提醒数据维护

三层记忆架构：
  1. 情景记忆 - 记录具体事件和对话
  2. 语义记忆 - 提炼可复用的知识
  3. 强制规则 - 必须遵守的行为约束

使用示例：
  >>> 这篇文章明天要发布
  → 自动添加到任务清单（紧急重要）

  >>> 帮我写一篇关于LLM的文章
  → 自动保存到: 01-内容生产/选题管理/02-待发布/

  >>> /briefing
  → 显示今日待办清单
        """)

    def show_status(self):
        """显示系统状态"""
        print(f"""
📊 系统状态
===================

工作区: {self.engine.workspace}
记忆库: {self.engine.memory_lib}
任务文件: {self.engine.tasks_file}

当前会话: {self.engine.state.get('current_session', '无')}

最近活动：
  • 每日简报: {self.engine.state.get('last_daily_briefing', '未运行')}
  • 周日提醒: {self.engine.state.get('last_sunday_reminder', '未运行')}
  • 月记合并: {self.engine.state.get('last_monthly_merge', '未运行')}
        """)

    def show_tasks(self):
        """显示任务清单"""
        if self.engine.tasks_file.exists():
            content = self.engine.tasks_file.read_text(encoding='utf-8')
            print("\n📋 任务清单")
            print("=" * 60)
            print(content)
        else:
            print("❌ 任务清单文件不存在")

    def show_briefing(self):
        """显示每日简报"""
        from engine import Scheduler
        scheduler = Scheduler(self.engine)
        briefing = scheduler._generate_daily_briefing()
        print(briefing)

    def show_memory_stats(self):
        """显示记忆统计"""
        import os

        episodic_dir = self.engine.memory_lib / "情景记忆"
        semantic_dir = self.engine.memory_lib / "语义记忆"
        forced_dir = self.engine.memory_lib / "强制规则"

        def count_files(directory):
            if not directory.exists():
                return 0
            return len([f for f in directory.rglob("*") if f.is_file()])

        print(f"""
🧠 记忆库统计
===================

情景记忆: {count_files(episodic_dir)} 个文件
语义记忆: {count_files(semantic_dir)} 个文件
强制规则: {count_files(forced_dir)} 个文件

总计: {count_files(self.engine.memory_lib)} 个文件
        """)

    def quit(self):
        """退出"""
        print("\n✓ 正在保存状态...")
        self.engine.save_state()
        self.running = False
        print("✓ 再见！")


def main():
    """主函数"""
    cli = RolandCLI()
    cli.start()


if __name__ == "__main__":
    main()
