#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI Roland v2.0 - Hook 观察捕获脚本

集成 Claude Code 的 PreToolUse/PostToolUse hooks，
实现 100% 可靠的工具使用观察记录。

基于 ECC v2.1 Hook 观察系统
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

# 添加系统路径
system_path = Path(__file__).parent.parent
sys.path.insert(0, str(system_path))

from homunculus_memory import HomunculusMemory, Observation, Config


class HookObserver:
    """Hook 观察器 - 捕获 Claude Code 工具使用事件"""

    def __init__(self, workspace=None):
        if workspace is None:
            # 从环境变量或当前目录检测
            workspace = os.environ.get('CLAUDE_WORKSPACE',
                                       Path.cwd().parent)

        self.workspace = Path(workspace)
        self.memory = HomunculusMemory(self.workspace)
        self.obs_log = self.workspace / "AI_Roland" / "logs" / "observations.jsonl"
        self.obs_log.parent.mkdir(parents=True, exist_ok=True)

    def _log_observation(self, obs_type, data):
        """记录观察日志（用于调试）"""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": obs_type,
            "data": data
        }

        with open(self.obs_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    def _detect_project_from_context(self, context_str: str) -> tuple:
        """从上下文中检测项目信息

        Returns:
            (project_id, project_name) tuple
        """
        import hashlib

        # 提取文件路径
        for line in str(context_str).split('\n'):
            if 'file_path' in line or 'Working directory' in line:
                # 提取路径作为项目标识
                for part in line.split('"'):
                    if ':' in part and ('\\' in part or '/' in part):
                        # 是路径
                        project_path = Path(part).resolve()
                        project_id = hashlib.md5(
                            str(project_path.parent).encode()
                        ).hexdigest()[:12]
                        return f"{project_path.parent.name} ({project_id})", project_path.parent.name

        # 默认使用当前项目
        return self.memory.project['id'], self.memory.project['name']

    def handle_pre_tool_use(self, event_data: dict) -> dict:
        """PreToolUse Hook 处理

        在工具调用前捕获，记录工具名称和参数
        """
        try:
            tool_name = event_data.get('tool_name', 'unknown')
            tool_input = event_data.get('tool_input', {})
            session_id = event_data.get('session_id', '')

            # 检测项目
            project_id, project_name = self._detect_project_from_context(tool_input)

            # 记录观察 - 使用正确的字段名
            observation = Observation(
                timestamp=datetime.now(timezone.utc).isoformat(),
                event="tool_start",
                tool=tool_name,
                session=session_id,
                project_id=project_id,
                project_name=project_name,
                input=json.dumps(tool_input, ensure_ascii=False)[:500] if isinstance(tool_input, dict) else str(tool_input)[:500],
                output=None,
                cwd=str(self.workspace),
                tool_use_id=""
            )

            self.memory.add_observation(observation)
            self._log_observation("pre_tool_use", {
                "tool": tool_name,
                "project": project_id
            })

            return {
                "status": "recorded",
                "tool": tool_name,
                "project": project_id
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def handle_post_tool_use(self, event_data: dict) -> dict:
        """PostToolUse Hook 处理

        在工具调用后捕获，记录结果和耗时
        """
        try:
            tool_name = event_data.get('tool_name', 'unknown')
            result = event_data.get('result', {})
            duration = event_data.get('duration_ms', 0)
            success = event_data.get('success', True)
            session_id = event_data.get('session_id', '')

            # 检测项目
            project_id, project_name = self._detect_project_from_context(result)

            # 记录观察
            observation = Observation(
                timestamp=datetime.now(timezone.utc).isoformat(),
                event="tool_complete",
                tool=tool_name,
                session=session_id,
                project_id=project_id,
                project_name=project_name,
                input=None,
                output=json.dumps(result, ensure_ascii=False)[:500] if isinstance(result, dict) else str(result)[:500],
                cwd=str(self.workspace),
                tool_use_id=""
            )

            self.memory.add_observation(observation)
            self._log_observation("post_tool_use", {
                "tool": tool_name,
                "duration": duration,
                "success": success,
                "project": project_id
            })

            return {
                "status": "recorded",
                "tool": tool_name,
                "project": project_id
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def handle_session_start(self, event_data: dict) -> dict:
        """SessionStart Hook 处理"""
        try:
            session_id = event_data.get('session_id', '')

            observation = Observation(
                timestamp=datetime.now(timezone.utc).isoformat(),
                event="session_start",
                tool="",
                session=session_id,
                project_id=self.memory.project['id'],
                project_name=self.memory.project['name'],
                input=None,
                output=None,
                cwd=str(self.workspace),
                tool_use_id=""
            )

            self.memory.add_observation(observation)

            return {"status": "recorded"}

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def handle_session_end(self, event_data: dict) -> dict:
        """SessionEnd Hook 处理 - 触发模式分析"""
        try:
            session_id = event_data.get('session_id', '')

            observation = Observation(
                timestamp=datetime.now(timezone.utc).isoformat(),
                event="session_end",
                tool="",
                session=session_id,
                project_id=self.memory.project['id'],
                project_name=self.memory.project['name'],
                input=None,
                output=None,
                cwd=str(self.workspace),
                tool_use_id=""
            )

            self.memory.add_observation(observation)

            # 会话结束时触发观察分析
            new_instincts = self.memory.analyze_observations()

            return {
                "status": "recorded",
                "new_patterns": len(new_instincts)
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}


def main():
    """命令行入口 - 用于 Claude Code Hook 配置"""
    import argparse

    parser = argparse.ArgumentParser(description="AI Roland Hook 观察器")
    parser.add_argument('--event', required=True,
                       choices=['pre_tool_use', 'post_tool_use',
                               'session_start', 'session_end'])
    parser.add_argument('--data', default='{}')
    parser.add_argument('--workspace', default=None)

    args = parser.parse_args()

    observer = HookObserver(args.workspace)

    # 解析事件数据
    try:
        event_data = json.loads(args.data)
    except:
        event_data = {}

    # 路由到对应处理器
    handlers = {
        'pre_tool_use': observer.handle_pre_tool_use,
        'post_tool_use': observer.handle_post_tool_use,
        'session_start': observer.handle_session_start,
        'session_end': observer.handle_session_end
    }

    result = handlers[args.event](event_data)

    # 输出结果（JSON格式，便于 Claude Code 解析）
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
