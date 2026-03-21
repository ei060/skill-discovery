#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PreToolUse Hook - 自动注入记忆到ECC Agent

在调用Task tool前自动加载AI Roland的记忆，并注入到agent执行上下文

v2.0: 修复 - 从stdin读取而不是环境变量
"""

import sys
import os
import json
import tempfile
from pathlib import Path

# 添加系统路径
system_path = Path(__file__).parent.parent
sys.path.insert(0, str(system_path))

def read_stdin_json():
    """从stdin读取JSON数据（Claude Code hook方式）"""
    try:
        stdin_data = sys.stdin.read()
        if not stdin_data:
            return None
        return json.loads(stdin_data)
    except:
        return None

def extract_agent_name_from_input(tool_input: dict) -> str:
    """从tool_input中提取agent名称"""
    if not isinstance(tool_input, dict):
        return ""

    # 可能的字段名
    subagent_type = tool_input.get('subagent_type', '')
    if subagent_type:
        return subagent_type

    # 尝试其他可能的字段
    agent = tool_input.get('agent', '')
    if agent:
        return agent

    return ""

def inject_memory(agent_name: str) -> str:
    """注入记忆，返回临时文件路径"""

    if not agent_name:
        return ""

    try:
        from agent_bridge import get_agent_bridge

        bridge = get_agent_bridge()

        # 准备执行上下文
        exec_ctx = bridge.prepare_execution_context(
            agent_name,
            "执行中..."  # 占位符
        )

        # 格式化记忆提示词
        memory_prompt = bridge.format_memory_prompt(exec_ctx)

        if not memory_prompt:
            return ""

        # 写入临时文件
        temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.md',
            prefix=f'agent_memory_{agent_name}_',
            delete=False,
            encoding='utf-8'
        )

        temp_file.write(memory_prompt)
        temp_file.close()

        # 设置环境变量，告诉ECC agent读取这个文件
        os.environ['CLAUDE_AGENT_MEMORY_FILE'] = temp_file.name

        # 记录日志
        log_file = Path(__file__).parent.parent / 'hooks' / 'memory_injection.log'
        with open(log_file, 'a', encoding='utf-8') as f:
            from datetime import datetime, timezone
            f.write(f"{datetime.now(timezone.utc).isoformat()} | "
                   f"Agent: {agent_name} | "
                   f"Memory: {len(memory_prompt)} chars | "
                   f"File: {temp_file.name}\n")

        return temp_file.name

    except Exception as e:
        # 静默失败，不影响正常执行
        error_file = Path(__file__).parent.parent / 'hooks' / 'memory_errors.log'
        with open(error_file, 'a', encoding='utf-8') as f:
            from datetime import datetime, timezone
            f.write(f"{datetime.now(timezone.utc).isoformat()} | "
                   f"Error: {str(e)} | "
                   f"Agent: {agent_name}\n")
        return ""

def main():
    """主函数"""

    # 从stdin读取hook数据（Claude Code标准方式）
    hook_data = read_stdin_json()

    if not hook_data:
        sys.exit(0)

    # 提取工具名称和输入
    tool_name = hook_data.get("tool_name", hook_data.get("tool", ""))
    tool_input = hook_data.get("tool_input", hook_data.get("input", {}))

    # 只处理Task tool
    if tool_name != "Task":
        sys.exit(0)

    # 提取agent名称
    agent_name = extract_agent_name_from_input(tool_input)

    # 如果能识别agent，注入记忆
    if agent_name:
        injected = inject_memory(agent_name)
        if injected:
            # 输出到stderr（会被hook系统捕获但不影响主流程）
            print(f"[Memory Injection] Agent: {agent_name}, Memory loaded: {injected}", file=sys.stderr)

    sys.exit(0)

if __name__ == "__main__":
    main()
