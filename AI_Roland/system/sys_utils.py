"""
系统工具模块 - 提供安全的系统资源访问

用于解决守护进程/特殊环境中的资源访问问题：
- sys.stdin 可能为 None（守护进程、Windows 服务）
- sys.stdout/sys.stderr 可能被重定向
- 文件描述符可能不可用

设计原则：
1. 防御性编程 - 先检查，再访问
2. 优雅降级 - 无法访问时返回默认值
3. 明确异常 - 捕获特定异常类型
"""

import sys
import os
from typing import Optional, Any
from contextlib import contextmanager


class SafeIO:
    """安全的系统 I/O 访问"""

    @staticmethod
    def is_interactive() -> bool:
        """
        检测是否在交互式终端中运行

        Returns:
            bool: True 表示交互式终端，False 表示后台/批处理
        """
        try:
            # 检查 stdin 是否存在且是 TTY
            if sys.stdin is None or not hasattr(sys.stdin, 'isatty'):
                return False

            if not sys.stdin.isatty():
                return False

            # 检查 stdout
            if not hasattr(sys.stdout, 'isatty'):
                return False

            if not sys.stdout.isatty():
                return False

            return True

        except (AttributeError, OSError, ValueError):
            # 任何异常都认为是非交互式环境
            return False

    @staticmethod
    def is_daemon() -> bool:
        """
        检测是否在守护进程中运行

        Returns:
            bool: True 表示守护进程环境
        """
        # 检查 stdin 是否被重定向或关闭
        if sys.stdin is None:
            return True

        try:
            # 尝试访问文件描述符
            if hasattr(sys.stdin, 'fileno'):
                fd = sys.stdin.fileno()
                # 检查是否是 /dev/null 或类似的空设备
                if os.name == 'posix':
                    try:
                        return os.path.sameopenfile(fd, os.open(os.devnull, os.O_RDONLY))
                    except OSError:
                        pass
            return False
        except (OSError, ValueError, AttributeError):
            return True

    @staticmethod
    def safe_read_stdin(max_length: int = 10240) -> Optional[str]:
        """
        安全地从 stdin 读取

        Args:
            max_length: 最大读取长度（防止内存溢出）

        Returns:
            读取的字符串，失败时返回 None
        """
        if sys.stdin is None:
            return None

        try:
            # 优先使用 buffer 读取（避免编码问题）
            if hasattr(sys.stdin, 'buffer'):
                raw_bytes = sys.stdin.buffer.read(max_length)
                if raw_bytes:
                    return raw_bytes.decode('utf-8', errors='replace')
                return ""
            else:
                # 降级到直接读取
                return sys.stdin.read(max_length)

        except (AttributeError, OSError, ValueError, UnicodeDecodeError):
            return None

    @staticmethod
    def safe_write_stdout(content: str) -> bool:
        """
        安全地向 stdout 写入

        Args:
            content: 要写入的内容

        Returns:
            bool: 是否成功
        """
        if sys.stdout is None:
            return False

        try:
            sys.stdout.write(content)
            sys.stdout.flush()
            return True
        except (AttributeError, OSError, ValueError):
            return False

    @staticmethod
    def safe_write_stderr(content: str) -> bool:
        """
        安全地向 stderr 写入

        Args:
            content: 要写入的内容

        Returns:
            bool: 是否成功
        """
        if sys.stderr is None:
            return False

        try:
            sys.stderr.write(content)
            sys.stderr.flush()
            return True
        except (AttributeError, OSError, ValueError):
            return False

    @staticmethod
    @contextmanager
    def safe_stdin_redirect(file_path: Optional[str] = None):
        """
        安全地重定向 stdin

        Args:
            file_path: 文件路径，None 表示使用 os.devnull

        Yields:
            是否成功
        """
        original_stdin = sys.stdin
        success = False

        try:
            if file_path is None:
                file_path = os.devnull

            with open(file_path, 'r', encoding='utf-8') as f:
                sys.stdin = f
                success = True
                yield True

        except (OSError, ValueError, IOError) as e:
            yield False
        finally:
            sys.stdin = original_stdin


def get_environment_info() -> dict:
    """
    获取环境信息（用于调试）

    Returns:
        包含环境信息的字典
    """
    info = {
        'is_interactive': SafeIO.is_interactive(),
        'is_daemon': SafeIO.is_daemon(),
        'sys.stdin_exists': sys.stdin is not None,
        'sys.stdout_exists': sys.stdout is not None,
        'sys.stderr_exists': sys.stderr is not None,
    }

    # 尝试获取更多详细信息
    if sys.stdin is not None:
        try:
            info['stdin_isatty'] = sys.stdin.isatty() if hasattr(sys.stdin, 'isatty') else None
            info['stdin_has_fileno'] = hasattr(sys.stdin, 'fileno')
            if info['stdin_has_fileno']:
                try:
                    info['stdin_fileno'] = sys.stdin.fileno()
                except (OSError, ValueError):
                    info['stdin_fileno'] = None
        except Exception as e:
            info['stdin_error'] = str(e)

    if sys.stdout is not None:
        try:
            info['stdout_isatty'] = sys.stdout.isatty() if hasattr(sys.stdout, 'isatty') else None
        except Exception as e:
            info['stdout_error'] = str(e)

    return info


# 便捷的别名
is_interactive = SafeIO.is_interactive
is_daemon = SafeIO.is_daemon
safe_read_stdin = SafeIO.safe_read_stdin
safe_write_stdout = SafeIO.safe_write_stdout
safe_write_stderr = SafeIO.safe_write_stderr


if __name__ == "__main__":
    # 测试代码
    print("环境信息:")
    import json
    print(json.dumps(get_environment_info(), indent=2, ensure_ascii=False))

    print(f"\n交互式: {is_interactive()}")
    print(f"守护进程: {is_daemon()}")
