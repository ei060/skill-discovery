"""
AI Roland 浏览器控制器（增强版 v3.2）
- 支持持久化浏览器会话
- 支持 Stealth 模式（undetected-chromedriver）
- 自动拦截检测和模式切换
- 集成 SmartFetcher 分层抓取策略
- 统一 API 接口
- 新增 PinchTab 和 Agent-Browser 适配器

v3.1 更新：
- 集成 Scrapling 作为轻量级抓取引擎
- 新增 smart_fetch() 方法，自动选择最佳抓取方式
- 分层决策：WebFetcher → Playwright → Stealth

v3.2 更新：
- 新增 PinchTab 适配器（多实例、Token 高效）
- 新增 Agent-Browser 适配器（Vercel AI SDK 集成）
- 支持工具链选择：自动/手动选择浏览器工具
"""

import time
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from datetime import datetime

# SmartFetcher - 分层抓取系统
try:
    from smart_fetcher import SmartFetcher
    SMARTFETCHER_AVAILABLE = True
except ImportError:
    SMARTFETCHER_AVAILABLE = False
    print("[警告] SmartFetcher 未安装，分层抓取不可用")

# Stealth 模式支持
try:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    STEALTH_AVAILABLE = True
except ImportError:
    STEALTH_AVAILABLE = False
    print("[警告] undetected-chromedriver 未安装，stealth 模式不可用")

# PinchTab 适配器
try:
    from pinchtab_adapter import PinchTabAdapter, PinchTabInstance
    PINCHTAB_AVAILABLE = True
except ImportError:
    PINCHTAB_AVAILABLE = False
    print("[提示] PinchTab 适配器未安装")

# Agent-Browser 适配器
try:
    from agent_browser_adapter import AgentBrowserAdapter, AgentBrowserController
    AGENT_BROWSER_AVAILABLE = True
except ImportError:
    AGENT_BROWSER_AVAILABLE = False
    print("[提示] Agent-Browser 适配器未安装")


