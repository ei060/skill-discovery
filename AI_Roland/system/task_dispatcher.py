#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
任务分发器 - TodoWrite 任务管理专用 Hook

只接管 TaskCreate 和 TaskUpdate 工具调用，将任务同步到 AI Roland 的任务状态管理器。

版本: 1.0
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# 添加系统路径（使用绝对路径，确保在子进程中也能正确导入）
system_path = Path(__file__).parent.parent
if str(system_path) not in sys.path:
    sys.path.insert(0, str(system_path))

# 调试：记录所有 hook 输入
DEBUG = True  # 生产环境可设为 False
debug_file = Path(__file__).parent / "task_dispatcher_debug.log"


def log_debug(message: str):
    """记录调试日志"""
    if DEBUG:
        with open(debug_file, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().isoformat()} | {message}\n")


def log_error(error: str, context: Dict = None):
    """记录分发错误"""
    error_file = Path(__file__).parent / "dispatcher_errors.log"
    with open(error_file, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now().isoformat()} | ERROR: {error}\n")
        if context:
            f.write(f"  Context: {json.dumps(context, ensure_ascii=False)}\n")


def read_stdin_json() -> Optional[Dict]:
    """从 stdin 读取 JSON 数据（安全地）"""
    try:
        # 使用安全的 stdin 读取
        from system.sys_utils import safe_read_stdin
        stdin_data = safe_read_stdin()
        if not stdin_data:
            return None
        return json.loads(stdin_data)
    except Exception as e:
        log_error(f"读取 stdin 失败: {e}")
        return None


def should_dispatch(hook_data: Dict) -> bool:
    """
    判断是否应该接管本次工具调用

    规则：
    - tool_name 为 TaskCreate 或 TaskUpdate → 接管
    - 其他工具 → 不接管
    """
    if not hook_data:
        return False

    tool_name = hook_data.get("tool_name", "")

    # 只接管 TodoWrite 相关的工具
    should = tool_name in ["TaskCreate", "TaskUpdate"]

    log_debug(f"路由判断: tool_name={tool_name}, should_dispatch={should}")

    return should


def dispatch_task_create(tool_input: Dict) -> Dict[str, Any]:
    """
    处理 TaskCreate 工具调用

    输入格式：
    {
        "subject": "任务名称",
        "description": "任务描述",
        "activeForm": "正在执行的任务"
    }
    """
    try:
        # 确保导入路径正确
        system_path = Path(__file__).parent.parent
        if str(system_path) not in sys.path:
            sys.path.insert(0, str(system_path))

        from task_state_manager import get_task_manager
        manager = get_task_manager()

        # 提取任务信息
        subject = tool_input.get("subject", "")
        description = tool_input.get("description", "")
        active_form = tool_input.get("activeForm", "")

        if not subject:
            return {"success": False, "error": "任务名称不能为空"}

        # 添加到活动任务
        success = manager.add_active_task(subject)

        # 如果有 activeForm，设置为焦点
        if active_form:
            manager.set_focus(active_form)

        # 如果有 description，添加为上下文笔记
        if description:
            manager.add_context_note(f"任务描述: {description}")

        # 同步到 TodoWrite 列表（如果存在）
        _sync_to_todolist(manager)

        return {
            "success": success,
            "task": subject,
            "message": f"任务已添加到 AI Roland 系统: {subject}"
        }

    except Exception as e:
        log_error(f"TaskCreate 分发失败: {e}", {"tool_input": tool_input})
        return {"success": False, "error": str(e)}


