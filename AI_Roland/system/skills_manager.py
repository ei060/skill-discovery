"""
Skills 插件系统 - 可扩展的 AI 能力
通过 /skill-name 调用自定义功能
"""

import sys
import os
# 修复 Windows 控制台中文乱码
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml


class Skill:
    """单个 Skill 插件"""

    def __init__(self, name: str, path: Path):
        self.name = name
        self.path = path
        self.config = self._load_config()
        self.enabled = self.config.get('enabled', True)

    def _load_config(self) -> Dict:
        """加载 Skill 配置"""
        config_file = self.path / "skill.yaml"

        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)

        # 默认配置
        return {
            "name": self.name,
            "description": f"Skill: {self.name}",
            "version": "1.0.0",
            "enabled": True,
            "parameters": [],
            "examples": []
        }

    def get_prompt_template(self) -> str:
        """获取提示词模板"""
        template_file = self.path / "prompt.md"

        if template_file.exists():
            return template_file.read_text(encoding='utf-8')

        return f"""# {self.name}

You are a skill called {self.name}.
Execute the requested task."""

    def execute(self, **kwargs) -> str:
        """执行 Skill"""
        template = self.get_prompt_template()

        # 替换模板中的变量
        for key, value in kwargs.items():
            template = template.replace(f"{{{key}}}", str(value))

        return template


class SkillsManager:
    """Skills 管理器"""

    def __init__(self, workspace_path=None):
        if workspace_path is None:
            current_dir = Path(__file__).parent
            self.workspace = current_dir.parent
        else:
            self.workspace = Path(workspace_path)

        self.skills_dir = self.workspace / "system" / "skills"
        self.skills_dir.mkdir(exist_ok=True)

        self.skills: Dict[str, Skill] = {}
        self._load_all_skills()

    def _load_all_skills(self):
        """加载所有 Skills"""
        for skill_path in self.skills_dir.iterdir():
            if skill_path.is_dir() and not skill_path.name.startswith('_'):
                skill = Skill(skill_path.name, skill_path)
                if skill.enabled:
                    self.skills[skill.name] = skill

    def list_skills(self) -> List[Dict[str, Any]]:
        """列出所有可用的 Skills"""
        return [
            {
                "name": name,
                "description": skill.config.get("description", ""),
                "version": skill.config.get("version", "1.0.0"),
                "examples": skill.config.get("examples", [])
            }
            for name, skill in self.skills.items()
        ]

    def get_skill(self, skill_name: str) -> Optional[Skill]:
        """获取指定 Skill"""
        return self.skills.get(skill_name)

    def execute_skill(self, skill_name: str, **kwargs) -> str:
        """执行指定 Skill"""
        skill = self.get_skill(skill_name)

        if not skill:
            return f"Error: Skill '{skill_name}' not found"

        return skill.execute(**kwargs)

    def parse_skill_command(self, command: str) -> Optional[Dict[str, Any]]:
        """解析 Skill 命令

        支持格式：
        /skill_name
        /skill_name arg1 arg2
        /skill_name key1=value1 key2=value2
        """
        if not command.startswith('/'):
            return None

        parts = command[1:].split()
        skill_name = parts[0]

        if skill_name not in self.skills:
            return None

        args = {}
        positional_args = []

        for part in parts[1:]:
            if '=' in part:
                key, value = part.split('=', 1)
                args[key] = value
            else:
                positional_args.append(part)

        return {
            "skill": skill_name,
            "args": args,
            "positional_args": positional_args
        }

    def create_skill(self, name: str, description: str = "", prompt_template: str = ""):
        """创建新 Skill"""
        skill_path = self.skills_dir / name
        skill_path.mkdir(exist_ok=True)

        # 创建配置文件
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

        # 创建提示词模板
        if not prompt_template:
            prompt_template = f"""# {name}

{{{{purpose}}}}

## 输入
{{{{input}}}}

## 要求
1. ...
2. ...
3. ...

## 输出
...
"""

        template_file = skill_path / "prompt.md"
        template_file.write_text(prompt_template, encoding='utf-8')

        # 重新加载
        skill = Skill(name, skill_path)
        self.skills[name] = skill

        return skill_path


def main():
    """测试 Skills 系统"""
    manager = SkillsManager()

    print("=== Skills 系统测试 ===\n")

    print("1. 列出所有 Skills:")
    skills = manager.list_skills()
    for skill in skills:
        print(f"   - {skill['name']}: {skill['description']}")

    print(f"\n   共 {len(skills)} 个 Skills\n")

    print("2. 测试创建新 Skill:")
    manager.create_skill(
        "test_skill",
        description="测试 Skill",
        prompt_template="# Test Skill\n\nInput: {input}\n\nOutput: ..."
    )
    print("   Skill 创建成功")

    print("\n3. 测试解析命令:")
    test_commands = [
        "/briefing",
        "/commit feat=add-feature",
        "/review pr=123"
    ]

    for cmd in test_commands:
        parsed = manager.parse_skill_command(cmd)
        if parsed:
            print(f"   {cmd}")
            print(f"     -> Skill: {parsed['skill']}")
            print(f"     -> Args: {parsed['args']}")


if __name__ == "__main__":
    main()
