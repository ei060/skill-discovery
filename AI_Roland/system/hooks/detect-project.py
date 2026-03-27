#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
项目检测脚本

从 Claude Code 的上下文中检测当前工作项目
用于 Hook 观察系统确定项目作用域
"""

import sys
import os
import re
import hashlib
from pathlib import Path


def detect_project_from_stdin() -> dict:
    """从标准输入读取上下文并检测项目（安全地）"""
    import json

    # 读取标准输入（安全地）
    from system.sys_utils import safe_read_stdin
    context = safe_read_stdin()

    if not context:
        # 没有输入，使用当前目录
        cwd = Path.cwd().resolve()
        project_id = hashlib.md5(str(cwd).encode()).hexdigest()[:12]

        return {
            "project_name": cwd.name,
            "project_id": f"{cwd.name} ({project_id})",
            "project_path": str(cwd),
            "detected_from": "cwd",
            "confidence": "low"
        }

    # 尝试解析 JSON
    try:
        data = json.loads(context)
        context_str = json.dumps(data)
    except:
        context_str = context

    # 提取文件路径
    file_paths = []

    # 匹配 Windows 路径
    for match in re.finditer(r'([A-Z]:\\[^"\n]+)', context_str):
        file_paths.append(match.group(1))

    # 匹配 Unix 路径
    for match in re.finditer(r'(/[a-zA-Z_/][^"\n]+)', context_str):
        file_paths.append(match.group(1))

    if file_paths:
        # 使用第一个文件的父目录作为项目根目录
        primary_path = Path(file_paths[0]).resolve()
        project_root = primary_path.parent

        # 生成项目 ID
        project_id = hashlib.md5(
            str(project_root).encode()
        ).hexdigest()[:12]

        return {
            "project_name": project_root.name,
            "project_id": f"{project_root.name} ({project_id})",
            "project_path": str(project_root),
            "detected_from": str(primary_path),
            "confidence": "high"
        }

    # 没有文件路径，使用当前目录
    cwd = Path.cwd().resolve()
    project_id = hashlib.md5(str(cwd).encode()).hexdigest()[:12]

    return {
        "project_name": cwd.name,
        "project_id": f"{cwd.name} ({project_id})",
        "project_path": str(cwd),
        "detected_from": "cwd",
        "confidence": "low"
    }


def main():
    """命令行入口"""
    import json

    result = detect_project_from_stdin()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
