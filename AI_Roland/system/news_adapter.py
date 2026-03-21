#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Roland 新闻适配器 - 6551 opennews-mcp 集成
提供简化的新闻获取接口，供 AI Roland workflow 使用
"""
import asyncio
import json
import sys
import io
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# 设置 UTF-8 输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 添加 MCP 路径
opennews_path = Path("D:/ClaudeWork/AI_Roland/system/skills/opennews-mcp/src")
sys.path.insert(0, str(opennews_path))

class NewsAdapter:
    """新闻适配器 - 简化 opennews-mcp 调用"""

    def __init__(self):
        self.api_client = None
        self._initialized = False

    def _ensure_client(self):
        """延迟导入和初始化 API 客户端"""
        if self._initialized:
            return True

        try:
            from opennews_mcp.api_client import NewsAPIClient
            from opennews_mcp.config import API_TOKEN, API_BASE_URL

            if not API_TOKEN or API_TOKEN == "YOUR_TOKEN_HERE":
                print("⚠️ opennews-mcp Token 未配置")
                return False

            self.api_client = NewsAPIClient()
            self._initialized = True
            return True
        except Exception as e:
            print(f"⚠️ opennews-mcp 初始化失败: {e}")
            return False

    async def get_latest_news(self, limit: int = 10) -> List[Dict]:
        """获取最新新闻"""
        if not self._ensure_client():
            return []

        try:
            result = await self.api_client.search_news(limit=limit, page=1)
            if result.get("data"):
                return self._format_news_list(result["data"])
            return []
        except Exception as e:
            print(f"获取新闻失败: {e}")
            return []

    async def search_news(self, keyword: str, limit: int = 10) -> List[Dict]:
        """搜索新闻"""
        if not self._ensure_client():
            return []

        try:
            result = await self.api_client.search_news(query=keyword, limit=limit, page=1)
            if result.get("data"):
                return self._format_news_list(result["data"])
            return []
        except Exception as e:
            print(f"搜索失败: {e}")
            return []

    def get_latest_news_sync(self, limit: int = 10) -> List[Dict]:
        """同步获取最新新闻"""
        try:
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run, self.get_latest_news(limit)
                )
                return future.result(timeout=30)
        except Exception as e:
            print(f"同步获取失败: {e}")
            return []

    def search_news_sync(self, keyword: str, limit: int = 10) -> List[Dict]:
        """同步搜索新闻"""
        try:
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run, self.search_news(keyword, limit)
                )
                return future.result(timeout=30)
        except Exception as e:
            print(f"同步搜索失败: {e}")
            return []

    def _format_news_list(self, news_data: List) -> List[Dict]:
        """格式化新闻列表"""
        formatted = []
        for news in news_data:
            item = {
                "id": news.get("id"),
                "source": news.get("source") or news.get("newsType", "Unknown"),
                "type": f"{news.get('engineType', '')}/{news.get('newsType', '')}",
                "text": news.get("text", "")[:200],
                "link": news.get("link", ""),
                "time": news.get("publishedAt", ""),
                "coins": [c.get("symbol", "") for c in (news.get("coins") or []) if c.get("symbol")],
                "score": news.get("aiScore"),
            }
            formatted.append(item)
        return formatted

    def format_for_display(self, news_list: List[Dict]) -> str:
        """格式化为显示文本"""
        if not news_list:
            return "未获取到新闻"

        lines = [f"📰 新闻摘要 ({len(news_list)} 条)\n"]

        for i, news in enumerate(news_list, 1):
            lines.append(f"{i}. {news['source']} - {news['type']}")
            if news['coins']:
                lines.append(f"   相关: {', '.join(news['coins'])}")
            if news['score']:
                lines.append(f"   评分: {news['score']}/100")
            lines.append(f"   内容: {news['text']}")
            lines.append("")

        return "\n".join(lines)


# 单例
_adapter: Optional[NewsAdapter] = None

def get_news_adapter() -> NewsAdapter:
    """获取新闻适配器单例"""
    global _adapter
    if _adapter is None:
        _adapter = NewsAdapter()
    return _adapter


# 便捷函数
def get_latest_news(limit: int = 10) -> str:
    """获取最新新闻 (便捷函数)"""
    adapter = get_news_adapter()
    news = adapter.get_latest_news_sync(limit)
    return adapter.format_for_display(news)


def search_news(keyword: str, limit: int = 10) -> str:
    """搜索新闻 (便捷函数)"""
    adapter = get_news_adapter()
    news = adapter.search_news_sync(keyword, limit)
    return adapter.format_for_display(news)


if __name__ == "__main__":
    # 测试
    print("="*60)
    print("测试 NewsAdapter")
    print("="*60)

    print("\n获取最新新闻...")
    print(get_latest_news(3))

    print("\n搜索 'Bitcoin'...")
    print(search_news("Bitcoin", 3))
