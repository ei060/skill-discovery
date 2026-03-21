"""
AI Roland Skills Matcher
智能技能匹配系统 - 根据用户意图自动推荐相关技能
"""

import re
import json
import sys
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# 设置环境变量（在导入其他模块之前）
os.environ['PYTHONIOENCODING'] = 'utf-8'


class SkillsMatcher:
    """技能智能匹配器"""

    def __init__(self):
        self.system_dir = Path(__file__).parent
        self.workspace = self.system_dir.parent
        self.skills_dir = self.workspace.parent / ".claude" / "skills"

        # 技能关键词映射
        self.skill_keywords = {
            # === .claude/skills/ 中的技能 ===
            "skill-discovery": {
                "keywords": ["搜索", "发现", "github", "reddit", "工具", "框架", "技能", "skill", "search", "find", "discover", "latest", "新工具"],
                "description": "自动发现最新的 AI 技能、工具和自动化框架"
            },
            "ai-roland-secretary": {
                "keywords": ["任务", "记忆", "会话", "上下文", "系统", "执行", "协调", "task", "memory", "session", "context", "briefing", "简报"],
                "description": "AI Roland 执行系统 - 管理任务、记忆和工作流"
            },
            "short-drama-script": {
                "keywords": ["短剧", "剧本", "创作", "小说", "故事", "drama", "script", "writing", "题材", "模板", "集数", "影视"],
                "description": "短剧剧本创作 - 专业级微短剧 AI 创作工具"
            },
            # === AI_Roland_RolandSkills/ 中的技能 ===
            "daily-briefing": {
                "keywords": ["晨间", "简报", "今日", "日程", "天气", "待办", "daily", "briefing", "today", "morning", "plan", "今天"],
                "description": "生成每日简报 - 显示任务、天气和日程"
            },
            "smart-commit": {
                "keywords": ["git", "commit", "提交", "版本", "仓库", "push", "代码提交", "conventional", "changelog"],
                "description": "智能生成 Git commit message - 遵循约定式提交规范"
            },
            "second-brain": {
                "keywords": ["第二大脑", "查询", "回忆", "检索", "知识", "问答", "notebooklm", "brain", "search", "recall", "记忆搜索"],
                "description": "第二大脑系统 - 通过 NotebookLM 进行深度问答和知识检索"
            },
            "ai-code-review": {
                "keywords": ["代码审查", "ci/cd", "pr", "pull request", "审查", "测试", "自动化", "review", "代码质量", "github actions"],
                "description": "AI 代码审查 - 设置 AI 驱动的代码审查和 CI/CD 流程"
            },
            # === AI_Roland/system/skills/ 中的技能 ===
            "browser-control": {
                "keywords": ["浏览器", "爬虫", "自动化", "browser", "selenium", "playwright", "爬取", "网页", "截图", "playwright"],
                "description": "浏览器自动化控制 - Playwright 框架支持"
            },
            "12306-booking": {
                "keywords": ["12306", "火车票", "订票", "抢票", "铁路", "ticket", "booking", "高铁", "动车", "车站", "余票"],
                "description": "12306 自动订票助手 - 全自动购票"
            },
            # === 新增技能 ===
            "mediacrawler": {
                "keywords": [
                    "爬虫", "爬取", "采集", "数据", "小红书", "抖音", "dy", "xhs", "快手", "ks",
                    "b站", "bili", "微博", "贴吧", "知乎", "评论", "帖子", "博主", "创作者",
                    "social", "media", "crawler", "scrape", "harvest", "monitor", "监控",
                    "热搜", "话题", "趋势", "舆论", "声量"
                ],
                "description": "多平台社交媒体数据采集 - 支持小红书/抖音/快手/B站/微博/贴吧/知乎"
            }
        }

    def discover_skills(self) -> List[Dict]:
        """发现所有可用技能"""
        skills = []

        if not self.skills_dir.exists():
            return skills

        for skill_path in self.skills_dir.iterdir():
            if not skill_path.is_dir():
                continue

            skill_md = skill_path / "SKILL.md"
            if not skill_md.exists():
                continue

            # 解析 SKILL.md
            skill_info = self._parse_skill_md(skill_md)
            skill_info["path"] = str(skill_path)
            skills.append(skill_info)

        return skills

    def _parse_skill_md(self, file_path: Path) -> Dict:
        """解析 SKILL.md 文件"""
        content = file_path.read_text(encoding="utf-8")

        # 提取 YAML frontmatter
        frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)

        info = {"name": file_path.parent.name, "description": "", "enabled": True}

        if frontmatter_match:
            yaml_content = frontmatter_match.group(1)
            # 简单解析 YAML（避免依赖）
            for line in yaml_content.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key == "name":
                        info["name"] = value
                    elif key == "description":
                        info["description"] = value

        # 如果 description 为空，使用关键词映射
        if not info["description"] and info["name"] in self.skill_keywords:
            info["description"] = self.skill_keywords[info["name"]]["description"]

        return info

    def match_skills(self, user_input: str) -> List[Dict]:
        """根据用户输入匹配相关技能"""
        user_input_lower = user_input.lower()

        matched_skills = []
        for skill_name, skill_info in self.skill_keywords.items():
            score = 0
            matched_keywords = []

            for keyword in skill_info["keywords"]:
                if keyword.lower() in user_input_lower:
                    score += 1
                    matched_keywords.append(keyword)

            if score > 0:
                matched_skills.append({
                    "name": skill_name,
                    "description": skill_info["description"],
                    "score": score,
                    "matched_keywords": matched_keywords
                })

        # 按匹配分数排序
        matched_skills.sort(key=lambda x: x["score"], reverse=True)

        return matched_skills

    def format_skills_list(self, skills: List[Dict]) -> str:
        """格式化技能列表"""
        if not skills:
            return "  [暂无可用技能]"

        lines = []
        lines.append("  ╔════════════════════════════════════════════════════════════╗")
        lines.append("  ║            🧩 可用技能 (Skills)                            ║")
        lines.append("  ╚════════════════════════════════════════════════════════════╝")
        lines.append("")

        for i, skill in enumerate(skills, 1):
            name = skill.get("name", "unknown")
            desc = skill.get("description", "无描述")
            lines.append(f"  [{i}] 📦 {name}")
            lines.append(f"      └─ {desc}")

        lines.append("")
        lines.append("  提示：提到相关关键词时，技能会自动激活")

        return "\n".join(lines)

    def format_match_recommendation(self, matched_skills: List[Dict]) -> str:
        """格式化匹配推荐"""
        if not matched_skills:
            return ""

        lines = []
        lines.append("")
        lines.append("  ╔════════════════════════════════════════════════════════════╗")
        lines.append("  ║         🎯 智能技能推荐 (基于你的问题)                     ║")
        lines.append("  ╚════════════════════════════════════════════════════════════╝")
        lines.append("")

        for skill in matched_skills[:3]:  # 最多显示 3 个
            name = skill["name"]
            desc = skill["description"]
            keywords = ", ".join(skill["matched_keywords"][:3])
            lines.append(f"  📦 {name}")
            lines.append(f"     └─ {desc}")
            lines.append(f"     └─ 匹配关键词: {keywords}")
            lines.append("")

        return "\n".join(lines)

    def get_context_aware_skills(self, recent_context: str = "") -> List[Dict]:
        """根据上下文获取相关技能"""
        all_skills = self.discover_skills()

        if not recent_context:
            return all_skills

        # 如果有上下文，进行排序
        scored_skills = []
        for skill in all_skills:
            score = 0
            name = skill.get("name", "")
            desc = skill.get("description", "").lower()

            # 检查名称和描述中的关键词
            if name in self.skill_keywords:
                for keyword in self.skill_keywords[name]["keywords"]:
                    if keyword.lower() in recent_context.lower():
                        score += 1

            if score > 0:
                skill["context_score"] = score
                scored_skills.append(skill)
            else:
                skill["context_score"] = 0
                scored_skills.append(skill)

        # 按上下文分数排序
        scored_skills.sort(key=lambda x: x.get("context_score", 0), reverse=True)

        return scored_skills


def main():
    """测试函数"""
    matcher = SkillsMatcher()

    print("=== 可用技能 ===")
    skills = matcher.discover_skills()
    print(matcher.format_skills_list(skills))

    print("\n=== 智能匹配测试 ===")
    test_queries = [
        "帮我搜索 GitHub 上的工具",           # skill-discovery
        "查看我的任务和记忆",                  # ai-roland-secretary
        "写一个短剧剧本",                      # short-drama-script
        "控制浏览器自动化操作",                # browser-control
        "生成今日简报",                        # daily-briefing
        "帮我生成 git commit",                # smart-commit
        "查询我的知识库",                      # second-brain
        "设置代码审查流程",                    # ai-code-review
        "订一张火车票",                        # 12306-booking
        "今天有什么任务",                      # daily-briefing
    ]

    for query in test_queries:
        print(f"\n查询: {query}")
        matched = matcher.match_skills(query)
        if matched:
            print(matcher.format_match_recommendation(matched))
        else:
            print("  (无匹配技能)")


if __name__ == "__main__":
    main()
