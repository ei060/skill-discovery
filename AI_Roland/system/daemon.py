"""
AI Roland 守护进程 - 始终保持运行状态
功能：后台运行、定时任务、自动监控、日志记录
"""

import sys
import os
import time
import json
import logging
from datetime import datetime
from pathlib import Path
from threading import Thread
import subprocess

# 添加system目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class RolandDaemon:
    """AI Roland 守护进程"""

    def __init__(self):
        # 设置路径
        self.system_dir = Path(__file__).parent
        self.workspace = self.system_dir.parent
        self.log_dir = self.workspace / "logs"
        self.log_dir.mkdir(exist_ok=True)

        # 设置日志
        log_file = self.log_dir / f"daemon_{datetime.now().strftime('%Y%m%d')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()  # 同时输出到控制台
            ]
        )
        self.logger = logging.getLogger(__name__)

        # 导入引擎
        from engine import RolandEngine
        self.engine = RolandEngine()
        self.running = False

        # 心跳配置（秒）
        self.heartbeat_interval = 60
        self.cron_check_interval = 30

    def start(self):
        """启动守护进程"""
        self.logger.info("="*60)
        self.logger.info("AI Roland 守护进程启动")
        self.logger.info("="*60)
        self.logger.info(f"工作区: {self.workspace}")
        self.logger.info(f"心跳间隔: {self.heartbeat_interval}秒")
        self.logger.info(f"Cron检查间隔: {self.cron_check_interval}秒")
        self.logger.info("")

        self.running = True

        # 启动各个功能线程
        self.heartbeat_thread = Thread(target=self._heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()

        self.monitor_thread = Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

        self.cron_thread = Thread(target=self._cron_loop, daemon=True)
        self.cron_thread.start()

        # 记录启动状态
        self._save_status("running")

        self.logger.info("[OK] 守护进程已启动，所有功能线程已开启")
        self.logger.info("")

        # 主循环 - 保持运行
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("\n收到停止信号，正在关闭...")
            self.stop()

    def stop(self):
        """停止守护进程"""
        self.running = False
        self._save_status("stopped")
        self.engine.save_state()

        self.logger.info("[OK] 守护进程已停止")
        self.logger.info("="*60)

    def _heartbeat_loop(self):
        """心跳循环 - 定期自主思考"""
        while self.running:
            try:
                # 计算新的心跳计数
                current_count = self.engine.state.get('heartbeat_count', 0)
                new_count = current_count + 1
                timestamp = datetime.now().isoformat()

                self.logger.info(f"[Heartbeat] 心跳 #{new_count}")

                # 更新心跳计数到独立文件（不再覆盖 system_state.json）
                self.engine.save_heartbeat(new_count, timestamp)

                # 同时更新内存中的状态（用于读取）
                self.engine.state["heartbeat_count"] = new_count
                self.engine.state["last_heartbeat"] = timestamp

                # 自动更新任务统计
                self._update_task_stats()

                # 自主思考：检查待办任务
                self._autonomous_thinking()

                # 等待下一次心跳
                time.sleep(self.heartbeat_interval)

            except Exception as e:
                self.logger.error(f"[Heartbeat] 错误: {e}")

    def _update_task_stats(self):
        """自动更新任务统计"""
        try:
            from task_utils import TaskStats
            stats = TaskStats(self.workspace)
            stats.update_stats()
        except Exception as e:
            self.logger.warning(f"[Stats] 更新统计失败: {e}")

    def _autonomous_thinking(self):
        """自主思考 - 系统应该做什么"""
        thoughts = []

        # 检查任务
        if self.engine.tasks_file.exists():
            content = self.engine.tasks_file.read_text(encoding='utf-8')
            import re
            urgent_tasks = len(re.findall(r'\[ \].*(?:紧急|明天|后天)', content))
            total_tasks = len(re.findall(r'- \[ \]', content))

            if urgent_tasks > 0:
                thoughts.append(f"检测到 {urgent_tasks} 个紧急任务")
            if total_tasks > 10:
                thoughts.append(f"待办任务较多: {total_tasks} 个")

        # 检查是否需要发送提醒
        now = datetime.now()
        hour = now.hour

        # 早上9点：自动生成简报
        if hour == 9 and self.engine.state.get("last_daily_briefing"):
            from datetime import timedelta
            last_briefing = datetime.fromisoformat(self.engine.state["last_daily_briefing"])
            if (now - last_briefing) > timedelta(hours=8):
                thoughts.append("应该生成晨间简报")
                self._generate_briefing()

        # 记录思考
        if thoughts:
            self.logger.info(f"[Thinking] {', '.join(thoughts)}")

    def _monitor_loop(self):
        """监控循环 - 监控系统状态"""
        while self.running:
            try:
                # 检查任务文件变化
                # 检查内存使用
                # 检查日志文件大小
                # 等等

                time.sleep(300)  # 每5分钟检查一次

            except Exception as e:
                self.logger.error(f"[Monitor] 错误: {e}")

    def _cron_loop(self):
        """Cron 任务循环"""
        while self.running:
            try:
                # 检查是否有 cron 任务需要执行
                # 这里可以集成 croniter 或简单的定时检查

                # 检查是否是周日上午（数据维护提醒）
                now = datetime.now()
                if now.weekday() == 6 and now.hour == 10 and now.minute == 0:
                    last_reminder = self.engine.state.get("last_sunday_reminder")
                    if last_reminder:
                        from datetime import timedelta
                        last_reminder_date = datetime.fromisoformat(last_reminder).date()
                        if now.date() > last_reminder_date:
                            self.logger.info("[Cron] 触发周日数据维护提醒")
                            self._send_sunday_reminder()

                time.sleep(self.cron_check_interval)

            except Exception as e:
                self.logger.error(f"[Cron] 错误: {e}")

    def _generate_briefing(self):
        """生成每日简报"""
        from engine import Scheduler
        scheduler = Scheduler(self.engine)
        briefing = scheduler._generate_daily_briefing()

        # 保存简报到文件
        briefing_file = self.workspace / "logs" / f"briefing_{datetime.now().strftime('%Y%m%d')}.txt"
        briefing_file.write_text(briefing, encoding='utf-8')

        self.logger.info(f"[Briefing] 每日简报已生成: {briefing_file}")
        self.logger.info(f"[Briefing] 内容:\n{briefing}")

    def _send_sunday_reminder(self):
        """发送周日提醒"""
        reminder = """---
[Sunday Data Maintenance Reminder]

Tasks to complete this week:
1. Enter data for published content (views, interactions, etc.)
2. Analyze which content performed well and why
3. Update viral content library status

Start now?
---
"""

        # 保存提醒
        reminder_file = self.workspace / "logs" / f"sunday_reminder_{datetime.now().strftime('%Y%m%d')}.txt"
        reminder_file.write_text(reminder, encoding='utf-8')

        self.logger.info(f"[Reminder] 周日提醒已生成: {reminder_file}")

        # 更新状态
        self.engine.state["last_sunday_reminder"] = datetime.now().isoformat()
        self.engine.save_state()

    def _save_status(self, status):
        """保存守护进程状态"""
        status_file = self.workspace / "daemon_status.json"
        status_data = {
            "status": status,
            "pid": os.getpid(),
            "start_time": datetime.now().isoformat(),
            "heartbeat_interval": self.heartbeat_interval
        }
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, ensure_ascii=False, indent=2)

    def process_input(self, user_input):
        """处理用户输入（可被外部调用）"""
        try:
            response = self.engine.process_user_input(user_input)

            # 记录输入
            self.logger.info(f"[Input] {user_input}")
            if response.get("messages"):
                for msg in response["messages"]:
                    self.logger.info(f"[Response] {msg}")

            return response

        except Exception as e:
            self.logger.error(f"[Error] 处理输入失败: {e}")
            return {"error": str(e)}


def main():
    """主函数"""
    daemon = RolandDaemon()

    # 检查是否已有实例在运行
    status_file = daemon.workspace / "daemon_status.json"
    if status_file.exists():
        with open(status_file, 'r', encoding='utf-8') as f:
            status = json.load(f)
            if status.get("status") == "running":
                print("[WARNING] 检测到守护进程已在运行")
                print(f"  PID: {status.get('pid')}")
                print(f"  启动时间: {status.get('start_time')}")
                print()
                response = input("是否停止旧进程并启动新进程？(y/n): ")
                if response.lower() != 'y':
                    print("已取消启动")
                    return

    # 启动守护进程
    daemon.start()


if __name__ == "__main__":
    main()
