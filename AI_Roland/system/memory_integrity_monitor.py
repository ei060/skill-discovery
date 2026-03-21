"""
记忆完整性监控模块
自动检测并提醒缺失的记忆记录
"""
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import logging


class MemoryIntegrityMonitor:
    """记忆完整性监控器"""

    def __init__(self, workspace):
        self.workspace = Path(workspace)
        self.diary_dir = self.workspace / "日记"
        self.semantic_memory_dir = self.workspace / "记忆库" / "语义记忆"
        self.chat_history = self.workspace / "对话历史.md"
        self.logger = logging.getLogger(__name__)

        # 扩展的工作区（包括外部项目）
        self.parent_workspace = self.workspace.parent

    def check_memory_gaps(self):
        """检查记忆空白期"""
        gaps = []

        if not self.diary_dir.exists():
            return gaps

        # 获取所有日记文件
        diary_files = sorted(self.diary_dir.glob("*.md"))

        if len(diary_files) < 2:
            return gaps

        # 解析日期并找出空白期
        dates = []
        for f in diary_files:
            try:
                # 从文件名提取日期：2026-02-20.md
                date_str = f.stem.split("_")[0]  # 处理 2026-03-01_补充记录
                date = datetime.strptime(date_str, "%Y-%m-%d")
                dates.append(date)
            except:
                continue

        # 检查日期间隔
        dates.sort()
        for i in range(len(dates) - 1):
            gap_days = (dates[i+1] - dates[i]).days
            if gap_days > 1:
                gaps.append({
                    "from": dates[i],
                    "to": dates[i+1],
                    "days": gap_days - 1,
                    "type": "diary_gap"
                })

        return gaps

    def detect_new_projects(self, since_days=7):
        """检测新项目（外部工作区）"""
        new_projects = []

        # 扫描父目录
        if not self.parent_workspace.exists():
            return new_projects

        since_date = datetime.now() - timedelta(days=since_days)

        # 检查所有子目录
        for item in self.parent_workspace.iterdir():
            if not item.is_dir():
                continue

            # 跳过已知目录
            if item.name in [".git", "node_modules", "__pycache__", "cache",
                           ".browser-profile", "AI_Roland", "AI_Roland_RolandSkills"]:
                continue

            # 检查是否有 .git 目录（说明是项目）
            git_dir = item / ".git"
            if git_dir.exists():
                # 获取最后修改时间
                last_modified = datetime.fromtimestamp(item.stat().st_mtime)

                if last_modified > since_date:
                    # 检查是否已在记忆中
                    project_name = item.name
                    if not self._is_project_recorded(project_name):
                        new_projects.append({
                            "name": project_name,
                            "path": str(item),
                            "last_modified": last_modified,
                            "type": "git_project"
                        })

        return new_projects

    def detect_new_files(self, since_days=3):
        """检测新的重要文件"""
        important_extensions = {'.md', '.py', '.js'}
        new_files = []

        since_date = datetime.now() - timedelta(days=since_days)

        # 扫描父目录
        for item in self.parent_workspace.glob("*"):
            if item.is_dir():
                continue

            # 只检查重要文件
            if item.suffix not in important_extensions:
                continue

            # 检查修改时间
            last_modified = datetime.fromtimestamp(item.stat().st_mtime)

            if last_modified > since_date:
                # 检查是否已记录
                if not self._is_file_recorded(item.name):
                    new_files.append({
                        "name": item.name,
                        "path": str(item),
                        "last_modified": last_modified,
                        "type": "important_file"
                    })

        return new_files

    def check_semantic_memory_coverage(self):
        """检查语义记忆覆盖率"""
        coverage = {
            "total_projects": 0,
            "recorded_projects": 0,
            "missing_projects": []
        }

        # 获取所有 git 项目
        projects = []
        for item in self.parent_workspace.iterdir():
            if not item.is_dir():
                continue

            git_dir = item / ".git"
            if git_dir.exists() and item.name != "AI_Roland":
                projects.append(item.name)

        coverage["total_projects"] = len(projects)

        # 检查每个项目是否有语义记忆
        for project in projects:
            if not self._is_project_recorded(project):
                coverage["missing_projects"].append(project)
            else:
                coverage["recorded_projects"] += 1

        return coverage

    def _is_project_recorded(self, project_name):
        """检查项目是否已记录在语义记忆中"""
        if not self.semantic_memory_dir.exists():
            return False

        # 搜索包含项目名的语义记忆
        pattern = project_name.lower().replace("-", "_").replace(" ", "_")

        for mem_file in self.semantic_memory_dir.glob("*.md"):
            try:
                content = mem_file.read_text(encoding='utf-8')
                if pattern in content.lower():
                    return True
            except:
                continue

        return False

    def _is_file_recorded(self, file_name):
        """检查文件是否已在对话历史中"""
        if not self.chat_history.exists():
            return False

        try:
            content = self.chat_history.read_text(encoding='utf-8')
            return file_name in content
        except:
            return False

    def generate_report(self):
        """生成记忆完整性报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "gaps": [],
            "new_projects": [],
            "new_files": [],
            "coverage": {},
            "recommendations": []
        }

        # 1. 检查日记空白
        gaps = self.check_memory_gaps()
        report["gaps"] = gaps

        if gaps:
            total_gap_days = sum(g["days"] for g in gaps)
            report["recommendations"].append(
                f"发现 {len(gaps)} 个记忆空白期，共 {total_gap_days} 天未记录"
            )

        # 2. 检测新项目
        new_projects = self.detect_new_projects(since_days=10)
        report["new_projects"] = new_projects

        if new_projects:
            report["recommendations"].append(
                f"发现 {len(new_projects)} 个未记录的项目"
            )

        # 3. 检测新文件
        new_files = self.detect_new_files(since_days=5)
        report["new_files"] = new_files[:10]  # 最多10个

        if new_files:
            report["recommendations"].append(
                f"发现 {len(new_files)} 个未记录的重要文件"
            )

        # 4. 检查语义记忆覆盖率
        coverage = self.check_semantic_memory_coverage()
        report["coverage"] = coverage

        if coverage["missing_projects"]:
            rate = coverage["recorded_projects"] / coverage["total_projects"] * 100 if coverage["total_projects"] > 0 else 0
            report["recommendations"].append(
                f"语义记忆覆盖率: {rate:.1f}% ({coverage['recorded_projects']}/{coverage['total_projects']})"
            )

        return report

    def get_daily_diary_status(self):
        """检查今日日记状态"""
        today = datetime.now().strftime("%Y-%m-%d")
        today_diary = self.diary_dir / f"{today}.md"

        return {
            "has_diary": today_diary.exists(),
            "diary_path": str(today_diary),
            "date": today
        }


def demo():
    """演示用法"""
    workspace = Path("D:/ClaudeWork/AI_Roland")
    monitor = MemoryIntegrityMonitor(workspace)

    report = monitor.generate_report()

    print("=" * 70)
    print("记忆完整性监控报告")
    print("=" * 70)
    print(f"检查时间: {report['timestamp']}")
    print()

    # 空白期
    if report['gaps']:
        print("[RED] 记忆空白期:")
        for gap in report['gaps']:
            print(f"  {gap['from'].date()} -> {gap['to'].date()} ({gap['days']}天)")
        print()

    # 新项目
    if report['new_projects']:
        print("[YELLOW] 未记录的项目:")
        for project in report['new_projects']:
            print(f"  - {project['name']} ({project['last_modified'].date()})")
        print()

    # 语义记忆覆盖率
    coverage = report['coverage']
    if coverage.get('total_projects', 0) > 0:
        rate = coverage['recorded_projects'] / coverage['total_projects'] * 100
        print(f"[INFO] 语义记忆覆盖率: {rate:.1f}%")
        if coverage['missing_projects']:
            print("   未记录项目:")
            for project in coverage['missing_projects']:
                print(f"     - {project}")
        print()

    # 建议
    if report['recommendations']:
        print("[TIPS] 建议:")
        for rec in report['recommendations']:
            print(f"  - {rec}")
        print()


if __name__ == "__main__":
    demo()
