"""
AI Roland Skills Manager v2.0
兼容 Vercel Skills SKILL.md 格式
支持技能发现、安装、更新
"""

import sys
import os
import subprocess
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import yaml
import re
from datetime import datetime

# UTF-8 设置
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    os.environ['PYTHONIOENCODING'] = 'utf-8'


class Skill:
    """Skill 插件 - 支持 SKILL.md 和 skill.yaml 两种格式"""

    def __init__(self, path: Path):
        self.path = path
        self.skill_file = None
        self.config = {}
        self.content = ""
        self.enabled = True
        self._load_skill()

    def _load_skill(self):
        """加载 Skill 配置和内容"""
        # 优先尝试 SKILL.md (Vercel 格式)
        skill_md = self.path / "SKILL.md"
        legacy_yaml = self.path / "skill.yaml"

        if skill_md.exists():
            self.skill_file = skill_md
            self._parse_skill_md(skill_md)
        elif legacy_yaml.exists():
            self.skill_file = legacy_yaml
            self._parse_legacy_yaml(legacy_yaml)
        else:
            # 默认配置
            self.config = {
                "name": self.path.name,
                "description": f"Skill: {self.path.name}",
                "version": "1.0.0"
            }

    def _parse_skill_md(self, file_path: Path):
        """解析 SKILL.md 格式（Vercel 标准）"""
        content = file_path.read_text(encoding='utf-8')

        # 提取 YAML frontmatter
        frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)

        if frontmatter_match:
            yaml_content = frontmatter_match.group(1)
            self.content = frontmatter_match.group(2).strip()

            try:
                self.config = yaml.safe_load(yaml_content) or {}
            except:
                self.config = {}
        else:
            self.content = content

        # 必需字段
        if 'name' not in self.config:
            self.config['name'] = self.path.name
        if 'description' not in self.config:
            self.config['description'] = f"Skill: {self.path.name}"

        # 可选字段
        self.enabled = not self.config.get('metadata', {}).get('internal', False)

    def _parse_legacy_yaml(self, file_path: Path):
        """解析旧的 skill.yaml 格式（向后兼容）"""
        with open(file_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f) or {}

        # 加载 prompt.md
        prompt_file = self.path / "prompt.md"
        if prompt_file.exists():
            self.content = prompt_file.read_text(encoding='utf-8')

    @property
    def name(self) -> str:
        return self.config.get('name', self.path.name)

    @property
    def description(self) -> str:
        return self.config.get('description', '')

    @property
    def version(self) -> str:
        return self.config.get('version', '1.0.0')

    @property
    def is_internal(self) -> bool:
        return self.config.get('metadata', {}).get('internal', False)

    def get_content(self) -> str:
        """获取 Skill 内容"""
        return self.content

    def execute(self, **kwargs) -> str:
        """执行 Skill"""
        template = self.get_content()

        # 替换模板中的变量
        for key, value in kwargs.items():
            template = template.replace(f"{{{key}}}", str(value))

        return template


