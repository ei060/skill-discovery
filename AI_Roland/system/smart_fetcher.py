"""
AI Roland SmartFetcher - 智能分层抓取系统

分层决策策略：
1. WebFetcher (Scrapling) - 静态页面，零浏览器
2. Playwright (标准模式) - JS 渲染页面
3. Playwright (Stealth 模式) - 有反爬的页面

自动决策逻辑：
- 先用 WebFetcher 试（快速）
- 检测到 JS 空壳 → 切换到 Playwright
- 检测到拦截 → 切换到 Stealth 模式
"""

import time
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime

# WebFetcher - 第一优先级
try:
    from web_fetcher import WebFetcher
    WEBFETCHER_AVAILABLE = True
except ImportError:
    WEBFETCHER_AVAILABLE = False

# Playwright - 第二/三优先级
try:
    from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class SmartFetcher:
    """
    智能分层抓取系统

    自动选择最合适的抓取方式：
    1. WebFetcher (Scrapling) - 静态内容
    2. Playwright (标准) - JS 渲染
    3. Playwright (Stealth) - 反爬虫
    """

    def __init__(self, user_data_dir: str = None, proxy: str = None):
        """
        初始化智能抓取器

        Args:
            user_data_dir: 用户数据目录
            proxy: 代理服务器
        """
        if user_data_dir is None:
            user_data_dir = Path(__file__).parent.parent / "browser_data"
        self.user_data_dir = Path(user_data_dir)
        self.user_data_dir.mkdir(parents=True, exist_ok=True)

        # 存储文件
        self.storage_file = self.user_data_dir / "storage_state.json"

        # 第一层：WebFetcher
        self.web_fetcher = WebFetcher(verify_ssl=False) if WEBFETCHER_AVAILABLE else None

        # 第二/三层：Playwright
        self.playwright = None
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None
        self.mode = None  # 'playwright' 或 'stealth'
        self.running = False
        self.proxy = proxy

        # 统计
        self.stats = {
            "total_fetches": 0,
            "webfetcher_success": 0,
            "playwright_success": 0,
            "stealth_success": 0,
            "escalations": 0
        }

    def fetch(self, url: str, auto_escalate: bool = True) -> Dict[str, Any]:
        """
        智能抓取网页

        Args:
            url: 目标 URL
            auto_escalate: 是否自动升级到浏览器模式

        Returns:
            {
                "success": bool,
                "method": str,  # "webfetcher", "playwright", "stealth"
                "url": str,
                "content": str,
                "metadata": dict,
                "escalated": bool
            }
        """
        self.stats["total_fetches"] += 1
        result = {
            "success": False,
            "method": None,
            "url": url,
            "content": None,
            "metadata": {
                "fetched_at": datetime.now().isoformat(),
                "response_time": 0,
                "escalated": False
            },
            "escalated": False
        }

        start_time = time.time()

        try:
            # 第一层：WebFetcher (Scrapling)
            if self.web_fetcher:
                print(f"[SmartFetcher] 尝试 WebFetcher: {url}")
                web_result = self.web_fetcher.fetch(url, method="auto")

                if web_result["success"]:
                    # 检查是否是 JS 空壳
                    if web_result.get("metadata", {}).get("is_js_shell"):
                        print(f"[SmartFetcher] 检测到 JS 空壳，升级到浏览器")
                        result["escalated"] = True
                        if auto_escalate:
                            result = self._fetch_with_playwright(url)
                    else:
                        # WebFetcher 成功
                        print(f"[SmartFetcher] WebFetcher 成功")
                        result["success"] = True
                        result["method"] = "webfetcher"
                        result["content"] = web_result["content"]
                        result["metadata"].update({
                            "engine": "scrapling",
                            "response_time": web_result.get("metadata", {}).get("response_time", 0)
                        })
                        self.stats["webfetcher_success"] += 1
                else:
                    # WebFetcher 失败，检查是否需要升级
                    error = web_result.get("error", "")
                    if self._should_escalate(error):
                        print(f"[SmartFetcher] WebFetcher 失败，升级: {error}")
                        result["escalated"] = True
                        if auto_escalate:
                            result = self._fetch_with_playwright(url)
                    else:
                        result["error"] = web_result.get("error")
            else:
                # 没有 WebFetcher，直接用 Playwright
                print(f"[SmartFetcher] WebFetcher 不可用，直接用 Playwright")
                result = self._fetch_with_playwright(url)

        except Exception as e:
            result["error"] = f"抓取异常: {str(e)}"
            # 尝试降级到 Playwright
            if auto_escalate:
                print(f"[SmartFetcher] 异常，降级到 Playwright: {e}")
                try:
                    result = self._fetch_with_playwright(url)
                    result["escalated"] = True
                except Exception as e2:
                    result["error"] = f"Playwright 也失败: {str(e2)}"

        result["metadata"]["response_time"] = round(time.time() - start_time, 2)
        return result

    def _should_escalate(self, error: str) -> bool:
        """判断是否需要升级到浏览器模式"""
        escalation_triggers = [
            "JS 渲染",
            "JavaScript",
            "需要浏览器",
            "空壳页面",
            "SSL",  # Scrapling 的 SSL 问题可能 Playwright 能处理
        ]
        return any(trigger in error for trigger in escalation_triggers)

    def _fetch_with_playwright(self, url: str, stealth_mode: bool = False) -> Dict[str, Any]:
        """使用 Playwright 获取内容"""
        if not PLAYWRIGHT_AVAILABLE:
            return {
                "success": False,
                "method": "playwright",
                "url": url,
                "error": "Playwright 未安装"
            }

        # 确保浏览器已启动
        if not self.running or not self.browser:
            self._start_playwright(stealth_mode=stealth_mode)

        # 如果需要 stealth 模式但当前不是
        if stealth_mode and self.mode != 'stealth':
            self._switch_to_stealth()

        print(f"[SmartFetcher] 使用 Playwright ({self.mode}): {url}")

        try:
            # 导航
            self.page.goto(url, wait_until="networkidle", timeout=30000)
            time.sleep(1)

            # 检测拦截
            if self._is_blocked():
                print(f"[SmartFetcher] 检测到拦截，切换到 Stealth")
                if self.mode != 'stealth':
                    self._switch_to_stealth()
                    # 重新导航
                    self.page.goto(url, wait_until="networkidle", timeout=30000)
                    time.sleep(1)

            # 获取内容
            content = self.page.content()

            return {
                "success": True,
                "method": self.mode,
                "url": url,
                "content": content,
                "metadata": {
                    "engine": "playwright",
                    "mode": self.mode
                }
            }

        except Exception as e:
            return {
                "success": False,
                "method": self.mode or "playwright",
                "url": url,
                "error": f"Playwright 失败: {str(e)}"
            }

    def _is_blocked(self) -> bool:
        """检测是否被拦截"""
        try:
            current_url = self.page.url

            # 检测登录页面
            if 'login' in current_url.lower() or 'i/flow' in current_url:
                return True

            # 检测 CAPTCHA
            page_text = self.page.inner_text("body").lower()
            if 'captcha' in page_text or 'robot' in page_text:
                return True

            return False
        except:
            return False

    def _start_playwright(self, stealth_mode: bool = False):
        """启动 Playwright"""
        if self.playwright is None:
            self.playwright = sync_playwright().start()

        launch_args = {
            'headless': False,
            'channel': 'chrome',
            'args': [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled',
            ],
        }

        # 代理
        if self.proxy:
            launch_args['proxy'] = {'server': self.proxy}

        self.browser = self.playwright.chromium.launch(**launch_args)

        # 加载存储状态
        storage_state = None
        if self.storage_file.exists():
            try:
                import json
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    storage_state = json.load(f)
            except:
                pass

        # 创建上下文
        self.context = self.browser.new_context(
            storage_state=storage_state,
            accept_downloads=True,
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        # 默认页面
        self.page = self.context.new_page()

        self.mode = 'playwright'
        self.running = True

        # 添加反检测脚本
        self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            window.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
        """)

        print(f"[SmartFetcher] Playwright 已启动 ({self.mode} 模式)")

    def _switch_to_stealth(self):
        """切换到 Stealth 模式（使用 undetected-chromedriver）"""
        # 保存当前状态
        if self.running:
            self._stop_playwright()

        # 启动 Stealth 模式
        try:
            import undetected_chromedriver as uc
            options = uc.ChromeOptions()
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument(f'--user-data-dir={self.user_data_dir}')
            options.add_argument('--profile-directory=Default')

            if self.proxy:
                options.add_argument(f'--proxy-server={self.proxy}')

            stealth_driver = uc.Chrome(version_main=145, options=options)
            stealth_driver.get("about:blank")

            # 标记模式
            self.mode = 'stealth'
            self.stealth_driver = stealth_driver

            print(f"[SmartFetcher] 已切换到 Stealth 模式")

        except ImportError:
            print("[警告] undetected-chromedriver 未安装，保持标准模式")
            self._start_playwright(stealth_mode=False)
        except Exception as e:
            print(f"[警告] Stealth 模式启动失败: {e}")
            self._start_playwright(stealth_mode=False)

    def _stop_playwright(self):
        """停止 Playwright"""
        if self.mode == 'stealth':
            if hasattr(self, 'stealth_driver') and self.stealth_driver:
                self.stealth_driver.quit()
                self.stealth_driver = None
        else:
            if self.context:
                try:
                    storage_state = self.context.storage_state()
                    with open(self.storage_file, 'w', encoding='utf-8') as f:
                        json.dump(storage_state, f, ensure_ascii=False, indent=2)
                except:
                    pass
                self.context.close()

            if self.browser:
                self.browser.close()

            if self.playwright:
                self.playwright.stop()

        self.running = False
        print("[SmartFetcher] Playwright 已停止")

    def close(self):
        """关闭所有资源"""
        if self.web_fetcher:
            self.web_fetcher.close()

        if self.running:
            self._stop_playwright()

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        total = self.stats["total_fetches"]
        webfetcher_rate = round(self.stats["webfetcher_success"] / total * 100, 1) if total > 0 else 0
        escalation_rate = round(self.stats["escalations"] / total * 100, 1) if total > 0 else 0

        return {
            "total_fetches": total,
            "webfetcher_success": self.stats["webfetcher_success"],
            "playwright_success": self.stats["playwright_success"],
            "stealth_success": self.stats["stealth_success"],
            "escalations": self.stats["escalations"],
            "webfetcher_success_rate": f"{webfetcher_rate}%",
            "escalation_rate": f"{escalation_rate}%"
        }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# 单例
_smart_fetcher = None


def get_smart_fetcher() -> SmartFetcher:
    """获取 SmartFetcher 单例"""
    global _smart_fetcher
    if _smart_fetcher is None:
        _smart_fetcher = SmartFetcher()
    return _smart_fetcher


# 测试
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python smart_fetcher.py <URL>")
        sys.exit(1)

    url = sys.argv[1]

    print(f"[SmartFetcher] 测试 URL: {url}")
    print()

    fetcher = SmartFetcher()

    try:
        result = fetcher.fetch(url)

        print()
        print("[结果]")
        print(f"  成功: {result['success']}")
        print(f"  方法: {result['method']}")
        print(f"  升级: {result['escalated']}")
        print(f"  响应时间: {result['metadata']['response_time']}秒")

        if result['success']:
            print(f"  内容长度: {len(result['content'])} 字符")
        else:
            print(f"  错误: {result.get('error', 'Unknown')}")

        print()
        print("[统计]")
        stats = fetcher.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")

    finally:
        fetcher.close()
