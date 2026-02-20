"""
AI Roland v2.0 快速功能验证
"""

import sys
import os
from pathlib import Path

# 添加system目录到路径
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """测试导入"""
    print("=" * 70)
    print("AI Roland v2.0 快速验证")
    print("=" * 70)
    print()

    print("[1/5] 测试引擎导入...")
    try:
        from engine import RolandEngine
        print("       [OK] engine.RolandEngine 导入成功")
    except Exception as e:
        print(f"       [ERROR] {e}")
        return False

    print()
    print("[2/5] 创建引擎实例...")
    try:
        engine = RolandEngine()
        print(f"       [OK] 工作区: {engine.workspace}")
        print(f"       [OK] 记忆库: {engine.memory_lib}")
    except Exception as e:
        print(f"       [ERROR] {e}")
        return False

    print()
    print("[3/5] 测试意图识别...")
    try:
        from engine import IntentParser
        parser = IntentParser(engine)
        intents = parser.parse("这篇文章明天要发布")
        print(f"       [OK] 识别到意图: {list(intents.keys())}")
    except Exception as e:
        print(f"       [ERROR] {e}")
        return False

    print()
    print("[4/5] 测试任务管理...")
    try:
        from engine import TaskManager
        task_manager = TaskManager(engine)
        print("       [OK] TaskManager 初始化成功")
    except Exception as e:
        print(f"       [ERROR] {e}")
        return False

    print()
    print("[5/5] 测试文件路由...")
    try:
        from engine import FileRouter
        router = FileRouter(engine)
        print("       [OK] FileRouter 初始化成功")
    except Exception as e:
        print(f"       [ERROR] {e}")
        return False

    print()
    print("=" * 70)
    print("[OK] 所有核心模块导入成功！")
    print("=" * 70)
    print()
    print("核心功能已验证:")
    print("  [OK] 引擎创建")
    print("  [OK] 意图识别")
    print("  [OK] 任务管理")
    print("  [OK] 文件路由")
    print()
    print("新增功能 (v2.0):")
    print("  [Heartbeat] 自主思考循环")
    print("  [Cron] 灵活定时任务")
    print("  [Cognitive State] 认知状态追踪")
    print("  [Browser] 浏览器自动化")
    print("  [Telegram] 手机远程控制")
    print("  [HTTP API] RESTful 接口")
    print("  [MCP] 工具暴露")
    print()
    print("启动方式:")
    print("  python cli.py         - 启动 CLI (v1.0)")
    print("  python cli_v2.py      - 启动增强 CLI (v2.0)")
    print("  双击 start_all.bat    - 启动所有服务")
    print()

    return True

if __name__ == "__main__":
    try:
        success = test_imports()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
