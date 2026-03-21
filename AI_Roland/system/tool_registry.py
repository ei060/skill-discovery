"""
AI Roland 工具注册表 - 自动发现和使用系统中各种工具

创建时间: 2026-03-13
用途: 让 AI 主动发现和使用系统中的各种专业工具
"""

from pathlib import Path
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
import json
import sys

# ============================================================================
# 数据结构
# ============================================================================

@dataclass
class Tool:
    """工具定义"""
    name: str                    # 工具名称
    description: str             # 描述
    category: str                # 分类
    file_path: str               # 文件路径
    keywords: List[str] = field(default_factory=list)  # 触发关键词
    requires: List[str] = field(default_factory=list)   # 依赖库
    enabled: bool = True         # 是否启用
    priority: int = 0            # 优先级 (越高越优先)

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'file_path': str(self.file_path),
            'keywords': self.keywords,
            'requires': self.requires,
            'enabled': self.enabled,
            'priority': self.priority
        }


# ============================================================================
# 工具注册表
# ============================================================================

class ToolRegistry:
    """工具注册中心"""

    def __init__(self, workspace: Path = None):
        self.workspace = workspace or Path("D:/ClaudeWork")
        self.tools: Dict[str, Tool] = {}
        self.category_index: Dict[str, List[str]] = {}  # category -> [tool_names]
        self.keyword_index: Dict[str, List[str]] = {}  # keyword -> [tool_names]
        self._initialize_builtin_tools()

    def _initialize_builtin_tools(self):
        """初始化内置工具库"""

        # ==================== 金融分析工具 ====================
        self.register(Tool(
            name="ai_buffett_pro",
            description="专业级AI量化交易系统 - 集成Qlib/RD-Agent/ML模型/回测引擎",
            category="金融",
            file_path=self.workspace / "ai_buffett_pro.py",
            keywords=["股票", "投资", "量化", "交易", "回测", "选股", "A股", "金融", "巴菲特", "buffett"],
            requires=["numpy", "pandas", "akshare"],
            priority=100
        ))

        self.register(Tool(
            name="ai_buffett_quant",
            description="AI巴菲特量化版 - 技术指标+机器学习选股",
            category="金融",
            file_path=self.workspace / "ai_buffett_quant.py",
            keywords=["量化", "选股", "技术分析", "指标", "机器学习"],
            requires=["numpy", "pandas", "akshare"],
            priority=90
        ))

        # ==================== 浏览器自动化 ====================
        self.register(Tool(
            name="browser_controller",
            description="浏览器控制器v3.1 - 支持Stealth模式+代理+持久化",
            category="浏览器",
            file_path=self.workspace / "AI_Roland" / "system" / "browser_controller.py",
            keywords=["浏览器", "爬虫", "自动化", "抓取", "网页", "playwright", "selenium", "twitter", "小红书"],
            requires=["playwright"],
            priority=100
        ))

        # ==================== 搜索工具 ====================
        self.register(Tool(
            name="perplexica_search",
            description="Perplexica AI搜索引擎 - 基于AI的智能搜索",
            category="搜索",
            file_path=self.workspace / "AI_Roland" / "system" / "skills" / "perplexica-search",
            keywords=["搜索", "查找", "perplexica", "信息", "资料"],
            requires=[],
            priority=80
        ))

        # ==================== 创作工具 ====================
        self.register(Tool(
            name="short_drama_script",
            description="短剧剧本创作 - 专业级微短剧AI创作工具",
            category="创作",
            file_path=self.workspace / ".claude" / "skills" / "short-drama-script",
            keywords=["剧本", "短剧", "创作", "故事", "剧本创作"],
            requires=[],
            priority=70
        ))

        # ==================== 购票工具 ====================
        self.register(Tool(
            name="12306_booking",
            description="12306购票助手 - 车票查询/余票监控/自动下单",
            category="生活",
            file_path=self.workspace / "AI_Roland" / "system" / "skills" / "12306-booking",
            keywords=["火车票", "12306", "购票", "高铁", "火车"],
            requires=["playwright"],
            priority=60
        ))

        # ==================== YouTube工具 ====================
        self.register(Tool(
            name="yt_search_download",
            description="YouTube搜索下载 - 视频/音频/字幕下载",
            category="媒体",
            file_path=self.workspace / ".claude" / "skills" / "yt-search-download",
            keywords=["youtube", "视频", "下载", "字幕", "yt-dlp"],
            requires=["yt-dlp"],
            priority=60
        ))

        # ==================== 记忆管理 ====================
        self.register(Tool(
            name="memory_search",
            description="记忆搜索 - 向量搜索系统记忆",
            category="系统",
            file_path=self.workspace / "AI_Roland" / "system" / "memory_search.py",
            keywords=["记忆", "搜索", "回忆", "历史"],
            requires=[],
            priority=50
        ))

        # ==================== 6551 新闻数据 ====================
        self.register(Tool(
            name="opennews_mcp",
            description="6551 opennews-mcp - 72+新闻源聚合 (Bloomberg/Reuters/CoinDesk等) + AI分析",
            category="数据",
            file_path=self.workspace / "AI_Roland" / "system" / "skills" / "opennews-mcp",
            keywords=["新闻", "资讯", "加密货币", "crypto", "比特币", "BTC", "市场", "opennews", "6551"],
            requires=["httpx"],
            priority=95
        ))

        # ==================== 网络抓取工具 ====================
        self.register(Tool(
            name="network_scraping",
            description="网络抓取工具集 - Twitter/Reddit/YouTube/知乎/小红书等平台数据获取",
            category="数据",
            file_path=self.workspace / ".claude" / "skills" / "network-scraping",
            keywords=["抓取", "爬虫", "twitter", "reddit", "youtube", "知乎", "小红书", "网络"],
            requires=["playwright"],
            priority=90
        ))

        self.register(Tool(
            name="second_brain",
            description="第二大脑 - 知识管理系统",
            category="系统",
            file_path=self.workspace / "AI_Roland" / "system" / "second_brain.py",
            keywords=["笔记", "知识", "第二大脑", "整理"],
            requires=[],
            priority=50
        ))

        # ==================== Telegram Bot ====================
        self.register(Tool(
            name="telegram_bot",
            description="Telegram Bot V2 - 消息推送+远程控制",
            category="通信",
            file_path=self.workspace / "AI_Roland" / "system" / "telegram_bot" / "bot_v2.py",
            keywords=["telegram", "bot", "推送", "消息"],
            requires=["python-telegram-bot", "anthropic"],
            priority=40
        ))

        # ==================== 代码分析 ====================
        self.register(Tool(
            name="ai_code_review",
            description="AI代码审查 - 自动代码质量分析",
            category="开发",
            file_path=self.workspace / "AI_Roland_RolandSkills" / "skills" / "ai-code-review",
            keywords=["代码", "审查", "review", "质量"],
            requires=[],
            priority=50
        ))

    def register(self, tool: Tool):
        """注册工具"""
        self.tools[tool.name] = tool

        # 分类索引
        if tool.category not in self.category_index:
            self.category_index[tool.category] = []
        self.category_index[tool.category].append(tool.name)

        # 关键词索引
        for keyword in tool.keywords:
            if keyword not in self.keyword_index:
                self.keyword_index[keyword] = []
            self.keyword_index[keyword].append(tool.name)

    def find_by_category(self, category: str) -> List[Tool]:
        """按分类查找工具"""
        names = self.category_index.get(category, [])
        return [self.tools[n] for n in names if self.tools[n].enabled]

    def find_by_keywords(self, text: str) -> List[Tool]:
        """按关键词查找工具"""
        text_lower = text.lower()
        matched = set()

        for keyword, names in self.keyword_index.items():
            if keyword.lower() in text_lower:
                matched.update(names)

        # 按优先级排序
        tools = [self.tools[n] for n in matched if self.tools[n].enabled]
        tools.sort(key=lambda t: t.priority, reverse=True)
        return tools

    def get_all_enabled(self) -> List[Tool]:
        """获取所有启用的工具"""
        return [t for t in self.tools.values() if t.enabled]

    def suggest_tools(self, task: str) -> List[Tool]:
        """为任务建议工具"""
        tools = self.find_by_keywords(task)

        # 如果没有直接匹配，尝试分类匹配
        if not tools:
            # 检查是否是金融相关
            finance_words = ["股票", "市场", "指数", "投资", "分析", "巴菲特", "buffett"]
            if any(w in task for w in finance_words):
                tools.extend(self.find_by_category("金融"))

            # 检查是否是浏览器相关
            browser_words = ["网页", "抓取", "爬虫", "登录", "浏览器"]
            if any(w in task for w in browser_words):
                tools.extend(self.find_by_category("浏览器"))

            # 检查是否是创作相关
            create_words = ["写", "创作", "剧本", "文章", "内容"]
            if any(w in task for w in create_words):
                tools.extend(self.find_by_category("创作"))

        # 去重并排序
        seen = set()
        unique_tools = []
        for t in tools:
            if t.name not in seen:
                seen.add(t.name)
                unique_tools.append(t)

        unique_tools.sort(key=lambda x: x.priority, reverse=True)
        return unique_tools

    def check_dependencies(self, tool: Tool) -> dict:
        """检查工具依赖"""
        result = {"available": True, "missing": []}

        for req in tool.requires:
            try:
                __import__(req)
            except ImportError:
                result["available"] = False
                result["missing"].append(req)

        return result

    def get_startup_prompt(self, task: str = "") -> str:
        """获取启动时工具提示"""
        lines = ["\n[Available Tools]:\n"]

        if task:
            tools = self.suggest_tools(task)
            lines.append(f"[Task: {task[:30]}...]")
        else:
            tools = self.get_all_enabled()[:5]

        for tool in tools[:5]:
            dep_status = self.check_dependencies(tool)
            status = "[OK]" if dep_status["available"] else "[--]"
            lines.append(f"  {status} {tool.name} - {tool.description[:40]}")

        return "\n".join(lines)


# ============================================================================
# 单例
# ============================================================================

_registry: Optional[ToolRegistry] = None

def get_registry() -> ToolRegistry:
    """获取工具注册表单例"""
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
    return _registry


# ============================================================================
# 使用示例
# ============================================================================

if __name__ == "__main__":
    registry = get_registry()

    # 显示所有工具
    print("=" * 60)
    print("AI Roland Tool Registry")
    print("=" * 60)

    for category, names in registry.category_index.items():
        print(f"\n[{category}]")
        for name in names:
            tool = registry.tools[name]
            dep = registry.check_dependencies(tool)
            status = "[OK]" if dep["available"] else "[--]"
            print(f"  {status} {name}: {tool.description[:50]}")

    # 测试任务匹配
    print("\n" + "=" * 60)
    print("Task Matching Test")
    print("=" * 60)

    test_tasks = [
        "分析今天A股市场",
        "抓取Twitter数据",
        "写一个短剧剧本",
        "查询火车票"
    ]

    for task in test_tasks:
        tools = registry.suggest_tools(task)
        print(f"\nTask: {task}")
        for tool in tools[:3]:
            print(f"  -> {tool.name}: {tool.description[:40]}")