def dispatch_task_update(tool_input: Dict) -> Dict[str, Any]:
    """
    处理 TaskUpdate 工具调用

    输入格式：
    {
        "taskId": "1",
        "subject": "任务名称",
        "status": "completed",
        "activeForm": "正在执行的任务"
    }
    """
    try:
        # 导入任务管理器（确保 sys.path 正确）
        import sys
        system_path = Path(__file__).parent.parent
        if str(system_path) not in sys.path:
            sys.path.insert(0, str(system_path))

        from task_state_manager import get_task_manager

        manager = get_task_manager()

        # 提取信息
        task_id = tool_input.get("taskId", "")
        subject = tool_input.get("subject", "")
        status = tool_input.get("status", "")
        active_form = tool_input.get("activeForm", "")

        result = {}

        # 处理状态变更
        if status == "completed" and subject:
            success = manager.complete_task(subject)
            result["success"] = success
            result["message"] = f"任务已完成: {subject}"

        elif status == "in_progress" and subject:
            # 重新添加到活动任务（如果不存在）
            manager.add_active_task(subject)
            if active_form:
                manager.set_focus(active_form)
            result["success"] = True
            result["message"] = f"任务恢复进行中: {subject}"

        else:
            # 只更新焦点
            if active_form:
                manager.set_focus(active_form)
            result["success"] = True
            result["message"] = f"任务焦点已更新"

        # 同步到 TodoWrite 列表
        _sync_to_todolist(manager)

        return result

    except Exception as e:
        log_error(f"TaskUpdate 分发失败: {e}", {"tool_input": tool_input})
        return {"success": False, "error": str(e)}


def _sync_to_todolist(manager) -> bool:
    """
    同步到 TodoWrite 任务列表文件（任务清单.md）

    这是可选功能，失败不影响主流程
    """
    try:
        # 读取当前任务列表
        tasks_file = Path(__file__).parent.parent.parent / "任务清单.md"
        if not tasks_file.exists():
            return False

        # 获取 TodoWrite 格式的任务列表
        todos = manager.load_todos()

        # 更新任务清单.md（可选）
        # 这里可以添加将 todos 同步到 markdown 文件的逻辑
        # 但为了简化，暂时跳过

        return True

    except Exception as e:
        # 同步失败不影响主流程
        log_debug(f"同步到任务清单失败: {e}")
        return False


def dispatch_to_task_manager(hook_data: Dict) -> Dict:
    """
    分发到任务管理器

    返回格式：
    {
        "action": "dispatch",
        "result": {...},
        "error": null
    }
    """
    tool_name = hook_data.get("tool_name", "")
    tool_input = hook_data.get("tool_input", {})

    log_debug(f"开始分发: {tool_name}")

    start_time = time.perf_counter()

    try:
        if tool_name == "TaskCreate":
            result = dispatch_task_create(tool_input)
        elif tool_name == "TaskUpdate":
            result = dispatch_task_update(tool_input)
        else:
            result = {"error": f"不支持的工具: {tool_name}"}

        elapsed = (time.perf_counter() - start_time) * 1000
        log_debug(f"分发完成: {elapsed:.2f}ms")

        return {
            "action": "dispatch",
            "result": result,
            "error": None
        }

    except Exception as e:
        elapsed = (time.perf_counter() - start_time) * 1000
        log_error(f"分发异常: {e} ({elapsed:.2f}ms)")
        return {
            "action": "dispatch",
            "result": None,
            "error": str(e)
        }


def main():
    """
    主函数 - Hook 入口点

    执行流程：
    1. 读取 hook 数据
    2. 判断是否接管
    3. 如果接管，分发到 task_manager
    4. 如果分发失败，返回 pass 让原流程继续
    """
    # 读取 hook 数据
    hook_data = read_stdin_json()

    if not hook_data:
        # 没有数据，直接退出
        sys.exit(0)

    # 路由判断
    if should_dispatch(hook_data):
        # 尝试分发
        try:
            result = dispatch_to_task_manager(hook_data)

            # 输出结果（作为调试信息）
            result_json = json.dumps(result, ensure_ascii=False)
            print(f"[TaskDispatcher] {result_json}", file=sys.stderr)

            # 无论成功失败，都返回 0 让原流程继续
            # hook 不能阻止工具执行，只能在前后增强
            sys.exit(0)

        except Exception as e:
            # 分发异常，记录错误但让原流程继续
            log_error(f"分发异常: {e}")
            print(f"[TaskDispatcher] 错误: {e}", file=sys.stderr)
            sys.exit(0)
    else:
        # 不接管，让原流程继续
        sys.exit(0)


if __name__ == "__main__":
    main()
