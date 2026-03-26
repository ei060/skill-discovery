#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
日志工具模块 - 提供日志轮转功能

为所有 hooks 提供统一的日志写入和轮转机制
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime, timezone


class HookLogger:
    """Hook 日志记录器 - 支持自动轮转"""

    # 单例模式：每个日志文件名对应一个 logger
    _loggers = {}

    @classmethod
    def get_logger(cls, log_name: str, log_dir: Path = None):
        """
        获取或创建日志记录器

        Args:
            log_name: 日志文件名（如 'memory_injection.log'）
            log_dir: 日志目录（默认为 hooks 目录）

        Returns:
            logging.Logger: 配置好的日志记录器
        """
        if log_name in cls._loggers:
            return cls._loggers[log_name]

        # 确定日志目录
        if log_dir is None:
            log_dir = Path(__file__).parent
        log_dir = Path(log_dir)

        # 创建 logger
        logger = logging.getLogger(f"hook.{log_name.replace('.log', '')}")
        logger.setLevel(logging.INFO)

        # 避免重复添加 handler
        if logger.handlers:
            return logger

        # 日志文件路径
        log_file = log_dir / log_name

        # 创建轮转文件处理器
        # 参数说明：
        # - maxBytes: 单个日志文件最大 1MB
        # - backupCount: 保留 5 个备份文件
        # - 总共最多保留 6MB 日志（1 个当前 + 5 个历史）
        handler = RotatingFileHandler(
            log_file,
            maxBytes=1 * 1024 * 1024,  # 1MB
            backupCount=5,
            encoding='utf-8'
        )

        # 设置日志格式
        formatter = logging.Formatter(
            '%(asctime)s.%(msecs)03d | %(message)s',
            datefmt='%Y-%m-%dT%H:%M:%S'
        )
        handler.setFormatter(formatter)

        logger.addHandler(handler)

        # 缓存 logger
        cls._loggers[log_name] = logger

        return logger

    @classmethod
    def log(cls, log_name: str, message: str, log_dir: Path = None):
        """
        写入日志（便捷方法）

        Args:
            log_name: 日志文件名
            message: 日志消息
            log_dir: 日志目录（可选）
        """
        logger = cls.get_logger(log_name, log_dir)
        logger.info(message)


def write_log_with_rotation(
    log_file_name: str,
    message: str,
    log_dir: Path = None
):
    """
    写入日志（兼容旧代码的函数接口）

    这个函数提供了与原有代码兼容的接口，内部使用 HookLogger 实现轮转

    Args:
        log_file_name: 日志文件名（如 'memory_injection.log'）
        message: 日志消息
        log_dir: 日志目录（可选，默认为 hooks 目录）

    Example:
        # 旧代码：
        # with open(log_file, 'a', encoding='utf-8') as f:
        #     f.write(f"{timestamp} | {message}\\n")

        # 新代码（推荐）：
        write_log_with_rotation('memory_injection.log', f"Agent: {agent_name}")
    """
    HookLogger.log(log_file_name, message, log_dir)


def check_log_sizes(log_dir: Path = None, max_size_mb: float = 1.0) -> dict:
    """
    检查所有日志文件的大小

    Args:
        log_dir: 日志目录（默认为 hooks 目录）
        max_size_mb: 最大允许大小（MB）

    Returns:
        dict: {log_name: {'size_kb': float, 'status': 'ok'|'warning'|'critical'}}
    """
    if log_dir is None:
        log_dir = Path(__file__).parent

    log_files = list(log_dir.glob('*.log'))
    result = {}

    for log_file in log_files:
        size_kb = log_file.stat().st_size / 1024

        if size_kb > max_size_mb * 1024:
            status = 'critical'
        elif size_kb > max_size_mb * 1024 * 0.8:
            status = 'warning'
        else:
            status = 'ok'

        result[log_file.name] = {
            'size_kb': round(size_kb, 2),
            'status': status
        }

    return result


def cleanup_old_logs(
    log_dir: Path = None,
    keep_days: int = 30,
    dry_run: bool = False
) -> list:
    """
    清理旧的轮转日志文件

    Args:
        log_dir: 日志目录
        keep_days: 保留天数
        dry_run: 是否只显示不删除

    Returns:
        list: 要删除的文件列表
    """
    if log_dir is None:
        log_dir = Path(__file__).parent

    # 查找所有轮转日志文件（如 .log.1, .log.2 等）
    rotated_logs = []
    for pattern in ['*.log.*', '*.log.?']:
        rotated_logs.extend(log_dir.glob(pattern))

    to_delete = []
    now = datetime.now(timezone.utc)

    for log_file in rotated_logs:
        # 获取文件修改时间
        mtime = datetime.fromtimestamp(log_file.stat().st_mtime, tz=timezone.utc)
        age_days = (now - mtime).days

        if age_days > keep_days:
            to_delete.append({
                'file': log_file,
                'age_days': age_days,
                'size_kb': log_file.stat().st_size / 1024
            })

    if not dry_run:
        for item in to_delete:
            item['file'].unlink()

    return to_delete


if __name__ == "__main__":
    """测试代码"""
    import sys

    print("=== 日志文件大小检查 ===")
    sizes = check_log_sizes()
    for name, info in sizes.items():
        status_icon = {'ok': '✅', 'warning': '⚠️', 'critical': '🔴'}[info['status']]
        print(f"{status_icon} {name}: {info['size_kb']} KB")

    print("\n=== 测试日志写入 ===")
    test_logger = HookLogger.get_logger('test.log')
    test_logger.info("Test log message with rotation")
    print("✅ 测试日志已写入")

    print("\n=== 检查旧日志 ===")
    old_logs = cleanup_old_logs(dry_run=True)
    if old_logs:
        print(f"找到 {len(old_logs)} 个旧日志文件：")
        for item in old_logs:
            print(f"  - {item['file'].name} ({item['age_days']} 天前, {item['size_kb']:.1f} KB)")
    else:
        print("✅ 没有需要清理的旧日志")
