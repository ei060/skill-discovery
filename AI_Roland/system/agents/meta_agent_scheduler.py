#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Meta-Agent 自动化调度

集成到 AI Roland Daemon，实现自动化的反思和学习
"""

import sys
import os
import time
import threading
from pathlib import Path
from datetime import datetime

# 简化的调度器（不依赖外部库）

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

from agents.meta_agent import MetaAgent, get_meta_agent


class MetaAgentScheduler:
    """Meta-Agent 调度器（简化版，不依赖外部库）"""

    def __init__(self):
        self.meta_agent = get_meta_agent()
        self.running = False
        self.thread = None

        # 上次执行时间
        self.last_daily_review = None
        self.last_weekly_opt = None
        self.last_cross_learn = None

    def daily_review_job(self):
        """每日审查任务"""
        try:
            print(f"\n[{datetime.now()}] 🔔 触发每日审查...")
            self.meta_agent.daily_review()
            self.last_daily_review = datetime.now()
            print(f"[{datetime.now()}] ✅ 每日审查完成")
        except Exception as e:
            print(f"[{datetime.now()}] ❌ 每日审查失败: {e}")

    def weekly_optimization_job(self):
        """每周优化任务"""
        try:
            print(f"\n[{datetime.now()}] 🔔 触发每周优化...")
            self.meta_agent.weekly_optimization()
            self.last_weekly_opt = datetime.now()
            print(f"[{datetime.now()}] ✅ 每周优化完成")
        except Exception as e:
            print(f"[{datetime.now()}] ❌ 每周优化失败: {e}")

    def cross_learning_job(self):
        """跨Agent学习任务（每3天）"""
        try:
            print(f"\n[{datetime.now()}] 🔔 触发跨Agent学习...")
            results = self.meta_agent.cross_agent_learning()
            self.last_cross_learn = datetime.now()
            print(f"[{datetime.now()}] ✅ 跨学习完成 - "
                  f"{len(results['best_practices_shared'])}条最佳实践")
        except Exception as e:
            print(f"[{datetime.now()}] ❌ 跨学习失败: {e}")

    def _should_run_daily(self):
        """检查是否应该执行每日审查"""
        now = datetime.now()
        if now.hour == 9 and now.minute == 0:
            if self.last_daily_review is None or (now - self.last_daily_review).days >= 1:
                return True
        return False

    def _should_run_weekly(self):
        """检查是否应该执行每周优化"""
        now = datetime.now()
        if now.weekday() == 0 and now.hour == 3 and now.minute == 0:  # 周一03:00
            if self.last_weekly_opt is None or (now - self.last_weekly_opt).days >= 7:
                return True
        return False

    def _should_run_cross_learn(self):
        """检查是否应该执行跨Agent学习"""
        if self.last_cross_learn is None:
            return True
        # 每3天执行一次
        if (datetime.now() - self.last_cross_learn).days >= 3:
            return True
        return False

    def start(self):
        """启动调度器"""
        if self.running:
            print("调度器已在运行")
            return

        self.running = True

        print("="*70)
        print("🤖 Meta-Agent 调度器已启动")
        print("="*70)
        print("📅 调度计划：")
        print("   - 每日 09:00：Agent审查")
        print("   - 每周一 03:00：记忆优化")
        print("   - 每3天：跨Agent学习")
        print("="*70)

        # 在后台线程运行
        def run_scheduler():
            while self.running:
                try:
                    if self._should_run_daily():
                        self.daily_review_job()
                    elif self._should_run_weekly():
                        self.weekly_optimization_job()
                    elif self._should_run_cross_learn():
                        self.cross_learning_job()
                except Exception as e:
                    print(f"[ERROR] 调度器异常: {e}")

                time.sleep(60)  # 每分钟检查一次

        self.thread = threading.Thread(target=run_scheduler, daemon=True)
        self.thread.start()

    def stop(self):
        """停止调度器"""
        self.running = False
        print("🛑 Meta-Agent 调度器已停止")

    def run_once(self, mode='daily'):
        """手动执行一次任务"""
        if mode == 'daily':
            self.daily_review_job()
        elif mode == 'weekly':
            self.weekly_optimization_job()
        elif mode == 'cross':
            self.cross_learning_job()


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="Meta-Agent 调度器")
    parser.add_argument('--start', action='store_true', help='启动调度器')
    parser.add_argument('--stop', action='store_true', help='停止调度器')
    parser.add_argument('--daily', action='store_true', help='执行每日审查')
    parser.add_argument('--weekly', action='store_true', help='执行每周优化')
    parser.add_argument('--cross', action='store_true', help='执行跨Agent学习')

    args = parser.parse_args()

    scheduler = MetaAgentScheduler()

    if args.start:
        scheduler.start()
        print("\n按 Ctrl+C 停止调度器...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            scheduler.stop()

    elif args.stop:
        scheduler.stop()

    elif args.daily:
        scheduler.run_once('daily')

    elif args.weekly:
        scheduler.run_once('weekly')

    elif args.cross:
        scheduler.run_once('cross')

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
