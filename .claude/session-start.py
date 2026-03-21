#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Claude Code Session Start Hook

在每个会话开始时自动执行，初始化 AI Roland 系统
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timezone

def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[Session Start {timestamp}] {message}")

def verify_system():
    """验证系统状态"""
    log("开始验证 AI Roland 系统...")

    workspace = Path("D:/ClaudeWork/AI_Roland")
    if not workspace.exists():
        log(f"警告: 工作目录不存在: {workspace}")
        return False

    log(f"工作目录: {workspace}")

    # 检查关键目录
    key_dirs = [
        workspace / "system" / "agents",
        workspace / "system" / "agents" / "memory",
        workspace / "system" / "agents" / "hooks"
    ]

    for dir_path in key_dirs:
        if dir_path.exists():
            log(f"  [OK] {dir_path.relative_to(workspace)}")
        else:
            log(f"  [WARN] {dir_path.relative_to(workspace)} 不存在")

    return True

def initialize_agent_system():
    """初始化 Agent 系统"""
    log("初始化 Agent 协作系统...")

    try:
        # 添加系统路径
        system_path = Path("D:/ClaudeWork/AI_Roland/system")
        if str(system_path) not in sys.path:
            sys.path.insert(0, str(system_path))
            log(f"  添加系统路径: {system_path}")

        # 导入必要的模块
        try:
            from agents.auto_agent_suggester import get_agent_suggester
            from agents.agent_activity_monitor import get_activity_monitor
            from agents.agent_enforcer import get_agent_enforcer
            from agents.agent_orchestrator_integrated import get_agent_orchestrator

            log("  [OK] 所有 Agent 模块导入成功")

            # 初始化单例
            suggester = get_agent_suggester()
            monitor = get_activity_monitor()
            enforcer = get_agent_enforcer()
            orchestrator = get_agent_orchestrator()

            log("  [OK] Agent 系统初始化完成")

            # 显示系统状态
            stats = monitor.get_activity_summary(days=7)
            log(f"  活跃度: {stats['active_agents']}/{len(stats)} agents")

            return True

        except ImportError as e:
            log(f"  [ERROR] 模块导入失败: {e}")
            return False

    except Exception as e:
        log(f"  [ERROR] 初始化失败: {e}")
        return False

def check_hooks_health():
    """检查 Hooks 健康状态"""
    log("检查 Hooks 健康状态...")

    hooks_dir = Path("D:/ClaudeWork/AI_Roland/system/agents/hooks")
    log_files = {
        'injection': hooks_dir / 'memory_injection.log',
        'save': hooks_dir / 'memory_save.log',
        'errors': hooks_dir / 'memory_errors.log'
    }

    all_ok = True
    for name, log_file in log_files.items():
        if log_file.exists():
            # 检查最后修改时间
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            age_hours = (datetime.now() - mtime).total_seconds() / 3600

            if age_hours < 1:
                log(f"  [OK] {name} 日志: 最近更新 ({int(age_hours*60)} 分钟前)")
            elif age_hours < 24:
                log(f"  [WARN] {name} 日志: {int(age_hours)} 小时前")
            else:
                log(f"  [ERROR] {name} 日志: {int(age_hours/24)} 天前 (停止工作)")
                all_ok = False
        else:
            log(f"  [WARN] {name} 日志: 不存在")

    return all_ok

def display_status():
    """显示系统状态"""
    log("\n" + "=" * 60)
    log("AI Roland 系统状态")
    log("=" * 60)

    log("\n可用功能:")
    log("  1. 智能任务分析 - 自动推荐合适的 Agent")
    log("  2. Agent 活跃度监控 - 跟踪 Agent 使用情况")
    log("  3. 强制参与规则 - 确保关键任务由专业 Agent 处理")
    log("  4. 自动触发 - 高匹配度任务自动调用 Agent")

    log("\n使用方法:")
    log("  对于任何任务，系统会自动:")
    log("  - 分析任务类型")
    log("  - 推荐最合适的 Agent")
    log("  - 记录执行过程")
    log("  - 累积经验教训")

    log("\n" + "=" * 60)

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("AI Roland Session Start Hook")
    print("=" * 60)

    success = True

    # 1. 验证系统
    if not verify_system():
        success = False

    # 2. 初始化 Agent 系统
    if not initialize_agent_system():
        success = False

    # 3. 检查 Hooks 健康状态
    hooks_ok = check_hooks_health()

    # 4. 显示状态
    display_status()

    # 总结
    if success:
        log("\n[SUCCESS] 系统初始化完成")
        if not hooks_ok:
            log("\n[WARNING] Hooks 系统未响应，使用备用方案")
    else:
        log("\n[ERROR] 系统初始化失败")

    print("=" * 60 + "\n")

    return 0  # 必须返回 0，否则会话启动会失败

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"[ERROR] Session start hook failed: {e}")
        sys.exit(1)  # 失败也要返回 0，避免阻止会话启动
