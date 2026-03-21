"""
Skill 安装前安全检查脚本
在使用 npx skills add 之前运行安全检查
"""

import sys
import io

# 设置 UTF-8 输出
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import subprocess
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional


class SkillSecurityScanner:
    """Skill 安全扫描器"""

    # 安全风险关键词
    RISKY_KEYWORDS = [
        # 数据窃取
        "exfiltrat", "steal", "upload_data", "send_data", "telemetry",
        # 权限提升
        "privilege", "escalate", "sudo", "root_access",
        # 网络攻击
        "ddos", "botnet", "attack", "exploit", "payload", "shellcode",
        # 加密货币
        "crypto", "bitcoin", "mining", "wallet", "cryptominer",
        # 可疑网络
        "socks5", "proxy_server", "bind_port", "reverse_shell",
        # 数据修改
        "delete_files", "wipe", "format", "rmdir",
    ]

    # 可信域名
    TRUSTED_DOMAINS = [
        "github.com",
        "gitlab.com",
        "bitbucket.org",
        "npmjs.com",
        "skills.sh",
    ]

    def __init__(self):
        self.results = {
            "skill_name": "",
            "source": "",
            "checks": [],
            "risk_level": "unknown",
            "recommendation": "",
        }

    def parse_skill_name(self, skill_input: str) -> str:
        """解析 Skill 名称"""
        # 格式: user/repo 或完整 URL
        if "/" in skill_input:
            return skill_input.split("/")[-1]
        return skill_input

    def check_github_repo(self, repo: str) -> Dict:
        """检查 GitHub 仓库"""
        print(f"🔍 检查 GitHub 仓库: {repo}")

        checks = []

        # 1. 检查仓库是否存在
        try:
            result = subprocess.run(
                ["gh", "repo", "view", repo, "--json", "name,owner,description,stargazerCount,defaultBranchRef"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                checks.append({
                    "name": "仓库存在性",
                    "status": "pass",
                    "detail": f"⭐ {data.get('stargazerCount', 0)} stars"
                })
                self.results["skill_name"] = data.get("name", repo)
            else:
                checks.append({
                    "name": "仓库存在性",
                    "status": "warn",
                    "detail": "仓库不存在或无访问权限"
                })
        except Exception as e:
            checks.append({
                "name": "仓库存在性",
                "status": "skip",
                "detail": f"gh cli 未安装: {str(e)[:30]}"
            })

        # 2. 获取 README
        try:
            readme_cmd = ["gh", "repo", "view", repo, "--json", "readme", "-q", ".readme"]
            result = subprocess.run(readme_cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                readme = result.stdout.lower()
                # 检查可疑关键词
                risky_found = [kw for kw in self.RISKY_KEYWORDS if kw in readme]
                if risky_found:
                    checks.append({
                        "name": "关键词扫描",
                        "status": "warn",
                        "detail": f"发现可疑词: {', '.join(risky_found[:3])}"
                    })
                else:
                    checks.append({
                        "name": "关键词扫描",
                        "status": "pass",
                        "detail": "未发现可疑关键词"
                    })
        except:
            pass

        # 3. 检查是否有 SKILL.md
        try:
            result = subprocess.run(
                ["gh", "api", f"repos/{repo}/contents/SKILL.md"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                checks.append({
                    "name": "规范文档",
                    "status": "pass",
                    "detail": "✅ 有 SKILL.md"
                })
            else:
                checks.append({
                    "name": "规范文档",
                    "status": "info",
                    "detail": "无 SKILL.md (非标准格式)"
                })
        except:
            pass

        return checks

    def check_npm_package(self, package: str) -> Dict:
        """检查 npm 包"""
        print(f"🔍 检查 npm 包: {package}")

        checks = []

        # npm view
        try:
            result = subprocess.run(
                ["npm", "view", package, "--json"],
                capture_output=True,
                text=True,
                timeout=15
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                checks.append({
                    "name": "包存在性",
                    "status": "pass",
                    "detail": f"v{data.get('version', 'unknown')}"
                })

                # 检查依赖
                deps = data.get("dependencies", {})
                if deps:
                    checks.append({
                        "name": "依赖数量",
                        "status": "info",
                        "detail": f"{len(deps)} 个依赖"
                    })
            else:
                checks.append({
                    "name": "包存在性",
                    "status": "fail",
                    "detail": "包不存在"
                })
        except Exception as e:
            checks.append({
                "name": "包存在性",
                "status": "skip",
                "detail": f"检查失败: {str(e)[:30]}"
            })

        return checks

    def check_source_trust(self, source: str) -> Dict:
        """检查来源可信度"""
        checks = []

        for domain in self.TRUSTED_DOMAINS:
            if domain in source:
                checks.append({
                    "name": "来源可信度",
                    "status": "pass",
                    "detail": f"✅ {domain}"
                })
                break
        else:
            checks.append({
                "name": "来源可信度",
                "status": "warn",
                "detail": f"⚠️ 未知来源: {source[:50]}"
            })

        return checks

    def scan_skill(self, skill_input: str) -> Dict:
        """扫描 Skill"""
        skill_name = self.parse_skill_name(skill_input)
        self.results["skill_name"] = skill_name
        self.results["source"] = skill_input

        all_checks = []

        # 判断类型并检查
        if skill_input.startswith("http") or "github.com" in skill_input:
            # GitHub 仓库
            # 提取 owner/repo
            if "github.com" in skill_input:
                match = re.search(r"github\.com/([^/]+/[^/]+)", skill_input)
                if match:
                    repo = match.group(1)
                    all_checks.extend(self.check_github_repo(repo))

            all_checks.extend(self.check_source_trust(skill_input))

        elif "/" in skill_input:
            # 可能是 GitHub repo
            all_checks.extend(self.check_github_repo(skill_input))
            all_checks.extend(self.check_source_trust("github.com/" + skill_input))

        else:
            # npm 包
            all_checks.extend(self.check_npm_package(skill_input))

        self.results["checks"] = all_checks

        # 计算风险等级
        self._calculate_risk()

        return self.results

    def _calculate_risk(self):
        """计算风险等级"""
        fail_count = sum(1 for c in self.results["checks"] if c["status"] == "fail")
        warn_count = sum(1 for c in self.results["checks"] if c["status"] == "warn")

        if fail_count > 0:
            self.results["risk_level"] = "high"
            self.results["recommendation"] = "❌ 不建议安装"
        elif warn_count >= 2:
            self.results["risk_level"] = "medium"
            self.results["recommendation"] = "⚠️ 谨慎安装"
        elif warn_count == 1:
            self.results["risk_level"] = "low"
            self.results["recommendation"] = "⚡ 可以安装"
        else:
            self.results["risk_level"] = "safe"
            self.results["recommendation"] = "✅ 推荐安装"

    def print_report(self):
        """打印报告"""
        print("\n" + "=" * 60)
        print(f"📋 Skill 安全检查报告")
        print("=" * 60)
        print(f"Skill: {self.results['skill_name']}")
        print(f"来源: {self.results['source']}")
        print(f"风险等级: {self._get_risk_icon(self.results['risk_level'])} {self.results['risk_level'].upper()}")
        print(f"建议: {self.results['recommendation']}")
        print("\n检查项:")

        for check in self.results["checks"]:
            icon = {
                "pass": "✅",
                "fail": "❌",
                "warn": "⚠️",
                "info": "ℹ️",
                "skip": "⊘"
            }.get(check["status"], "?")
            print(f"  {icon} {check['name']}: {check['detail']}")

        print("=" * 60 + "\n")

        return self.results["risk_level"] in ["safe", "low"]

    def _get_risk_icon(self, level: str) -> str:
        return {
            "safe": "🟢",
            "low": "🟡",
            "medium": "🟠",
            "high": "🔴",
            "unknown": "⚪"
        }.get(level, "?")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python skill_security_check.py <skill_name_or_url>")
        print("示例:")
        print("  python skill_security_check.py joeseesun/yt-search-download")
        print("  python skill_security_check.py https://github.com/user/repo")
        sys.exit(1)

    skill_input = sys.argv[1]

    scanner = SkillSecurityScanner()
    scanner.scan_skill(skill_input)
    safe = scanner.print_report()

    sys.exit(0 if safe else 1)


if __name__ == "__main__":
    main()
