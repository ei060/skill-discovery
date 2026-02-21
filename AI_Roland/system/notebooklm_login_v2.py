"""
NotebookLM 直接登录助手（反自动化检测版本）
使用 notebooklm 的 browser_profile 完成登录
"""

import sys
import time
import json
from pathlib import Path

# 添加 system 目录到路径
system_dir = Path(__file__).parent
sys.path.insert(0, str(system_dir))

from playwright.sync_api import sync_playwright


def notebooklm_direct_login():
    """
    使用 notebooklm 的 browser_profile 直接登录
    """
    profile_dir = Path("C:/Users/DELL/.notebooklm/browser_profile")
    storage_file = Path("C:/Users/DELL/.notebooklm/storage_state.json")

    print("="*60)
    print("NotebookLM 直接登录助手（反检测版）")
    print("="*60)
    print(f"[配置] Browser Profile: {profile_dir}")
    print(f"[配置] Storage File: {storage_file}")

    p = sync_playwright().start()

    try:
        # 使用持久化上下文，指定 notebooklm 的配置文件
        print("\n[启动] 正在启动浏览器...")
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=False,
            channel="chrome",
            args=[
                # 反自动化检测参数
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-site-isolation-trials',
                # 添加真实的 Chrome 标识
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            ],
            # 禁用自动化标志
            ignore_default_args=['--enable-automation'],
            # 设置视口
            viewport={'width': 1280, 'height': 720},
            # 设置语言
            locale='zh-CN',
            timezone_id='Asia/Shanghai',
        )

        # 注入 JavaScript 移除 automation 标识
        contexts = [context]
        for ctx in contexts:
            ctx.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['zh-CN', 'zh', 'en']
                });
                window.chrome = {
                    runtime: {}
                };
            """)

        # 默认页面或新建页面
        if len(context.pages) > 0:
            page = context.pages[0]
        else:
            page = context.new_page()

        print("[导航] 打开 Google...")
        page.goto("https://accounts.google.com", wait_until="networkidle")

        print("\n" + "="*60)
        print("[请操作] 在浏览器中完成 Google 登录")
        print("="*60)
        print("提示：")
        print("  1. 如果已经登录，会跳转到账户页面")
        print("  2. 如果未登录，请输入 Google 账号密码")
        print("  3. 完成后访问: https://notebooklm.google.com")
        print("  4. 这次应该不会提示'浏览器不安全'")
        print("="*60 + "\n")

        # 等待用户登录
        print("[等待] 等待你完成登录...")
        print("[提示] 完成登录并看到 NotebookLM 主页后按 Ctrl+C")

        # 保持浏览器运行直到用户中断
        try:
            while True:
                time.sleep(1)

                # 定期检查 URL
                current_url = page.url
                if "notebooklm.google.com" in current_url:
                    # 在 NotebookLM 页面，每30秒保存一次
                    pass
        except KeyboardInterrupt:
            print("\n\n[用户] 请求停止，正在保存 session...")

        # 验证 NotebookLM 访问
        print("\n[验证] 检查 NotebookLM 访问...")
        page.goto("https://notebooklm.google.com")
        time.sleep(3)

        current_url = page.url
        if "notebooklm.google.com" in current_url:
            print("[成功] 已可以访问 NotebookLM！")

            # 保存 storage state
            print("[保存] 正在保存 session...")
            storage_state = context.storage_state()
            with open(storage_file, 'w', encoding='utf-8') as f:
                json.dump(storage_state, f, ensure_ascii=False, indent=2)

            print(f"[保存] Session 已保存到: {storage_file}")

            # 检查 cookies
            cookies = storage_state.get('cookies', [])
            google_cookies = [c for c in cookies if 'google' in c.get('domain', '')]
            cookie_names = [c.get('name') for c in google_cookies]
            print(f"[Cookies] 找到 {len(google_cookies)} 个 Google cookies")
            print(f"[Cookies] 关键 cookies: {[n for n in cookie_names if n in ['SID', 'HSID', 'SSID', 'APISID', 'SAPISID']]}")

            if 'SID' in cookie_names:
                print("\n" + "="*60)
                print("[完成] 登录成功！包含 SID cookie")
                print("="*60)
                print("\n现在可以运行:")
                print("  notebooklm list  # 查看笔记本")
                print("  notebooklm ask \"你好\" # 提问")
            else:
                print("\n[警告] 未找到 SID cookie")
                print("[建议] 可能需要在浏览器中重新登录 Google")
        else:
            print(f"[失败] 无法访问 NotebookLM")
            print(f"[URL] {current_url}")

    except Exception as e:
        print(f"\n[错误] {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'context' in locals():
            context.close()
        p.stop()
        print("[完成] 浏览器已停止")


if __name__ == "__main__":
    notebooklm_direct_login()
