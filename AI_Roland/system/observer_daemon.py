#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI Roland v2.0 - Observer 后台进程

独立运行的观察分析服务，实时监控观察数据，
自动检测模式、创建本能并执行进化。

基于 ECC v2.1 Observer 代理
"""

import sys
import os
import io
import time
import json
import signal
import threading
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional

# 修复 Windows 编码
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

# 添加系统路径
system_path = Path(__file__).parent
sys.path.insert(0, str(system_path))

from homunculus_memory import HomunculusMemory, Instinct, Observation, Config


class ObserverDaemon:
    """Observer 后台守护进程

    功能:
    1. 实时监控观察数据
    2. 自动检测模式并创建本能
    3. 执行本能进化 (decay, cleanup, promote)
    4. 生成观察报告
    """

    def __init__(self, workspace=None):
        if workspace is None:
            workspace = Config.WORKSPACE

        self.workspace = Path(workspace)
        self.memory = HomunculusMemory(self.workspace)

        # 配置
        self.analysis_interval = 300  # 5分钟分析一次
        self.daily_check_hour = 3     # 每天3点执行维护
        self.observation_threshold = 10  # 最少观察数才分析

        # 状态
        self.running = False
        self.last_analysis_time = None
        self.last_daily_check = None

        # 统计
        self.stats = {
            "analyses_run": 0,
            "instincts_created": 0,
            "instincts_evolved": 0,
            "observations_processed": 0
        }

        # 日志文件
        self.log_file = self.workspace / "AI_Roland" / "logs" / "observer.log"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log(self, message: str, level: str = "INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}\n"

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)

        print(log_entry.strip())

    def analyze_observations(self) -> List[Instinct]:
        """分析观察记录，检测模式

        Returns:
            新创建的本能列表
        """
        observations = self.memory.get_observations(limit=200)

        if len(observations) < self.observation_threshold:
            self.log(f"观察记录不足 ({len(observations)}/{self.observation_threshold})，跳过分析", "DEBUG")
            return []

        self.log(f"开始分析 {len(observations)} 条观察记录", "INFO")

        # 统计工具使用模式
        tool_patterns = {}
        sequence_patterns = {}

        for i, obs in enumerate(observations):
            # 工具频率分析
            tool = obs.get('tool', '')
            if tool:
                if tool not in tool_patterns:
                    tool_patterns[tool] = {"count": 0, "contexts": []}
                tool_patterns[tool]["count"] += 1
                if obs.get('input'):
                    tool_patterns[tool]["contexts"].append(obs['input'][:100])

            # 序列模式分析 (连续的工具使用)
            if i > 0:
                prev_tool = observations[i-1].get('tool', '')
                if prev_tool and tool:
                    seq_key = f"{prev_tool} -> {tool}"
                    if seq_key not in sequence_patterns:
                        sequence_patterns[seq_key] = {"count": 0}
                    sequence_patterns[seq_key]["count"] += 1

        new_instincts = []

        # 从工具模式创建本能
        for tool, data in tool_patterns.items():
            if data["count"] >= 5:  # 重复5次以上
                # 清理工具名中的非法字符（Windows 文件名）
                safe_tool = tool.lower().replace(':', '-').replace('_', '-').replace('/', '-').replace('\\', '-')
                instinct_id = f"use-{safe_tool}"
                existing = self.memory.get_instinct(instinct_id)

                if not existing:
                    # 分析使用上下文
                    contexts = data["contexts"][-5:]  # 最近5次
                    context_sample = contexts[0] if contexts else ""

                    instinct = Instinct(
                        id=instinct_id,
                        trigger=f"当需要使用 {tool} 工具时",
                        action=f"使用 {tool} 工具完成操作",
                        confidence=0.7,
                        domain=tool,
                        source="observer-analysis",
                        lifecycle_stage="sprout"
                    )

                    self.memory.add_instinct(
                        id=instinct.id,
                        trigger=instinct.trigger,
                        action=instinct.action,
                        confidence=instinct.confidence,
                        domain=instinct.domain
                    )

                    new_instincts.append(instinct)
                    self.log(f"创建本能: {instinct.id} (基于 {data['count']} 次观察)", "INFO")

        # 从序列模式创建本能
        for seq, data in sequence_patterns.items():
            if data["count"] >= 3:  # 重复3次以上
                # 清理序列名中的非法字符（Windows 文件名）
                safe_seq = seq.lower().replace(' -> ', '-then-').replace(':', '-').replace('_', '-').replace('/', '-').replace('\\', '-')
                instinct_id = f"seq-{safe_seq}"
                existing = self.memory.get_instinct(instinct_id)

                if not existing:
                    tools = seq.split(" -> ")
                    instinct = Instinct(
                        id=instinct_id,
                        trigger=f"当使用 {tools[0]} 后需要继续操作时",
                        action=f"接着使用 {tools[1]} 工具",
                        confidence=0.75,
                        domain="sequence",
                        source="observer-sequence",
                        lifecycle_stage="sprout"
                    )

                    self.memory.add_instinct(
                        id=instinct.id,
                        trigger=instinct.trigger,
                        action=instinct.action,
                        confidence=instinct.confidence,
                        domain=instinct.domain
                    )

                    new_instincts.append(instinct)
                    self.log(f"创建序列本能: {instinct.id} (基于 {data['count']} 次观察)", "INFO")

        return new_instincts

    def run_daily_maintenance(self):
        """执行每日维护任务"""
        now = datetime.now()

        # 检查是否是维护时间
        if self.last_daily_check:
            last_check_date = self.last_daily_check.date()
            if last_check_date >= now.date():
                return  # 今天已经执行过

        if now.hour != self.daily_check_hour:
            return  # 不是维护时间

        self.log("开始每日维护任务", "INFO")

        # 1. 执行置信度衰减
        decayed = self.memory.decay_all()
        self.log(f"置信度衰减: {decayed}", "INFO")

        # 2. 清理枯萎本能
        cleaned = self.memory.cleanup_withered()
        self.log(f"清理枯萎本能: {cleaned}", "INFO")

        # 3. 生成每日报告
        self.generate_daily_report()

        self.last_daily_check = now
        self.stats["instincts_evolved"] += sum(decayed.values())
        self.stats["instincts_evolved"] += sum(cleaned.values())

    def generate_daily_report(self):
        """生成每日观察报告"""
        report = {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "project": self.memory.project,
            "stats": self.memory.stats.copy(),
            "observer_stats": self.stats.copy()
        }

        report_file = (self.workspace / "AI_Roland" / "logs" /
                      f"daily_report_{datetime.now().strftime('%Y%m%d')}.json")

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)

        self.log(f"每日报告已生成: {report_file}", "INFO")

    def check_and_analyze(self):
        """检查并执行分析"""
        now = datetime.now()

        # 检查是否需要分析
        if self.last_analysis_time:
            elapsed = (now - self.last_analysis_time).total_seconds()
            if elapsed < self.analysis_interval:
                return

        self.log("触发观察分析", "INFO")

        # 执行分析
        new_instincts = self.analyze_observations()

        # 更新统计
        self.stats["analyses_run"] += 1
        self.stats["instincts_created"] += len(new_instincts)

        self.last_analysis_time = now

        if new_instincts:
            self.log(f"本轮创建 {len(new_instincts)} 个新本能", "INFO")

    def run_once(self):
        """运行一次分析（用于测试）"""
        self.log("Observer 单次运行", "INFO")

        new_instincts = self.analyze_observations()
        self.stats["analyses_run"] += 1
        self.stats["instincts_created"] += len(new_instincts)

        return {
            "new_instincts": len(new_instincts),
            "total_instincts": self.memory.stats["total_instincts"],
            "observations": len(self.memory.get_observations())
        }

    def start(self):
        """启动 Observer 后台进程"""
        self.log("=" * 50, "INFO")
        self.log("AI Roland Observer Daemon 启动", "INFO")
        self.log(f"工作空间: {self.workspace}", "INFO")
        self.log(f"项目: {self.memory.project['name']} ({self.memory.project['id']})", "INFO")
        self.log("=" * 50, "INFO")

        self.running = True

        try:
            while self.running:
                # 检查并分析
                self.check_and_analyze()

                # 检查每日维护
                self.run_daily_maintenance()

                # 等待
                time.sleep(30)  # 每30秒检查一次

        except KeyboardInterrupt:
            self.log("\n收到停止信号，正在关闭...", "INFO")
        finally:
            self.stop()

    def stop(self):
        """停止 Observer"""
        self.running = False
        self.log(f"Observer 已停止", "INFO")
        self.log(f"运行统计: {self.stats}", "INFO")


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="AI Roland Observer Daemon")
    parser.add_argument('--workspace', default=None, help='工作目录')
    parser.add_argument('--once', action='store_true', help='运行一次后退出')
    parser.add_argument('--interval', type=int, default=300, help='分析间隔（秒）')

    args = parser.parse_args()

    observer = ObserverDaemon(args.workspace)
    if args.interval:
        observer.analysis_interval = args.interval

    if args.once:
        # 单次运行
        result = observer.run_once()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 持续运行
        observer.start()


if __name__ == "__main__":
    main()
