#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证 AI Roland Hooks 是否正确配置和工作
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def check_settings():
    """检查配置文件"""
    settings_file = Path.home() / ".claude" / "settings.local.json"

    print("="*60)
    print("AI Roland Hooks 验证工具")
    print("="*60)

    if not settings_file.exists():
        print(f"\n[ERROR] 配置文件不存在: {settings_file}")
        return False

    try:
        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)
    except Exception as e:
        print(f"\n[ERROR] 无法读取配置: {e}")
        return False

    hooks = settings.get("hooks", {})

    # 检查 PreToolUse
    pre_hooks = hooks.get("PreToolUse", [])
    has_inject = any(
        "inject_memory" in hook.get("command", "")
        for hook_group in pre_hooks
        for hook in hook_group.get("hooks", [])
        if hook.get("type") == "command"
    )

    # 检查 PostToolUse
    post_hooks = hooks.get("PostToolUse", [])
    has_save = any(
        "save_memory" in hook.get("command", "")
        for hook_group in post_hooks
        for hook in hook_group.get("hooks", [])
        if hook.get("type") == "command"
    )

    print("\n配置检查:")
    print(f"  PreToolUse Hook (inject_memory): {'[OK]' if has_inject else '[MISSING]'}")
    print(f"  PostToolUse Hook (save_memory):   {'[OK]' if has_save else '[MISSING]'}")

    if not (has_inject and has_save):
        print("\n[ERROR] Hooks 未正确配置！")
        return False

    print("\n[OK] 配置正确！")
    return True

def check_log_files():
    """检查日志文件"""
    workspace = Path.cwd()
    log_dir = workspace / "AI_Roland" / "system" / "agents" / "hooks"

    print("\n" + "="*60)
    print("日志文件检查")
    print("="*60)

    logs = {
        "memory_injection.log": log_dir / "memory_injection.log",
        "memory_errors.log": log_dir / "memory_errors.log"
    }

    for name, path in logs.items():
        if path.exists():
            mtime = datetime.fromtimestamp(path.stat().st_mtime)
            size = path.stat().st_size
            print(f"\n[OK] {name}")
            print(f"     路径: {path}")
            print(f"     大小: {size} bytes")
            print(f"     修改: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")

            # 显示最后几行
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        print(f"     最后日志: {lines[-1].strip()[:100]}")
            except:
                pass
        else:
            print(f"\n[INFO] {name} - 尚未生成（等待首次 Task 调用）")

def check_temp_files():
    """检查临时记忆文件"""
    import tempfile

    print("\n" + "="*60)
    print("临时文件检查")
    print("="*60)

    temp_dir = Path(tempfile.gettempdir())
    temp_files = list(temp_dir.glob("agent_memory_*.md"))

    if temp_files:
        print(f"\n[OK] 找到 {len(temp_files)} 个临时记忆文件")
        for f in temp_files[:5]:  # 只显示前5个
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            print(f"  - {f.name} ({mtime.strftime('%H:%M:%S')})")
    else:
        print("\n[INFO] 尚无临时记忆文件（等待首次 Task 调用）")

def main():
    # 1. 检查配置
    if not check_settings():
        print("\n" + "="*60)
        print("配置验证失败！")
        print("="*60)
        print("\n可能原因:")
        print("1. Claude Code 未重启（配置未加载）")
        print("2. 配置文件被覆盖")
        print("3. 路径错误")
        print("\n解决方法:")
        print("1. 完全关闭 Claude Code")
        print("2. 重新打开")
        print("3. 再次运行此验证")
        return

    # 2. 检查日志
    check_log_files()

    # 3. 检查临时文件
    check_temp_files()

    # 4. 总结
    print("\n" + "="*60)
    print("验证总结")
    print("="*60)

    print("\n配置状态: [OK]")
    print("\n下一步:")
    print("1. 在 Claude Code 中调用 Task 工具，例如:")
    print("   - 调用 code-reviewer agent")
    print("   - 调用 planner agent")
    print("2. 调用后，再次运行此验证脚本检查日志")
    print("3. 查看日志确认记忆是否被注入和保存")

if __name__ == "__main__":
    main()
