#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI Roland Agent系统完整测试

验证所有子系统是否正常工作
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime, timezone

# 修复Windows编码
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

# 添加系统路径
system_path = Path(__file__).parent
sys.path.insert(0, str(system_path))


class TestRunner:
    """测试运行器"""

    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0

    def run_test(self, test_name: str, test_func):
        """运行单个测试"""
        self.total_tests += 1

        print(f"\n{'='*60}")
        print(f"测试 {self.total_tests}: {test_name}")
        print('='*60)

        try:
            test_func()
            self.passed_tests += 1
            self.results.append({
                'name': test_name,
                'status': 'PASS',
                'message': '测试通过'
            })
            print("✅ PASS")
        except Exception as e:
            self.failed_tests += 1
            self.results.append({
                'name': test_name,
                'status': 'FAIL',
                'message': str(e)
            })
            print(f"❌ FAIL: {str(e)}")

    def print_summary(self):
        """打印测试总结"""
        print(f"\n{'='*60}")
        print("测试总结")
        print('='*60)
        print(f"总测试数: {self.total_tests}")
        print(f"通过: {self.passed_tests} ✅")
        print(f"失败: {self.failed_tests} ❌")
        print(f"通过率: {(self.passed_tests/self.total_tests*100):.1f}%")

        if self.failed_tests > 0:
            print("\n失败的测试:")
            for result in self.results:
                if result['status'] == 'FAIL':
                    print(f"  ❌ {result['name']}: {result['message']}")

        print('='*60)


# ==================== 测试用例 ====================

def test_memory_system():
    """测试1: 记忆系统"""
    from agent_memory import get_agent_memory_manager

    mgr = get_agent_memory_manager()

    # 测试获取Agent记忆
    memory = mgr.get_agent_memory('code_reviewer')

    assert memory is not None, "无法获取Agent记忆"
    assert memory.agent_name == 'code_reviewer', "Agent名称不匹配"

    # 测试添加记忆
    memory.add_work_item({
        'type': 'test',
        'content': '测试记忆'
    })

    assert len(memory.working_memory) > 0, "无法添加工作记忆"

    # 测试搜索
    results = memory.search('测试')
    assert len(results) > 0, "搜索功能不工作"


def test_communication_system():
    """测试2: 协作通信系统"""
    from agent_communication import get_collaboration_hub, AgentCapability

    hub = get_collaboration_hub()

    # 测试能力注册
    cap = AgentCapability(
        agent_name='test_agent',
        agent_type='test',
        expertise=['testing'],
        capabilities=['test_execution'],
        skill_level=80
    )

    hub.register_capability(cap)

    assert 'test_agent' in hub.capabilities, "能力注册失败"

    # 测试统计
    stats = hub.get_statistics()
    assert stats['registered_agents'] > 0, "没有注册的Agent"


def test_active_participation():
    """测试3: 主动参与引擎"""
    from active_participation import get_active_participation_engine

    engine = get_active_participation_engine()

    # 测试分析用户输入
    test_input = "请帮我审查这段代码的安全性"
    report = engine.get_participation_report(test_input)

    assert 'total_suggestions' in report, "报告格式错误"
    assert 'recommendations' in report, "缺少推荐信息"

    # 验证至少有一个建议（因为包含"审查"和"安全"关键词）
    assert report['total_suggestions'] >= 1, "应该至少有一个建议"


def test_agent_orchestrator():
    """测试4: Agent编排器"""
    from agent_orchestrator import get_agent_orchestrator

    orchestrator = get_agent_orchestrator()

    # 测试咨询子Agent
    test_input = "我要设计一个新的API接口"
    result = orchestrator.consult_sub_agents(test_input)

    assert 'consultation_result' in result, "缺少咨询结果"
    assert len(result['consultation_result']) > 0, "咨询结果为空"


def test_consult_agents():
    """测试5: 便捷咨询工具"""
    import consult_agents

    # 测试简洁格式
    result_simple = consult_agents.consult_agents(
        "请帮我审查这段代码",
        format='simple'
    )

    assert len(result_simple) > 0, "简洁格式结果为空"

    # 测试JSON格式
    result_json = consult_agents.consult_agents(
        "请帮我审查这段代码",
        format='json'
    )

    data = json.loads(result_json)
    assert 'user_input' in data, "JSON格式错误"


