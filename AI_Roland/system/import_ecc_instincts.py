#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
导入 everything-claude-code 的本能到 AI Roland
"""

import sys
import yaml
from pathlib import Path

# 修复 Windows 编码
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

# 添加系统路径
system_path = Path(__file__).parent
sys.path.insert(0, str(system_path))

from homunculus_memory import HomunculusMemory, Instinct


def parse_instincts_file(file_path: Path):
    """解析本能文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 按分隔符分割文档
    parts = content.split('---')
    instincts = []

    i = 0
    while i < len(parts):
        part = parts[i].strip()
        if not part:
            i += 1
            continue

        # 尝试解析为 YAML frontmatter
        try:
            frontmatter = yaml.safe_load(part)
            if frontmatter and 'id' in frontmatter:
                # 这是一个有效的 frontmatter
                # 下一个部分是内容
                i += 1
                content_part = parts[i] if i < len(parts) else ''

                # 提取 Action 部分
                action_lines = []
                in_action = False
                for line in content_part.split('\n'):
                    if line.strip() == '## Action':
                        in_action = True
                        continue
                    if in_action:
                        if line.startswith('##'):
                            break
                        action_lines.append(line)

                action = '\n'.join(action_lines).strip()
                if not action:
                    action = frontmatter.get('trigger', '')

                instincts.append({
                    'frontmatter': frontmatter,
                    'action': action
                })
        except:
            pass

        i += 1

    return instincts


def main():
    """主函数"""
    memory = HomunculusMemory(Path(r'D:\ClaudeWork\AI_Roland'))

    instincts_file = Path(r'D:\ClaudeWork\everything-claude-code\.claude\homunculus\instincts\inherited\everything-claude-code-instincts.yaml')

    if not instincts_file.exists():
        print(f"错误: 找不到文件 {instincts_file}")
        return

    print("=" * 60)
    print("导入 everything-claude-code 本能")
    print("=" * 60)
    print()

    # 解析本能
    parsed = parse_instincts_file(instincts_file)
    print(f"解析到 {len(parsed)} 条本能")
    print()

    # 导入本能
    imported = 0
    skipped = 0

    for item in parsed:
        fm = item['frontmatter']
        action = item['action']

        instinct_id = fm.get('id', '')
        if not instinct_id:
            continue

        # 检查是否已存在
        if instinct_id in memory.instincts:
            print(f"- (已存在) {instinct_id}")
            skipped += 1
            continue

        # 确定生命周期阶段
        confidence = fm.get('confidence', 0.7)
        if confidence >= 0.8:
            lifecycle = 'green-leaf'
            priority = 'P1'
        else:
            lifecycle = 'sprout'
            priority = 'P2'

        # 创建本能
        instinct = Instinct(
            id=instinct_id,
            trigger=fm.get('trigger', ''),
            action=action[:300],
            confidence=confidence,
            domain=fm.get('domain', 'general'),
            scope='global',
            source='everything-claude-code',
            lifecycle_stage=lifecycle,
            priority=priority,
            source_repo=fm.get('source_repo', 'affaan-m/everything-claude-code')
        )

        # 保存
        memory.instincts[instinct_id] = instinct
        memory._save_instinct(instinct)
        imported += 1
        print(f"✓ {instinct_id}")

    print()
    print("=" * 60)
    print(f"导入完成")
    print(f"  新导入: {imported} 条")
    print(f"  已存在: {skipped} 条")
    print(f"  总计: {len(memory.instincts)} 条本能")
    print("=" * 60)


if __name__ == "__main__":
    main()