class BrowserController:
    """增强版浏览器控制器（v3.2 - 支持多工具链）"""

    # 工具链枚举
    TOOL_AUTO = "auto"       # 自动选择
    TOOL_PLAYWRIGHT = "playwright"  # 标准 Playwright
    TOOL_STEALTH = "stealth"        # Stealth 模式
    TOOL_PINCHTAB = "pinchtab"      # PinchTab (多实例)
    TOOL_AGENT_BROWSER = "agent_browser"  # Agent-Browser (Vercel)

    def __init__(self, user_data_dir: str = None, proxy: str = None, tool: str = TOOL_AUTO):
        """
        初始化浏览器控制器

        Args:
            user_data_dir: 用户数据目录，用于保存会话状态
            proxy: 代理服务器 (格式: "protocol://user:pass@host:port" 或 "protocol://host:port")
            tool: 工具选择 (auto/playwright/stealth/pinchtab/agent_browser)
        """
        if user_data_dir is None:
            user_data_dir = Path(__file__).parent.parent / "browser_data"
        self.user_data_dir = Path(user_data_dir)
        self.user_data_dir.mkdir(parents=True, exist_ok=True)

        # Cookie 文件路径
        self.cookie_file = self.user_data_dir / "cookies.json"
        self.storage_file = self.user_data_dir / "storage_state.json"

        # 工具选择
        self.tool = tool

        # SmartFetcher - 分层抓取系统
        self.smart_fetcher = SmartFetcher(user_data_dir, proxy) if SMARTFETCHER_AVAILABLE else None

        # Playwright 引擎
        self.playwright = None
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None

        # Stealth 引擎（Selenium + undetected-chromedriver）
        self.stealth_driver = None

        # PinchTab 适配器
        self.pinchtab: PinchTabAdapter = None
        self.pinchtab_instance: PinchTabInstance = None

        # Agent-Browser 适配器
        self.agent_browser: AgentBrowserController = None

        # 状态
        self.running = False
        self.mode = None  # 'playwright', 'stealth', 'pinchtab', 'agent_browser'
        self.headless = False
        self.proxy = proxy  # 代理配置

        # 统计信息
        self.stats = {
            "smart_fetch_count": 0,
            "smart_fetch_success": 0,
            "browser_fetch_count": 0,
            "tool_used": None
        }

    def start(self, headless: bool = False, channel: str = "chrome", stealth_mode: bool = False):
        """
        启动浏览器

        Args:
            headless: 是否无头模式
            channel: 浏览器类型 (chrome, msedge, chromium)
            stealth_mode: 是否使用 stealth 模式（绕过机器人检测）
        """
        self.headless = headless

        if stealth_mode and STEALTH_AVAILABLE:
            self._start_stealth(headless)
        else:
            if stealth_mode and not STEALTH_AVAILABLE:
                print("[警告] stealth_mode=True 但 undetected-chromedriver 未安装，使用标准模式")
            self._start_playwright(headless, channel)

        self.running = True

    def _start_playwright(self, headless: bool, channel: str):
        """启动标准 Playwright 模式"""
        self.mode = 'playwright'
        self.playwright = sync_playwright().start()

        # 启动浏览器
        launch_args = {
            'headless': headless,
            'channel': channel,
            'args': [
                '--no-sandbox',
                '--disable-setuid-sandbox',
            ],
        }

        # 添加代理支持
        if self.proxy:
            launch_args['proxy'] = {'server': self.proxy}
            print(f"[浏览器] 使用代理: {self.proxy}")

        self.browser = self.playwright.chromium.launch(**launch_args)

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

        print(f"[浏览器] 已启动 ({channel}) - 标准模式")
        print(f"[浏览器] 用户数据: {self.user_data_dir}")
        print(f"[浏览器] 无头模式: {headless}")

    def _start_stealth(self, headless: bool):
        """启动 Stealth 模式（undetected-chromedriver）"""
        self.mode = 'stealth'

        options = uc.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')

        # 使用用户数据目录（保持会话持久化）
        options.add_argument(f'--user-data-dir={self.user_data_dir}')
        options.add_argument('--profile-directory=Default')

        # 添加代理支持
        if self.proxy:
            options.add_argument(f'--proxy-server={self.proxy}')
            print(f"[浏览器] 使用代理: {self.proxy}")

        # 启动 undetected-chromedriver
        self.stealth_driver = uc.Chrome(
            version_main=145,  # Chrome 版本
            options=options,
            headless=headless
        )

        # 自动加载之前保存的 cookies（如果有）
        if self.cookie_file.exists():
            try:
                import pickle
                with open(self.cookie_file, 'rb') as f:
                    cookies = pickle.load(f)
                # 添加 cookies
                for cookie in cookies:
                    try:
                        self.stealth_driver.add_cookie(cookie)
                    except:
                        pass
                print(f"[浏览器] 已加载保存的 cookies")
            except Exception as e:
                print(f"[浏览器] 加载 cookies 失败: {e}")

        print(f"[浏览器] 已启动 - Stealth 模式")
        print(f"[浏览器] 用户数据: {self.user_data_dir}")
        print(f"[浏览器] 无头模式: {headless}")
        print(f"[浏览器] 反机器人检测: 已启用")
        if self.proxy:
            print(f"[浏览器] 代理服务器: {self.proxy}")

    def switch_to_stealth(self):
        """切换到 Stealth 模式（检测到拦截时自动调用）"""
        if self.mode == 'stealth':
            print("[浏览器] 已经是 Stealth 模式")
            return

        print("[浏览器] 检测到拦截，切换到 Stealth 模式...")

        # 保存当前状态
        self.stop()

        # 启动 stealth 模式
        self._start_stealth(self.headless)
        self.running = True

    def stop(self):
        """停止浏览器并保存 session"""
        if self.mode == 'stealth':
            self._stop_stealth()
        elif self.mode == 'pinchtab':
            self._stop_pinchtab()
        elif self.mode == 'agent_browser':
            self._stop_agent_browser()
        else:
            self._stop_playwright()

        self.running = False

    # ============================================================
    # PinchTab 适配器方法 (v3.2 新增)
    # ============================================================

    def start_pinchtab(self, instance_name: str = "default", headless: bool = True,
                       port: int = None) -> bool:
        """
        启动 PinchTab 实例

        PinchTab 优势：
        - Token 高效 (~800 tokens/page)
        - 多实例隔离
        - HTTP API

        Args:
            instance_name: 实例名称
            headless: 是否无头模式
            port: 指定端口
        """
        if not PINCHTAB_AVAILABLE:
            print("[错误] PinchTab 不可用，请先安装: npm install -g pinchtab")
            return False

        if self.pinchtab is None:
            self.pinchtab = PinchTabAdapter(base_port=9867)

        self.pinchtab_instance = self.pinchtab.create_instance(
            instance_name, headless=headless, port=port
        )

        if self.pinchtab_instance:
            self.mode = 'pinchtab'
            self.running = True
            self.stats["tool_used"] = "pinchtab"
            return True
        return False

    def _stop_pinchtab(self):
        """停止 PinchTab 实例"""
        if self.pinchtab_instance:
            self.pinchtab_instance.stop()
            self.pinchtab_instance = None

    def pinchtab_navigate(self, url: str) -> Dict[str, Any]:
        """使用 PinchTab 导航"""
        if not self.pinchtab_instance:
            return {"error": "PinchTab 未启动"}
        return self.pinchtab_instance.navigate(url)

    def pinchtab_snapshot(self, interactive: bool = True, compact: bool = True) -> Dict[str, Any]:
        """获取 PinchTab 快照"""
        if not self.pinchtab_instance:
            return {"error": "PinchTab 未启动"}
        return self.pinchtab_instance.snapshot(interactive=interactive, compact=compact)

    def pinchtab_text(self) -> Dict[str, Any]:
        """提取文本 (Token 高效)"""
        if not self.pinchtab_instance:
            return {"error": "PinchTab 未启动"}
        return self.pinchtab_instance.text()

    def pinchtab_click(self, ref: str) -> Dict[str, Any]:
        """点击元素 (通过 ref)"""
        if not self.pinchtab_instance:
            return {"error": "PinchTab 未启动"}
        return self.pinchtab_instance.click(ref)

    # ============================================================
    # Agent-Browser 适配器方法 (v3.2 新增)
    # ============================================================

    def start_agent_browser(self) -> bool:
        """
        启动 Agent-Browser

        Agent-Browser 优势：
        - Vercel AI SDK 原生集成
        - ref 系统稳定
        - TypeScript 类型安全
        """
        if not AGENT_BROWSER_AVAILABLE:
            print("[错误] Agent-Browser 不可用，请先安装: npm install -g agent-browser")
            return False

        self.agent_browser = AgentBrowserController()
        self.mode = 'agent_browser'
        self.running = True
        self.stats["tool_used"] = "agent_browser"
        return True

    def _stop_agent_browser(self):
        """停止 Agent-Browser"""
        if self.agent_browser:
            self.agent_browser.close()
            self.agent_browser = None

    def agent_browser_open(self, url: str) -> Dict[str, Any]:
        """使用 Agent-Browser 打开 URL"""
        if not self.agent_browser:
            return {"error": "Agent-Browser 未启动"}
        return self.agent_browser.open(url)

    def agent_browser_snapshot(self, interactive: bool = False) -> Dict[str, Any]:
        """获取 Agent-Browser 快照"""
        if not self.agent_browser:
            return {"error": "Agent-Browser 未启动"}
        return self.agent_browser.snapshot(interactive=interactive)

    def agent_browser_click(self, ref: str) -> Dict[str, Any]:
        """点击元素 (通过 ref)"""
        if not self.agent_browser:
            return {"error": "Agent-Browser 未启动"}
        return self.agent_browser.click(ref)

    def _stop_playwright(self):
        """停止 Playwright 模式"""
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

        print("[浏览器] 已停止")

    def _stop_stealth(self):
        """停止 Stealth 模式"""
        if self.stealth_driver:
            # 保存 cookies（保持登录状态）
            try:
                import pickle
                cookies = self.stealth_driver.get_cookies()
                with open(self.cookie_file, 'wb') as f:
                    pickle.dump(cookies, f)
                print(f"[浏览器] Cookies 已保存")
            except Exception as e:
                print(f"[浏览器] 保存 cookies 失败: {e}")

            self.stealth_driver.quit()
            print("[浏览器] Stealth 模式已停止")

    def smart_fetch(self, url: str, use_browser_fallback: bool = True) -> Dict[str, Any]:
        """
        智能抓取网页 - 自动选择最佳方式

        这是 v3.1 的核心功能，分层决策：
        1. WebFetcher (Scrapling) - 静态页面，零浏览器
        2. Playwright (标准) - JS 渲染页面
        3. Playwright (Stealth) - 有反爬的页面

        Args:
            url: 目标 URL
            use_browser_fallback: 是否在 WebFetcher 失败后降级到浏览器

        Returns:
            {
                "success": bool,
                "method": str,  # "webfetcher", "playwright", "stealth"
                "url": str,
                "content": str,
                "metadata": dict,
                "escalated": bool  # 是否从轻量级升级到浏览器
            }
        """
        self.stats["smart_fetch_count"] += 1

        print(f"[浏览器] smart_fetch: {url}")

        # 优先使用 SmartFetcher（分层抓取系统）
        if self.smart_fetcher:
            result = self.smart_fetcher.fetch(url, auto_escalate=use_browser_fallback)

            if result["success"]:
                self.stats["smart_fetch_success"] += 1

            print(f"[浏览器] smart_fetch 结果: {result['method']}, 成功: {result['success']}")
            return result

        # 降级：直接使用浏览器
        if use_browser_fallback:
            print(f"[浏览器] SmartFetcher 不可用，使用浏览器")

            # 确保浏览器已启动
            if not self.is_running():
                self.start(headless=True)

            # 导航
            self.goto(url, wait_until="networkidle", detect_block=True)

            # 获取内容
            if self.mode == 'stealth' and self.stealth_driver:
                content = self.stealth_driver.page_source
            else:
                content = self.page.content()

            return {
                "success": True,
                "method": self.mode or "browser",
                "url": url,
                "content": content,
                "metadata": {
                    "engine": "browser",
                    "mode": self.mode
                },
                "escalated": False
            }

        return {
            "success": False,
            "method": "none",
            "url": url,
            "error": "SmartFetcher 不可用且浏览器降级被禁用"
        }

    def goto(self, url: str, wait_until: str = "networkidle", detect_block: bool = True):
        """
        导航到指定URL

        Args:
            url: 目标URL
            wait_until: 等待条件 (load, domcontentloaded, networkidle)
            detect_block: 是否检测拦截并自动切换到 stealth 模式
        """
        if not self.is_running():
            raise RuntimeError("浏览器未启动，请先调用 start()")

        print(f"[浏览器] 导航到: {url}")

        if self.mode == 'stealth':
            # Stealth 模式使用 Selenium
            self.stealth_driver.get(url)
            time.sleep(10)  # Stealth 模式需要更长等待时间
        else:
            # Playwright 模式
            self.page.goto(url, wait_until=wait_until)
            time.sleep(1)

        # 检测拦截
        if detect_block and self.mode == 'playwright':
            if self._is_blocked():
                print("[警告] 检测到拦截，切换到 Stealth 模式...")
                self.switch_to_stealth()
                # 重新导航
                self.goto(url, wait_until, detect_block=False)

    def _is_blocked(self) -> bool:
        """检测是否被拦截（登录页、CAPTCHA等）"""
        try:
            current_url = self.get_url()

            # 检测登录页面
            if 'login' in current_url.lower() or 'i/flow' in current_url:
                return True

            # 检测 CAPTCHA
            if self.mode == 'playwright':
                page_text = self.page.inner_text("body").lower()
                if 'captcha' in page_text or 'robot' in page_text:
                    return True

            return False

        except:
            return False

    def wait_for_selector(self, selector: str, timeout: int = 30000):
        """等待选择器出现"""
        if not self.is_running():
            raise RuntimeError("浏览器未启动")

        print(f"[浏览器] 等待元素: {selector}")

        if self.mode == 'stealth':
            # Stealth 模式使用 Selenium
            WebDriverWait(self.stealth_driver, timeout/1000).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
        else:
            # Playwright 模式
            self.page.wait_for_selector(selector, timeout=timeout)

    def click(self, selector: str):
        """点击元素"""
        if not self.is_running():
            raise RuntimeError("浏览器未启动")

        print(f"[浏览器] 点击: {selector}")

        if self.mode == 'stealth':
            self.stealth_driver.find_element(By.CSS_SELECTOR, selector).click()
        else:
            self.page.click(selector)

        time.sleep(0.5)

    def fill(self, selector: str, value: str):
        """填写表单"""
        if not self.is_running():
            raise RuntimeError("浏览器未启动")

        print(f"[浏览器] 填写: {selector} = {value[:20]}...")

        if self.mode == 'stealth':
            self.stealth_driver.find_element(By.CSS_SELECTOR, selector).send_keys(value)
        else:
            self.page.fill(selector, value)

        time.sleep(0.3)

    def screenshot(self, path: str = None):
        """
        截图

        Args:
            path: 保存路径，默认自动生成
        """
        if not self.is_running():
            raise RuntimeError("浏览器未启动")

        if path is None:
            path = self.user_data_dir / f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

        if self.mode == 'stealth':
            self.stealth_driver.save_screenshot(str(path))
        else:
            self.page.screenshot(path=str(path))

        print(f"[浏览器] 截图已保存: {path}")
        return path

    def get_url(self) -> str:
        """获取当前URL"""
        if not self.is_running():
            raise RuntimeError("浏览器未启动")

        if self.mode == 'stealth':
            return self.stealth_driver.current_url
        else:
            return self.page.url

    def get_text(self, selector: str = None) -> str:
        """
        获取页面文本

        Args:
            selector: 指定选择器，None则获取整个页面
        """
        if not self.is_running():
            raise RuntimeError("浏览器未启动")

        if self.mode == 'stealth':
            if selector:
                return self.stealth_driver.find_element(By.CSS_SELECTOR, selector).text
            else:
                return self.stealth_driver.find_element(By.TAG_NAME, "body").text
        else:
            if selector:
                element = self.page.query_selector(selector)
                return element.inner_text() if element else ""
            else:
                return self.page.inner_text("body")

    def evaluate(self, script: str):
        """执行JavaScript"""
        if not self.is_running():
            raise RuntimeError("浏览器未启动")

        if self.mode == 'stealth':
            return self.stealth_driver.execute_script(script)
        else:
            return self.page.evaluate(script)

    def wait_for_navigation(self, timeout: int = 30000):
        """等待导航完成"""
        if not self.is_running():
            raise RuntimeError("浏览器未启动")

        print(f"[浏览器] 等待导航...")

        if self.mode == 'playwright':
            self.page.wait_for_load_state("networkidle", timeout=timeout)
        else:
            time.sleep(3)  # Stealth 模式简单等待

    def close_page(self):
        """关闭当前页面"""
        if self.mode == 'playwright' and self.page:
            self.page.close()
            if len(self.context.pages) > 0:
                self.page = self.context.pages[0]

    def new_page(self, url: str = None):
        """打开新页面"""
        if not self.is_running():
            raise RuntimeError("浏览器未启动")

        if self.mode == 'playwright':
            page = self.context.new_page()
            if url:
                page.goto(url)
            return page

    def is_running(self) -> bool:
        """检查浏览器是否运行中"""
        if self.mode == 'stealth':
            try:
                return self.stealth_driver is not None
            except:
                return False
        else:
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
        print(f"[浏览器] 运行模式: {self.mode}")
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

    def get_page_content(self, use_javascript: bool = True) -> dict:
        """
        获取当前页面内容（优先级模式）

        Args:
            use_javascript: 是否优先使用 JavaScript 提取

        Returns:
            dict: 包含页面内容的字典，包含 success 和 data/error 字段
        """
        result = {"success": False, "method": None, "data": None, "error": None}

        # 优先级1: JavaScript 提取（最可靠，适用于动态内容）
        if use_javascript and self.mode == 'stealth' and self.stealth_driver:
            try:
                # 增强版 Twitter/X 提取脚本
                twitter_script = """
                (function() {
                    // 辅助函数：清理文本
                    function cleanText(str) {
                        if (!str) return null;
                        return str.replace(/\\n+/g, ' ').trim();
                    }

                    // 获取页面标题
                    var title = document.title;

                    // 获取当前URL
                    var url = window.location.href;

                    // 尝试多种方式获取推文文本
                    var tweetText = null;

                    // 方式1: data-testid="tweetText"
                    var tweetTextEl = document.querySelector('[data-testid="tweetText"]');
                    if (tweetTextEl) {
                        tweetText = cleanText(tweetTextEl.innerText);
                    }

                    // 方式2: 查找所有推文并获取第一个
                    if (!tweetText) {
                        var tweets = document.querySelectorAll('[data-testid="tweet"]');
                        if (tweets.length > 0) {
                            var textEl = tweets[0].querySelector('[data-testid="tweetText"]');
                            if (textEl) {
                                tweetText = cleanText(textEl.innerText);
                            }
                        }
                    }

                    // 方式3: 获取页面主要文本内容
                    if (!tweetText) {
                        var article = document.querySelector('article');
                        if (article) {
                            tweetText = cleanText(article.innerText);
                        }
                    }

                    // 如果都没有，获取body前3000字符
                    if (!tweetText) {
                        tweetText = document.body.innerText.substring(0, 3000);
                    }

                    // 获取作者信息
                    var author = null;
                    var authorNameEl = document.querySelector('[data-testid="User-Name"]');
                    if (authorNameEl) {
                        author = cleanText(authorNameEl.innerText);
                    }

                    // 获取时间
                    var timeEl = document.querySelector('time');
                    var time = timeEl ? timeEl.getAttribute('datetime') : null;

                    // 返回结果
                    return {
                        text: tweetText,
                        author: author,
                        time: time,
                        url: url,
                        title: title
                    };
                })();
                """

                content = self.stealth_driver.execute_script(twitter_script)

                if content and content.get('text'):
                    result["success"] = True
                    result["method"] = "javascript"
                    result["data"] = content
                else:
                    # JavaScript 返回空数据，尝试下一优先级
                    result["error"] = "JavaScript提取: 未找到内容"

            except Exception as e:
                result["error"] = f"JavaScript提取失败: {str(e)}"

        # 优先级2: HTML 源码解析（备用方案）
        if not result.get("success") and self.mode == 'stealth' and self.stealth_driver:
            try:
                page_source = self.stealth_driver.page_source
                result["success"] = True
                result["method"] = "html_source"
                result["data"] = {"html": page_source[:20000]}  # 前20000字符
                return result
            except Exception as e:
                result["error"] = f"HTML解析失败: {str(e)}"

        # 优先级3: 截图（最后备选）
        if not result.get("success"):
            try:
                screenshot_path = self.user_data_dir / "screenshot.png"
                self.stealth_driver.save_screenshot(str(screenshot_path))
                result["success"] = True
                result["method"] = "screenshot"
                result["data"] = {"screenshot": str(screenshot_path)}
            except Exception as e:
                result["error"] = f"截图失败: {str(e)}"

        return result


