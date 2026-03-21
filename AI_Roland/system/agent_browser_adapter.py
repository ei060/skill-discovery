"""
Agent-Browser 适配器 - Vercel AI SDK 原生浏览器控制

Agent-Browser 是 Vercel Labs 开发的浏览器自动化工具，特点：
- TypeScript 原生支持
- Vercel AI SDK 集成
- ref 系统稳定引用
- 跨平台统一接口

GitHub: https://github.com/vercel/agent-browser
文档: https://github.com/vercel/agent-browser#readme
"""

import subprocess
import json
import re
import time
from typing import Optional, Dict, List, Any, Tuple
from pathlib import Path
import os


class RefParser:
    """解析 Agent-Browser 的 ref 系统输出"""

    # ref 匹配模式: [ref=e1] 或 [ref="e1"]
    REF_PATTERN = re.compile(r'\[ref(?:["\']?)=?(\w+)["\']?\]')
    # 元素类型: - heading "..." [ref=e1] [level=1]
    ELEMENT_PATTERN = re.compile(r'^\s*-\s+(\w+):\s+"([^"]*)"')

    @staticmethod
    def parse_snapshot(output: str) -> Dict[str, Any]:
        """
        解析 snapshot 命令输出

        Args:
            output: agent-browser snapshot 命令的输出

        Returns:
            {
                "title": "页面标题",
                "url": "页面URL",
                "nodes": [
                    {"ref": "e1", "role": "heading", "name": "...", "level": 1},
                    ...
                ]
            }
        """
        nodes = []
        title = ""
        url = ""

        lines = output.strip().split('\n')
        for line in lines:
            # 提取标题
            if line.startswith('#') and not title:
                title = line.lstrip('#').strip()
                continue

            # 提取 URL
            if ' | ' in line and not url:
                url = line.split('|')[0].strip()
                continue

            # 解析元素行
            ref_match = RefParser.REF_PATTERN.search(line)
            if ref_match:
                ref = ref_match.group(1)
                element_match = RefParser.ELEMENT_PATTERN.search(line)
                if element_match:
                    role = element_match.group(1)
                    name = element_match.group(2)

                    node = {
                        "ref": ref,
                        "role": role,
                        "name": name
                    }

                    # 提取额外属性 (level, depth 等)
                    attrs = re.findall(r'\[(\w+)=(\w+|\d+)\]', line)
                    for key, value in attrs:
                        try:
                            node[key] = int(value) if value.isdigit() else value
                        except:
                            node[key] = value

                    nodes.append(node)

        return {
            "title": title,
            "url": url,
            "nodes": nodes,
            "count": len(nodes)
        }

    @staticmethod
    def extract_refs(output: str) -> List[str]:
        """提取所有 ref ID"""
        return RefParser.REF_PATTERN.findall(output)


