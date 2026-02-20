"""
简单测试脚本 - 验证引擎是否正常工作
"""

import sys
import os

# 添加system目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import RolandEngine

def test_engine():
    """测试引擎基本功能"""
    print("=" * 60)
    print("AI Roland Engine Test")
    print("=" * 60)
    print()

    # 创建引擎实例
    print("1. Creating engine...")
    engine = RolandEngine()
    print("   [OK] Engine created")
    print(f"   Workspace: {engine.workspace}")
    print()

    # 测试状态保存
    print("2. Testing state management...")
    engine.save_state()
    print("   [OK] State saved")
    print()

    # 测试意图识别
    print("3. Testing intent parser...")
    test_inputs = [
        "这篇文章明天要发布",
        "任务已经完成了",
        "帮我写一篇关于AI的文章"
    ]

    for test_input in test_inputs:
        print(f"   Input: {test_input}")
        response = engine.process_user_input(test_input)
        print(f"   Actions: {len(response['actions_taken'])}")
        print(f"   Messages: {response['messages']}")

    print()
    print("4. Testing scheduler...")
    from engine import Scheduler
    scheduler = Scheduler(engine)
    actions = scheduler.check_scheduled_tasks()
    print(f"   Scheduled actions: {len(actions)}")
    for action in actions:
        print(f"   - {action.get('action')}: {action.get('content', '')[:50]}...")

    print()
    print("=" * 60)
    print("All tests passed!")
    print("=" * 60)

if __name__ == "__main__":
    test_engine()
