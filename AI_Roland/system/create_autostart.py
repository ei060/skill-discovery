"""
创建启动快捷方式 - 添加到 Windows 启动文件夹
"""

import os
import sys
from pathlib import Path

def create_startup_shortcut():
    """创建启动快捷方式"""
    print("="*60)
    print("AI Roland 自启动设置")
    print("="*60)
    print()

    # 获取启动文件夹
    import winshell
    startup_folder = winshell.startup()

    # 获取当前目录
    system_dir = Path(__file__).parent
    daemon_script = system_dir / "daemon.py"
    python_exe = sys.executable

    # 创建批处理文件
    batch_file = system_dir / "autostart_daemon.bat"
    batch_content = f"""@echo off
chcp 65001 >nul
cd /d "{system_dir}"
start /MIN "" "{python_exe}" "{daemon_script}"
"""

    with open(batch_file, 'w', encoding='gbk') as f:
        f.write(batch_content)

    print(f"[OK] 批处理文件已创建: {batch_file}")

    # 创建快捷方式
    try:
        from win32com.client import Dispatch

        shortcut_path = startup_folder / "AI Roland.lnk"

        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.Targetpath = str(batch_file)
        shortcut.WorkingDirectory = str(system_dir)
        shortcut.save()

        print(f"[OK] 快捷方式已创建: {shortcut_path}")
        print()
        print("系统将在下次登录时自动启动 AI Roland")
        print()
        print("如需立即启动，请运行:")
        print(f"  {batch_file}")
        print()
        return True

    except ImportError:
        print("[WARNING] 需要安装 pywin32 创建快捷方式")
        print("请运行: pip install pywin32")
        print()
        print("临时方案:")
        print(f"  手动复制 {batch_file} 到启动文件夹:")
        print(f"    {startup_folder}")
        print()
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def main():
    """主函数"""
    success = create_startup_shortcut()

    if success:
        print("="*60)
        print("设置完成！")
        print("="*60)
    else:
        print("="*60)
        print("设置未完成，请手动操作")
        print("="*60)


if __name__ == "__main__":
    main()