class AgentBrowserController:
    """
    Agent-Browser 控制器

    通过 CLI 命令控制浏览器，支持：
    - 导航
    - 快照 (含 ref)
    - 点击 (通过 ref)
    - 填写表单
    - 截图
    """

    def __init__(self, bin_path: str = "agent-browser"):
        """
        初始化控制器

        Args:
            bin_path: agent-browser 可执行文件路径
        """
        self.bin_path = bin_path
        self.current_url: Optional[str] = None
        self.last_snapshot: Optional[Dict[str, Any]] = None

    def _run(self, args: List[str], timeout: int = 30) -> Tuple[int, str, str]:
        """
        运行 agent-browser 命令

        Returns:
            (exit_code, stdout, stderr)
        """
        cmd = [self.bin_path] + args
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='replace'
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "命令超时"
        except FileNotFoundError:
            return -2, "", f"未找到 {self.bin_path}，请先安装: npm install -g agent-browser"
        except Exception as e:
            return -3, "", str(e)

    def install(self) -> bool:
        """安装/更新 Chromium 浏览器"""
        print("正在安装 Chromium 浏览器...")
        code, stdout, stderr = self._run(["install"], timeout=300)
        if code == 0:
            print("✓ Chromium 安装完成")
            return True
        else:
            print(f"✗ 安装失败: {stderr}")
            return False

    def open(self, url: str) -> Dict[str, Any]:
        """
        打开 URL

        Args:
            url: 目标 URL

        Returns:
            {"success": bool, "url": str, "message": str}
        """
        code, stdout, stderr = self._run(["open", url], timeout=60)

        if code == 0:
            self.current_url = url
            return {
                "success": True,
                "url": url,
                "message": stdout.strip() or f"已打开 {url}"
            }
        else:
            return {
                "success": False,
                "url": url,
                "message": stderr or stdout
            }

    def close(self) -> Dict[str, Any]:
        """关闭浏览器"""
        code, stdout, stderr = self._run(["close"])
        self.current_url = None
        self.last_snapshot = None

        return {
            "success": code == 0,
            "message": stderr or stdout or "浏览器已关闭"
        }

    def snapshot(self, interactive: bool = False,
                 compact: bool = False) -> Dict[str, Any]:
        """
        获取页面快照

        Args:
            interactive: 只显示可交互元素
            compact: 紧凑格式

        Returns:
            解析后的快照数据
        """
        args = ["snapshot"]
        if interactive:
            args.append("--interactive")
        if compact:
            args.append("--compact")

        code, stdout, stderr = self._run(args)

        if code == 0 and stdout:
            parsed = RefParser.parse_snapshot(stdout)
            self.last_snapshot = parsed
            return parsed
        else:
            return {
                "error": stderr or "快照失败",
                "raw_output": stdout
            }

    def click(self, ref: str) -> Dict[str, Any]:
        """
        点击元素

        Args:
            ref: 元素引用 (如 "e1", "e2")
        """
        # ref 不需要 # 前缀
        ref = ref.lstrip('#')

        code, stdout, stderr = self._run(["click", ref])

        return {
            "success": code == 0,
            "ref": ref,
            "message": stderr or stdout or f"已点击 {ref}"
        }

    def fill(self, ref: str, value: str) -> Dict[str, Any]:
        """
        填写输入框 (直接设置值)

        Args:
            ref: 元素引用
            value: 要填写的值
        """
        ref = ref.lstrip('#')

        code, stdout, stderr = self._run(["fill", ref, value])

        return {
            "success": code == 0,
            "ref": ref,
            "value": value,
            "message": stderr or stdout or f"已填写 {ref}"
        }

    def type(self, ref: str, text: str) -> Dict[str, Any]:
        """
        模拟键盘输入 (逐字符)

        Args:
            ref: 元素引用
            text: 要输入的文本
        """
        ref = ref.lstrip('#')

        code, stdout, stderr = self._run(["type", ref, text])

        return {
            "success": code == 0,
            "ref": ref,
            "text": text,
            "message": stderr or stdout or f"已输入到 {ref}"
        }

    def press(self, key: str) -> Dict[str, Any]:
        """
        按键

        Args:
            key: 按键名称 (Enter, Tab, Escape, ArrowDown 等)
        """
        code, stdout, stderr = self._run(["press", key])

        return {
            "success": code == 0,
            "key": key,
            "message": stderr or stdout or f"已按下 {key}"
        }

    def screenshot(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        截图

        Args:
            output_path: 保存路径 (可选)
        """
        args = ["screenshot"]
        if output_path:
            args.extend(["--output", output_path])

        code, stdout, stderr = self._run(args)

        return {
            "success": code == 0,
            "path": output_path,
            "message": stderr or stdout or "截图已保存"
        }

    def eval_js(self, expression: str) -> Dict[str, Any]:
        """
        执行 JavaScript

        Args:
            expression: JavaScript 表达式
        """
        code, stdout, stderr = self._run(["eval", expression])

        try:
            result = json.loads(stdout) if stdout else None
            return {
                "success": code == 0,
                "result": result,
                "expression": expression
            }
        except:
            return {
                "success": code == 0,
                "raw_output": stdout,
                "expression": expression
            }

    def find_ref(self, text: str) -> Optional[str]:
        """
        在上次快照中查找包含指定文本的元素

        Args:
            text: 要搜索的文本

        Returns:
            第一个匹配的 ref，或 None
        """
        if not self.last_snapshot:
            self.snapshot()

        if self.last_snapshot:
            for node in self.last_snapshot.get("nodes", []):
                if text.lower() in node.get("name", "").lower():
                    return node.get("ref")

        return None

    def click_text(self, text: str) -> Dict[str, Any]:
        """
        点击包含指定文本的元素

        Args:
            text: 要查找的文本
        """
        ref = self.find_ref(text)
        if ref:
            return self.click(ref)
        else:
            return {
                "success": False,
                "message": f"未找到包含 '{text}' 的元素"
            }

    def wait_for_text(self, text: str, timeout: int = 10,
                      interval: float = 0.5) -> bool:
        """
        等待指定文本出现在页面上

        Args:
            text: 要等待的文本
            timeout: 超时时间（秒）
            interval: 检查间隔
        """
        start = time.time()
        while time.time() - start < timeout:
            if self.find_ref(text):
                return True
            time.sleep(interval)
        return False


class AgentBrowserAdapter:
    """
    Agent-Browser 高级适配器

    提供更友好的 API 和自动化流程
    """

    def __init__(self):
        self.controller = AgentBrowserController()

    def open_and_analyze(self, url: str, wait: float = 2.0) -> Dict[str, Any]:
        """
        打开页面并分析

        Args:
            url: 目标 URL
            wait: 等待页面加载时间

        Returns:
            页面分析结果
        """
        result = self.controller.open(url)
        if result["success"]:
            time.sleep(wait)
            snapshot = self.controller.snapshot(interactive=True)
            return {
                **result,
                "snapshot": snapshot
            }
        return result

    def fill_form(self, fields: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        批量填写表单

        Args:
            fields: {ref/文本: value} 映射

        Returns:
            每个字段的填写结果
        """
        results = []
        for ref_or_text, value in fields.items():
            # 判断是 ref 还是文本
            if ref_or_text.startswith("e") or ref_or_text.startswith("#"):
                result = self.controller.fill(ref_or_text, value)
            else:
                # 尝试按文本查找
                ref = self.controller.find_ref(ref_or_text)
                if ref:
                    result = self.controller.fill(ref, value)
                else:
                    result = {"success": False, "message": f"未找到: {ref_or_text}"}
            results.append(result)
        return results

    def click_sequence(self, refs_or_texts: List[str]) -> List[Dict[str, Any]]:
        """
        顺序点击多个元素

        Args:
            refs_or_texts: ref 或文本列表

        Returns:
            每次点击的结果
        """
        results = []
        for item in refs_or_texts:
            if item.startswith("e") or item.startswith("#"):
                result = self.controller.click(item)
            else:
                ref = self.controller.find_ref(item)
                if ref:
                    result = self.controller.click(ref)
                else:
                    result = {"success": False, "message": f"未找到: {item}"}
            results.append(result)

            if not result["success"]:
                break

            time.sleep(0.5)  # 点击间隔

        return results

    def smart_fetch(self, url: str) -> Dict[str, Any]:
        """
        智能获取页面内容

        结合 snapshot 和 JavaScript 提取，获取页面主要文本内容
        """
        result = self.open_and_analyze(url)

        if result.get("success"):
            # 提取页面文本
            text_result = self.controller.eval_js(
                "document.body.innerText"
            )

            return {
                "url": url,
                "title": result.get("snapshot", {}).get("title", ""),
                "text": text_result.get("result", ""),
                "nodes": result.get("snapshot", {}).get("nodes", [])
            }

        return result

    def close(self):
        """关闭浏览器"""
        return self.controller.close()


# 便捷函数
def quick_browse(url: str) -> Dict[str, Any]:
    """快速浏览并返回页面分析"""
    adapter = AgentBrowserAdapter()
    try:
        result = adapter.open_and_analyze(url)
        return result
    finally:
        adapter.close()


# CLI 测试入口
if __name__ == "__main__":
    print("=== Agent-Browser 适配器测试 ===\n")

    controller = AgentBrowserController()

    # 测试 1: 检查是否安装
    print("1. 检查 Agent-Browser...")
    code, _, _ = controller._run(["--version"])
    if code != 0:
        print("请先安装: npm install -g agent-browser")
        exit(1)
    print("✓ Agent-Browser 已安装")

    # 测试 2: 打开页面
    print("\n2. 打开测试页面...")
    result = controller.open("https://example.com")
    print(f"结果: {result['message']}")

    # 测试 3: 获取快照
    print("\n3. 获取页面快照...")
    time.sleep(2)
    snapshot = controller.snapshot(interactive=True)
    print(f"标题: {snapshot.get('title', 'N/A')}")
    print(f"元素数量: {snapshot.get('count', 0)}")
    print("\n前 5 个元素:")
    for node in snapshot.get('nodes', [])[:5]:
        print(f"  - [{node['ref']}] {node['role']}: {node['name']}")

    # 测试 4: 关闭
    print("\n4. 关闭浏览器...")
    controller.close()
    print("✓ 测试完成")
