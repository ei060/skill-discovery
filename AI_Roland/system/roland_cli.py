#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI Roland v2.0 - 命令行工具集

提供 /evolve, /promote, /memory, /instincts 等命令
"""

import sys
import os
import io
import json
import argparse
from pathlib import Path
from datetime import datetime

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

from homunculus_memory import HomunculusMemory, Instinct, Config


class RolandCLI:
    """AI Roland 命令行工具"""

    def __init__(self, workspace=None):
        if workspace is None:
            workspace = Config.WORKSPACE

        self.workspace = Path(workspace)
        self.memory = HomunculusMemory(self.workspace)

    def cmd_evolve(self, instinct_id: str, boost: float = 0.1) -> dict:
        """进化指定本能

        Args:
            instinct_id: 本能ID
            boost: 提升的置信度

        Returns:
            操作结果
        """
        instinct = self.memory.get_instinct(instinct_id)

        if not instinct:
            return {
                "status": "error",
                "message": f"本能 '{instinct_id}' 不存在"
            }

        old_confidence = instinct.confidence
        old_stage = instinct.lifecycle_stage

        # 提升置信度
        new_confidence = min(1.0, old_confidence + boost)

        # 更新生命周期阶段
        if new_confidence >= Config.CONFIDENCE_GREEN:
            new_stage = "green"
        elif new_confidence >= Config.CONFIDENCE_SPROUT:
            new_stage = "sprout"
        elif new_confidence >= Config.CONFIDENCE_YELLOW_LOW:
            new_stage = "yellow"
        elif new_confidence >= Config.CONFIDENCE_WITHERED:
            new_stage = "withered"
        else:
            new_stage = "soil"

        # 更新本能
        self.memory.update_instinct(
            instinct_id=instinct_id,
            confidence=new_confidence,
            lifecycle_stage=new_stage
        )

        return {
            "status": "success",
            "instinct_id": instinct_id,
            "old_confidence": old_confidence,
            "new_confidence": new_confidence,
            "old_stage": old_stage,
            "new_stage": new_stage,
            "boost": boost
        }

    def cmd_promote(self, instinct_id: str) -> dict:
        """将项目本能提升为全局本能

        Args:
            instinct_id: 本能ID

        Returns:
            操作结果
        """
        instinct = self.memory.get_instinct(instinct_id)

        if not instinct:
            return {
                "status": "error",
                "message": f"本能 '{instinct_id}' 不存在"
            }

        if instinct.scope == "global":
            return {
                "status": "info",
                "message": f"本能 '{instinct_id}' 已经是全局本能"
            }

        # 检查提升条件
        if instinct.confidence < Config.PROMOTE_CONFIDENCE_THRESHOLD:
            return {
                "status": "error",
                "message": f"本能置信度不足 ({instinct.confidence:.2f} < {Config.PROMOTE_CONFIDENCE_THRESHOLD})"
            }

        # 提升到全局
        self.memory.promote_to_global(instinct_id)

        return {
            "status": "success",
            "instinct_id": instinct_id,
            "old_scope": instinct.scope,
            "new_scope": "global",
            "confidence": instinct.confidence
        }

    def cmd_memory(self) -> str:
        """获取记忆系统状态报告"""
        return self.memory.get_status_report()

    def cmd_instincts(self, filter_stage: str = None, filter_scope: str = None) -> list:
        """列出所有本能

        Args:
            filter_stage: 过滤生命周期阶段
            filter_scope: 过滤作用域

        Returns:
            本能列表
        """
        # 直接从 instincts 字典获取
        instincts = list(self.memory.instincts.values())

        if filter_stage:
            instincts = [i for i in instincts if i.lifecycle_stage == filter_stage]

        if filter_scope:
            instincts = [i for i in instincts if i.scope == filter_scope]

        return [
            {
                "id": i.id,
                "trigger": i.trigger[:50] + "..." if len(i.trigger) > 50 else i.trigger,
                "confidence": i.confidence,
                "stage": i.lifecycle_stage,
                "scope": i.scope,
                "domain": i.domain
            }
            for i in instincts
        ]

    def cmd_search(self, query: str) -> list:
        """搜索本能

        Args:
            query: 搜索关键词

        Returns:
            匹配的本能列表
        """
        results = self.memory.search(query, top_k=10)

        return [
            {
                "id": r["instinct"].id,
                "trigger": r["instinct"].trigger[:50] + "..." if len(r["instinct"].trigger) > 50 else r["instinct"].trigger,
                "confidence": r["instinct"].confidence,
                "stage": r["instinct"].lifecycle_stage,
                "score": r["score"]
            }
            for r in results
        ]

    def cmd_observations(self, limit: int = 20) -> list:
        """获取观察记录

        Args:
            limit: 返回数量

        Returns:
            观察记录列表
        """
        observations = self.memory.get_observations(limit)

        return [
            {
                "timestamp": o.get("timestamp"),
                "event": o.get("event"),
                "tool": o.get("tool"),
                "session": o.get("session")
            }
            for o in observations
        ]

    def cmd_decay(self) -> dict:
        """执行置信度衰减"""
        return self.memory.decay_all()

    def cmd_cleanup(self) -> dict:
        """清理枯萎本能"""
        return self.memory.cleanup_withered()

    def cmd_boost(self, instinct_id: str, amount: float = None) -> dict:
        """提升本能置信度（重要标记）

        Args:
            instinct_id: 本能ID
            amount: 提升量（默认使用 BOOST_IMPORTANT）

        Returns:
            操作结果
        """
        if amount is None:
            amount = Config.BOOST_IMPORTANT

        return self.cmd_evolve(instinct_id, amount)

    def cmd_analyze(self) -> dict:
        """触发观察分析"""
        new_instincts = self.memory.analyze_observations()

        return {
            "new_instincts": len(new_instincts),
            "instincts": [
                {
                    "id": i.id,
                    "trigger": i.trigger[:50]
                }
                for i in new_instincts
            ]
        }


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="AI Roland v2.0 命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
命令示例:
  roland evolve <instinct_id>              进化指定本能
  roland promote <instinct_id>             提升本能到全局
  roland memory                             查看记忆状态
  roland instincts --stage green            列出绿叶期本能
  roland search "git"                       搜索本能
  roland observations                       查看观察记录
  roland decay                              执行衰减
  roland cleanup                            清理枯萎本能
  roland boost <instinct_id>                重要标记本能
  roland analyze                            触发观察分析
        """
    )

    parser.add_argument('command', choices=[
        'evolve', 'promote', 'memory', 'instincts', 'search',
        'observations', 'decay', 'cleanup', 'boost', 'analyze'
    ], help='要执行的命令')
    parser.add_argument('arg', nargs='?', help='命令参数')
    parser.add_argument('--workspace', help='工作目录')
    parser.add_argument('--boost', type=float, help='提升量')
    parser.add_argument('--stage', help='过滤生命周期阶段')
    parser.add_argument('--scope', help='过滤作用域')
    parser.add_argument('--limit', type=int, default=20, help='返回数量限制')
    parser.add_argument('--json', action='store_true', help='JSON格式输出')

    args = parser.parse_args()

    # 初始化 CLI
    cli = RolandCLI(args.workspace)

    # 执行命令
    result = None

    if args.command == 'evolve':
        if not args.arg:
            print("错误: 请指定本能ID")
            return 1
        boost = args.boost if args.boost is not None else 0.1
        result = cli.cmd_evolve(args.arg, boost)

    elif args.command == 'promote':
        if not args.arg:
            print("错误: 请指定本能ID")
            return 1
        result = cli.cmd_promote(args.arg)

    elif args.command == 'memory':
        result = cli.cmd_memory()

    elif args.command == 'instincts':
        result = cli.cmd_instincts(args.stage, args.scope)

    elif args.command == 'search':
        if not args.arg:
            print("错误: 请指定搜索关键词")
            return 1
        result = cli.cmd_search(args.arg)

    elif args.command == 'observations':
        result = cli.cmd_observations(args.limit)

    elif args.command == 'decay':
        result = cli.cmd_decay()

    elif args.command == 'cleanup':
        result = cli.cmd_cleanup()

    elif args.command == 'boost':
        if not args.arg:
            print("错误: 请指定本能ID")
            return 1
        result = cli.cmd_boost(args.arg, args.boost)

    elif args.command == 'analyze':
        result = cli.cmd_analyze()

    # 输出结果
    if args.json or isinstance(result, (dict, list)):
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result)

    return 0


if __name__ == "__main__":
    sys.exit(main())
