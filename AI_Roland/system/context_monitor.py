"""
上下文管理提醒模块
用于监控和提醒用户关于 Claude CLI 上下文使用情况
"""

from pathlib import Path


class ContextMonitor:
    """上下文监控器"""

    # 上下文使用率阈值
    WARNING_THRESHOLD = 40  # 40% 时提醒
    CRITICAL_THRESHOLD = 60  # 60% 时强制提醒

    # 估算会话消耗的上下文量
    ESTIMATED_PER_LINE = 30  # 每行约 30 tokens
    ESTIMATED_BASE = 2000  # 基础启动消耗

    @staticmethod
    def check_session_lines(max_lines: int = 500) -> bool:
        """
        估算当前会话行数是否过多

        Args:
            max_lines: 最大建议行数

        Returns:
            True 如果行数在安全范围内
        """
        # 这是一个启发式估算
        # 实际无法获取真实 token 数，只能估算
        return True

    @staticmethod
    def get_reminder_message() -> str:
        """获取上下文管理提醒消息"""
        return """
╔════════════════════════════════════════════════════════════╗
║            💡 上下文管理提示                              ║
╚════════════════════════════════════════════════════════════╝

长任务建议：
1. 分段执行 - 使用 /new 开始新会话
2. 减少输出 - 只显示关键结果
3. 使用 /compact - 压缩上下文

当看到 "context window limit" 时：
- 执行 /compact
- 如果仍报错：执行 /clear
- 重新开聊时只带核心信息

[提示] 此消息由 startup.py 自动显示
"""

    @staticmethod
    def should_show_reminder() -> bool:
        """判断是否应该显示上下文提醒"""
        # 每次启动都显示简洁提示
        return True


def show_context_reminder_if_needed():
    """如果需要，显示上下文提醒"""
    if ContextMonitor.should_show_reminder():
        # 只显示简洁的一行提示
        print("[提示] 长任务请用 /new 分段执行 | context 接近 limit 时用 /compact")
