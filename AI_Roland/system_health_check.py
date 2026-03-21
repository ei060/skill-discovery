"""
AI Roland 系统健康检查模块（独立运行版）
用于验证所有组件是否正常工作
"""
import os
import sys
import json
from datetime import datetime
from pathlib import Path


def main():
    """主函数"""
    print("=" * 60)
    print("AI Roland 系统健康检查")
    print("=" * 60)
    print()

    # 获取工作区路径
    if len(sys.argv) > 1:
        workspace = Path(sys.argv[1])
    else:
        # 默认使用相对路径
        workspace = Path(__file__).parent.parent if "__file__" in locals() else Path(".").absolute() / "AI_Roland"

    print(f"工作区: {workspace}")
    print()

    all_ok = True

    # 1. 检查目录结构
    print("[1/6] 目录结构检查...")
    required_dirs = [
        "system",
        "日记",
        "记忆库/语义记忆",
        "记忆库/强制规则"
    ]

    for dir_name in required_dirs:
        dir_path = workspace / dir_name
        if dir_path.exists():
            print(f"  [OK] {dir_name}/ 存在")
        else:
            print(f"  [WARN] {dir_name}/ 不存在")
            all_ok = False

    # 2. 检查核心文件
    print()
    print("[2/6] 核心文件检查...")
    required_files = [
        "对话历史.md",
        "任务清单.md",
        "system_state.json",
        "CLAUDE.md",
        "system/engine.py",
        "system/daemon.py",
        "system/session_start.py"
    ]

    for file_name in required_files:
        file_path = workspace / file_name
        if file_path.exists():
            print(f"  [OK] {file_name} 存在")
        else:
            print(f"  [WARN] {file_name} 不存在")
            all_ok = False

    # 3. 检查守护进程
    print()
    print("[3/6] 守护进程检查...")
    daemon_status = workspace / "daemon_status.json"

    if daemon_status.exists():
        with open(daemon_status, 'r', encoding='utf-8') as f:
            status = json.load(f)

        if status.get("status") == "running":
            pid = status.get("pid")
            # 尝试检查进程
            try:
                import psutil
                if psutil.pid_exists(pid):
                    print(f"  [OK] 守护进程运行中 (PID: {pid})")
                else:
                    print(f"  [WARN] 守护进程标记为运行但进程不存在 (PID: {pid})")
                    all_ok = False
            except ImportError:
                print(f"  [INFO] 守护进程标记为运行 (PID: {pid})")
        else:
            print(f"  [WARN] 守护进程已停止")
            all_ok = False
    else:
        print("  [INFO] 守护进程未启动")

    # 4. 检查记忆系统
    print()
    print("[4/6] 记忆系统检查...")

    # 统计文件数量
    semantic_dir = workspace / "记忆库" / "语义记忆"
    diary_dir = workspace / "日记"

    if semantic_dir.exists():
        semantic_count = len(list(semantic_dir.glob("*.md")))
        print(f"  [OK] 语义记忆: {semantic_count} 个")
    else:
        print("  [WARN] 语义记忆目录不存在")
        all_ok = False

    if diary_dir.exists():
        diary_count = len(list(diary_dir.glob("*.md")))
        print(f"  [OK] 日记: {diary_count} 个")
    else:
        print("  [WARN] 日记目录不存在")
        all_ok = False

    chat_history = workspace / "对话历史.md"
    if chat_history.exists():
        print(f"  [OK] 对话历史: 存在")
    else:
        print("  [WARN] 对话历史文件不存在")
        all_ok = False

    # 5. 检查 Skills
    print()
    print("[5/6] Skills 检查...")
    skills_dir = workspace.parent / ".claude" / "skills"

    if skills_dir.exists():
        skills = [d.name for d in skills_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
        if skills:
            print(f"  [OK] 已加载 {len(skills)} 个技能:")
            for skill in skills:
                print(f"       - {skill}")
        else:
            print("  [INFO] 未发现技能")
    else:
        print("  [INFO] Skills 目录不存在")

    # 6. 总结
    print()
    print("[6/6] 总结")
    print("-" * 60)

    if all_ok:
        print("  [OK] 所有组件正常")
        print()
        print("  ✓ 系统完全就绪")
        print("  ✓ 可以正常使用")
    else:
        print("  [WARN] 发现一些问题")
        print()
        print("  建议运行: python AI_Roland/system/daemon_health_check.py")

    print()
    print("=" * 60)
    print()

    return 0 if all_ok else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
