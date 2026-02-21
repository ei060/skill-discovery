"""
NotebookLM Google 登录助手（同步版本）
使用持久化浏览器控制器完成授权
"""

import sys
import time
from pathlib import Path

# 添加 system 目录到路径
system_dir = Path(__file__).parent
sys.path.insert(0, str(system_dir))

from browser_controller import BrowserController


def notebooklm_login():
    """
    启动浏览器并等待用户完成 Google 登录

    NotebookLM 需要 Google 账号授权，通过浏览器完成：
    1. 打开 Google 登录页面
    2. 用户手动登录
    3. 登录成功后，session 会被保存
    4. 后续 notebooklm 命令可以直接使用已保存的 session
    """

    controller = BrowserController()

    try:
        print("="*60)
        print("NotebookLM Google 登录")
        print("="*60)

        # 启动浏览器
        controller.start(headless=False, channel="chrome")

        # 导航到 Google（NotebookLM 需要访问 Google 服务）
        print("\n[步骤 1/3] 打开 Google...")
        controller.goto("https://accounts.google.com")

        print("\n" + "="*60)
        print("[步骤 2/3] 请在浏览器中完成 Google 登录")
        print("="*60)
        print("提示：")
        print("  1. 如果已经登录，此步骤会自动跳过")
        print("  2. 如果未登录，请输入你的 Google 账号密码")
        print("  3. 登录成功后，浏览器会跳转到 Google 账户页面")
        print("="*60 + "\n")

        # 等待用户登录（等待 URL 变成 Google 账户页面）
        print("[等待] 等待你完成登录...")

        # 检查是否已登录或等待登录
        max_wait = 300  # 5分钟超时
        waited = 0

        while waited < max_wait:
            time.sleep(2)
            waited += 2

            current_url = controller.get_url()

            # 已登录的标志：跳转到 myaccount 页面或 accounts.google.com/signinchooser
            if "myaccount.google.com" in current_url or "accounts.google.com/signinchooser" in current_url:
                print(f"\n[OK] 检测到登录成功！")
                print(f"[URL] {current_url}")
                break

            # 还在登录页面
            if "accounts.google.com" in current_url and "signin" in current_url:
                if waited % 10 == 0:  # 每10秒提示一次
                    print(f"[等待] 仍在等待登录... ({waited}s)")
                continue

        if waited >= max_wait:
            print("\n[超时] 登录等待超时（5分钟）")
            print("提示：如果已经完成登录，session 已保存，可以继续使用")
        else:
            print("\n[步骤 3/3] 验证登录状态...")

            # 验证：尝试访问 Google Notebook（检查是否真的有权限）
            controller.goto("https://notebooklm.google.com")

            time.sleep(3)

            current_url = controller.get_url()

            if "notebooklm.google.com" in current_url:
                print("\n" + "="*60)
                print("[成功] Google 登录验证成功！")
                print("="*60)
                print(f"[URL] {current_url}")
                print("\n现在你可以：")
                print("  1. 使用 notebooklm 命令行工具")
                print("  2. Session 会自动保存，无需重复登录")
                print("  3. 浏览器可以关闭，或保持打开用于手动操作")
            else:
                print("\n[警告] 未能访问 NotebookLM")
                print(f"[URL] {current_url}")
                print("可能原因：")
                print("  - NotebookLM 服务在当前地区不可用")
                print("  - 需要 VPN 代理")
                print("  - 账号权限问题")

        print("\n" + "="*60)
        print("保持浏览器运行（按 Ctrl+C 停止）")
        print("="*60 + "\n")

        # 保持浏览器打开，用户可以继续手动操作
        controller.run_interactive()

    except Exception as e:
        print(f"\n[错误] {e}")
        import traceback
        traceback.print_exc()
    finally:
        controller.stop()


def verify_login():
    """
    验证已有的 NotebookLM session
    不打开浏览器，只检查登录状态
    """
    controller = BrowserController()

    try:
        print("[验证] 检查 NotebookLM 登录状态...")

        # 使用已保存的 session
        controller.start(headless=True, channel="chrome")

        # 尝试访问 NotebookLM
        controller.goto("https://notebooklm.google.com")

        time.sleep(2)

        current_url = controller.get_url()

        if "notebooklm.google.com" in current_url:
            print("[OK] 已登录 NotebookLM")
            return True
        else:
            print("[未登录] 需要重新登录")
            print(f"[URL] {current_url}")
            return False

    except Exception as e:
        print(f"[错误] {e}")
        return False
    finally:
        controller.stop()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="NotebookLM Google 登录助手")
    parser.add_argument("--verify", action="store_true", help="验证登录状态（不打开浏览器）")
    args = parser.parse_args()

    if args.verify:
        verify_login()
    else:
        notebooklm_login()