# 单例模式
_controller = None


def get_controller(proxy: str = None, headless: bool = None) -> BrowserController:
    """
    获取浏览器控制器单例

    Args:
        proxy: 代理服务器 (格式: "protocol://user:pass@host:port" 或 "protocol://host:port")
        headless: 是否无头模式 (None=自动检测，True=强制无头，False=强制显示窗口)
    """
    global _controller
    if _controller is None or not _controller.is_running():
        _controller = BrowserController(proxy=proxy)
        # 自动检测：如果未指定，检查是否在后台环境
        if headless is None:
            # 使用 sys_utils 的安全接口检测环境
            from sys_utils import SafeIO
            is_interactive = SafeIO.is_interactive()
            headless = not is_interactive
        _controller.start(headless=headless)
    return _controller


def main():
    """测试/演示功能"""
    import sys

    # 检查命令行参数
    stealth_mode = '--stealth' in sys.argv

    controller = BrowserController()

    try:
        # 启动浏览器
        if stealth_mode:
            print("[测试] 启动 Stealth 模式...")
            controller.start(headless=False, stealth_mode=True)

            # 测试 Twitter（无需登录）
            controller.goto("https://x.com/binghe/status/2027685265817694668")

            # 提取推文
            tweet_text = controller.get_text('article[role="article"]')
            print("\n推文内容:")
            print("-" * 70)
            print(tweet_text[:500])
            print("-" * 70)

        else:
            print("[测试] 启动标准模式...")
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
