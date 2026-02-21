"""
AI Roland 自动启动脚本（v2.0）
Claude 打开工作区时自动执行，恢复完整上下文
"""

import sys
import os
from pathlib import Path

# 设置 UTF-8 输出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 添加system目录到路径
system_dir = Path(__file__).parent.parent / "AI_Roland" / "system"
sys.path.insert(0, str(system_dir))

# 导入并执行增强版启动脚本
try:
    from session_start import SessionStarter

    starter = SessionStarter()
    result = starter.start_session()

    # 显示完整的上下文恢复简报
    print(result["briefing"])

    # 显示启动状态
    if result.get("daemon_started"):
        print("[OK] 守护进程已自动启动")
    else:
        print("[INFO] 守护进程已在运行")

    # 提示用户可以开始工作
    print("\n✓ 上下文已恢复，可以继续工作\n")

except Exception as e:
    print(f"[ERROR] AI Roland 启动失败: {e}")
    print("\n提示:")
    print(f"  1. 确认 AI_Roland 目录存在于: {Path(__file__).parent.parent}")
    print(f"  2. 确认 system/session_start.py 文件存在")
    print(f"  3. 手动运行: python {system_dir / 'session_start.py'}")

