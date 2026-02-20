"""
Windows 服务安装脚本 - 让 AI Roland 开机自动启动
"""

import sys
import os
import subprocess
from pathlib import Path

def install_as_service():
    """安装为 Windows 服务"""
    print("="*60)
    print("AI Roland Windows 服务安装")
    print("="*60)
    print()

    # 检查管理员权限
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if not is_admin:
            print("[ERROR] 需要管理员权限")
            print("请右键点击此脚本，选择'以管理员身份运行'")
            return False
    except:
        pass

    print("[INFO] 正在安装 Windows 服务...")
    print()

    # 创建服务脚本
    system_dir = Path(__file__).parent
    service_script = system_dir / "daemon_service.py"

    # 使用 task scheduler 方式（更简单）
    print("[方式1] 使用任务计划程序（推荐）")
    print("-"*60)

    task_name = "AI_Roland_Daemon"
    script_path = system_dir / "daemon.py"
    python_exe = sys.executable

    # 创建任务计划命令
    cmd = [
        'schtasks', '/create',
        '/tn', task_name,
        '/tr', f'"{python_exe}" "{script_path}"',
        '/sc', 'onlogon',
        '/rl', 'highest',
        '/f'
    ]

    print(f"命令: {' '.join(cmd)}")
    print()

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("[OK] 任务计划创建成功！")
            print()
            print("系统将:")
            print("  - 每次登录时自动启动 AI Roland")
            print("  - 在后台持续运行")
            print("  - 自动执行定时任务")
            print()
            print("管理命令:")
            print(f"  查看任务: schtasks /query /tn {task_name}")
            print(f"  删除任务: schtasks /delete /tn {task_name} /f")
            print(f"  立即运行: schtasks /run /tn {task_name}")
            print()
            return True
        else:
            print(f"[ERROR] 创建失败: {result.stderr}")
            return False

    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def install_startup_shortcut():
    """安装到启动文件夹（备选方案）"""
    print()
    print("[方式2] 添加到启动文件夹")
    print("-"*60)

    import winshell

    startup_folder = winshell.startup()
    system_dir = Path(__file__).parent
    daemon_script = system_dir / "daemon.py"

    # 创建快捷方式
    shortcut_path = startup_folder / "AI Roland.lnk"

    try:
        from win32com.client import Dispatch
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.Targetpath = str(sys.executable)
        shortcut.Arguments = f'"{daemon_script}"'
        shortcut.WorkingDirectory = str(system_dir)
        shortcut.save()

        print(f"[OK] 快捷方式已创建: {shortcut_path}")
        print()
        print("系统将在下次登录时自动启动 AI Roland")
        print()
        return True

    except ImportError:
        print("[ERROR] 需要安装 pywin32")
        print("请运行: pip install pywin32")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def main():
    """主函数"""
    print()
    print("请选择安装方式:")
    print("  1. 任务计划程序（推荐）")
    print("  2. 启动文件夹")
    print("  3. 两种都安装")
    print()

    choice = input("请输入选择 (1/2/3): ").strip()

    if choice == '1':
        install_as_service()
    elif choice == '2':
        install_startup_shortcut()
    elif choice == '3':
        install_as_service()
        install_startup_shortcut()
    else:
        print("[ERROR] 无效选择")
        return

    print()
    print("="*60)
    print("安装完成！")
    print("="*60)
    print()
    print("测试命令:")
    print("  python daemon.py           # 手动启动守护进程")
    print("  python daemon.py &         # 后台启动（Linux/Mac）")
    print()


if __name__ == "__main__":
    main()
