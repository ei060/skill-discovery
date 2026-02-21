"""
NotebookLM 集成快速测试
验证混合智能工作流
"""

import sys
from pathlib import Path

# 添加路径
system_dir = Path(__file__).parent / "AI_Roland" / "system" / "skills"
sys.path.insert(0, str(system_dir))

from notebooklm_skill import NotebookLMSkill
from notebooklm_integration import NotebookLMIntegration


def test_basic_functionality():
    """测试基础功能"""
    print("="*60)
    print("测试 1：基础功能")
    print("="*60)

    skill = NotebookLMSkill()

    # 测试列出笔记本
    print("\n[测试] 列出笔记本...")
    notebooks = skill.list_notebooks()
    print(f"✓ 找到 {len(notebooks)} 个笔记本")
    for nb in notebooks[:3]:
        print(f"  - {nb['id'][:16]}... | {nb['title']}")

    return len(notebooks) > 0


def test_hybrid_analysis():
    """测试混合分析"""
    print("\n" + "="*60)
    print("测试 2：混合分析工作流")
    print("="*60)

    integration = NotebookLMIntegration()

    # 使用第一个笔记本进行测试
    notebooks = integration.execute_command('list', [])
    if not notebooks['success']:
        print("✗ 无法获取笔记本列表")
        return False

    # 提取第一个笔记本 ID
    lines = notebooks['output'].split('\n')
    notebook_id = None
    for line in lines:
        if '|' in line and 'ID' not in line and '---' not in line:
            parts = line.split('|')
            if parts[0].strip():
                notebook_id = parts[0].strip()[:20]
                break

    if not notebook_id:
        print("✗ 未找到可用笔记本")
        return False

    print(f"\n[测试] 使用笔记本: {notebook_id}")
    print("[测试] 生成混合分析提示词...")

    # 测试混合分析提示词生成
    prompt = integration.analyze_with_local_ai(
        notebook_id,
        "总结这个笔记本的核心内容"
    )

    print(f"✓ 生成了 {len(prompt)} 字符的提示词")
    print("\n[提示词预览]（前500字符）:")
    print(prompt[:500] + "...")

    return True


def test_integration_info():
    """测试集成信息"""
    print("\n" + "="*60)
    print("测试 3：集成信息")
    print("="*60)

    from notebooklm_integration import skill_info

    info = skill_info()

    print(f"\nSkill 名称: {info['name']}")
    print(f"描述: {info['description']}")
    print(f"版本: {info['version']}")
    print(f"\n能力:")

    for capability in info['capabilities']:
        print(f"  - {capability}")

    print(f"\n使用示例:")
    for method, desc in info['usage'].items():
        print(f"  {method}: {desc}")

    return True


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("NotebookLM 集成测试套件")
    print("="*60)

    results = []

    # 测试 1：基础功能
    try:
        results.append(("基础功能", test_basic_functionality()))
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        results.append(("基础功能", False))

    # 测试 2：混合分析
    try:
        results.append(("混合分析", test_hybrid_analysis()))
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        results.append(("混合分析", False))

    # 测试 3：集成信息
    try:
        results.append(("集成信息", test_integration_info()))
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        results.append(("集成信息", False))

    # 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")

    print(f"\n总计: {passed}/{total} 通过")

    if passed == total:
        print("\n🎉 所有测试通过！集成工作正常。")
        print("\n下一步:")
        print("  1. 查看 AI_Roland/记忆库/语义记忆/集成方案_NotebookLM与本地AI混合智能.md")
        print("  2. 尝试使用不同的工作流")
        print("  3. 根据需要扩展功能")
    else:
        print("\n⚠️ 部分测试失败，请检查配置。")


if __name__ == "__main__":
    main()
