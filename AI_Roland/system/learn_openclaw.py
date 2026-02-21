"""
OpenClaw 文档系统学习工作流
使用 AI Roland x NotebookLM 自动化系统学习
"""

import sys
import os
from pathlib import Path

from ai_roland_notebook import AIRolandKnowledgeManager
from datetime import datetime
import time


class OpenClawLearningWorkflow:
    """OpenClaw 系统学习工作流"""

    def __init__(self):
        self.manager = AIRolandKnowledgeManager()
        self.base_url = "https://docs.openclaw.ai"

    def step1_discover_sitemap(self):
        """步骤1：发现并抓取 sitemap"""
        print("\n" + "="*60)
        print("步骤 1/5：发现并抓取 Sitemap")
        print("="*60)

        urls = self.manager.discover_and_fetch_sitemap(self.base_url)

        if not urls:
            print("[错误] 未能找到 sitemap")
            return []

        print(f"\n[成功] 发现 {len(urls)} 个文档")
        print(f"[来源] {self.base_url}")

        # 保存 URL 列表
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        url_file = self.manager.cache_dir / f"openclaw_urls_{timestamp}.txt"
        url_file.parent.mkdir(parents=True, exist_ok=True)

        with open(url_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(urls))

        print(f"[保存] URL 列表: {url_file}")

        return urls

    def step2_create_notebook(self):
        """步骤2：创建 OpenClaw 学习知识库"""
        print("\n" + "="*60)
        print("步骤 2/5：创建 OpenClaw 学习知识库")
        print("="*60)

        notebook_name = f"OpenClaw 文档学习_{datetime.now().strftime('%Y%m%d')}"
        notebook_id = self.manager.create_knowledge_base(notebook_name)

        if notebook_id:
            print(f"\n[成功] 知识库创建成功")
            print(f"[名称] {notebook_name}")
            print(f"[ID] {notebook_id}")
            return notebook_id

        print(f"\n[失败] 创建知识库失败")
        return None

    def step3_batch_import(self, notebook_id, urls):
        """步骤3：批量导入文档"""
        print("\n" + "="*60)
        print("步骤 3/5：批量导入文档到 NotebookLM")
        print("="*60)

        print(f"\n[导入] 准备导入 {len(urls)} 个文档...")

        # 由于文档数量可能很多，先导入前20个作为演示
        demo_urls = urls[:20]

        results = self.manager.batch_add_sources(demo_urls, delay=3.0)

        print(f"\n[导入完成]")
        print(f"  成功: {results.get('success', 0)}")
        print(f"  跳过: {results.get('skipped', 0)}")
        print(f"  失败: {results.get('failed', 0)}")

        return results

    def step4_learning_questions(self, notebook_id):
        """步骤4：自动学习核心概念"""
        print("\n" + "="*60)
        print("步骤 4/5：自动学习核心概念")
        print("="*60)

        learning_questions = [
            "OpenClaw 的核心功能是什么？",
            "如何安装和配置 OpenClaw？",
            "什么是 Gateway？如何启动？",
            "如何配置 channels（通道）？",
            "Skills 系统如何工作？",
            "如何配置 Hooks？",
            "OpenClaw 支持哪些聊天应用？",
            "如何通过 API 控制 OpenClaw？",
            "Dashboard 如何使用？",
            "OpenClaw 的最佳实践是什么？"
        ]

        print(f"\n[学习] {len(learning_questions)} 个核心问题")
        print("-"*60)

        answers = []
        for i, question in enumerate(learning_questions, 1):
            print(f"\n[{i}/{len(learning_questions)}] {question}")

            # 使用英文查询避免乱码
            english_question = self._translate_to_english(question)
            result = self.manager.run_notebooklm(['ask', english_question], timeout=120)

            if result['success']:
                output = result['stdout']
                if 'Answer:' in output:
                    answer = output.split('Answer:')[1].split('Conversation:')[0].strip()
                    # 简短显示
                    short_answer = answer[:200] + "..." if len(answer) > 200 else answer
                    print(f"[回答] {short_answer}")
                    answers.append({
                        'question': question,
                        'answer': short_answer
                    })
                else:
                    print("[回答] 未能提取回答")
            else:
                print(f"[错误] {result.get('stderr', '未知错误')}")

            time.sleep(2)

        return answers

    def step5_generate_resources(self, notebook_id):
        """步骤5：生成学习资源"""
        print("\n" + "="*60)
        print("步骤 5/5：生成学习资源")
        print("="*60)

        print("\n[生成] 学习指南...")

        result = self.manager.run_notebooklm(['summary'], timeout=180)

        if result['success']:
            print("[成功] 学习指南已生成")
            print("\n[其他可用资源]")
            print("  - 播客式音频概述")
            print("  - 思维导图")
            print("  - 演示文稿")
            print("  - 测验题")
        else:
            print(f"[错误] {result.get('stderr', '未知错误')}")

        return result

    def _translate_to_english(self, chinese_question: str) -> str:
        """中文问题转英文"""
        translations = {
            "OpenClaw 的核心功能是什么？": "What are the core features of OpenClaw?",
            "如何安装和配置 OpenClaw？": "How to install and configure OpenClaw?",
            "什么是 Gateway？如何启动？": "What is Gateway and how to start it?",
            "如何配置 channels（通道）？": "How to configure channels?",
            "Skills 系统如何工作？": "How does the Skills system work?",
            "如何配置 Hooks？": "How to configure Hooks?",
            "OpenClaw 支持哪些聊天应用？": "What chat apps does OpenClaw support?",
            "如何通过 API 控制 OpenClaw？": "How to control OpenClaw via API?",
            "Dashboard 如何使用？": "How to use the Dashboard?",
            "OpenClaw 的最佳实践是什么？": "What are the best practices for OpenClaw?"
        }
        return translations.get(chinese_question, chinese_question)

    def run_full_workflow(self):
        """运行完整工作流"""
        print("\n" + "="*70)
        print("OpenClaw 系统学习 - 完整自动化流程")
        print("="*70)
        print(f"[目标] 系统学习 OpenClaw 文档")
        print(f"[来源] {self.base_url}")
        print(f"[时间] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)

        # Step 1: 发现 sitemap
        urls = self.step1_discover_sitemap()
        if not urls:
            return

        # Step 2: 创建知识库
        notebook_id = self.step2_create_notebook()
        if not notebook_id:
            return

        # Step 3: 批量导入
        self.step3_batch_import(notebook_id, urls)

        # Step 4: 自动学习
        answers = self.step4_learning_questions(notebook_id)

        # Step 5: 生成资源
        self.step5_generate_resources(notebook_id)

        # 最终总结
        print("\n" + "="*70)
        print("学习完成！")
        print("="*70)
        print(f"[知识库] Notebook ID: {notebook_id}")
        print(f"[文档数] 已导入 {min(20, len(urls))} 个文档（演示）")
        print(f"[问题数] 已回答 {len(answers)} 个核心问题")
        print(f"\n[下一步]")
        print(f"  1. 继续提问：python AI_Roland/system/notebooklm_wrapper.py ask '你的问题'")
        print(f"  2. 生成更多资源：python AI_Roland/system/notebooklm_wrapper.py generate audio")
        print(f"  3. 查看 notebook: https://notebooklm.google.com")
        print("="*70)


def main():
    """主函数"""
    workflow = OpenClawLearningWorkflow()

    try:
        workflow.run_full_workflow()
    except KeyboardInterrupt:
        print("\n\n[中断] 用户取消")
    except Exception as e:
        print(f"\n[错误] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
