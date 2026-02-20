"""
Hooks 系统 - 让 AI 感知工作环境
在特定事件发生时自动触发脚本
"""

import sys
import os
# 修复 Windows 控制台中文乱码
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


class HooksManager:
    """Hooks 管理器"""

    def __init__(self, workspace_path=None):
        if workspace_path is None:
            current_dir = Path(__file__).parent
            self.workspace = current_dir.parent
        else:
            self.workspace = Path(workspace_path)

        self.config_file = self.workspace / "config" / "hooks.yaml"
        self.log_file = self.workspace / "logs" / "hooks.log"
        self.log_file.parent.mkdir(exist_ok=True)

        self.hooks = self._load_hooks()

    def _load_hooks(self) -> Dict[str, List[str]]:
        """加载 Hooks 配置"""
        import yaml

        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)

        # 默认 Hooks
        return {
            "user_prompt_submit": [
                "echo '[Hook] 用户提交问题'",
                "date"
            ],
            "assistant_response": [
                "echo '[Hook] AI 回复完成'"
            ],
            "tool_call": [],
            "session_start": [],
            "session_end": []
        }

    def _log(self, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"{timestamp} {message}\n"

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)

    def execute_hooks(self, event_name: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行指定事件的所有 Hooks

        Args:
            event_name: 事件名称 (user_prompt_submit, assistant_response, etc.)
            context: 上下文信息

        Returns:
            执行结果字典
        """
        if event_name not in self.hooks:
            return {"status": "no_hooks", "event": event_name}

        hooks = self.hooks[event_name]
        if not hooks:
            return {"status": "no_hooks", "event": event_name}

        results = []
        self._log(f"[Event] {event_name}")

        for hook in hooks:
            try:
                self._log(f"[Hook] 执行: {hook}")

                # 执行 Hook 命令
                result = subprocess.run(
                    hook,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.workspace
                )

                results.append({
                    "command": hook,
                    "returncode": result.returncode,
                    "stdout": result.stdout.strip(),
                    "stderr": result.stderr.strip()
                })

                self._log(f"[Result] 返回码: {result.returncode}")

                if result.stdout:
                    self._log(f"[Stdout] {result.stdout.strip()}")

                if result.stderr:
                    self._log(f"[Stderr] {result.stderr.strip()}")

            except subprocess.TimeoutExpired:
                self._log(f"[Error] Hook 超时: {hook}")
                results.append({
                    "command": hook,
                    "error": "timeout"
                })
            except Exception as e:
                self._log(f"[Error] {str(e)}")
                results.append({
                    "command": hook,
                    "error": str(e)
                })

        return {
            "status": "executed",
            "event": event_name,
            "results": results,
            "count": len(results)
        }

    def trigger_user_prompt_submit(self, user_input: str = "") -> Dict[str, Any]:
        """用户提交问题时触发"""
        return self.execute_hooks("user_prompt_submit", {"input": user_input})

    def trigger_assistant_response(self, response: str = "") -> Dict[str, Any]:
        """AI 回复后触发"""
        return self.execute_hooks("assistant_response", {"response": response})

    def trigger_tool_call(self, tool_name: str = "", args: Dict = None) -> Dict[str, Any]:
        """AI 调用工具时触发"""
        return self.execute_hooks("tool_call", {"tool": tool_name, "args": args})

    def trigger_session_start(self) -> Dict[str, Any]:
        """会话开始时触发"""
        return self.execute_hooks("session_start")

    def trigger_session_end(self) -> Dict[str, Any]:
        """会话结束时触发"""
        return self.execute_hooks("session_end")


def main():
    """测试 Hooks 系统"""
    manager = HooksManager()

    print("=== Hooks 系统测试 ===\n")

    print("1. 触发 user_prompt_submit 事件:")
    result = manager.trigger_user_prompt_submit("测试问题")
    print(f"   状态: {result['status']}")
    print(f"   执行数量: {result.get('count', 0)}")

    print("\n2. 触发 assistant_response 事件:")
    result = manager.trigger_assistant_response("测试回复")
    print(f"   状态: {result['status']}")

    print("\n3. 查看日志:")
    print(manager.log_file.read_text(encoding='utf-8')[-500:])


if __name__ == "__main__":
    main()