def test_memory_injection_hook():
    """测试6: 记忆注入Hook"""
    hook_file = system_path / 'hooks' / 'inject_memory.py'

    assert hook_file.exists(), "记忆注入Hook不存在"

    # 测试Hook可执行
    import subprocess
    result = subprocess.run(
        [sys.executable, str(hook_file)],
        capture_output=True,
        text=True,
        timeout=5
    )

    # Hook应该能正常退出（即使没有实际注入）
    assert result.returncode == 0, f"Hook执行失败: {result.stderr}"


def test_smart_trigger():
    """测试7: 智能触发Hook"""
    from hooks.smart_trigger import should_trigger

    # 测试应该触发的情况
    assert should_trigger("请帮我审查这段代码的安全性") == True, "应该触发"
    assert should_trigger("我要设计一个新系统的架构") == True, "应该触发"

    # 测试不应该触发的情况
    assert should_trigger("读取文件") == False, "不应该触发"
    assert should_trigger("简单") == False, "不应该触发"


def test_integration():
    """测试8: 集成测试"""
    from consult_agents import consult_agents

    # 测试完整流程
    test_scenarios = [
        ("请帮我审查这段用户认证代码的安全性", "HIGH"),
        ("我要开发一个新的API功能", "MEDIUM"),
        ("读取config.yaml", "SIMPLE")
    ]

    for user_input, expected_type in test_scenarios:
        result = consult_agents(user_input, format='simple')

        if expected_type == "SIMPLE":
            assert "简单任务" in result or "直接处理" in result, \
                f"简单任务判断错误: {result}"
        else:
            assert "建议调用" in result or "建议使用" in result, \
                f"复杂任务判断错误: {result}"


def test_performance():
    """测试9: 性能测试"""
    import time
    from consult_agents import consult_agents

    # 测试响应时间
    start = time.time()
    result = consult_agents("请帮我审查这段代码的安全性", format='simple')
    elapsed = time.time() - start

    assert elapsed < 1.0, f"响应时间过长: {elapsed:.2f}秒"

    print(f"  ⚡ 响应时间: {elapsed*1000:.1f}ms")


def test_memory_persistence():
    """测试10: 记忆持久化"""
    from agent_memory import get_agent_memory_manager
    import tempfile

    mgr = get_agent_memory_manager()

    # 获取记忆
    memory = mgr.get_agent_memory('test_persistence')

    # 添加测试数据
    test_item = {
        'type': 'test',
        'content': '持久化测试',
        'timestamp': datetime.now(timezone.utc).isoformat()
    }

    memory.add_work_item(test_item)

    # 保存
    mgr._save_agent_memory('test_persistence')

    # 验证文件存在
    memory_file = system_path / 'memory' / 'test_persistence.json'
    assert memory_file.exists(), "记忆文件未保存"

    # 清理
    if memory_file.exists():
        memory_file.unlink()


# ==================== 主程序 ====================

def main():
    """主函数"""

    print("\n" + "="*60)
    print("AI Roland Agent系统完整测试")
    print("="*60)
    print(f"开始时间: {datetime.now(timezone.utc).isoformat()}")

    runner = TestRunner()

    # 运行所有测试
    runner.run_test("记忆系统", test_memory_system)
    runner.run_test("协作通信系统", test_communication_system)
    runner.run_test("主动参与引擎", test_active_participation)
    runner.run_test("Agent编排器", test_agent_orchestrator)
    runner.run_test("便捷咨询工具", test_consult_agents)
    runner.run_test("记忆注入Hook", test_memory_injection_hook)
    runner.run_test("智能触发Hook", test_smart_trigger)
    runner.run_test("集成测试", test_integration)
    runner.run_test("性能测试", test_performance)
    runner.run_test("记忆持久化", test_memory_persistence)

    # 打印总结
    runner.print_summary()

    # 保存测试结果
    results_file = system_path / 'test_results.json'
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'total_tests': runner.total_tests,
            'passed_tests': runner.passed_tests,
            'failed_tests': runner.failed_tests,
            'pass_rate': runner.passed_tests / runner.total_tests * 100,
            'results': runner.results
        }, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 测试结果已保存到: {results_file}")

    # 返回退出码
    sys.exit(0 if runner.failed_tests == 0 else 1)


if __name__ == "__main__":
    main()
