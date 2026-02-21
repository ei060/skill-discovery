"""
AI Roland 的第二大脑系统
NotebookLM 作为 AI Roland 的外挂知识库
"""

import subprocess
import json
import sys
import os
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# UTF-8 设置
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    os.environ['PYTHONIOENCODING'] = 'utf-8'


class SecondBrain:
    """第二大脑系统"""

    def __init__(self, notebook_id: str = None):
        """
        初始化第二大脑

        Args:
            notebook_id: NotebookLM notebook ID
        """
        self.notebook_id = notebook_id or "6f279652"  # AI Roland 系统文档
        self.memory_dir = Path("D:/ClaudeWork/AI_Roland")
        self.query_history = []
        self.health_status = None
        self.fallback_mode = False

    def check_connection(self) -> bool:
        """
        检查 NotebookLM 连接健康状态

        Returns:
            True if connection is healthy
        """
        result = self.run_notebooklm(['list'], timeout=30)
        self.health_status = result['success']
        self.fallback_mode = not result['success']

        if not result['success']:
            print(f"[警告] NotebookLM 连接失败，切换到降级模式")
            print(f"[原因] {result.get('stderr', '未知错误')[:100]}")

        return result['success']

    def run_notebooklm(self, args: List[str], timeout: int = 120) -> Dict:
        """运行 notebooklm 命令"""
        try:
            result = subprocess.run(
                ['notebooklm'] + args,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='replace'
            )
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def query(self, question: str, context: str = "", retry: bool = True) -> Optional[str]:
        """
        向第二大脑提问

        Args:
            question: 问题
            context: 额外上下文
            retry: 是否在失败时重试

        Returns:
            回答内容
        """
        # 首次查询时检查连接
        if self.health_status is None:
            self.check_connection()

        # 如果处于降级模式，尝试本地搜索
        if self.fallback_mode:
            print(f"[降级模式] 使用本地记忆搜索")
            return self._local_fallback_search(question)

        # 使用当前 notebook
        full_question = f"{context}\n\n问题: {question}" if context else question

        print(f"\n[第二大脑] 查询中...")
        print(f"[问题] {question[:100]}...")

        result = self.run_notebooklm(['ask', full_question], timeout=180)

        if result['success']:
            # 提取回答
            output = result['stdout']
            if 'Answer:' in output:
                answer = output.split('Answer:')[1].split('Conversation:')[0].strip()

                # 记录查询历史
                self.query_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'question': question,
                    'context': context,
                    'answer': answer[:500] + "..." if len(answer) > 500 else answer,
                    'source': 'notebooklm'
                })

                return answer
            else:
                print(f"[警告] 未找到回答格式")
                return None

        # 连接失败，切换到降级模式
        print(f"[错误] NotebookLM 连接失败")
        if retry:
            print(f"[重试] 检查连接状态...")
            self.check_connection()
            if not self.fallback_mode:
                return self.query(question, context, retry=False)

        self.fallback_mode = True
        return self._local_fallback_search(question)

    def _local_fallback_search(self, question: str) -> Optional[str]:
        """
        降级模式：使用本地记忆搜索

        Args:
            question: 问题

        Returns:
            搜索结果
        """
        print(f"[本地搜索] 搜索相关记忆...")

        # 导入记忆搜索模块
        try:
            sys.path.insert(0, str(self.memory_dir / "system"))
            from memory_search import MemorySearch

            searcher = MemorySearch()
            results = searcher.search(question, top_k=3)

            if results:
                response = f"[本地记忆搜索结果]\n\n"
                for i, result in enumerate(results, 1):
                    response += f"{i}. {result['title']} (相似度: {result['similarity']:.2f})\n"
                    response += f"   {result['summary'][:150]}...\n\n"

                # 记录查询历史
                self.query_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'question': question,
                    'answer': response[:300],
                    'source': 'local_fallback'
                })

                return response
            else:
                return "[本地搜索] 未找到相关记忆"

        except Exception as e:
            print(f"[错误] 本地搜索失败: {e}")
            return None

    def search_memory(self, keywords: List[str]) -> List[str]:
        """
        搜索记忆中的相关内容

        Args:
            keywords: 关键词列表

        Returns:
            相关内容列表
        """
        # 构造搜索问题
        query = f"搜索包含以下关键词的内容: {', '.join(keywords)}"
        return self.query(query)

    def get_context(self, topic: str) -> Optional[str]:
        """
        获取特定主题的上下文

        Args:
            topic: 主题

        Returns:
            相关上下文
        """
        return self.query(f"关于'{topic}'的所有信息")

    def recall_decision(self, decision_description: str) -> Optional[str]:
        """
        回忆决策背景

        Args:
            decision_description: 决策描述

        Returns:
            决策背景信息
        """
        return self.query(
            f"关于'{decision_description}'这个决策",
            context="请提供决策的背景、理由、讨论过程和结果"
        )

    def suggest_questions(self, topic: str = None) -> List[str]:
        """
        建议应该问的问题

        Args:
            topic: 特定主题（可选）

        Returns:
            建议的问题列表
        """
        if topic:
            return [
                f"关于'{topic}'的核心概念是什么？",
                f"'{topic}'有哪些主要功能？",
                f"如何使用'{topic}'？",
                f"'{topic}'的最佳实践是什么？"
            ]
        else:
            return [
                "AI Roland 的核心功能有哪些？",
                "如何配置 AI Roland？",
                "对话历史如何管理？",
                "记忆系统如何工作？"
            ]


