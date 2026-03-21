#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI Roland 系统状态检查工具

用法:
    python status.py           # 查看格式化的状态报告
    python status.py --json    # 输出 JSON 格式
    python status.py --raw     # 原始数据（用于脚本）
"""

import sys
import os
import json
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

from engine import RolandEngine


def main():
    """主入口"""
    engine = RolandEngine()

    # 解析命令行参数
    args = sys.argv[1:]
    output_format = "text"  # 默认文本格式

    if "--json" in args:
        output_format = "json"
    elif "--raw" in args:
        output_format = "raw"

    # 获取状态
    status = engine.get_system_status()

    if output_format == "json":
        print(json.dumps(status, ensure_ascii=False, indent=2, default=str))
    elif output_format == "raw":
        # 仅输出关键统计数据
        sections = status.get("sections", {})
        print(f"agents:{sections.get('agents', {}).get('total', 0)}")
        print(f"skills:{sections.get('skills', {}).get('total', 0)}")
        print(f"instincts:{sections.get('instincts', {}).get('total', 0)}")
        print(f"observations:{sections.get('observations', {}).get('total', 0)}")
    else:
        # 默认：格式化的文本报告
        print(engine.format_system_status(status))


if __name__ == "__main__":
    main()
