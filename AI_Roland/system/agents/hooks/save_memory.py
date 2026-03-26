#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PostToolUse Hook - 自动保存执行经验到AI Roland记忆

在Task tool执行后自动保存结果到记忆系统

v2.0: 修复 - 从stdin读取而不是环境变量
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime, timezone

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

def extract_agent_info_from_input(tool_input: dict) -> tuple:
    """从tool_input中提取agent信息（PreToolUse阶段）"""
    agent_name = tool_input.get('subagent_type', '')
    task = tool_input.get('prompt', tool_input.get('description', ''))
    return agent_name, task

def extract_agent_info_from_output(tool_output: dict) -> tuple:
    """从tool_output中提取agent信息（PostToolUse阶段）"""
    # tool_output可能包含agentId等信息
    agent_id = tool_output.get('agentId', '')
    # 需要从input阶段获取，这里返回空
    return '', ''

def sanitize_string(text: str) -> str:
    """清理字符串中的非法 Unicode 字符（如代理对）"""
    if not text:
        return text

    # 移除代理对（surrogate pairs）
    # UTF-8 编码无法处理 0xD800-0xDFFF 范围的字符
    cleaned = []
    for char in text:
        try:
            # 尝试编码为 UTF-8
            char.encode('utf-8')
            cleaned.append(char)
        except (UnicodeEncodeError, UnicodeDecodeError):
            # 如果失败，替换为安全字符
            cleaned.append('�')  # Unicode 替换字符

    return ''.join(cleaned)


def save_execution_experience(agent_name: str, task: str):
    """保存执行经验"""

    if not agent_name or not task:
        return

    try:
        from agent_memory import get_agent_memory_manager

        # 映射agent名称
        mapping = {
            'code-reviewer': 'code_reviewer',
            'planner': 'planner',
            'architect': 'architect',
            'security-reviewer': 'security_reviewer',
            'doc-updater': 'doc_writer',
            'tdd-guide': 'tdd_guide',
            'e2e-runner': 'e2e_runner',
            'python-reviewer': 'python_reviewer',
            'go-reviewer': 'go_reviewer',
            'kotlin-reviewer': 'kotlin_reviewer',
            'database-reviewer': 'database_reviewer'
        }

        roland_name = mapping.get(agent_name, agent_name.replace('-', '_'))

        # 清理任务字符串（移除非法 Unicode 字符）
        clean_task = sanitize_string(task)

        # 获取记忆管理器
        mgr = get_agent_memory_manager()
        memory = mgr.get_agent_memory(roland_name)

        # 保存经验
        memory.add_professional_memory({
            'type': 'task_execution',
            'task': clean_task[:500],  # 限制长度
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'success': True
        })

        # 保存到文件
        mgr._save_agent_memory(roland_name)

        # 记录日志（使用轮转系统）
        from log_utils import write_log_with_rotation
        write_log_with_rotation(
            'memory_save.log',
            f"Agent: {agent_name} -> {roland_name} | Experience saved"
        )

    except Exception as e:
        # 静默失败
        from log_utils import write_log_with_rotation
        write_log_with_rotation(
            'memory_errors.log',
            f"Save Error: {str(e)} | Agent: {agent_name}"
        )

def cleanup_temp_files():
    """清理临时记忆文件"""
    try:
        # 清理环境变量中的临时文件
        temp_file = os.environ.get('CLAUDE_AGENT_MEMORY_FILE')
        if temp_file and os.path.exists(temp_file):
            os.unlink(temp_file)
            os.environ['CLAUDE_AGENT_MEMORY_FILE'] = ''
    except:
        pass

def main():
    """主函数"""

    # 从stdin读取hook数据（Claude Code标准方式）
    hook_data = read_stdin_json()

    # 清理临时文件（无论是否成功）
    cleanup_temp_files()

    if not hook_data:
        sys.exit(0)

    # 提取工具名称和输入
    tool_name = hook_data.get("tool_name", hook_data.get("tool", ""))
    tool_input = hook_data.get("tool_input", hook_data.get("input", {}))

    # 只处理Task tool
    if tool_name != "Task":
        sys.exit(0)

    # 提取agent信息（从tool_input）
    agent_name, task = extract_agent_info_from_input(tool_input)

    # 保存经验
    if agent_name and task:
        save_execution_experience(agent_name, task)
        print(f"[Memory Save] Agent: {agent_name}, Experience saved", file=sys.stderr)

    sys.exit(0)

if __name__ == "__main__":
    main()