class SkillsManager:
    """AI Roland Skills Manager v2.0"""

    # 支持的技能搜索路径
    SKILL_SEARCH_PATHS = [
        "skills/",
        "skills/.curated/",
        "skills/.experimental/",
        "skills/.system/",
        ".agents/skills/",
        ".claude/skills/",
    ]

    def __init__(self, workspace_path=None):
        if workspace_path is None:
            current_dir = Path(__file__).parent
            self.workspace = current_dir.parent
        else:
            self.workspace = Path(workspace_path)

        self.skills_dir = self.workspace / "system" / "skills"
        self.skills_dir.mkdir(exist_ok=True)

        self.installed_skills_file = self.workspace / "config" / "installed_skills.json"
        self.installed_skills_file.parent.mkdir(exist_ok=True)

        self.skills: Dict[str, Skill] = {}
        self.installed_skills = self._load_installed_skills()
        self._load_all_skills()

    def _load_installed_skills(self) -> Dict:
        """加载已安装的技能记录"""
        if self.installed_skills_file.exists():
            with open(self.installed_skills_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_installed_skills(self):
        """保存已安装的技能记录"""
        with open(self.installed_skills_file, 'w', encoding='utf-8') as f:
            json.dump(self.installed_skills, f, ensure_ascii=False, indent=2)

    def _load_all_skills(self):
        """加载所有 Skills"""
        for skill_path in self.skills_dir.iterdir():
            if skill_path.is_dir() and not skill_path.name.startswith('_'):
                skill = Skill(skill_path)
                if skill.enabled:
                    self.skills[skill.name] = skill

    def list_skills(self, include_internal: bool = False) -> List[Dict[str, Any]]:
        """列出所有可用的 Skills"""
        skills = []
        for name, skill in self.skills.items():
            if not include_internal and skill.is_internal:
                continue

            skills.append({
                "name": skill.name,
                "description": skill.description,
                "version": skill.version,
                "path": str(skill.path),
                "format": "SKILL.md" if (skill.path / "SKILL.md").exists() else "legacy",
                "internal": skill.is_internal
            })

        return sorted(skills, key=lambda x: x['name'])

    def get_skill(self, skill_name: str) -> Optional[Skill]:
        """获取指定 Skill"""
        return self.skills.get(skill_name)

    def execute_skill(self, skill_name: str, **kwargs) -> str:
        """执行指定 Skill"""
        skill = self.get_skill(skill_name)

        if not skill:
            return f"Error: Skill '{skill_name}' not found"

        return skill.execute(**kwargs)

    def discover_skills(self, repo_path: str = None) -> List[Dict[str, Any]]:
        """发现可用的技能

        Args:
            repo_path: 仓库路径（本地或远程 URL）
        """
        if repo_path:
            return self._discover_remote_skills(repo_path)
        else:
            return self._discover_local_skills()

    def _discover_local_skills(self) -> List[Dict[str, Any]]:
        """发现本地可用的技能"""
        discovered = []

        for search_path in self.SKILL_SEARCH_PATHS:
            path = self.workspace / search_path
            if path.exists():
                for skill_path in path.rglob("SKILL.md"):
                    skill_dir = skill_path.parent
                    skill = Skill(skill_dir)

                    # 跳过内部技能
                    if skill.is_internal:
                        continue

                    discovered.append({
                        "name": skill.name,
                        "description": skill.description,
                        "path": str(skill_dir.relative_to(self.workspace)),
                        "source": "local"
                    })

        return discovered

    def _discover_remote_skills(self, repo_url: str) -> List[Dict[str, Any]]:
        """发现远程仓库的技能"""
        # 使用 npx skills discover
        try:
            result = subprocess.run(
                ['npx', 'skills', 'add', repo_url, '--list'],
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8',
                errors='replace'
            )

            if result.returncode == 0:
                # 解析输出
                skills = []
                for line in result.stdout.split('\n'):
                    if line.strip():
                        skills.append({
                            "name": line.strip(),
                            "source": repo_url
                        })
                return skills

        except Exception as e:
            print(f"[警告] 无法发现远程技能: {e}")

        return []

    def install_skill(self, repo_url: str, skill_name: str = None,
                     global_install: bool = False) -> bool:
        """安装技能

        Args:
            repo_url: 仓库 URL（支持 GitHub shorthands）
            skill_name: 技能名称（可选，安装所有技能时不指定）
            global_install: 是否全局安装

        Returns:
            是否成功
        """
        try:
            cmd = ['npx', 'skills', 'add', repo_url]

            if skill_name:
                cmd.extend(['--skill', skill_name])

            if global_install:
                cmd.append('-g')

            # 添加 --yes 跳过确认
            cmd.append('-y')

            # 限制只安装到 AI Roland
            cmd.extend(['--agent', 'openclaw'])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                encoding='utf-8',
                errors='replace'
            )

            if result.returncode == 0:
                # 记录安装
                install_record = {
                    "repo": repo_url,
                    "skill": skill_name,
                    "installed_at": datetime.now().isoformat(),
                    "global": global_install
                }

                key = f"{repo_url}:{skill_name or 'all'}"
                self.installed_skills[key] = install_record
                self._save_installed_skills()

                # 重新加载技能
                self._load_all_skills()

                return True

            print(f"[错误] 安装失败: {result.stderr}")
            return False

        except Exception as e:
            print(f"[错误] 安装异常: {e}")
            return False

    def update_skills(self) -> Dict[str, Any]:
        """更新所有已安装的技能"""
        try:
            result = subprocess.run(
                ['npx', 'skills', 'update'],
                capture_output=True,
                text=True,
                timeout=300,
                encoding='utf-8',
                errors='replace'
            )

            success = result.returncode == 0

            return {
                "success": success,
                "stdout": result.stdout,
                "stderr": result.stderr
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def check_updates(self) -> List[Dict[str, Any]]:
        """检查技能更新"""
        try:
            result = subprocess.run(
                ['npx', 'skills', 'check'],
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8',
                errors='replace'
            )

            # 解析输出
            updates = []
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'update available' in line.lower():
                        updates.append({"status": "available", "message": line.strip()})

            return updates

        except Exception as e:
            return [{"status": "error", "error": str(e)}]

    def create_skill(self, name: str, description: str = "",
                    content: str = "", use_v2_format: bool = True) -> Path:
        """创建新 Skill

        Args:
            name: 技能名称
            description: 描述
            content: 技能内容
            use_v2_format: 是否使用 SKILL.md 格式（推荐）
        """
        skill_path = self.skills_dir / name
        skill_path.mkdir(exist_ok=True)

        if use_v2_format:
            # 创建 SKILL.md（Vercel 格式）
            if not content:
                content = f"""# {name}

{description}

## When to Use

Describe when this skill should be used.

## Instructions

1. Step one
2. Step two
3. Step three

## Examples

Example usage of this skill.
"""

            skill_md = f"""---
name: {name}
description: {description or f"Skill: {name}"}
version: 1.0.0
---

{content}
"""

            (skill_path / "SKILL.md").write_text(skill_md, encoding='utf-8')

        else:
            # 创建旧格式（向后兼容）
            config = {
                "name": name,
                "description": description or f"Skill: {name}",
                "version": "1.0.0",
                "enabled": True,
                "parameters": [],
                "examples": []
            }

            config_file = skill_path / "skill.yaml"
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True)

            if not content:
                content = f"""# {name}

{description}

## 输入
{{{{input}}}}

## 要求
1. ...
2. ...
3. ...

## 输出
...
"""

            (skill_path / "prompt.md").write_text(content, encoding='utf-8')

        # 重新加载
        skill = Skill(skill_path)
        self.skills[name] = skill

        return skill_path

    def export_to_vercel_format(self, skill_name: str) -> Optional[Path]:
        """导出技能为 Vercel SKILL.md 格式

        Args:
            skill_name: 要导出的技能名称

        Returns:
            导出文件路径
        """
        skill = self.get_skill(skill_name)
        if not skill:
            return None

        # 生成 SKILL.md
        skill_md = f"""---
name: {skill.name}
description: {skill.description}
version: {skill.version}
---

{skill.content}
"""

        # 保存到 skills/<name>/SKILL.md
        export_dir = self.workspace / "skills" / skill.name
        export_dir.mkdir(parents=True, exist_ok=True)

        export_file = export_dir / "SKILL.md"
        export_file.write_text(skill_md, encoding='utf-8')

        return export_file


