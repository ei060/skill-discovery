"""
AI Roland 浏览器控制器（同步版本 v2）
提供持久化浏览器会话，支持远程操作
使用普通 launch + 手动保存 cookies 实现 session 持久化
"""

import time
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from datetime import datetime


class BrowserController:
    """持久化浏览器控制器（同步版本 v2）"""

    def __init__(self, user_data_dir: str = None):
        """
        初始化浏览器控制器

        Args:
            user_data_dir: 用户数据目录，用于保存会话状态
        """
        if user_data_dir is None:
            user_data_dir = Path(__file__).parent.parent / "browser_data"
        self.user_data_dir = Path(user_data_dir)
        self.user_data_dir.mkdir(parents=True, exist_ok=True)

        # Cookie 文件路径
        self.cookie_file = self.user_data_dir / "cookies.json"
        self.storage_file = self.user_data_dir / "storage_state.json"

        self.playwright = None
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None
        self.running = False

    def start(self, headless: bool = False, channel: str = "chrome"):
        """
        启动浏览器

        Args:
            headless: 是否无头模式
            channel: 浏览器类型 (chrome, msedge, chromium)
        """
        self.playwright = sync_playwright().start()

        # 启动浏览器
        self.browser = self.playwright.chromium.launch(
            headless=headless,
            channel=channel,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
            ],
        )

        # 如果有保存的 storage state，加载它
        storage_state = None
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    storage_state = json.load(f)
                print(f"[浏览器] 已加载保存的 session")
            except Exception as e:
                print(f"[浏览器] 加载 session 失败: {e}")

        # 创建上下文
        self.context = self.browser.new_context(
            storage_state=storage_state,
            accept_downloads=True,
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        # 默认页面
        self.page = self.context.new_page()

        self.running = True

        print(f"[浏览器] 已启动 ({channel})")
        print(f"[浏览器] 用户数据: {self.user_data_dir}")
        print(f"[浏览器] 无头模式: {headless}")

    def stop(self):
        """停止浏览器并保存 session"""
        if self.context:
            # 保存 storage state (cookies, localStorage, sessionStorage)
            try:
                storage_state = self.context.storage_state()
                with open(self.storage_file, 'w', encoding='utf-8') as f:
                    json.dump(storage_state, f, ensure_ascii=False, indent=2)
                print(f"[浏览器] Session 已保存")
            except Exception as e:
                print(f"[浏览器] 保存 session 失败: {e}")

            self.context.close()

        if self.browser:
            self.browser.close()

        if self.playwright:
            self.playwright.stop()

        self.running = False
        print("[浏览器] 已停止")

    def goto(self, url: str, wait_until: str = "networkidle"):
        """
        导航到指定URL

        Args:
            url: 目标URL
            wait_until: 等待条件 (load, domcontentloaded, networkidle)
        """
        if not self.page:
            raise RuntimeError("浏览器未启动，请先调用 start()")

        print(f"[浏览器] 导航到: {url}")
        self.page.goto(url, wait_until=wait_until)
        time.sleep(1)  # 额外等待页面稳定

    def wait_for_selector(self, selector: str, timeout: int = 30000):
        """
        等待选择器出现

        Args:
            selector: CSS选择器
            timeout: 超时时间(毫秒)
        """
        if not self.page:
            raise RuntimeError("浏览器未启动")

        print(f"[浏览器] 等待元素: {selector}")
        self.page.wait_for_selector(selector, timeout=timeout)

    def click(self, selector: str):
        """点击元素"""
        if not self.page:
            raise RuntimeError("浏览器未启动")

        print(f"[浏览器] 点击: {selector}")
        self.page.click(selector)
        time.sleep(0.5)

    def fill(self, selector: str, value: str):
        """填写表单"""
        if not self.page:
            raise RuntimeError("浏览器未启动")

        print(f"[浏览器] 填写: {selector} = {value[:20]}...")
        self.page.fill(selector, value)
        time.sleep(0.3)

    def type_text(self, selector: str, text: str, delay: int = 100):
        """模拟打字（慢速输入）"""
        if not self.page:
            raise RuntimeError("浏览器未启动")

        print(f"[浏览器] 打字: {selector}")
        self.page.type(selector, text, delay=delay)
        time.sleep(0.3)

    def screenshot(self, path: str = None):
        """
        截图

        Args:
            path: 保存路径，默认自动生成
        """
        if not self.page:
            raise RuntimeError("浏览器未启动")

        if path is None:
            path = self.user_data_dir / f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

        self.page.screenshot(path=str(path))
        print(f"[浏览器] 截图已保存: {path}")
        return path

    def get_url(self) -> str:
        """获取当前URL"""
        if not self.page:
            raise RuntimeError("浏览器未启动")
        return self.page.url

    def get_text(self, selector: str = None) -> str:
        """
        获取页面文本

        Args:
            selector: 指定选择器，None则获取整个页面
        """
        if not self.page:
            raise RuntimeError("浏览器未启动")

        if selector:
            element = self.page.query_selector(selector)
            return element.inner_text() if element else ""
        else:
            return self.page.inner_text("body")

    def evaluate(self, script: str):
        """执行JavaScript"""
        if not self.page:
            raise RuntimeError("浏览器未启动")

        return self.page.evaluate(script)

    def wait_for_navigation(self, timeout: int = 30000):
        """等待导航完成"""
        if not self.page:
            raise RuntimeError("浏览器未启动")

        print(f"[浏览器] 等待导航...")
        self.page.wait_for_load_state("networkidle", timeout=timeout)

    def close_page(self):
        """关闭当前页面"""
        if self.page:
            self.page.close()
            if len(self.context.pages) > 0:
                self.page = self.context.pages[0]

    def new_page(self, url: str = None) -> Page:
        """打开新页面"""
        if not self.context:
            raise RuntimeError("浏览器未启动")

        page = self.context.new_page()
        if url:
            page.goto(url)

        return page

    def is_running(self) -> bool:
        """检查浏览器是否运行中"""
        return self.running and self.browser and self.browser.is_connected()

    def run_interactive(self):
        """
        交互模式：保持浏览器运行，等待用户操作

        在此模式下，浏览器会一直保持打开状态，
        用户可以手动操作，或通过其他脚本控制
        """
        print("\n" + "="*60)
        print("[浏览器] 交互模式启动")
        print("="*60)
        print(f"[浏览器] 浏览器已启动并保持运行")
        print(f"[浏览器] 用户数据目录: {self.user_data_dir}")
        print(f"[浏览器] Session 会自动保存")
        print(f"[浏览器] 按 Ctrl+C 停止")
        print("="*60 + "\n")

        try:
            # 保持运行
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[浏览器] 收到停止信号")
        finally:
            self.stop()


# 单例模式
_controller = None


def get_controller() -> BrowserController:
    """获取浏览器控制器单例"""
    global _controller
    if _controller is None or not _controller.is_running():
        _controller = BrowserController()
        _controller.start(headless=False)
    return _controller


def main():
    """测试/演示功能"""
    controller = BrowserController()

    try:
        # 启动浏览器
        controller.start(headless=False, channel="chrome")

        # 导航到 Google（示例）
        controller.goto("https://www.google.com")

        # 保持浏览器打开
        controller.run_interactive()

    except Exception as e:
        print(f"[错误] {e}")
        import traceback
        traceback.print_exc()
    finally:
        controller.stop()


if __name__ == "__main__":
    main()
