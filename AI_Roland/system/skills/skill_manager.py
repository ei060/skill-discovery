"""
AI Roland 技能管理器 - 标准化技能系统

借鉴 ECC 的技能格式，实现统一的技能管理
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict, field


@dataclass
class SkillMetadata:
    """技能元数据"""
    name: str
    description: str
    version: str
    author: str
    origin: str
    tags: List[str]
    category: str
    priority: int  # 1-10, 1最高
    depends_on: List[str]
    last_updated: str
    skill_file: str = ""
    status: str = "active"  # active, deprecated, experimental

    def to_dict(self) -> Dict:
        return asdict(self)


class SkillManager:
    """技能管理器"""

    def __init__(self):
        self.skills_dir = Path(__file__).parent
        self.registry_file = self.skills_dir / "skills_registry.json"
        self.skills: Dict[str, SkillMetadata] = {}
        self._load_registry()

    def _load_registry(self):
        """加载技能注册表"""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for name, meta in data.items():
                    self.skills[name] = SkillMetadata(**meta)
            except Exception as e:
                print(f"[WARN] 加载技能注册表失败: {e}")

        # 扫描技能目录
        self._scan_skills()

    def _scan_skills(self):
        """扫描技能目录，自动发现技能"""
        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue

            # 检查 SKILL.md
            skill_file = skill_dir / "SKILL.md"
            if skill_file.exists():
                self._register_skill_from_file(skill_file)

            # 检查 Python 技能
            py_files = list(skill_dir.glob("*.py"))
            if py_files and not skill_file.exists():
                # 为纯 Python 技能生成 SKILL.md
                self._generate_skill_markdown(skill_dir)

    def _register_skill_from_file(self, skill_file: Path):
        """从 SKILL.md 文件注册技能"""
        try:
            content = skill_file.read_text(encoding='utf-8')

            # 解析 YAML frontmatter
            yaml_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if yaml_match:
                yaml_content = yaml_match.group(1)
                import yaml
                frontmatter = yaml.safe_load(yaml_content)

                # 创建元数据
                name = frontmatter.get('name', skill_file.parent.name)
                meta = SkillMetadata(
                    name=name,
                    description=frontmatter.get('description', ''),
                    version=frontmatter.get('version', '1.0.0'),
                    author=frontmatter.get('author', 'AI Roland'),
                    origin=frontmatter.get('origin', 'AI_Roland'),
                    tags=frontmatter.get('tags', []),
                    category=frontmatter.get('category', 'general'),
                    priority=frontmatter.get('priority', 5),
                    depends_on=frontmatter.get('depends_on', []),
                    last_updated=frontmatter.get('last_updated', datetime.now().strftime('%Y-%m-%d')),
                    skill_file=str(skill_file),
                    status='active'
                )
                self.skills[name] = meta
        except Exception as e:
            print(f"[WARN] 解析技能文件失败 {skill_file}: {e}")

    def _generate_skill_markdown(self, skill_dir: Path):
        """为纯 Python 技能生成 SKILL.md"""
        py_files = list(skill_dir.glob("*.py"))
        if not py_files:
            return

        skill_name = skill_dir.name
        main_py = py_files[0]

        # 尝试从 Python 文件提取文档字符串
        doc_content = ""
        try:
            with open(main_py, 'r', encoding='utf-8') as f:
                content = f.read()
                # 提取模块文档字符串
                doc_match = re.match(r'^"""(.+?)"""', content, re.DOTALL)
                if doc_match:
                    doc_content = doc_match.group(1)
        except:
            pass

        # 生成 SKILL.md
        skill_md = f"""---
name: {skill_name}
description: {doc_content.split(chr(10))[0] if doc_content else skill_name + ' skill'}
version: 1.0.0
author: AI Roland
origin: AI_Roland
tags: [python, automation]
category: automated
priority: 5
depends_on: []
last_updated: 2026-03-15
---

# {skill_name.replace('-', ' ').title()}

{doc_content if doc_content else f'自动化技能: {skill_name}'}

## Installation

```bash
# 将技能添加到系统
cd AI_Roland/system/skills/{skill_name}
```

## Usage

```python
from system.skills.{skill_name} import main

# 使用技能
main.run()
```

## Files

- `{main_py.name}`" - 主脚本
"""

        (skill_dir / "SKILL.md").write_text(skill_md, encoding='utf-8')

        # 注册技能
        self._register_skill_from_file(skill_dir / "SKILL.md")

    def get_skill(self, name: str) -> Optional[SkillMetadata]:
        """获取技能元数据"""
        return self.skills.get(name)

    def list_skills(self, category: str = None, tag: str = None) -> List[SkillMetadata]:
        """列出技能"""
        skills = list(self.skills.values())

        if category:
            skills = [s for s in skills if s.category == category]

        if tag:
            skills = [s for s in skills if tag in s.tags]

        return sorted(skills, key=lambda x: x.priority)

    def search_skills(self, query: str) -> List[SkillMetadata]:
        """搜索技能"""
        query_lower = query.lower()
        results = []

        for skill in self.skills.values():
            # 搜索名称、描述、标签
            desc = (skill.description or "").lower()
            tags = (skill.tags or [])
            if (query_lower in skill.name.lower() or
                query_lower in desc or
                any(query_lower in tag.lower() for tag in tags)):
                results.append(skill)

        return results

    def save_registry(self):
        """保存技能注册表"""
        def serialize_meta(obj):
            """处理特殊类型序列化"""
            from datetime import date, datetime
            if isinstance(obj, (date, datetime)):
                return obj.isoformat()
            raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

        data = {name: meta.to_dict() for name, meta in self.skills.items()}
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=serialize_meta)

    def get_briefing(self) -> str:
        """获取技能简报"""
        lines = []
        lines.append("## 📚 AI Roland 技能库")
        lines.append("")
        lines.append(f"**总数**: {len(self.skills)}")
        lines.append("")

        # 按类别分组
        categories = {}
        for skill in self.skills.values():
            cat = skill.category or 'other'
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(skill)

        for cat, skills_list in sorted(categories.items()):
            lines.append(f"### {cat.title()}")
            for skill in sorted(skills_list, key=lambda x: x.priority):
                status_icon = "✅" if skill.status == "active" else "⚠️"
                lines.append(f"- {status_icon} **{skill.name}**")
                lines.append(f"  - {skill.description[:80]}...")
                lines.append("")

        return "\n".join(lines)


# 便捷函数
_manager = None

def get_skill_manager() -> SkillManager:
    """获取技能管理器单例"""
    global _manager
    if _manager is None:
        _manager = SkillManager()
    return _manager


if __name__ == "__main__":
    manager = SkillManager()
    manager.save_registry()
    print(manager.get_briefing())
