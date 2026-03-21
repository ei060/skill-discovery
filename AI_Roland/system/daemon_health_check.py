"""
AI Roland 系统健康检查模块
验证所有组件是否正常工作
"""
import os
import sys
import json
from datetime import datetime
from pathlib import Path


def check_daemon():
    """检查守护进程状态"""
    workspace = Path(__file__).parent.parent
    daemon_status = workspace / "daemon_status.json"

    if not daemon_status.exists():
        return {
            "status": "not_initialized",
            "message": "守护进程未初始化"
        }

    with open(daemon_status, 'r', encoding='utf-8') as f:
        status = json.load(f)

    if status.get("status") == "running":
        pid = status.get("pid")
        # 检查进程是否存在
        try:
            import psutil
            if psutil.pid_exists(pid):
                return {
                    "status": "healthy",
                    "pid": pid,
                    "uptime": status.get("start_time"),
                    "message": "守护进程运行中"
                }
        except ImportError:
            pass

        return {
            "status": "unhealthy",
            "message": f"守护进程标记为运行但 PID {pid} 不存在"
        }

    return {
        "status": "stopped",
        "message": "守护进程已停止"
    }


def check_memory_system():
    """检查记忆系统"""
    workspace = Path(__file__).parent.parent

    checks = {
        "对话历史": workspace / "对话历史.md",
        "任务清单": workspace / "任务清单.md",
        "日记目录": workspace / "日记",
        "记忆库": workspace / "记忆库",
    }

    results = {}
    for name, path in checks.items():
        if path.exists():
            results[name] = "ok"
        else:
            results[name] = "missing"

    # 检查语义记忆数量
    semantic_dir = workspace / "记忆库" / "语义记忆"
    if semantic_dir.exists():
        mem_count = len(list(semantic_dir.glob("*.md")))
        results["语义记忆数量"] = mem_count
    else:
        results["语义记忆数量"] = 0

    # 检查日记数量
    diary_dir = workspace / "日记"
    if diary_dir.exists():
        diary_count = len(list(diary_dir.glob("*.md")))
        results["日记数量"] = diary_count
    else:
        results["日记数量"] = 0

    return results


def check_skills():
    """检查 Skills 系统"""
    skills_dir = Path(__file__).parent.parent.parent / ".claude" / "skills"

    if not skills_dir.exists():
        return {
            "status": "no_skills_dir",
            "skills": []
        }

    skills = [d.name for d in skills_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]

    return {
        "status": "ok" if skills else "no_skills",
        "skills": skills,
        "count": len(skills)
    }


def check_system_state():
    """检查系统状态文件"""
    workspace = Path(__file__).parent.parent
    state_file = workspace / "system_state.json"

    if not state_file.exists():
        return {
            "status": "missing",
            "message": "系统状态文件不存在"
        }

    try:
        with open(state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)

        # 检查关键字段
        required_fields = ["last_daily_briefing", "last_sunday_reminder", "last_monthly_merge"]
        missing_fields = [f for f in required_fields if f not in state]

        return {
            "status": "ok" if not missing_fields else "incomplete",
            "state": state,
            "missing_fields": missing_fields
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


def health_check():
    """完整的健康检查"""
    print("=" * 60)
    print("AI Roland 系统健康检查")
    print("=" * 60)
    print()

    all_ok = True

    # 1. 守护进程检查
    print("[1/5] 守护进程检查...")
    daemon = check_daemon()
    if daemon["status"] == "healthy":
        print(f"  [OK] 守护进程运行中 (PID: {daemon['pid']})")
    elif daemon["status"] == "stopped":
        print(f"  [WARN] 守护进程已停止 - 需要启动")
        all_ok = False
    else:
        print(f"  [WARN] {daemon['message']}")
        all_ok = False

    # 2. 记忆系统检查
    print()
    print("[2/5] 记忆系统检查...")
    memory = check_memory_system()

    if memory.get("对话历史") == "missing":
        print("  [WARN] 对话历史文件缺失")
        all_ok = False
    else:
        print(f"  [OK] 对话历史: 存在")

    if memory.get("任务清单") == "missing":
        print("  [WARN] 任务清单文件缺失")
        all_ok = False
    else:
        print(f"  [OK] 任务清单: 存在")

    print(f"  [INFO] 语义记忆: {memory.get('语义记忆数量', 0)} 个")
    print(f"  [INFO] 日记: {memory.get('日记数量', 0)} 个")

    # 3. Skills 检查
    print()
    print("[3/5] Skills 系统检查...")
    skills = check_skills()
    if skills["status"] == "ok":
        print(f"  [OK] 已加载 {skills['count']} 个技能:")
        for skill in skills["skills"]:
            print(f"       - {skill}")
    elif skills["status"] == "no_skills":
        print("  [WARN] 未发现技能")

    # 4. 系统状态检查
    print()
    print("[4/5] 系统状态检查...")
    state = check_system_state()
    if state["status"] == "ok":
        print("  [OK] 系统状态文件正常")
    else:
        print(f"  [WARN] {state['message']}")
        all_ok = False

    # 5. 总结
    print()
    print("[5/5] 总结")
    print("-" * 60)

    if all_ok:
        print("  [OK] 所有组件运行正常")
        print()
        print("  系统已就绪，可以正常使用")
    else:
        print("  [WARN] 发现一些问题")
        print()
        print("  建议:")
        print("  1. 运行修复脚本")
        print("  2. 检查日志文件")
        print("  3. 手动启动守护进程")

    print()
    print("=" * 60)

    return all_ok


def main():
    """主函数"""
    import sys
    import io

    # 设置编码
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    health_check()


if __name__ == "__main__":
    main()
