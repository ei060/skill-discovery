"""
AI Roland 监控面板 - 查看守护进程状态
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

def show_status():
    """显示系统状态"""
    print("="*60)
    print("AI Roland 系统状态")
    print("="*60)
    print()

    # 路径
    system_dir = Path(__file__).parent
    workspace = system_dir.parent
    status_file = workspace / "daemon_status.json"
    state_file = workspace / "system_state.json"
    tasks_file = workspace / "任务清单.md"
    log_dir = workspace / "logs"

    # 1. 守护进程状态
    print("[守护进程状态]")
    print("-"*60)
    if status_file.exists():
        with open(status_file, 'r', encoding='utf-8') as f:
            status = json.load(f)

        daemon_status = status.get('status', 'unknown')
        pid = status.get('pid', 'N/A')
        start_time = status.get('start_time', 'N/A')

        status_icon = "[RUNNING]" if daemon_status == "running" else "[STOPPED]"

        print(f"  状态: {status_icon}")
        print(f"  PID: {pid}")
        print(f"  启动时间: {start_time}")

        # 检查进程是否还在运行
        if pid != 'N/A':
            try:
                import psutil
                if psutil.pid_exists(pid):
                    process = psutil.Process(pid)
                    print(f"  进程: 存在 (运行时间: {datetime.now() - datetime.fromisoformat(start_time)})")
                else:
                    print(f"  进程: 不存在 (可能已停止)")
            except ImportError:
                print(f"  进程: 未知 (需要 psutil: pip install psutil)")
    else:
        print("  状态: [STOPPED]")
        print("  守护进程未启动")
    print()

    # 2. 系统状态
    print("[系统状态]")
    print("-"*60)
    if state_file.exists():
        with open(state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)

        print(f"  心跳计数: {state.get('heartbeat_count', 0)}")
        print(f"  上次心跳: {state.get('last_heartbeat', 'N/A')}")
        print(f"  上次简报: {state.get('last_daily_briefing', 'N/A')}")
        print(f"  当前会话: {state.get('current_session', 'N/A')}")
    else:
        print("  未找到系统状态文件")
    print()

    # 3. 任务统计
    print("[任务统计]")
    print("-"*60)
    if tasks_file.exists():
        content = tasks_file.read_text(encoding='utf-8')

        import re
        total_tasks = len(re.findall(r'- \[ \]', content))
        done_tasks = len(re.findall(r'- \[x\]', content))
        urgent_tasks = len(re.findall(r'【紧急重要】.*?- \[ \]', content, re.DOTALL))

        print(f"  总任务: {total_tasks}")
        print(f"  已完成: {done_tasks}")
        print(f"  待办: {total_tasks - done_tasks}")
        print(f"  紧急: {urgent_tasks}")
    else:
        print("  未找到任务清单")
    print()

    # 4. 最近日志
    print("[最近日志]")
    print("-"*60)
    log_files = sorted(log_dir.glob("daemon_*.log"), reverse=True)
    if log_files:
        latest_log = log_files[0]
        print(f"  日志文件: {latest_log.name}")

        # 读取最后20行
        with open(latest_log, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            recent_lines = lines[-20:] if len(lines) > 20 else lines

        print("  最近活动:")
        for line in recent_lines:
            line = line.strip()
            if line:
                print(f"    {line}")
    else:
        print("  未找到日志文件")
    print()

    # 5. 操作提示
    print("[操作]")
    print("-"*60)
    print("  启动守护进程: python daemon.py")
    print("  停止守护进程: Ctrl+C (在守护进程窗口)")
    print("  查看实时日志: tail -f logs/daemon_YYYYMMDD.log")
    print("  查看本状态: python monitor.py")
    print()

    print("="*60)


def interact():
    """交互模式"""
    while True:
        print("\n命令:")
        print("  status - 显示状态")
        print("  logs   - 查看日志")
        print("  tasks  - 查看任务")
        print("  quit   - 退出")

        cmd = input("\n>>> ").strip().lower()

        if cmd == 'status':
            show_status()
        elif cmd == 'logs':
            # 打开最新日志文件
            log_dir = Path(__file__).parent.parent / "logs"
            log_files = sorted(log_dir.glob("daemon_*.log"), reverse=True)
            if log_files:
                print(f"\n打开日志: {log_files[0]}")
                os.system(f"notepad {log_files[0]}")
        elif cmd == 'tasks':
            tasks_file = Path(__file__).parent.parent / "任务清单.md"
            if tasks_file.exists():
                os.system(f"notepad {tasks_file}")
        elif cmd == 'quit':
            break
        else:
            print("[ERROR] 未知命令")


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == '-i':
        interact()
    else:
        show_status()


if __name__ == "__main__":
    main()
