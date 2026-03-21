#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI Roland 决策建议接口

供 Claude 调用的简单接口，返回基于学习的建议
"""

import sys
import os
import io
import json
from pathlib import Path

# 修复 Windows 编码
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

# 添加系统路径
system_path = Path(__file__).parent
sys.path.insert(0, str(system_path))

from instinct_matcher import get_instinct_matcher


def recommend(user_input: str, url: str = "") -> dict:
    """
    获取 AI Roland 的决策建议

    Args:
        user_input: 用户的输入
        url: 相关的 URL（可选）

    Returns:
        建议字典，包含:
        - recommended_action: 推荐的行动类型
        - skill: 推荐的技能（如果适用）
        - instinct: 推荐的本能（如果适用）
        - reason: 推荐理由
        - confidence: 置信度
    """
    matcher = get_instinct_matcher()

    context = {
        'user_input': user_input,
        'url': url,
        'session_id': ''
    }

    suggestion = matcher.suggest_action(context)

    # 简化输出
    result = {
        'input': user_input,
        'url': url,
        'recommendation': None
    }

    if suggestion['recommended_action']:
        rec = suggestion['recommended_action']
        rec_type = rec.get('type', 'none')

        if rec_type == 'use_skill':
            result['recommendation'] = {
                'type': 'skill',
                'name': rec['skill'],
                'reason': rec.get('reason', ''),
                'confidence': rec.get('confidence', 0)
            }
        elif rec_type == 'follow_instinct':
            result['recommendation'] = {
                'type': 'instinct',
                'id': rec['instinct'],
                'action': rec.get('action', ''),
                'confidence': rec.get('confidence', 0)
            }

    # 添加可用技能信息
    result['available_skills'] = [s.name for s in suggestion.get('available_skills', [])]
    result['matched_instincts_count'] = len(suggestion.get('matched_instincts', []))

    return result


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python ask_ai_roland.py \"用户输入\" [URL]")
        print()
        print("示例:")
        print('  python ask_ai_roland.py "抓取这个推文" "https://twitter.com/elon/status/123"')
        print('  python ask_ai_roland.py "下载YouTube视频"')
        sys.exit(1)

    user_input = sys.argv[1]
    url = sys.argv[2] if len(sys.argv) > 2 else ""

    result = recommend(user_input, url)

    # 输出 JSON
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
