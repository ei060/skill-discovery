#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI Roland v2.0 - 命令别名系统

提供快捷命令别名，简化常用操作。

别名映射:
  /m  -> memory     (查看记忆状态)
  /i  -> instincts  (列出本能)
  /s  -> search     (搜索本能)
  /e  -> evolve     (进化本能)
  /p  -> promote    (提升到全局)
  /b  -> boost      (重要标记)
  /o  -> observations (查看观察记录)
  /a  -> analyze    (触发分析)
  /d  -> decay      (置信度衰减)
  /c  -> cleanup    (清理枯萎)
  /h  -> help       (显示帮助)
"""

import sys
import os
import io
import subprocess
from pathlib import Path

# 修复 Windows 编码
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass


class RolandAlias:
    """AI Roland 命令别名系统"""

    # 别名映射 (使用 m- 前缀避免 Windows 路径问题)
    ALIASES = {
        # 记忆管理
        'm': 'memory',
        'memory': 'memory',
        'mem': 'memory',

        # 本能管理
        'i': 'instincts',
        'instincts': 'instincts',
        'list': 'instincts',
        'ls': 'instincts',

        # 搜索
        's': 'search',
        'search': 'search',
        'find': 'search',

        # 进化
        'e': 'evolve',
        'evolve': 'evolve',
        'up': 'evolve',

        # 提升
        'p': 'promote',
        'promote': 'promote',
        'upgrade': 'promote',

        # 重要标记
        'b': 'boost',
        'boost': 'boost',
        'star': 'boost',

        # 观察记录
        'o': 'observations',
        'obs': 'observations',
        'log': 'observations',

        # 分析
        'a': 'analyze',
        'analyze': 'analyze',
        'analyse': 'analyze',

        # 维护
        'd': 'decay',
        'decay': 'decay',

        'c': 'cleanup',
        'cleanup': 'cleanup',
        'clean': 'cleanup',

        # 帮助
        'h': 'help',
        'help': 'help',
        '?': 'help',
    }

    # 命令描述
    DESCRIPTIONS = {
        'memory': '查看记忆系统状态',
        'instincts': '列出所有本能',
        'search': '搜索本能',
        'evolve': '进化指定本能',
        'promote': '提升本能到全局',
        'boost': '重要标记本能',
        'observations': '查看观察记录',
        'analyze': '触发观察分析',
        'decay': '执行置信度衰减',
        'cleanup': '清理枯萎本能',
    }

    def __init__(self, workspace=None):
        if workspace is None:
            workspace = Path(__file__).parent.parent

        self.workspace = Path(workspace)
        self.cli_path = self.workspace / "system" / "roland_cli.py"

    def resolve_alias(self, alias: str) -> str:
        """解析别名到完整命令"""
        return self.ALIASES.get(alias.lower(), alias)

    def execute(self, command: str, *args, **kwargs):
        """执行命令（通过别名或直接命令）"""
        # 解析别名
        resolved = self.resolve_alias(command)

        if resolved == 'help':
            self.show_help()
            return 0

        # 构建完整命令
        cmd_args = [sys.executable, str(self.cli_path), resolved]

        # 处理不同类型的命令参数
        # 某些命令需要位置参数 (arg)，这些参数需要放在选项之前
        positional_arg = None
        remaining_args = list(args)

        # 移除已经被 kwargs 处理的标志
        if kwargs.get('json', False):
            remaining_args = [a for a in remaining_args if a != '--json']
        if kwargs.get('stage'):
            remaining_args = [a for a in remaining_args if a != '--stage']
        if kwargs.get('scope'):
            remaining_args = [a for a in remaining_args if a != '--scope']

        if resolved in ('search', 'evolve', 'promote', 'boost'):
            # 这些命令的第一个非选项参数是 arg
            if remaining_args:
                # 查找第一个非选项参数
                for i, arg in enumerate(remaining_args):
                    if not arg.startswith('--'):
                        positional_arg = arg
                        remaining_args.pop(i)
                        break

        # 添加位置参数（如果有）
        if positional_arg:
            cmd_args.append(positional_arg)

        # 添加选项参数
        if kwargs.get('json', False):
            cmd_args.append('--json')

        if kwargs.get('stage'):
            cmd_args.extend(['--stage', kwargs['stage']])

        if kwargs.get('scope'):
            cmd_args.extend(['--scope', kwargs['scope']])

        if kwargs.get('limit'):
            cmd_args.extend(['--limit', str(kwargs['limit'])])

        # 添加剩余参数（如 --boost）
        cmd_args.extend(remaining_args)

        # 执行命令
        result = subprocess.run(cmd_args, cwd=self.workspace)

        return result.returncode

    def show_help(self):
        """显示帮助信息"""
        print("=" * 60)
        print("AI Roland v2.0 - 命令别名系统")
        print("=" * 60)
        print()

        print("📋 记忆管理")
        print("  m, memory, mem        查看记忆系统状态")
        print("  o, obs, log           查看观察记录")
        print()

        print("🧬 本能管理")
        print("  i, instincts, list    列出所有本能")
        print("  s, search, find       搜索本能")
        print()

        print("⬆️  进化与提升")
        print("  e, evolve, up         进化指定本能")
        print("  p, promote, upgrade   提升到全局")
        print("  b, boost, star        重要标记")
        print()

        print("🔧 系统维护")
        print("  a, analyze            触发观察分析")
        print("  d, decay              置信度衰减")
        print("  c, cleanup, clean     清理枯萎本能")
        print()

        print("ℹ️  帮助")
        print("  h, help, ?            显示此帮助")
        print()

        print("使用示例:")
        print("  python roland_alias.py m                    # 查看状态")
        print("  python roland_alias.py s git               # 搜索")
        print("  python roland_alias.py e use-read --boost 0.2")
        print()

    def list_aliases(self):
        """列出所有别名"""
        print("可用别名:")
        print()

        # 按类别分组
        groups = {}
        for alias, command in self.ALIASES.items():
            if command not in groups:
                groups[command] = []
            groups[command].append(alias)

        for command, aliases in sorted(groups.items()):
            if command in self.DESCRIPTIONS:
                desc = self.DESCRIPTIONS[command]
                alias_str = ', '.join(sorted(aliases, key=len))
                print(f"  {alias_str:30s} -> {command:12s} # {desc}")


def main():
    """命令行入口"""
    import argparse

    # 简化参数解析
    raw_args = sys.argv[1:]

    if not raw_args:
        RolandAlias().show_help()
        return 0

    # 检查是否是列出别名
    if '--list' in raw_args or raw_args[0] in ['--list', '-l', 'list']:
        RolandAlias().list_aliases()
        return 0

    # 检查是否是帮助
    if raw_args[0] in ['--help', '-h', 'help', 'h', '?']:
        RolandAlias().show_help()
        return 0

    # 第一个参数是命令（别名）
    cmd_arg = raw_args[0].lstrip('/')  # 移除可能的斜杠前缀
    command = RolandAlias.ALIASES.get(cmd_arg.lower(), cmd_arg)

    # 如果是 help 命令
    if command == 'help':
        RolandAlias().show_help()
        return 0

    # 构建命令行
    cmd_args = [sys.executable, str(Path(__file__).parent / "roland_cli.py"), command]

    # 添加剩余参数
    remaining_args = raw_args[1:]

    # 对于需要位置参数的命令，第一个非选项参数是 arg
    if command in ('search', 'evolve', 'promote', 'boost'):
        # 查找第一个非选项参数作为位置参数
        positional_arg = None
        for i, arg in enumerate(remaining_args):
            if not arg.startswith('--'):
                positional_arg = arg
                remaining_args.pop(i)
                break

        if positional_arg:
            cmd_args.append(positional_arg)

    # 添加剩余参数（选项）
    cmd_args.extend(remaining_args)

    # 执行命令
    result = subprocess.run(cmd_args, cwd=Path(__file__).parent.parent)

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
