"""
NotebookLM 集成 Skill
将 NotebookLM 与本地 AI 结合，实现混合智能工作流
"""

import subprocess
import json
import os
from pathlib import Path
from datetime import datetime


class NotebookLMSkill:
    """NotebookLM 集成技能"""

    def __init__(self):
        self.workspace = Path(__file__).parent.parent.parent
        self.cache_dir = self.workspace / "cache" / "notebooklm"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def run_command(self, args):
        """运行 notebooklm 命令"""
        try:
            result = subprocess.run(
                ['notebooklm'] + args,
                capture_output=True,
                text=True,
                timeout=120,
                encoding='utf-8',
                errors='replace'
            )
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Command timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def list_notebooks(self):
        """列出所有笔记本"""
        result = self.run_command(['list'])
        if result['success']:
            return self._parse_notebooks(result['stdout'])
        return []

    def _parse_notebooks(self, output):
        """解析笔记本列表输出"""
        notebooks = []
        lines = output.split('\n')
        for line in lines:
            if '|' in line and 'ID' not in line and '----' not in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 4 and parts[0]:
                    notebooks.append({
                        'id': parts[0][:20],  # 截取前20字符
                        'title': parts[1] if len(parts) > 1 else '',
                        'owner': parts[2] if len(parts) > 2 else '',
                        'created': parts[3] if len(parts) > 3 else ''
                    })
        return notebooks

    def use_notebook(self, notebook_id):
        """选择笔记本"""
        result = self.run_command(['use', notebook_id])
        return result['success']

    def ask(self, question, notebook_id=None):
        """向笔记本提问"""
        if notebook_id:
            self.use_notebook(notebook_id)

        result = self.run_command(['ask', question])
        if result['success']:
            return self._parse_answer(result['stdout'])
        return None

    def _parse_answer(self, output):
        """解析回答"""
        # 提取 Answer 后的内容
        if 'Answer:' in output:
            parts = output.split('Answer:', 1)
            if len(parts) > 1:
                answer = parts[1].strip()
                # 移除 Conversation 信息
                if 'Conversation:' in answer:
                    answer = answer.split('Conversation:')[0].strip()
                return answer
        return output

    def create_notebook(self, title):
        """创建新笔记本"""
        result = self.run_command(['create', title])
        return result['success']

    def add_source(self, source_path):
        """添加源文档"""
        result = self.run_command(['source', 'add', source_path])
        return result['success']

    def generate(self, artifact_type):
        """生成内容"""
        result = self.run_command(['generate', artifact_type])
        return result['success'], result.get('stdout', '')

    def summary(self):
        """生成摘要"""
        return self.generate('summary')

    def analyze_with_local_ai(self, notebook_id, question):
        """
        混合分析：NotebookLM + 本地 AI

        工作流：
        1. NotebookLM 分析文档并回答
        2. 本地 AI 进一步处理和提炼
        3. 返回综合结果
        """
        # Step 1: 从 NotebookLM 获取基础信息
        notebooklm_answer = self.ask(question, notebook_id)

        # Step 2: 构建提示词，让本地 AI 进行进一步分析
        prompt = f"""基于以下 NotebookLM 的分析结果，请进行进一步分析和提炼：

**问题**：{question}

**NotebookLM 的回答**：
{notebooklm_answer}

请完成以下任务：
1. 总结核心要点（3-5条）
2. 提取关键洞察
3. 识别可能的后续问题或研究方向
4. 如果有信息缺失，指出需要补充的内容

**输出格式**：
```markdown
## 核心要点
1. ...

## 关键洞察
...

## 后续方向
...

## 信息缺口
...
```
"""
        return prompt

    def collaborative_analysis(self, notebook_id, questions):
        """
        协作分析：多轮交互

        1. NotebookLM 回答初始问题
        2. 本地 AI 生成追问
        3. NotebookLM 回答追问
        4. 本地 AI 综合并提炼最终结论
        """
        results = []

        for i, question in enumerate(questions):
            # NotebookLM 回答
            answer = self.ask(question, notebook_id)
            results.append({
                'question': question,
                'notebooklm_answer': answer,
                'round': i + 1
            })

            # 本地 AI 生成追问（最后一轮不追问）
            if i < len(questions) - 1:
                follow_up_prompt = f"""基于以下问答，生成1-2个有价值的追问：

**问题**：{question}
**回答**：{answer}

请生成追问（直接输出追问内容，每行一个）：
"""
                results[-1]['follow_up_prompt'] = follow_up_prompt

        return results

    def document_workflow(self, files, analysis_type='research'):
        """
        文档分析工作流

        Args:
            files: 文件路径列表
            analysis_type: 分析类型 ('research', 'code', 'legal', 'creative')

        Returns:
            工作流执行结果
        """
        workflow = {
            'start_time': datetime.now().isoformat(),
            'files': files,
            'type': analysis_type,
            'steps': []
        }

        # Step 1: 创建笔记本
        notebook_title = f"{analysis_type.capitalize()} Analysis {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if self.create_notebook(notebook_title):
            workflow['steps'].append({'step': 1, 'action': 'create_notebook', 'status': 'success', 'title': notebook_title})
        else:
            return {'error': 'Failed to create notebook'}

        # Step 2: 添加源文档
        for file in files:
            if self.add_source(file):
                workflow['steps'].append({'step': 2, 'action': 'add_source', 'file': file, 'status': 'success'})
            else:
                workflow['steps'].append({'step': 2, 'action': 'add_source', 'file': file, 'status': 'failed'})

        # Step 3: 根据类型生成不同的分析
        analysis_prompts = {
            'research': [
                "总结这些文档的核心研究问题和发现",
                "比较文档中使用的方法论",
                "识别研究中的共同主题和差异",
                "指出研究中的局限性或未来方向"
            ],
            'code': [
                "解释这个项目的核心架构",
                "列出主要的模块和它们的职责",
                "识别关键算法和数据流",
                "指出代码中的设计模式"
            ],
            'legal': [
                "列出所有关键条款和条件",
                "识别潜在的法律风险",
                "总结各方的权利和义务",
                "指出需要澄清的模糊条款"
            ],
            'creative': [
                "总结这些材料的核心主题",
                "提取可用于创作的关键元素",
                "识别潜在的叙事线索",
                "建议创作方向和角度"
            ]
        }

        prompts = analysis_prompts.get(analysis_type, analysis_prompts['research'])

        # Step 4: 执行分析
        for i, prompt in enumerate(prompts):
            answer = self.ask(prompt)
            workflow['steps'].append({
                'step': 4,
                'action': 'analyze',
                'question': prompt,
                'answer': answer,
                'round': i + 1
            })

        # Step 5: 生成总结
        success, summary = self.summary()
        workflow['steps'].append({'step': 5, 'action': 'summary', 'content': summary})

        workflow['end_time'] = datetime.now().isoformat()

        # 保存工作流结果
        workflow_file = self.cache_dir / f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(workflow_file, 'w', encoding='utf-8') as f:
            json.dump(workflow, f, ensure_ascii=False, indent=2)

        return workflow

    def smart_research(self, topic, files=None):
        """
        智能研究助手

        结合 NotebookLM 的文档理解能力和本地 AI 的推理能力
        """
        result = {
            'topic': topic,
            'files': files or [],
            'timestamp': datetime.now().isoformat(),
            'phases': []
        }

        # Phase 1: 创建研究笔记本
        title = f"Research: {topic}"
        self.create_notebook(title)
        result['phases'].append({'phase': 1, 'action': 'create_notebook', 'title': title})

        # Phase 2: 添加文档（如果有）
        if files:
            for file in files:
                self.add_source(file)
            result['phases'].append({'phase': 2, 'action': 'add_sources', 'count': len(files)})

        # Phase 3: 初始探索问题
        exploration_questions = [
            f"关于 {topic} 的核心概念有哪些？",
            f"这个领域的主要挑战是什么？",
            f"有哪些重要的理论或方法？"
        ]

        exploration_results = []
        for q in exploration_questions:
            answer = self.ask(q)
            exploration_results.append({'question': q, 'answer': answer})

        result['phases'].append({'phase': 3, 'action': 'exploration', 'results': exploration_results})

        # Phase 4: 深入分析（由本地 AI 完成）
        deep_analysis_prompt = self.analyze_with_local_ai(
            None,
            f"对 {topic} 进行深入分析，整合多维度的视角"
        )

        result['phases'].append({
            'phase': 4,
            'action': 'deep_analysis',
            'local_ai_prompt': deep_analysis_prompt
        })

        # Phase 5: 生成研究摘要
        success, summary = self.summary()
        result['phases'].append({'phase': 5, 'action': 'summary', 'content': summary})

        return result


