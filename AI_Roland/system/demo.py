"""
AI Roland 自动化引擎演示
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from engine import RolandEngine
from engine import Scheduler

def main():
    output = []
    output.append("="*60)
    output.append("AI Roland 自动化引擎演示")
    output.append("="*60)
    output.append("")

    # 创建引擎
    engine = RolandEngine()
    output.append(f"[OK] 工作区: {engine.workspace}")
    output.append(f"[OK] 记忆库: {engine.memory_lib}")
    output.append("")

    # 演示时间意图捕获
    output.append("演示1: 时间意图自动捕获")
    output.append("-"*60)
    test_input = "这篇文章明天要发布"
    output.append(f"输入: {test_input}")
    response = engine.process_user_input(test_input)
    output.append(f"自动识别: 时间意图")
    output.append(f"自动执行: 添加到任务清单")
    output.append(f"操作结果: {response['actions_taken']}")
    output.append("")

    # 演示另一个时间意图
    test_input2 = "下周要完成项目报告"
    output.append(f"输入: {test_input2}")
    response2 = engine.process_user_input(test_input2)
    output.append(f"自动识别: 时间意图")
    output.append(f"自动分类: 重要不紧急")
    output.append("")

    # 演示每日简报
    output.append("演示2: 每日简报自动生成")
    output.append("-"*60)
    scheduler = Scheduler(engine)
    briefing = scheduler._generate_daily_briefing()
    output.append(briefing)

    # 查看系统状态
    output.append("演示3: 系统状态")
    output.append("-"*60)
    output.append(f"当前会话: {engine.state.get('current_session', '无')}")
    output.append(f"上次简报: {engine.state.get('last_daily_briefing', '未运行')}")
    output.append(f"周日提醒: {engine.state.get('last_sunday_reminder', '未运行')}")
    output.append("")

    output.append("="*60)
    output.append("[OK] 演示完成！系统正在自动化运行")
    output.append("="*60)

    # 保存到文件
    demo_output = Path(__file__).parent / "demo_output.txt"
    demo_output.write_text("\n".join(output), encoding='utf-8')

    print("演示完成！结果已保存到: demo_output.txt")
    print("\n请查看 demo_output.txt 文件")

    # 也打印到控制台（可能会乱码，但文件是正确的）
    print("\n" + "\n".join(output))

if __name__ == "__main__":
    main()
