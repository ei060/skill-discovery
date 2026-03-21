"""
独立的 TodoWrite 冷启动验证脚本
在完全新的 Python 进程中运行
"""
import sys
sys.path.insert(0, "D:/ClaudeWork/AI_Roland/system")

from engine import RolandEngine
import json
from pathlib import Path

print("=" * 60)
print("TodoWrite 冷启动验证（独立进程）")
print("=" * 60)

# 验证1：文件检查
print("\n[验证1] 检查 current_task.json...")
state_file = Path("D:/ClaudeWork/AI_Roland/current_task.json")
with open(state_file, "r", encoding="utf-8") as f:
    data = json.load(f)

if "todos" in data and len(data["todos"]) >= 1:
    print(f"  [PASS] todos 字段存在，包含 {len(data['todos'])} 个任务")
    print(f"  [INFO] last_todo_update: {data.get('last_todo_update')}")
else:
    print("  [FAIL] todos 数据异常")
    sys.exit(1)

# 验证2：Engine 实例创建和读取
print("\n[验证2] 创建 RolandEngine 并读取...")
engine = RolandEngine()
todos = engine.get_todos()

if len(todos) >= 1:
    print(f"  [PASS] 成功读取 {len(todos)} 个任务")
    for i, t in enumerate(todos[:3]):
        print(f"    - 任务{i+1}: {t.get('subject')} ({t.get('status')})")
else:
    print("  [FAIL] 读取失败")
    sys.exit(1)

# 验证3：写入功能
print("\n[验证3] 测试写入功能...")
new_todos = [
    {"id": "cold-1", "subject": "冷启动验证-任务1", "status": "pending"},
    {"id": "cold-2", "subject": "冷启动验证-任务2", "status": "in_progress", "activeForm": "正在验证"},
    {"id": "cold-3", "subject": "冷启动验证-任务3", "status": "completed"}
]
result = engine.update_todos(new_todos)
if result:
    print("  [PASS] 写入成功")
else:
    print("  [FAIL] 写入失败")
    sys.exit(1)

# 验证4：重新读取验证
print("\n[验证4] 新实例重新读取...")
engine2 = RolandEngine()
todos2 = engine2.get_todos()
if len(todos2) == 3:
    print(f"  [PASS] 新实例成功读取 {len(todos2)} 个任务")
    for t in todos2:
        print(f"    - {t.get('subject')} ({t.get('status')})")
else:
    print(f"  [FAIL] 预期3个任务，实际{len(todos2)}个")
    sys.exit(1)

# 验证5：渲染功能
print("\n[验证5] 渲染功能...")
render = engine2.get_todos_render()
if "冷启动验证-任务1" in render and "⏳" in render:
    print("  [PASS] 渲染正常")
else:
    print("  [FAIL] 渲染异常")
    sys.exit(1)

print("\n" + "=" * 60)
print("[SUCCESS] 所有冷启动验证通过！")
print("=" * 60)