class AIRolandWithSecondBrain:
    """集成第二大脑的 AI Roland"""

    def __init__(self):
        self.second_brain = SecondBrain()
        self.local_memory = Path("D:/ClaudeWork/AI_Roland")

    def respond_with_memory(self, user_query: str) -> Dict:
        """
        结合第二大脑回答用户查询

        Args:
            user_query: 用户查询

        Returns:
            回答结果
        """
        print(f"\n{'='*60}")
        print(f"[AI Roland] 用户查询: {user_query}")
        print(f"{'='*60}")

        # Step 1: 查询第二大脑
        print(f"\n[Step 1] 查询第二大脑...")
        memory_answer = self.second_brain.query(user_query)

        if memory_answer:
            print(f"\n[第二大脑回答]:")
            print(f"{memory_answer[:300]}...")

        # Step 2: 本地处理
        print(f"\n[Step 2] 本地 AI 整合...")

        response = {
            'user_query': user_query,
            'memory_context': memory_answer,
            'local_ai_response': None,
            'timestamp': datetime.now().isoformat()
        }

        return response

    def setup_knowledge_bases(self) -> Dict:
        """
        设置专题知识库

        为不同主题创建独立的 notebook
        """
        knowledge_bases = {
            '系统文档': 'AI Roland 系统文档',
            '对话历史': 'AI Roland 对话历史',
            '技术方案': 'AI Roland 技术方案',
            '使用指南': 'AI Roland 使用指南'
        }

        print("\n[设置] 创建专题知识库")
        print("="*60)

        created = {}
        for name, title in knowledge_bases.items():
            print(f"\n[{name}] 创建: {title}")
            # 这里可以调用 notebooklm create
            created[name] = {'title': title, 'status': '待创建'}

        return created

    def sync_memory_to_second_brain(self) -> Dict:
        """
        同步记忆到第二大脑

        将 AI Roland 的对话历史、语义记忆等同步到 NotebookLM
        """
        print("\n[同步] 记忆到第二大脑")
        print("="*60)

        sync_results = {
            '对话历史': [],
            '语义记忆': [],
            '日记': [],
            'timestamp': datetime.now().isoformat()
        }

        # 1. 对话历史
        history_file = self.local_memory / "对话历史.md"
        if history_file.exists():
            print(f"\n[同步] 对话历史...")
            result = self.second_brain.run_notebooklm(
                ['source', 'add', str(history_file)]
            )
            sync_results['对话历史'].append({
                'file': str(history_file),
                'success': result['success']
            })

        # 2. 语义记忆
        memory_dir = self.local_memory / "记忆库" / "语义记忆"
        if memory_dir.exists():
            print(f"\n[同步] 语义记忆（最新的5个）...")
            memory_files = sorted(memory_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]
            for mem_file in memory_files:
                result = self.second_brain.run_notebooklm(['source', 'add', str(mem_file)])
                sync_results['语义记忆'].append({
                    'file': str(mem_file.name),
                    'success': result['success']
                })
                time.sleep(1)

        # 3. 日记
        diary_dir = self.local_memory / "日记"
        if diary_dir.exists():
            print(f"\n[同步] 日记（最新的5个）...")
            diary_files = sorted(diary_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]
            for diary_file in diary_files:
                result = self.second_brain.run_notebooklm(['source', 'add', str(diary_file)])
                sync_results['日记'].append({
                    'file': str(diary_file.name),
                    'success': result['success']
                })
                time.sleep(1)

        # 统计
        total_synced = sum(len(results) for results in sync_results.values() if isinstance(results, list))
        success_count = sum(sum(1 for r in results if r.get('success', False)) for results in sync_results.values() if isinstance(results, list))

        print(f"\n{'='*60}")
        print(f"[同步完成] 总计: {total_synced}, 成功: {success_count}")
        print(f"{'='*60}\n")

        return sync_results


def main():
    """演示第二大脑功能"""
    import sys

    if len(sys.argv) < 2:
        print("AI Roland 第二大脑系统")
        print("\n命令:")
        print("  python second_brain.py query <question>     # 查询第二大脑")
        print("  python second_brain.py search <keywords>    # 搜索记忆")
        print("  python second_brain.py recall <decision>    # 回忆决策")
        print("  python second_brain.py suggest              # 建议问题")
        print("  python second_brain.py sync                 # 同步记忆")
        return

    command = sys.argv[1]
    brain = AIRolandWithSecondBrain()

    if command == 'query':
        if len(sys.argv) < 3:
            print("用法: python second_brain.py query <question>")
            return
        question = ' '.join(sys.argv[2:])
        response = brain.respond_with_memory(question)
        print(f"\n[完整回答]:\n{response}")

    elif command == 'search':
        if len(sys.argv) < 3:
            print("用法: python second_brain.py search <keyword1,keyword2,...>")
            return
        keywords = sys.argv[2].split(',')
        results = brain.second_brain.search_memory(keywords)
        print(f"\n[搜索结果]:\n{results}")

    elif command == 'recall':
        if len(sys.argv) < 3:
            print("用法: python second_brain.py recall <decision_description>")
            return
        decision = ' '.join(sys.argv[2:])
        context = brain.second_brain.recall_decision(decision)
        print(f"\n[决策背景]:\n{context}")

    elif command == 'suggest':
        if len(sys.argv) >= 3:
            topic = sys.argv[2]
        else:
            topic = None
        questions = brain.second_brain.suggest_questions(topic)
        print(f"\n[建议问题]:")
        for i, q in enumerate(questions, 1):
            print(f"  {i}. {q}")

    elif command == 'sync':
        results = brain.sync_memory_to_second_brain()
        print(f"\n[同步结果]:\n{json.dumps(results, ensure_ascii=False, indent=2)}")


if __name__ == "__main__":
    main()
