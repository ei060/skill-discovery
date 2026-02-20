"""
AI Roland - Claude 会话集成版
只在启动 Claude 时运行，随会话结束而停止
"""

import sys
import os
import time
import json
import logging
from datetime import datetime
from pathlib import Path
from threading import Thread

# 添加system目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class ClaudeIntegratedRoland:
    """与 Claude 会话集成的 AI Roland"""

    def __init__(self, session_id=None):
        # 设置路径
        self.system_dir = Path(__file__).parent
        self.workspace = self.system_dir.parent
        self.log_dir = self.workspace / "logs"
        self.log_dir.mkdir(exist_ok=True)

        # 会话ID
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")

        # 设置日志
        log_file = self.log_dir / f"claude_session_{self.session_id}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8')
            ]
        )
        self.logger = logging.getLogger(__name__)

        # 导入引擎
        from engine import RolandEngine
        self.engine = RolandEngine()

        # 设置会话状态
        self.engine.state["claude_session"] = self.session_id
        self.engine.state["claude_bound"] = True
        self.engine.save_state()

        self.running = False
        self.threads = []

        self.logger.info("="*60)
        self.logger.info(f"Claude 会话集成版启动 - Session: {self.session_id}")
        self.logger.info("="*60)

    def start(self):
        """启动（仅在 Claude 会话中运行）"""
        self.running = True

        # 启动轻量级监控线程
        monitor_thread = Thread(target=self._monitor_loop, daemon=True)
        monitor_thread.start()
        self.threads.append(monitor_thread)

        self.logger.info("[OK] Claude 集成模式已启动")
        self.logger.info("      - 随 Claude 会话运行")
        self.logger.info("      - 会话结束时自动停止")

        return {
            "status": "running",
            "session": self.session_id,
            "mode": "claude_integrated"
        }

    def stop(self):
        """停止（Claude 会话结束时）"""
        self.running = False

        # 更新状态
        self.engine.state["claude_session"] = None
        self.engine.state["claude_bound"] = False
        self.engine.state["last_session_end"] = datetime.now().isoformat()
        self.engine.save_state()

        self.logger.info(f"[STOP] Claude 会话结束 - Session: {self.session_id}")
        self.logger.info("="*60)

    def _monitor_loop(self):
        """轻量级监控循环"""
        while self.running:
            try:
                # 每5分钟记录一次状态
                self.engine.state["heartbeat_count"] = self.engine.state.get("heartbeat_count", 0) + 1
                self.engine.state["last_heartbeat"] = datetime.now().isoformat()
                self.engine.save_state()

                time.sleep(300)  # 5分钟

            except Exception as e:
                self.logger.error(f"[ERROR] {e}")

    def process(self, user_input):
        """处理用户输入（由 Claude 调用）"""
        try:
            response = self.engine.process_user_input(user_input)

            self.logger.info(f"[Input] {user_input[:100]}")
            if response.get("messages"):
                for msg in response["messages"]:
                    self.logger.info(f"[Response] {msg}")

            return response

        except Exception as e:
            self.logger.error(f"[ERROR] {e}")
            return {"error": str(e)}

    def get_status(self):
        """获取状态"""
        return {
            "session": self.session_id,
            "running": self.running,
            "workspace": str(self.workspace),
            "heartbeat_count": self.engine.state.get("heartbeat_count", 0),
            "last_heartbeat": self.engine.state.get("last_heartbeat")
        }


# 全局实例
_claude_roland = None

def get_instance():
    """获取 Claude 集成实例（单例）"""
    global _claude_roland

    if _claude_roland is None:
        _claude_roland = ClaudeIntegratedRoland()
        _claude_roland.start()

    return _claude_roland


def process_input(user_input):
    """处理输入的便捷函数"""
    roland = get_instance()
    return roland.process(user_input)


def get_status():
    """获取状态的便捷函数"""
    roland = get_instance()
    return roland.get_status()


def cleanup():
    """清理函数（会话结束时调用）"""
    global _claude_roland

    if _claude_roland is not None:
        _claude_roland.stop()
        _claude_roland = None


# 当模块被导入时自动启动
if __name__ != "__main__":
    # 在 Claude 环境中自动启动
    roland = get_instance()
    print(f"[AI Roland] Claude 集成模式已启动 (Session: {roland.session_id})")
