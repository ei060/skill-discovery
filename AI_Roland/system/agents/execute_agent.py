#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI Roland 代理执行器

让 Claude 直接以代理身份执行任务
支持代理独立记忆系统
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
parent_path = Path(__file__).parent.parent
sys.path.insert(0, str(system_path))
sys.path.insert(0, str(parent_path))

from engine import RolandEngine

# 导入记忆模块
try:
    from agent_memory import get_agent_memory_manager
except ImportError:
    from agents.agent_memory import get_agent_memory_manager


def execute_agent(agent_name: str, task: str, context: dict = None) -> dict:
    """
    执行代理任务 - 生成代理执行指令供 Claude 使用

    Args:
        agent_name: 代理名称
        task: 任务描述
        context: 上下文信息

    Returns:
        代理执行信息
    """
    engine = RolandEngine()
    memory_manager = get_agent_memory_manager()

    # 获取代理配置
    agent_config = engine.agent_manager.get_agent(agent_name)
    if not agent_config:
        return {
            "status": "error",
            "error": f"代理 {agent_name} 不存在"
        }

    # 获取代理记忆
    agent_memory = memory_manager.get_agent_memory(agent_name)

    # 搜索相关记忆
    relevant_memories = agent_memory.search(task)

    # 创建代理任务文件
    agent_task_file = system_path / "current_task.md"

    # 构建记忆上下文
    memory_context = ""
    if relevant_memories:
        memory_context = "\n## 相关经验\n\n"
        for i, mem in enumerate(relevant_memories[:5], 1):
            source = mem.get('source', 'unknown')
            content = mem.get('content') or mem.get('type') or str(mem)
            memory_context += f"{i}. [{source}] {content}\n"

    task_content = f"""# {agent_config.name.upper()} 代理任务

## 系统角色
{agent_config.system_prompt}

## 你的工作记忆
你有独立的记忆系统，包含:
- 过去完成的任务和经验
- 常见模式和最佳实践
- 专业领域的知识积累

{memory_context}

## 当前任务
{task}

## 可用工具
{', '.join(agent_config.tools)}

## 执行要求
1. 以上述 {agent_config.name} 的身份思考
2. 参考你的相关经验
3. 使用可用的工具完成任务
4. 完成后，重要经验会被自动记录到你的记忆中
5. 完成后返回到主 AI Roland

## 记忆状态
- 工作记忆: {len(agent_memory.working_memory)} 项
- 专业记忆: {len(agent_memory.professional_memory)} 项
- 已完成任务: {agent_memory.stats['tasks_completed']} 个
"""

    # 写入任务文件
    agent_task_file.write_text(task_content, encoding='utf-8')

    # 添加到工作记忆
    agent_memory.add_work_item({
        'type': 'new_task',
        'task': task,
        'context': context or {}
    })

    memory_manager._save_agent_memory(agent_name)

    return {
        "status": "ready",
        "agent": agent_name,
        "agent_file": str(agent_task_file),
        "instruction": f"请以 {agent_config.name} 代理的身份执行任务。查看文件: {agent_task_file}",
        "system_prompt": agent_config.system_prompt,
        "tools": agent_config.tools,
        "model": agent_config.model,
        "memory_stats": {
            "working": len(agent_memory.working_memory),
            "professional": len(agent_memory.professional_memory),
            "completed": agent_memory.stats['tasks_completed']
        }
    }


def complete_agent_task(agent_name: str, task: str, result: dict):
    """
    完成代理任务 - 记录结果到记忆

    Args:
        agent_name: 代理名称
        task: 任务描述
        result: 执行结果
    """
    memory_manager = get_agent_memory_manager()

    # 记录任务完成
    memory_manager.record_task_completion(agent_name, task, result)

    # 同步到全局系统
    memory_manager.sync_to_global()

    return {
        "status": "recorded",
        "agent": agent_name,
        "memory_updated": True
    }


def main():
    """命令行入口"""
    if len(sys.argv) < 3:
        print("用法: python execute_agent.py <代理名> <任务描述>")
        print()
        print("可用代理:")
        engine = RolandEngine()
        for agent in engine.agent_manager.list_agents():
            print(f"  - {agent.name}: {agent.description}")
        sys.exit(1)

    agent_name = sys.argv[1]
    task = ' '.join(sys.argv[2:])

    result = execute_agent(agent_name, task)

    if result["status"] == "error":
        print(f"错误: {result['error']}")
        sys.exit(1)

    print("=" * 60)
    print(f"代理任务已创建: {agent_name}")
    print("=" * 60)
    print()
    print(result["instruction"])
    print()
    print(f"任务文件: {result['agent_file']}")
    print(f"推荐模型: {result['model']}")
    print(f"可用工具: {result['tools']}")
    print()
    print(f"记忆状态:")
    print(f"  工作记忆: {result['memory_stats']['working']} 项")
    print(f"  专业记忆: {result['memory_stats']['professional']} 项")
    print(f"  已完成: {result['memory_stats']['completed']} 个任务")


if __name__ == "__main__":
    main()