def main():
    """测试 Skills Manager v2.0"""
    manager = SkillsManager()

    print("=" * 60)
    print("AI Roland Skills Manager v2.0")
    print("=" * 60)

    print("\n1. 列出所有 Skills:")
    skills = manager.list_skills()
    for skill in skills:
        print(f"   [{skill['format']}] {skill['name']}")
        print(f"       {skill['description']}")
        if skill.get('internal'):
            print(f"       (内部技能)")

    print(f"\n   共 {len(skills)} 个 Skills")

    print("\n2. 发现本地技能:")
    discovered = manager.discover_skills()
    for skill in discovered:
        print(f"   - {skill['name']}: {skill.get('description', 'N/A')}")
        print(f"     来源: {skill['source']}")
        print(f"     路径: {skill.get('path', 'N/A')}")

    print("\n3. 创建新 Skill (SKILL.md 格式):")
    skill_path = manager.create_skill(
        "test_skill_v2",
        description="测试 SKILL.md 格式",
        content="# Test Skill\n\n这是一个测试技能。"
    )
    print(f"   ✅ 创建成功: {skill_path}")

    print("\n4. 导出为 Vercel 格式:")
    export_path = manager.export_to_vercel_format("test_skill_v2")
    if export_path:
        print(f"   ✅ 导出成功: {export_path}")


if __name__ == "__main__":
    main()
