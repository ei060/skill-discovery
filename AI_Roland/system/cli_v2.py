"""
AI Roland 增强版命令行界面 v2.0
集成所有新功能：Heartbeat, Cron, Browser, Telegram, API, MCP
"""

import sys
import os

# 添加system目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine_v2 import RolandEngineV2

class RolandCLIV2:
    """增强版命令行交互界面"""

    def __init__(self):
        self.engine = RolandEngineV2()
        self.running = False

    def start(self):
        """启动 CLI"""
        self.print_header()
        self.show_menu()

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
                print("\n\n[OK] 会话已结束")
                self.shutdown()
                break
            except Exception as e:
                print(f"[ERROR] {e}")

    def print_header(self):
        """打印头部信息"""
        print("=" * 70)
        print("AI Roland v2.0 - 增强版")
        print("=" * 70)
        print()
        print("新增功能:")
        print("  [Heartbeat] 自主思考循环")
        print("  [Cron]     灵活定时任务")
        print("  [Brain]    认知状态追踪")
        print("  [Browser]  浏览器自动化")
        print("  [Telegram] 手机远程控制")
        print("  [API]      HTTP 接口")
        print("  [MCP]      工具暴露")
        print()

    def show_menu(self):
        """显示菜单"""
        print("可用命令:")
        print("  基础:")
        print("    /help        - 显示帮助")
        print("    /status      - 查看系统状态")
        print("    /tasks       - 查看任务清单")
        print("    /briefing    - 生成每日简报")
        print("    /memory      - 查看记忆统计")
        print()
        print("  新增:")
        print("    /heartbeat   - 心跳控制")
        print("    /cron        - Cron 任务管理")
        print("    /brain       - 认知状态")
        print("    /commit      - 创建 commit")
        print("    /search      - 网页搜索")
        print("    /telegram    - Telegram 操作")
        print("    /api         - API 控制")
        print()
        print("  系统:")
        print("    /quit        - 退出")
        print()
        print("或者直接输入你的想法，系统会自动识别意图...")
        print()

    def handle_command(self, command):
        """处理命令"""
        cmd = command.lower().split()

        if cmd[0] == "/help":
            self.show_help()
        elif cmd[0] == "/status":
            self.show_status()
        elif cmd[0] == "/tasks":
            self.show_tasks()
        elif cmd[0] == "/briefing":
            self.show_briefing()
        elif cmd[0] == "/memory":
            self.show_memory_stats()
        elif cmd[0] == "/heartbeat":
            self.handle_heartbeat(cmd[1:] if len(cmd) > 1 else [])
        elif cmd[0] == "/cron":
            self.handle_cron(cmd[1:] if len(cmd) > 1 else [])
        elif cmd[0] == "/brain":
            self.handle_brain(cmd[1:] if len(cmd) > 1 else [])
        elif cmd[0] == "/commit":
            self.handle_commit(cmd[1:] if len(cmd) > 1 else [])
        elif cmd[0] == "/search":
            self.handle_search(cmd[1:] if len(cmd) > 1 else [])
        elif cmd[0] == "/telegram":
            self.handle_telegram(cmd[1:] if len(cmd) > 1 else [])
        elif cmd[0] == "/api":
            self.handle_api(cmd[1:] if len(cmd) > 1 else [])
        elif cmd[0] == "/quit":
            self.quit()
        else:
            print(f"[ERROR] 未知命令: {command}")
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
                if isinstance(action, dict):
                    print(f"    - {action.get('action', 'unknown')}")
                else:
                    print(f"    - {action}")

        print()

    # ===== 基础命令 =====

    def show_help(self):
        """显示帮助"""
        print("""
[HELP] AI Roland v2.0 帮助
==========================

基础功能：
  /status      - 查看系统运行状态
  /tasks       - 查看任务清单
  /briefing    - 生成每日简报
  /memory      - 查看记忆统计

新增功能：
  /heartbeat start [秒]  - 启动心跳循环
  /heartbeat stop        - 停止心跳循环
  /cron list             - 列出所有 cron 任务
  /cron add <表达式> <动作>  - 添加 cron 任务
  /brain show            - 显示认知状态
  /brain emotion <值>    - 更新情绪状态
  /commit <消息>         - 创建 commit
  /search <关键词>       - 网页搜索
  /telegram send <消息>  - 发送 Telegram 消息
  /api start             - 启动 API 服务器

自动化功能：
  时间意图捕获 - 说"明天"、"下周"等自动添加任务
  发布状态更新 - 说"已发布"自动移动文件
  智能存储路由 - 自动分类文件到正确位置

示例：
  >>> 明天要写报告
  >>> /heartbeat start 30
  >>> /cron add "0 9 * * *" daily_briefing
  >>> /search Python 最新进展
  >>> /commit 完成了项目重构
        """)

    def show_status(self):
        """显示系统状态"""
        print(f"""
[STATUS] 系统状态
===================

工作区: {self.engine.workspace}
记忆库: {self.engine.memory_lib}
大脑: {self.engine.brain_dir}

运行状态:
  心跳运行: {self.engine._heartbeat_running}
  心跳计数: {self.engine.state.get('heartbeat_count', 0)}
  上次心跳: {self.engine.state.get('last_heartbeat', '未运行')}

最近活动:
  每日简报: {self.engine.state.get('last_daily_briefing', '未运行')}
  周日提醒: {self.engine.state.get('last_sunday_reminder', '未运行')}

认知状态:
  情绪: {self.engine.cognitive_state.get_emotion()}
        """)

    def show_tasks(self):
        """显示任务清单"""
        if self.engine.tasks_file.exists():
            content = self.engine.tasks_file.read_text(encoding='utf-8')
            print("\n[TASKS] 任务清单")
            print("=" * 70)
            print(content)
        else:
            print("[ERROR] 任务清单文件不存在")

    def show_briefing(self):
        """显示每日简报"""
        from engine import Scheduler
        scheduler = Scheduler(self.engine)
        briefing = scheduler._generate_daily_briefing()
        print(briefing)

    def show_memory_stats(self):
        """显示记忆统计"""
        episodic_dir = self.engine.memory_lib / "情景记忆"
        semantic_dir = self.engine.memory_lib / "语义记忆"
        forced_dir = self.engine.memory_lib / "强制规则"

        def count_files(directory):
            if not directory.exists():
                return 0
            return len([f for f in directory.rglob("*") if f.is_file()])

        print(f"""
[MEMORY] 记忆库统计
===================

情景记忆: {count_files(episodic_dir)} 个文件
语义记忆: {count_files(semantic_dir)} 个文件
强制规则: {count_files(forced_dir)} 个文件

总计: {count_files(self.engine.memory_lib)} 个文件

认知状态:
  记忆日志: {self.engine.brain_dir / 'memory.jsonl'}
  Commit 历史: {self.engine.cognitive_state.commit_file}
        """)

    # ===== 新增命令 =====

    def handle_heartbeat(self, args):
        """处理心跳命令"""
        if not args:
            # 显示心跳状态
            status = "运行中" if self.engine._heartbeat_running else "已停止"
            print(f"[HEARTBEAT] 状态: {status}")
            print(f"  计数: {self.engine.state.get('heartbeat_count', 0)}")
            print(f"  上次: {self.engine.state.get('last_heartbeat', 'N/A')}")
            print()
            print("用法:")
            print("  /heartbeat start [秒]  - 启动心跳（默认60秒）")
            print("  /heartbeat stop        - 停止心跳")
            return

        if args[0] == "start":
            interval = int(args[1]) if len(args) > 1 else 60
            self.engine.start_heartbeat(interval)
            print(f"[OK] 心跳已启动（间隔: {interval}秒）")

        elif args[0] == "stop":
            self.engine.stop_heartbeat()
            print("[OK] 心跳已停止")

        else:
            print("[ERROR] 未知参数")
            print("用法: /heartbeat [start|stop] [间隔]")

    def handle_cron(self, args):
        """处理 cron 命令"""
        if not args:
            # 列出所有 cron 任务
            jobs = self.engine.cron_manager.list_jobs()
            print(f"[CRON] 定时任务 ({len(jobs)} 个)")
            print("=" * 70)
            for job in jobs:
                status = "启用" if job.get("enabled", True) else "禁用"
                print(f"  [{status}] {job['name']}")
                print(f"        表达式: {job['cron']}")
                print(f"        动作: {job['action']}")
                print(f"        下次运行: {job.get('next_run', 'N/A')}")
                print()
            return

        if args[0] == "list":
            self.handle_cron([])

        elif args[0] == "add":
            if len(args) < 3:
                print("[ERROR] 缺少参数")
                print("用法: /cron add <cron表达式> <动作> [名称]")
                return

            cron_expr = args[1]
            action = args[2]
            name = args[3] if len(args) > 3 else f"任务-{len(self.engine.cron_manager.list_jobs()) + 1}"

            job = self.engine.cron_manager.add_job(name, cron_expr, action)
            print(f"[OK] Cron 任务已添加:")
            print(f"  名称: {name}")
            print(f"  表达式: {cron_expr}")
            print(f"  动作: {action}")
            print(f"  下次运行: {job.get('next_run')}")

        else:
            print("[ERROR] 未知参数")
            print("用法: /cron [list|add]")

    def handle_brain(self, args):
        """处理认知状态命令"""
        if not args:
            self.handle_brain(["show"])
            return

        if args[0] == "show":
            emotion = self.engine.cognitive_state.get_emotion()
            print("[BRAIN] 认知状态")
            print("=" * 70)
            print(f"情绪状态:")
            for key, value in emotion.items():
                print(f"  {key}: {value}")
            print()
            print(f"心跳计数: {self.engine.state.get('heartbeat_count', 0)}")

        elif args[0] == "emotion":
            if len(args) < 2:
                print("[ERROR] 缺少参数")
                print("用法: /brain emotion <energy|focus|stress|satisfaction> <值>")
                return

            key = args[1]
            value = float(args[2])

            emotion = self.engine.cognitive_state.get_emotion()
            emotion[key] = value
            self.engine.cognitive_state.update_emotion(emotion)

            print(f"[OK] 情绪已更新: {key} = {value}")

        else:
            print("[ERROR] 未知参数")
            print("用法: /brain [show|emotion]")

    def handle_commit(self, args):
        """处理 commit 命令"""
        if not args:
            print("[ERROR] 缺少 commit 消息")
            print("用法: /commit <消息>")
            return

        message = " ".join(args)
        timestamp = self.engine.cognitive_state.commit(message)

        print(f"[OK] Commit 已创建:")
        print(f"  时间: {timestamp}")
        print(f"  消息: {message}")

    def handle_search(self, args):
        """处理搜索命令"""
        if not args:
            print("[ERROR] 缺少搜索关键词")
            print("用法: /search <关键词>")
            return

        query = " ".join(args)
        print(f"[SEARCH] 搜索: {query}")
        result = self.engine.browser.search(query)
        print(f"[OK] {result.get('status', 'unknown')}")

    def handle_telegram(self, args):
        """处理 Telegram 命令"""
        if not args:
            print("[TELEGRAM] Telegram 操作")
            print("用法:")
            print("  /telegram send <消息>  - 发送消息")
            print("  /telegram briefing     - 发送每日简报")
            return

        if args[0] == "send":
            if len(args) < 2:
                print("[ERROR] 缺少消息内容")
                return

            from telegram_bot import TelegramBot
            bot = TelegramBot(self.engine)
            message = " ".join(args[1:])
            result = bot.send_message(message)
            print(f"[OK] {result}")

        elif args[0] == "briefing":
            from telegram_bot import TelegramBot
            bot = TelegramBot(self.engine)
            result = bot.send_daily_briefing()
            print(f"[OK] {result}")

        else:
            print("[ERROR] 未知参数")
            print("用法: /telegram [send|briefing]")

    def handle_api(self, args):
        """处理 API 命令"""
        if not args:
            print("[API] API 服务器控制")
            print("用法:")
            print("  /api start  - 启动 API 服务器")
            return

        if args[0] == "start":
            print("[INFO] 启动 API 服务器...")
            print("[INFO] 在新窗口中运行: python http_api.py")
            import subprocess
            subprocess.Popen(["python", "http_api.py"],
                           cwd=os.path.dirname(os.path.abspath(__file__)))
            print("[OK] API 服务器已启动（在新窗口中）")
            print("[INFO] 访问 http://localhost:3000 查看文档")

        else:
            print("[ERROR] 未知参数")
            print("用法: /api [start]")

    # ===== 系统命令 =====

    def quit(self):
        """退出"""
        print("\n[OK] 正在关闭系统...")
        self.shutdown()
        print("[OK] 再见！")

    def shutdown(self):
        """关闭系统"""
        # 停止心跳
        if self.engine._heartbeat_running:
            self.engine.stop_heartbeat()

        # 保存状态
        self.engine.save_state()

        # 标记不运行
        self.running = False


def main():
    """主函数"""
    cli = RolandCLIV2()
    cli.start()


if __name__ == "__main__":
    main()
