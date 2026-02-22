"""
AI Roland Skills CLI 集成
提供便捷的命令行接口来管理技能
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path
from typing import List, Optional

# UTF-8 设置
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    os.environ['PYTHONIOENCODING'] = 'utf-8'


class SkillsCLI:
    """Skills CLI 集成"""

    def __init__(self, workspace_path: str = None):
        if workspace_path is None:
            self.workspace = Path(__file__).parent.parent
        else:
            self.workspace = Path(workspace_path)

    def add(self, repo: str, skill: str = None,
            global_install: bool = False, yes: bool = False) -> bool:
        """安装技能

        Args:
            repo: 仓库 URL（支持 GitHub shorthands）
            skill: 技能名称（可选）
            global_install: 是否全局安装
            yes: 跳过确认

        Returns:
            是否成功
        """
        cmd = ['npx', 'skills', 'add', repo]

        if skill:
            cmd.extend(['--skill', skill])

        if global_install:
            cmd.append('-g')

        if yes:
            cmd.append('-y')

        # 限制只安装到 OpenClaw（AI Roland 的代理）
        cmd.extend(['--agent', 'openclaw'])

        print(f"[Skills] 正在安装: {repo}")
        if skill:
            print(f"[Skills] 技能: {skill}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                encoding='utf-8',
                errors='replace'
            )

            if result.returncode == 0:
                print(f"[Skills] ✅ 安装成功")
                if result.stdout:
                    print(result.stdout)
                return True
            else:
                print(f"[Skills] ❌ 安装失败")
                if result.stderr:
                    print(result.stderr)
                return False

        except subprocess.TimeoutExpired:
            print(f"[Skills] ❌ 安装超时")
            return False
        except Exception as e:
            print(f"[Skills] ❌ 安装异常: {e}")
            return False

    def list(self, global_install: bool = False) -> List[str]:
        """列出已安装的技能

        Args:
            global_install: 是否列出全局技能

        Returns:
            技能列表
        """
        cmd = ['npx', 'skills', 'list']

        if global_install:
            cmd.append('-g')

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8',
                errors='replace'
            )

            if result.returncode == 0:
                skills = []
                for line in result.stdout.split('\n'):
                    if line.strip():
                        skills.append(line.strip())
                return skills

        except Exception as e:
            print(f"[Skills] 列出技能失败: {e}")

        return []

    def find(self, query: str = None) -> List[str]:
        """搜索技能

        Args:
            query: 搜索关键词（可选，交互模式）

        Returns:
            技能列表
        """
        cmd = ['npx', 'skills', 'find']

        if query:
            cmd.append(query)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8',
                errors='replace'
            )

            if result.returncode == 0:
                skills = []
                for line in result.stdout.split('\n'):
                    if line.strip():
                        skills.append(line.strip())
                return skills

        except Exception as e:
            print(f"[Skills] 搜索失败: {e}")

        return []

    def remove(self, skill: str = None, global_install: bool = False,
               yes: bool = False) -> bool:
        """移除技能

        Args:
            skill: 技能名称
            global_install: 是否从全局移除
            yes: 跳过确认

        Returns:
            是否成功
        """
        cmd = ['npx', 'skills', 'remove']

        if skill:
            cmd.extend(['--skill', skill])
        else:
            cmd.append('--all')

        if global_install:
            cmd.append('-g')

        if yes:
            cmd.append('-y')

        print(f"[Skills] 正在移除: {skill or '所有技能'}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8',
                errors='replace'
            )

            if result.returncode == 0:
                print(f"[Skills] ✅ 移除成功")
                return True
            else:
                print(f"[Skills] ❌ 移除失败")
                if result.stderr:
                    print(result.stderr)
                return False

        except Exception as e:
            print(f"[Skills] ❌ 移除异常: {e}")
            return False

    def check(self) -> List[str]:
        """检查更新

        Returns:
            有更新的技能列表
        """
        try:
            result = subprocess.run(
                ['npx', 'skills', 'check'],
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8',
                errors='replace'
            )

            updates = []
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'update available' in line.lower():
                        updates.append(line.strip())

            return updates

        except Exception as e:
            print(f"[Skills] 检查更新失败: {e}")
            return []

    def update(self) -> bool:
        """更新所有技能

        Returns:
            是否成功
        """
        print("[Skills] 正在更新所有技能...")

        try:
            result = subprocess.run(
                ['npx', 'skills', 'update'],
                capture_output=True,
                text=True,
                timeout=300,
                encoding='utf-8',
                errors='replace'
            )

            if result.returncode == 0:
                print(f"[Skills] ✅ 更新成功")
                if result.stdout:
                    print(result.stdout)
                return True
            else:
                print(f"[Skills] ❌ 更新失败")
                if result.stderr:
                    print(result.stderr)
                return False

        except Exception as e:
            print(f"[Skills] ❌ 更新异常: {e}")
            return False

    def init(self, name: str = None) -> bool:
        """创建新技能模板

        Args:
            name: 技能名称（可选）

        Returns:
            是否成功
        """
        cmd = ['npx', 'skills', 'init']

        if name:
            cmd.append(name)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8',
                errors='replace'
            )

            if result.returncode == 0:
                print(f"[Skills] ✅ 技能模板创建成功")
                if result.stdout:
                    print(result.stdout)
                return True
            else:
                print(f"[Skills] ❌ 创建失败")
                if result.stderr:
                    print(result.stderr)
                return False

        except Exception as e:
            print(f"[Skills] ❌ 创建异常: {e}")
            return False


def main():
    """命令行接口"""
    parser = argparse.ArgumentParser(
        description='AI Roland Skills CLI - 管理你的 AI 技能',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s add vercel-labs/agent-skills          # 安装技能仓库
  %(prog)s add vercel-labs/agent-skills -s daily-briefing  # 安装特定技能
  %(prog)s list                                  # 列出所有技能
  %(prog)s find typescript                       # 搜索技能
  %(prog)s remove daily-briefing                 # 移除技能
  %(prog)s check                                 # 检查更新
  %(prog)s update                                # 更新所有技能
  %(prog)s init my-skill                         # 创建新技能
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # add 命令
    add_parser = subparsers.add_parser('add', help='安装技能')
    add_parser.add_argument('repo', help='仓库 URL（支持 GitHub shorthands）')
    add_parser.add_argument('-s', '--skill', help='安装特定技能')
    add_parser.add_argument('-g', '--global', action='store_true', help='全局安装')
    add_parser.add_argument('-y', '--yes', action='store_true', help='跳过确认')

    # list 命令
    list_parser = subparsers.add_parser('list', help='列出已安装的技能', aliases=['ls'])
    list_parser.add_argument('-g', '--global', action='store_true', help='列出全局技能')

    # find 命令
    find_parser = subparsers.add_parser('find', help='搜索技能')
    find_parser.add_argument('query', nargs='?', help='搜索关键词')

    # remove 命令
    remove_parser = subparsers.add_parser('remove', help='移除技能', aliases=['rm'])
    remove_parser.add_argument('-s', '--skill', help='移除特定技能')
    remove_parser.add_argument('-g', '--global', action='store_true', help='从全局移除')
    remove_parser.add_argument('-y', '--yes', action='store_true', help='跳过确认')

    # check 命令
    subparsers.add_parser('check', help='检查更新')

    # update 命令
    subparsers.add_parser('update', help='更新所有技能')

    # init 命令
    init_parser = subparsers.add_parser('init', help='创建新技能模板')
    init_parser.add_argument('name', nargs='?', help='技能名称')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    cli = SkillsCLI()

    if args.command == 'add':
        cli.add(args.repo, args.skill, getattr(args, 'global', False), args.yes)

    elif args.command in ['list', 'ls']:
        skills = cli.list(getattr(args, 'global', False))
        if skills:
            print("\n".join(skills))
        else:
            print("[Skills] 没有已安装的技能")

    elif args.command == 'find':
        skills = cli.find(args.query)
        if skills:
            print("\n".join(skills))
        else:
            print("[Skills] 未找到匹配的技能")

    elif args.command in ['remove', 'rm']:
        cli.remove(args.skill, getattr(args, 'global', False), args.yes)

    elif args.command == 'check':
        updates = cli.check()
        if updates:
            print("[Skills] 发现更新:")
            print("\n".join(updates))
        else:
            print("[Skills] 所有技能都是最新版本")

    elif args.command == 'update':
        cli.update()

    elif args.command == 'init':
        cli.init(args.name)


if __name__ == "__main__":
    main()
