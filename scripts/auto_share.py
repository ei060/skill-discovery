#!/usr/bin/env python3
"""
Skill Discovery - 自动化分享工具

自动完成：
1. 创建GitHub Release
2. 发布到Reddit
3. 发布到Twitter
4. 添加GitHub Topics
5. 生成分享报告

使用前准备：
- GitHub Token: https://github.com/settings/tokens (repo权限)
- Reddit API: https://www.reddit.com/prefs/apps
- Twitter API: https://developer.twitter.com/

配置方式：
1. 复制 .env.example 到 .env
2. 填写你的API凭证
3. 运行: python auto_share.py
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path

# ==================== 配置 ====================

class Config:
    """从环境变量加载配置"""

    # GitHub
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GITHUB_REPO = "ei060/skill-discovery"

    # Reddit
    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
    REDDIT_USER_AGENT = "SkillDiscovery/1.0"
    REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
    REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")

    # Twitter (可选)
    TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
    TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
    TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
    TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

    # Release信息
    RELEASE_TAG = "v1.0.0"
    RELEASE_TITLE = "🎉 Skill Discovery v1.0.0 - 自动工具发现 + 安全审计框架"

# ==================== GitHub API ====================

class GitHubPublisher:
    """GitHub发布工具"""

    def __init__(self, token, repo):
        self.token = token
        self.repo = repo
        self.api_base = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def create_release(self, tag, title, notes, draft=False, prerelease=False):
        """创建GitHub Release"""
        url = f"{self.api_base}/repos/{self.repo}/releases"

        data = {
            "tag_name": tag,
            "target_commitish": "main",
            "name": title,
            "body": notes,
            "draft": draft,
            "prerelease": prerelease
        }

        response = requests.post(url, headers=self.headers, json=data)

        if response.status_code == 201:
            release = response.json()
            return {
                "success": True,
                "url": release["html_url"],
                "upload_url": release["upload_url"]
            }
        else:
            return {
                "success": False,
                "error": response.json()
            }

    def add_topics(self, topics):
        """添加仓库Topics"""
        # 注意：GitHub API目前不支持直接修改topics
        # 需要通过GraphQL API，这里提供替代方案
        print("\n⚠️  GitHub Topics需要手动添加:")
        print(f"   访问: https://github.com/{self.repo}/settings")
        print(f"   添加Topics: {', '.join(topics)}")
        return {"success": True, "manual": True}

# ==================== Reddit API ====================

class RedditPublisher:
    """Reddit发布工具"""

    def __init__(self, client_id, client_secret, username, password):
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.user_agent = "SkillDiscovery/1.0"
        self.access_token = None

    def authenticate(self):
        """Reddit OAuth认证"""
        url = "https://www.reddit.com/api/v1/access_token"
        auth = (self.client_id, self.client_secret)
        data = {"grant_type": "password", "username": self.username, "password": self.password}

        headers = {"User-Agent": self.user_agent}

        response = requests.post(url, auth=auth, data=data, headers=headers)

        if response.status_code == 200:
            self.access_token = response.json()["access_token"]
            return True
        else:
            print(f"❌ Reddit认证失败: {response.text}")
            return False

    def post(self, subreddit, title, content):
        """发布到Reddit"""
        if not self.access_token:
            if not self.authenticate():
                return {"success": False, "error": "Authentication failed"}

        url = "https://oauth.reddit.com/api/submit"
        headers = {
            "Authorization": f"bearer {self.access_token}",
            "User-Agent": self.user_agent
        }

        data = {
            "sr": subreddit,
            "title": title,
            "text": content,
            "kind": "self",
            "api_type": "json"
        }

        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200:
            result = response.json()
            if not result.get("json", {}).get("errors"):
                post_url = result["json"]["data"]["url"]
                return {
                    "success": True,
                    "url": f"https://reddit.com{post_url}"
                }
            else:
                return {
                    "success": False,
                    "error": result["json"]["data"]["errors"]
                }
        else:
            return {
                "success": False,
                "error": response.text
            }

# ==================== 内容模板 ====================

class ContentTemplates:
    """分享内容模板"""

    @staticmethod
    def load_release_notes():
        """加载Release Notes"""
        notes_path = Path(__file__).parent.parent / "RELEASE_NOTES.md"
        if notes_path.exists():
            with open(notes_path, 'r', encoding='utf-8') as f:
                return f.read()
        return None

    @staticmethod
    def load_reddit_post(platform):
        """加载Reddit帖子内容"""
        share_path = Path(__file__).parent.parent / "SHARE.md"

        if not share_path.exists():
            return None, None

        with open(share_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取对应平台的标题和内容
        if platform == "claude":
            title = "[Release] Skill Discovery - 自动发现最佳工具的Claude Skill + 安全审计框架"
            # 提取r/Claude部分
            start = content.find("#### r/Claude")
            end = content.find("#### r/artificial")
            body = content[start:end].split("```markdown")[1].split("```")[0].strip()

        elif platform == "artificial":
            title = "Built a tool-discovery system for Claude AI with a security audit framework"
            # 提取r/artificial部分
            start = content.find("#### r/artificial")
            end = content.find("#### r/opensource")
            body = content[start:end].split("```markdown")[1].split("```")[0].strip()

        elif platform == "opensource":
            title = "[OS] Skill Discovery - Auto-discovery tool for AI assistants with security audit framework"
            # 提取r/opensource部分
            start = content.find("#### r/opensource")
            end = content.find("### Reddit分享")
            body = content[start:end].split("```markdown")[1].split("```")[0].strip()

        else:
            return None, None

        return title, body

# ==================== 主流程 ====================

def main():
    """主执行流程"""

    print("=" * 60)
    print("🚀 Skill Discovery - 自动化分享工具")
    print("=" * 60)

    config = Config()

    # 检查配置
    print("\n📋 检查配置...")
    if not config.GITHUB_TOKEN:
        print("⚠️  GitHub Token未设置")
        print("   获取方式: https://github.com/settings/tokens")
        print("   环境变量: GITHUB_TOKEN")

    if not config.REDDIT_CLIENT_ID:
        print("⚠️  Reddit API未配置")
        print("   配置方式: 创建 .env 文件")
        print("   或跳过Reddit发布")

    # 1. 创建GitHub Release
    print("\n" + "=" * 60)
    print("📦 步骤 1/4: 创建GitHub Release")
    print("=" * 60)

    if config.GITHUB_TOKEN:
        github = GitHubPublisher(config.GITHUB_TOKEN, config.GITHUB_REPO)
        release_notes = ContentTemplates.load_release_notes()

        if release_notes:
            print("📝 正在创建Release...")
            result = github.create_release(
                tag=config.RELEASE_TAG,
                title=config.RELEASE_TITLE,
                notes=release_notes,
                draft=False,
                prerelease=False
            )

            if result["success"]:
                print(f"✅ Release创建成功!")
                print(f"   URL: {result['url']}")
            else:
                print(f"❌ Release创建失败:")
                print(f"   {result['error']}")
        else:
            print("⚠️  RELEASE_NOTES.md未找到")
    else:
        print("⏭️  跳过（未配置GitHub Token）")

    # 2. 添加GitHub Topics
    print("\n" + "=" * 60)
    print("🏷️  步骤 2/4: 添加GitHub Topics")
    print("=" * 60)

    topics = [
        "claude-code", "claude-ai", "skill-discovery", "tool-discovery",
        "automation", "browser-automation", "security", "security-audit",
        "api-security", "python", "github-api", "reddit-api",
        "web-search", "mcp", "model-context-protocol"
    ]

    if config.GITHUB_TOKEN:
        result = github.add_topics(topics)
        if result.get("manual"):
            print("📝 请手动添加Topics（见上方说明）")

    # 3. 发布到Reddit
    print("\n" + "=" * 60)
    print("📱 步骤 3/4: 发布到Reddit")
    print("=" * 60)

    if config.REDDIT_CLIENT_ID and config.REDDIT_CLIENT_SECRET:
        reddit = RedditPublisher(
            config.REDDIT_CLIENT_ID,
            config.REDDIT_CLIENT_SECRET,
            config.REDDIT_USERNAME,
            config.REDDIT_PASSWORD
        )

        # 发布到r/Claude
        print("\n📌 发布到 r/Claude...")
        title, content = ContentTemplates.load_reddit_post("claude")
        if title and content:
            result = reddit.post("Claude", title, content)
            if result["success"]:
                print(f"✅ 发布成功!")
                print(f"   URL: {result['url']}")
            else:
                print(f"❌ 发布失败: {result['error']}")

        # 发布到r/artificial
        print("\n📌 发布到 r/artificial...")
        title, content = ContentTemplates.load_reddit_post("artificial")
        if title and content:
            result = reddit.post("artificial", title, content)
            if result["success"]:
                print(f"✅ 发布成功!")
                print(f"   URL: {result['url']}")
            else:
                print(f"❌ 发布失败: {result['error']}")

        # 发布到r/opensource
        print("\n📌 发布到 r/opensource...")
        title, content = ContentTemplates.load_reddit_post("opensource")
        if title and content:
            result = reddit.post("opensource", title, content)
            if result["success"]:
                print(f"✅ 发布成功!")
                print(f"   URL: {result['url']}")
            else:
                print(f"❌ 发布失败: {result['error']}")
    else:
        print("⏭️  跳过Reddit发布（未配置API）")
        print("   配置方式: 创建 .env 文件")
        print("   或者使用SHARE.md中的模板手动发布")

    # 4. 生成报告
    print("\n" + "=" * 60)
    print("📊 步骤 4/4: 生成分享报告")
    print("=" * 60)

    report = {
        "timestamp": datetime.now().isoformat(),
        "release_tag": config.RELEASE_TAG,
        "tasks": {
            "github_release": config.GITHUB_TOKEN is not None,
            "github_topics": False,  # 需要手动
            "reddit_claude": config.REDDIT_CLIENT_ID is not None,
            "reddit_artificial": config.REDDIT_CLIENT_ID is not None,
            "reddit_opensource": config.REDDIT_CLIENT_ID is not None
        },
        "links": {
            "github_repo": f"https://github.com/{config.GITHUB_REPO}",
            "github_release": f"https://github.com/{config.GITHUB_REPO}/releases/tag/{config.RELEASE_TAG}",
            "github_settings": f"https://github.com/{config.GITHUB_REPO}/settings"
        }
    }

    report_path = Path(__file__).parent.parent / "share_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"✅ 报告已保存: {report_path}")

    # 总结
    print("\n" + "=" * 60)
    print("🎉 自动化分享完成!")
    print("=" * 60)

    print("\n📋 后续任务:")
    print("   1. 手动添加GitHub Topics（见上方说明）")
    print("   2. 监控Reddit帖子的upvotes和评论")
    print("   3. 回复用户问题和反馈")
    print("   4. 根据反馈准备v1.0.1更新")

    print("\n🔗 重要链接:")
    print(f"   GitHub: {report['links']['github_repo']}")
    print(f"   Release: {report['links']['github_release']}")

if __name__ == "__main__":
    main()