# CLI 接口
def main():
    """命令行接口"""
    import sys

    skill = NotebookLMSkill()

    if len(sys.argv) < 2:
        print("NotebookLM Skill - 集成本地 AI")
        print("\n用法:")
        print("  python notebooklm_skill.py list                    # 列出笔记本")
        print("  python notebooklm_skill.py ask <notebook-id> <question>  # 提问")
        print("  python notebooklm_skill.py workflow <files> <type> # 文档分析工作流")
        print("  python notebooklm_skill.py research <topic>        # 智能研究")
        return

    command = sys.argv[1]

    if command == 'list':
        notebooks = skill.list_notebooks()
        print("\n笔记本列表:")
        for nb in notebooks:
            print(f"  - {nb['id'][:16]}... | {nb['title']}")

    elif command == 'ask':
        if len(sys.argv) < 4:
            print("用法: python notebooklm_skill.py ask <notebook-id> <question>")
            return
        notebook_id = sys.argv[2]
        question = ' '.join(sys.argv[3:])
        answer = skill.ask(notebook_id, question)
        print(f"\n问题: {question}")
        print(f"\n回答:\n{answer}")

    elif command == 'hybrid':
        """混合分析：NotebookLM + 本地 AI"""
        if len(sys.argv) < 4:
            print("用法: python notebooklm_skill.py hybrid <notebook-id> <question>")
            return
        notebook_id = sys.argv[2]
        question = ' '.join(sys.argv[3:])

        # 获取 NotebookLM 回答
        notebooklm_answer = skill.ask(notebook_id, question)

        # 生成本地 AI 提示词
        local_ai_prompt = skill.analyze_with_local_ai(notebook_id, question)

        print(f"\n=== 混合分析模式 ===")
        print(f"\nNotebookLM 回答:\n{notebooklm_answer}")
        print(f"\n本地 AI 提示词:\n{local_ai_prompt}")
        print(f"\n提示: 请将上述提示词提供给本地 AI 进行进一步分析")

    elif command == 'workflow':
        """文档分析工作流"""
        if len(sys.argv) < 4:
            print("用法: python notebooklm_skill.py workflow <file1,file2,...> <type>")
            print("类型: research, code, legal, creative")
            return
        files = sys.argv[2].split(',')
        analysis_type = sys.argv[3]

        print(f"\n=== 文档分析工作流 ===")
        print(f"文件: {len(files)} 个")
        print(f"类型: {analysis_type}")
        print(f"开始分析...\n")

        result = skill.document_workflow(files, analysis_type)

        print(f"工作流完成!")
        print(f"步骤数: {len(result['steps'])}")
        print(f"详情: {result.get('steps', [])}")

    elif command == 'research':
        """智能研究助手"""
        if len(sys.argv) < 3:
            print("用法: python notebooklm_skill.py research <topic>")
            return
        topic = ' '.join(sys.argv[2:])

        print(f"\n=== 智能研究助手 ===")
        print(f"主题: {topic}\n")

        result = skill.smart_research(topic)
        print(f"研究完成!")
        print(f"阶段数: {len(result['phases'])}")

    else:
        print(f"未知命令: {command}")


if __name__ == "__main__":
    main()
