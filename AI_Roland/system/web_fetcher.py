"""
AI Roland WebFetcher - 轻量级网页抓取器（第一优先级）
- 集成 Scrapling 作为主要抓取引擎
- 支持多种提取方式（Scrapling、Jina Reader、Nitter等）
- 作为 BrowserController 的轻量级前置方案
- 分层决策：静态→HTTP，JS→浏览器，反爬→Stealth
"""

import re
import json
import time
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse, urlunparse
from datetime import datetime
from pathlib import Path

# Scrapling - 优先使用
try:
    from scrapling.fetchers import Fetcher as ScraplingFetcher
    SCRAPLING_AVAILABLE = True
except ImportError:
    SCRAPLING_AVAILABLE = False
    print("[警告] Scrapling 未安装，将使用备用方案")

# Requests - 备用方案
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("[警告] requests 未安装，部分功能不可用")


class WebFetcher:
    """
    轻量级网页抓取器

    设计原则：
    1. 零浏览器启动，快速响应
    2. 多种提取方式，自动降级
    3. 智能判断是否适用
    4. 失败时提供明确原因
    """

    def __init__(self, timeout: int = 10, user_agent: str = None, verify_ssl: bool = False, use_scrapling: bool = True):
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.use_scrapling = use_scrapling and SCRAPLING_AVAILABLE
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        self.session = None
        if REQUESTS_AVAILABLE:
            self.session = requests.Session()
            self.session.headers.update({'User-Agent': self.user_agent})
            self.session.verify = verify_ssl
            if not verify_ssl:
                # 禁用 SSL 警告
                import urllib3
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # 统计信息
        self.stats = {
            "total_attempts": 0,
            "success": 0,
            "failed": 0,
            "by_method": {}
        }

        # 引擎状态
        self.engines = {
            "scrapling": SCRAPLING_AVAILABLE,
            "requests": REQUESTS_AVAILABLE,
            "jina": REQUESTS_AVAILABLE,
            "nitter": REQUESTS_AVAILABLE
        }

    def is_suitable(self, url: str) -> Dict[str, Any]:
        """
        判断是否适合使用 WebFetcher

        返回：{
            "suitable": bool,
            "reason": str,
            "confidence": float  # 0-1
        }
        """
        domain = urlparse(url).netloc.lower()

        # 明确适合的场景
        suitable_patterns = {
            # 博客和文档
            "blog.", "docs.", "dev.", "developer.",
            # 新闻和文章
            "news.", "article", "wiki.", "medium.com",
            # 技术站点
            "github.com", "gitlab.com", "stackoverflow.com",
            "reddit.com", "hn.", "hackernews",
            # Markdown 转换服务
            "r.jina.ai",
        }

        # 明确不适合的场景
        unsuitable_patterns = {
            # 需要登录/JS渲染的社交媒体
            "twitter.com", "x.com", "facebook.com", "instagram.com",
            "tiktok.com", "linkedin.com",
            # 视频平台
            "youtube.com", "youtu.be", "bilibili.com",
            # SPA 应用
            "web.app", "firebaseapp.com",
        }

        # 检查不适用模式
        for pattern in unsuitable_patterns:
            if pattern in domain:
                return {
                    "suitable": False,
                    "reason": f"域名包含 {pattern}，需要浏览器渲染",
                    "confidence": 0.9,
                    "suggestion": "use_browser"
                }

        # 检查适用模式
        for pattern in suitable_patterns:
            if pattern in domain:
                return {
                    "suitable": True,
                    "reason": f"域名包含 {pattern}，通常是静态内容",
                    "confidence": 0.8,
                    "suggestion": "use_webfetch"
                }

        # 默认：可能适用，但不确定
        return {
            "suitable": True,
            "reason": "无明确不适合特征，可尝试",
            "confidence": 0.5,
            "suggestion": "try_webfetch_first"
        }

    def fetch(self, url: str, method: str = "auto") -> Dict[str, Any]:
        """
        抓取网页内容

        Args:
            url: 目标 URL
            method: 提取方式
                - "auto": 自动选择最佳方式（优先 Scrapling）
                - "scrapling": 使用 Scrapling Fetcher
                - "direct": 直接 HTTP 请求（requests）
                - "jina": Jina Reader API
                - "nitter": Twitter Nitter 实例
                - "all": 尝试所有方式

        Returns:
            {
                "success": bool,
                "method": str,
                "url": str,
                "content": str,
                "metadata": dict,
                "error": str (如果失败)
            }
        """
        self.stats["total_attempts"] += 1
        result = {
            "success": False,
            "method": None,
            "url": url,
            "content": None,
            "metadata": {
                "fetched_at": datetime.now().isoformat(),
                "response_time": 0,
                "content_length": 0
            },
            "error": None
        }

        start_time = time.time()

        try:
            if method == "auto":
                # 自动选择最佳方式
                result = self._auto_fetch(url)
            elif method == "scrapling":
                result = self._scrapling_fetch(url)
            elif method == "direct":
                result = self._direct_fetch(url)
            elif method == "jina":
                result = self._jina_fetch(url)
            elif method == "nitter":
                result = self._nitter_fetch(url)
            elif method == "all":
                result = self._try_all(url)
            else:
                result["error"] = f"未知的 method: {method}"

        except Exception as e:
            result["error"] = f"抓取异常: {str(e)}"

        # 确保字段存在
        if "metadata" not in result:
            result["metadata"] = {}

        # 记录统计
        result["metadata"]["response_time"] = round(time.time() - start_time, 2)
        if result["success"]:
            result["metadata"]["content_length"] = len(result.get("content", ""))
            self.stats["success"] += 1
        else:
            self.stats["failed"] += 1

        # 记录方法统计
        method_name = result.get("method", "unknown")
        if method_name not in self.stats["by_method"]:
            self.stats["by_method"][method_name] = {"success": 0, "failed": 0}
        if result["success"]:
            self.stats["by_method"][method_name]["success"] += 1
        else:
            self.stats["by_method"][method_name]["failed"] += 1

        return result

    def _auto_fetch(self, url: str) -> Dict[str, Any]:
        """自动选择最佳提取方式"""
        domain = urlparse(url).netloc.lower()

        # 第一优先级：Scrapling（如果可用）
        if self.use_scrapling and SCRAPLING_AVAILABLE:
            scrapling_result = self._scrapling_fetch(url)
            if scrapling_result["success"]:
                return scrapling_result

        # Twitter/X -> Nitter
        if "twitter.com" in domain or "x.com" in domain:
            # 先尝试 Jina（更稳定）
            jina_result = self._jina_fetch(url)
            if jina_result["success"]:
                return jina_result
            # 降级到 Nitter
            return self._nitter_fetch(url)

        # 优先尝试 Jina Reader（最稳定）
        jina_result = self._jina_fetch(url)
        if jina_result["success"] and len(jina_result.get("content", "")) > 100:
            return jina_result

        # Jina 失败或内容太少，尝试直接请求
        direct_result = self._direct_fetch(url)
        if direct_result["success"]:
            return direct_result

        # 都失败了，返回 Jina 的错误（通常更详细）
        return jina_result

    def _scrapling_fetch(self, url: str) -> Dict[str, Any]:
        """使用 Scrapling Fetcher 获取内容"""
        if not SCRAPLING_AVAILABLE:
            return {
                "success": False,
                "method": "scrapling",
                "url": url,
                "content": None,
                "metadata": {},
                "error": "Scrapling 未安装"
            }

        try:
            # 使用 Scrapling Fetcher
            page = ScraplingFetcher.get(url, verify=self.verify_ssl, timeout=self.timeout)

            # 获取内容
            content = page.html_content

            # 检测是否是 JS 空壳页面
            if self._is_js_shell(content):
                return {
                    "success": False,
                    "method": "scrapling",
                    "url": url,
                    "content": content,
                    "metadata": {
                        "status": page.status,
                        "is_js_shell": True
                    },
                    "error": "页面需要 JS 渲染（检测到空壳页面）",
                    "suggestion": "use_browser"
                }

            return {
                "success": True,
                "method": "scrapling",
                "url": url,
                "content": content,
                "metadata": {
                    "status": page.status,
                    "encoding": page.encoding,
                    "is_html": self._is_html(content),
                    "engine": "scrapling"
                }
            }

        except Exception as e:
            error_msg = str(e)
            # 检测是否是 SSL 错误
            if "SSL" in error_msg or "certificate" in error_msg:
                return {
                    "success": False,
                    "method": "scrapling",
                    "url": url,
                    "content": None,
                    "metadata": {},
                    "error": f"SSL 证书验证失败: {error_msg}",
                    "suggestion": "try_with_verify_false"
                }
            return {
                "success": False,
                "method": "scrapling",
                "url": url,
                "content": None,
                "metadata": {},
                "error": f"Scrapling 请求失败: {error_msg}"
            }

    def _direct_fetch(self, url: str) -> Dict[str, Any]:
        """直接 HTTP 请求获取 HTML"""
        if not REQUESTS_AVAILABLE:
            return {
                "success": False,
                "method": "direct",
                "url": url,
                "error": "requests 库未安装"
            }

        try:
            response = self.session.get(
                url,
                timeout=self.timeout,
                allow_redirects=True,
                verify=self.verify_ssl,
                headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                }
            )

            if response.status_code == 200:
                content = response.text

                # 检测是否是 JS 渲染页面的空壳
                if self._is_js_shell(content):
                    return {
                        "success": False,
                        "method": "direct",
                        "url": url,
                        "error": "页面需要 JS 渲染（检测到空壳页面）",
                        "suggestion": "use_browser"
                    }

                return {
                    "success": True,
                    "method": "direct",
                    "url": url,
                    "content": content,
                    "metadata": {
                        "status_code": response.status_code,
                        "content_type": response.headers.get("Content-Type", ""),
                        "encoding": response.encoding,
                        "is_html": self._is_html(content)
                    }
                }
            else:
                return {
                    "success": False,
                    "method": "direct",
                    "url": url,
                    "error": f"HTTP {response.status_code}"
                }

        except requests.Timeout:
            return {
                "success": False,
                "method": "direct",
                "url": url,
                "error": f"请求超时（{self.timeout}秒）"
            }
        except Exception as e:
            return {
                "success": False,
                "method": "direct",
                "url": url,
                "error": f"请求失败: {str(e)}"
            }

    def _jina_fetch(self, url: str) -> Dict[str, Any]:
        """使用 Jina Reader API（转为 Markdown）"""
        if not REQUESTS_AVAILABLE:
            return {
                "success": False,
                "method": "jina",
                "url": url,
                "content": None,
                "metadata": {},
                "error": "requests 库未安装"
            }

        # Jina Reader API
        jina_url = f"https://r.jina.ai/{url}"

        try:
            response = self.session.get(
                jina_url,
                timeout=self.timeout,
                verify=self.verify_ssl,
                headers={'Accept': 'text/markdown'}
            )

            if response.status_code == 200:
                content = response.text.strip()

                # 检查是否有实际内容
                if len(content) < 50:
                    return {
                        "success": False,
                        "method": "jina",
                        "url": url,
                        "content": None,
                        "metadata": {},
                        "error": f"Jina 返回内容过短（{len(content)} 字符）"
                    }

                # 检查是否是错误信息
                if content.startswith("error:") or "couldn't fetch" in content.lower():
                    return {
                        "success": False,
                        "method": "jina",
                        "url": url,
                        "content": None,
                        "metadata": {},
                        "error": f"Jina 错误: {content[:200]}"
                    }

                return {
                    "success": True,
                    "method": "jina",
                    "url": url,
                    "content": content,
                    "metadata": {
                        "format": "markdown",
                        "content_length": len(content),
                        "is_markdown": True
                    }
                }
            else:
                return {
                    "success": False,
                    "method": "jina",
                    "url": url,
                    "content": None,
                    "metadata": {},
                    "error": f"Jina HTTP {response.status_code}"
                }

        except Exception as e:
            return {
                "success": False,
                "method": "jina",
                "url": url,
                "content": None,
                "metadata": {},
                "error": f"Jina 请求失败: {str(e)}"
            }

    def _nitter_fetch(self, url: str) -> Dict[str, Any]:
        """使用 Nitter 实例抓取 Twitter"""
        if not REQUESTS_AVAILABLE:
            return {
                "success": False,
                "method": "nitter",
                "url": url,
                "content": None,
                "metadata": {},
                "error": "requests 库未安装"
            }

        # Nitter 公共实例列表
        nitter_instances = [
            "nitter.net",
            "nitter.poast.org",
            "nitter.privacydev.net",
            "nitter.1d4.us",
            "nitter.kavin.rocks"
        ]

        # 转换 URL
        # https://x.com/user/status/123 -> https://nitter.net/user/status/123
        parsed = urlparse(url)

        for instance in nitter_instances:
            try:
                nitter_url = urlunparse((
                    parsed.scheme,
                    instance,
                    parsed.path,
                    parsed.params,
                    parsed.query,
                    parsed.fragment
                ))

                response = self.session.get(
                    nitter_url,
                    timeout=self.timeout,
                    verify=self.verify_ssl,
                    headers={'Accept': 'text/html'}
                )

                if response.status_code == 200:
                    content = response.text

                    # 检查是否被限流
                    if "rate limit" in content.lower() or "too many requests" in content.lower():
                        continue  # 尝试下一个实例

                    # 检查是否有实际推文内容
                    if "tweet-content" not in content and "timeline" not in content:
                        continue  # 可能不是有效的推文页面

                    return {
                        "success": True,
                        "method": "nitter",
                        "url": url,
                        "content": content,
                        "metadata": {
                            "nitter_instance": instance,
                            "original_url": url,
                            "nitter_url": nitter_url,
                            "is_twitter": True
                        }
                    }

            except Exception as e:
                # 尝试下一个实例
                continue

        return {
            "success": False,
            "method": "nitter",
            "url": url,
            "content": None,
            "metadata": {},
            "error": "所有 Nitter 实例都失败（可能被限流或 URL 无效）"
        }

    def _try_all(self, url: str) -> Dict[str, Any]:
        """尝试所有方法，返回最成功的结果"""
        methods = ["jina", "direct"]
        if "twitter.com" in url or "x.com" in url:
            methods = ["nitter", "jina"]

        for method in methods:
            if method == "jina":
                result = self._jina_fetch(url)
            elif method == "direct":
                result = self._direct_fetch(url)
            elif method == "nitter":
                result = self._nitter_fetch(url)

            if result["success"]:
                return result

        # 所有方法都失败
        return {
            "success": False,
            "method": "all",
            "url": url,
            "content": None,
            "metadata": {},
            "error": f"所有方法都失败（尝试了: {', '.join(methods)}）"
        }

    def _is_html(self, content: str) -> bool:
        """检测是否是 HTML"""
        html_indicators = ["<html", "<head", "<body", "<div", "<p>", "<!DOCTYPE"]
        content_lower = content.lower()
        return any(indicator.lower() in content_lower for indicator in html_indicators)

    def _is_js_shell(self, html: str) -> bool:
        """
        检测是否是需要 JS 渲染的空壳页面

        特征：
        - 几乎没有可见内容
        - 大量 JS 脚本标签
        - 包含 "JavaScript is not available" 等提示
        """
        # 移除 script 标签内容
        without_scripts = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        without_scripts = re.sub(r'<style[^>]*>.*?</style>', '', without_scripts, flags=re.DOTALL)

        # 获取可见文本
        visible_text = re.sub(r'<[^>]+>', ' ', without_scripts)
        visible_text = ' '.join(visible_text.split())

        # 检查是否过短（少于200字符且没有实际内容）
        if len(visible_text) < 200:
            # 检查是否是 JS 不可用提示
            js_disabled_phrases = [
                "javascript is not available",
                "enable javascript",
                "javascript must be enabled",
                "请启用javascript",
                "需要javascript"
            ]
            if any(phrase in visible_text.lower() for phrase in js_disabled_phrases):
                return True

            # 检查是否有大量 script 标签但内容很少
            script_count = html.count('<script')
            if script_count > 5 and len(visible_text) < 100:
                return True

        return False

    def extract_text(self, content: str, url: str = "") -> Dict[str, Any]:
        """
        从 HTML 内容中提取主要文本

        Returns:
            {
                "title": str,
                "text": str,
                "links": list,
                "images": list,
                "metadata": dict
            }
        """
        result = {
            "title": "",
            "text": "",
            "links": [],
            "images": [],
            "metadata": {}
        }

        try:
            from html.parser import HTMLParser

            class TextExtractor(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.title = ""
                    self.in_title = False
                    self.text_parts = []
                    self.links = []
                    self.images = []
                    self.in_script = False
                    self.in_style = False

                def handle_starttag(self, tag, attrs):
                    if tag == "title":
                        self.in_title = True
                    elif tag == "script":
                        self.in_script = True
                    elif tag == "style":
                        self.in_style = True
                    elif tag == "a":
                        for attr, val in attrs:
                            if attr == "href":
                                self.links.append(val)
                    elif tag == "img":
                        for attr, val in attrs:
                            if attr == "src":
                                self.images.append(val)

                def handle_endtag(self, tag):
                    if tag == "title":
                        self.in_title = False
                    elif tag == "script":
                        self.in_script = False
                    elif tag == "style":
                        self.in_style = False

                def handle_data(self, data):
                    if self.in_title:
                        self.title += data
                    elif not self.in_script and not self.in_style:
                        text = data.strip()
                        if text:
                            self.text_parts.append(text)

            parser = TextExtractor()
            parser.feed(content)

            result["title"] = parser.title
            # 合并文本段落
            result["text"] = " ".join(parser.text_parts)
            result["links"] = parser.links
            result["images"] = parser.images

        except Exception as e:
            result["metadata"]["error"] = str(e)

        return result

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        total = self.stats["total_attempts"]
        success_rate = round(self.stats["success"] / total * 100, 1) if total > 0 else 0

        return {
            "total_attempts": total,
            "success": self.stats["success"],
            "failed": self.stats["failed"],
            "success_rate": f"{success_rate}%",
            "by_method": self.stats["by_method"]
        }

    def close(self):
        """关闭会话"""
        if self.session:
            self.session.close()


# 单例
_fetcher = None


def get_fetcher() -> WebFetcher:
    """获取 WebFetcher 单例"""
    global _fetcher
    if _fetcher is None:
        _fetcher = WebFetcher()
    return _fetcher


def quick_fetch(url: str, timeout: int = 10) -> Dict[str, Any]:
    """
    快速抓取网页（便捷函数）

    Args:
        url: 目标 URL
        timeout: 超时时间（秒）

    Returns:
        抓取结果字典
    """
    fetcher = WebFetcher(timeout=timeout)
    result = fetcher.fetch(url)
    fetcher.close()
    return result


# 命令行测试
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python web_fetcher.py <URL> [method]")
        print()
        print("示例:")
        print("  python web_fetcher.py https://example.com")
        print("  python web_fetcher.py https://x.com/user/status/123 nitter")
        print()
        print("方法: auto, direct, jina, nitter, all")
        sys.exit(1)

    url = sys.argv[1]
    method = sys.argv[2] if len(sys.argv) > 2 else "auto"

    print(f"[WebFetcher] 抓取: {url}")
    print(f"[WebFetcher] 方法: {method}")
    print()

    fetcher = WebFetcher()

    # 先判断是否适合
    suitable = fetcher.is_suitable(url)
    print(f"[分析] 适合性: {suitable['suitable']}")
    print(f"[分析] 原因: {suitable['reason']}")
    print(f"[分析] 置信度: {suitable['confidence']}")
    print()

    # 执行抓取
    result = fetcher.fetch(url, method=method)

    print(f"[结果] 成功: {result['success']}")
    print(f"[结果] 方法: {result['method']}")
    print(f"[结果] 响应时间: {result['metadata'].get('response_time', 0)}秒")

    if result['success']:
        content = result['content']
        print(f"[结果] 内容长度: {len(content)} 字符")
        print()
        print("=" * 70)
        print(content[:1000])  # 只显示前1000字符
        if len(content) > 1000:
            print("...")
        print("=" * 70)
    else:
        print(f"[错误] {result['error']}")
        if 'suggestion' in result:
            print(f"[建议] {result['suggestion']}")

    print()
    print("[统计]")
    stats = fetcher.get_stats()
    for key, value in stats.items():
        if key != "by_method":
            print(f"  {key}: {value}")

    fetcher.close()
