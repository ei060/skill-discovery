"""
PinchTab 适配器 - 多实例浏览器控制器

PinchTab 是一个高效的浏览器自动化工具，特点：
- Token 高效 (~800 tokens/page)
- 多实例隔离
- HTTP API 接口
- 单文件部署 (12MB)

GitHub: https://github.com/pinchtab/pinchtab
文档: https://pinchtab.com/docs
"""

import subprocess
import time
import json
import requests
from typing import Optional, Dict, List, Any
from pathlib import Path
import os
import signal


class PinchTabInstance:
    """单个 PinchTab 实例"""

    def __init__(self, name: str, port: int, base_url: str = "http://127.0.0.1"):
        self.name = name
        self.port = port
        self.base_url = f"{base_url}:{port}"
        self.process: Optional[subprocess.Popen] = None
        self.current_tab: Optional[str] = None

    def start(self, headless: bool = True) -> bool:
        """启动 PinchTab 服务器"""
        try:
            # 设置环境变量
            env = os.environ.copy()
            env["BRIDGE_PORT"] = str(self.port)
            env["BRIDGE_HEADLESS"] = "true" if headless else "false"

            # 启动进程
            log_file = Path(__file__).parent.parent / "logs" / f"pinchtab_{self.name}.log"
            log_file.parent.mkdir(parents=True, exist_ok=True)

            self.process = subprocess.Popen(
                ["npx", "pinchtab"],
                env=env,
                stdout=open(log_file, "w"),
                stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
            )

            # 等待服务启动
            for _ in range(30):  # 最多等待 30 秒
                try:
                    resp = requests.get(f"{self.base_url}/health", timeout=2)
                    if resp.status_code == 200:
                        return True
                except:
                    time.sleep(1)

            return False
        except Exception as e:
            print(f"[错误] 启动 PinchTab 实例 {self.name} 失败: {e}")
            return False

    def stop(self) -> bool:
        """停止实例"""
        if self.process:
            try:
                if os.name == "nt":
                    # Windows: 使用 taskkill
                    subprocess.run(["taskkill", "/F", "/PID", str(self.process.pid)],
                                   capture_output=True)
                else:
                    # Unix: 发送 SIGTERM
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                self.process.wait(timeout=5)
                return True
            except:
                try:
                    self.process.terminate()
                    self.process.wait(timeout=5)
                    return True
                except:
                    return False
        return True

    def health(self) -> Dict[str, Any]:
        """检查实例健康状态"""
        try:
            resp = requests.get(f"{self.base_url}/health", timeout=5)
            return resp.json()
        except:
            return {"status": "error", "message": "无法连接到实例"}

    def navigate(self, url: str) -> Dict[str, Any]:
        """导航到指定 URL"""
        try:
            resp = requests.post(
                f"{self.base_url}/navigate",
                json={"url": url},
                timeout=30
            )
            result = resp.json()
            self.current_tab = result.get("tabId")
            return result
        except Exception as e:
            return {"error": str(e)}

    def snapshot(self, interactive: bool = True, compact: bool = True,
                 max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """
        获取页面快照

        Args:
            interactive: 只返回可交互元素
            compact: 紧凑格式 (最 token 高效)
            max_tokens: 限制 token 数量
        """
        try:
            params = {
                "interactive": interactive,
                "compact": compact
            }
            if max_tokens:
                params["maxTokens"] = max_tokens

            resp = requests.get(
                f"{self.base_url}/snapshot",
                params=params,
                timeout=10
            )
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def text(self, raw: bool = False) -> Dict[str, Any]:
        """
        提取页面文本 (token 高效，~800 tokens)

        Args:
            raw: 返回原始文本而非结构化
        """
        try:
            params = {"raw": raw} if raw else {}
            resp = requests.get(
                f"{self.base_url}/text",
                params=params,
                timeout=10
            )
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def click(self, ref: str) -> Dict[str, Any]:
        """点击元素 (通过 ref)"""
        try:
            resp = requests.post(
                f"{self.base_url}/action",
                json={"kind": "click", "ref": ref},
                timeout=10
            )
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def fill(self, ref: str, text: str) -> Dict[str, Any]:
        """填写输入框"""
        try:
            resp = requests.post(
                f"{self.base_url}/action",
                json={"kind": "fill", "ref": ref, "value": text},
                timeout=10
            )
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def type_text(self, ref: str, text: str) -> Dict[str, Any]:
        """模拟键盘输入"""
        try:
            resp = requests.post(
                f"{self.base_url}/action",
                json={"kind": "type", "ref": ref, "value": text},
                timeout=10
            )
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def press(self, key: str) -> Dict[str, Any]:
        """按键 (Enter, Tab, Escape 等)"""
        try:
            resp = requests.post(
                f"{self.base_url}/action",
                json={"kind": "press", "key": key},
                timeout=10
            )
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def screenshot(self, output_path: Optional[str] = None, quality: int = 80) -> bytes:
        """
        截图

        Args:
            output_path: 保存路径
            quality: JPEG 质量 (1-100)

        Returns:
            图片字节
        """
        try:
            params = {"quality": quality}
            resp = requests.get(
                f"{self.base_url}/screenshot",
                params=params,
                timeout=10
            )

            if output_path:
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(resp.content)

            return resp.content
        except Exception as e:
            print(f"[错误] 截图失败: {e}")
            return b""

    def eval_js(self, expression: str) -> Dict[str, Any]:
        """执行 JavaScript"""
        try:
            resp = requests.post(
                f"{self.base_url}/eval",
                json={"expression": expression},
                timeout=10
            )
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def tabs(self, action: str = "list", url: Optional[str] = None,
             tab_id: Optional[str] = None) -> Dict[str, Any]:
        """
        标签页管理

        Args:
            action: list, new, close
            url: 新标签页的 URL
            tab_id: 要关闭的标签页 ID
        """
        try:
            if action == "list":
                resp = requests.get(f"{self.base_url}/tabs", timeout=5)
            elif action == "new" and url:
                resp = requests.post(
                    f"{self.base_url}/tabs",
                    json={"url": url},
                    timeout=30
                )
            elif action == "close" and tab_id:
                resp = requests.delete(
                    f"{self.base_url}/tabs/{tab_id}",
                    timeout=5
                )
            else:
                return {"error": "无效的 action 或缺少参数"}
            return resp.json()
        except Exception as e:
            return {"error": str(e)}


class PinchTabAdapter:
    """
    PinchTab 多实例管理器

    用于管理多个隔离的浏览器实例，每个实例有独立的：
    - 端口
    - Profile (cookie, storage)
    - Chrome 进程

    使用场景：
    - 多账户登录
    - 并行任务
    - 隔离测试环境
    """

    def __init__(self, base_port: int = 9867):
        self.base_port = base_port
        self.instances: Dict[str, PinchTabInstance] = {}
        self.next_port = base_port

    def create_instance(self, name: str, headless: bool = True,
                        port: Optional[int] = None) -> PinchTabInstance:
        """
        创建新实例

        Args:
            name: 实例名称
            headless: 是否无头模式
            port: 指定端口 (可选)

        Returns:
            PinchTabInstance 对象
        """
        if name in self.instances:
            print(f"[警告] 实例 {name} 已存在")
            return self.instances[name]

        if port is None:
            port = self.next_port
            self.next_port += 1

        instance = PinchTabInstance(name, port)
        if instance.start(headless):
            self.instances[name] = instance
            print(f"[✓] PinchTab 实例 {name} 已启动 (端口 {port})")
        else:
            print(f"[✗] PinchTab 实例 {name} 启动失败")

        return instance

    def get_instance(self, name: str) -> Optional[PinchTabInstance]:
        """获取已存在的实例"""
        return self.instances.get(name)

    def stop_instance(self, name: str) -> bool:
        """停止指定实例"""
        instance = self.instances.get(name)
        if instance:
            if instance.stop():
                del self.instances[name]
                print(f"[✓] 实例 {name} 已停止")
                return True
        return False

    def stop_all(self) -> None:
        """停止所有实例"""
        for name in list(self.instances.keys()):
            self.stop_instance(name)

    def list_instances(self) -> List[Dict[str, Any]]:
        """列出所有实例状态"""
        result = []
        for name, instance in self.instances.items():
            health = instance.health()
            result.append({
                "name": name,
                "port": instance.port,
                "status": health.get("status", "unknown"),
                "current_tab": instance.current_tab
            })
        return result

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口 - 自动清理"""
        self.stop_all()


# 便捷函数 - 快速使用
def quick_fetch(url: str, headless: bool = True) -> Dict[str, Any]:
    """
    快速抓取网页 (token 高效)

    Args:
        url: 目标 URL
        headless: 是否无头模式

    Returns:
        包含 text 和 snapshot 的字典
    """
    with PinchTabAdapter() as adapter:
        instance = adapter.create_instance("quick", headless)
        instance.navigate(url)
        time.sleep(2)  # 等待页面加载

        return {
            "text": instance.text(),
            "snapshot": instance.snapshot(),
            "url": url
        }


# CLI 测试入口
if __name__ == "__main__":
    print("=== PinchTab 适配器测试 ===\n")

    # 测试 1: 创建实例
    print("1. 创建实例...")
    adapter = PinchTabAdapter()

    # 测试 2: 启动多个实例
    print("\n2. 启动多个实例...")
    instance1 = adapter.create_instance("test1", headless=True)
    instance2 = adapter.create_instance("test2", headless=True, port=9868)

    # 测试 3: 导航
    print("\n3. 导航测试...")
    result1 = instance1.navigate("https://example.com")
    print(f"实例 1 导航: {result1.get('title', 'N/A')}")

    result2 = instance2.navigate("https://www.google.com")
    print(f"实例 2 导航: {result2.get('title', 'N/A')}")

    # 测试 4: 快照
    print("\n4. 快照测试...")
    time.sleep(2)
    snap1 = instance1.snapshot(interactive=True, compact=True)
    print(f"实例 1 快照: {snap1.get('count', 0)} 个节点")

    # 测试 5: 文本提取
    print("\n5. 文本提取测试...")
    text1 = instance1.text()
    print(f"实例 1 文本: {text1.get('text', '')[:100]}...")

    # 测试 6: 列出实例
    print("\n6. 实例列表...")
    for info in adapter.list_instances():
        print(f"  - {info['name']}: 端口 {info['port']}, 状态 {info['status']}")

    # 清理
    print("\n7. 清理...")
    adapter.stop_all()
    print("✓ 测试完成")
