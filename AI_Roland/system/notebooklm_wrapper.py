"""
NotebookLM 编码修复包装器
解决 Windows 中文乱码问题
"""

import subprocess
import sys
import os
from pathlib import Path

# 强制 UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    os.environ['PYTHONIOENCODING'] = 'utf-8'


class NotebookLMEncoder:
    """NotebookLM 编码处理"""

    def __init__(self):
        self.cache_dir = Path("D:/ClaudeWork/AI_Roland/cache/notebooklm")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def run_command_safe(self, args: list) -> dict:
        """
        运行 notebooklm 命令，安全处理编码

        Args:
            args: 命令参数

        Returns:
            结果字典
        """
        try:
            # 设置环境变量
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'

            # 运行命令
            result = subprocess.run(
                ['notebooklm'] + args,
                capture_output=True,
                text=True,
                timeout=120,
                encoding='utf-8',
                errors='replace',  # 替换无法解码的字符
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            # 尝试修复输出中的乱码
            stdout = self._fix_encoding(result.stdout)
            stderr = self._fix_encoding(result.stderr)

            return {
                'success': result.returncode == 0,
                'stdout': stdout,
                'stderr': stderr,
                'returncode': result.returncode,
                'raw_stdout': result.stdout,
                'raw_stderr': result.stderr
            }

        except subprocess.TimeoutExpired:
            return {'success': False, 'error': '命令超时'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _fix_encoding(self, text: str) -> str:
        """
        修复文本编码问题

        Args:
            text: 原始文本

        Returns:
            修复后的文本
        """
        if not text:
            return text

        # 尝试常见的编码问题修复
        try:
            # 如果是乱码，尝试重新编码
            if '?' in text and len(text) > 10:
                # 可能是编码问题，返回清理后的版本
                # 移除连续的问号
                import re
                text = re.sub(r'\?{2,}', '', text)
                text = text.replace('?', '')

            return text

        except Exception:
            return text

    def ask_with_fallback(self, question: str, notebook_id: str = None) -> dict:
        """
        提问（带乱码处理）

        Args:
            question: 问题
            notebook_id: 笔记本ID

        Returns:
            结果字典
        """
        # 如果问题包含中文，提供英文版本作为备选
        import re

        has_chinese = bool(re.search(r'[\u4e00-\u9fff]', question))

        result = self.run_command_safe(['ask', question])

        if not result['success'] or has_chinese:
            # 检查输出是否包含大量乱码
            if result.get('stdout'):
                question_marks = result['stdout'].count('?')
                if question_marks > 20:  # 大量乱码
                    print("\n[检测] 发现乱码，使用英文查询...")
                    english_question = self._translate_to_english(question)
                    print(f"[英文查询] {english_question}")

                    result = self.run_command_safe(['ask', english_question])
                    result['original_question'] = question
                    result['english_question'] = english_question
                    result['used_english'] = True

        return result

    def _translate_to_english(self, chinese_text: str) -> str:
        """
        简单的中文到英文翻译（常见术语）

        Args:
            chinese_text: 中文文本

        Returns:
            英文文本
        """
        # 常见术语翻译表
        translations = {
            "如何": "How to",
            "什么": "What",
            "为什么": "Why",
            "怎么": "How",
            "使用": "Use",
            "功能": "Features",
            "配置": "Configuration",
            "系统": "System",
            "文档": "Documentation",
            "笔记": "Note",
            "记忆": "Memory",
            "历史": "History",
            "对话": "Conversation",
            "任务": "Task",
            "清单": "List",
            "指南": "Guide",
            "核心": "Core",
            "主要": "Main",
            "关键": "Key",
            "重要": "Important",
            "浏览器": "Browser",
            "控制器": "Controller",
            "自动化": "Automation",
            "第二大脑": "Second Brain",
            "知识": "Knowledge",
            "管理": "Management",
            "查询": "Query",
            "搜索": "Search",
            "同步": "Sync"
        }

        # 简单替换
        result = chinese_text
        for cn, en in translations.items():
            result = result.replace(cn, en)

        return result

    def get_clean_output(self, result: dict) -> str:
        """
        获取清理后的输出

        Args:
            result: run_command_safe 的结果

        Returns:
            清理后的文本
        """
        if not result.get('success'):
            return result.get('error', 'Unknown error')

        output = result.get('stdout', '')

        # 提取 Answer 部分
        if 'Answer:' in output:
            answer = output.split('Answer:')[1]
            if 'Conversation:' in answer:
                answer = answer.split('Conversation:')[0]

            # 清理乱码
            answer = self._fix_encoding(answer.strip())

            return answer

        return output


def demo_safe_query():
    """演示安全的查询方式"""
    encoder = NotebookLMEncoder()

    print("="*60)
    print("NotebookLM 中文乱码修复演示")
    print("="*60)

    # 测试中文查询
    print("\n[测试] 中文查询...")
    result = encoder.ask_with_fallback("AI Roland 的核心功能有哪些？")

    if result['success']:
        clean_output = encoder.get_clean_output(result)

        print("\n[回答] （前500字符）:")
        print(clean_output[:500] + "..." if len(clean_output) > 500 else clean_output)

        if result.get('used_english'):
            print("\n[提示] 由于编码问题，使用了英文查询")
            print(f"[英文问题] {result['english_question']}")

    # 保存结果
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    result_file = encoder.cache_dir / f"query_result_{timestamp}.txt"

    with open(result_file, 'w', encoding='utf-8') as f:
        f.write(f"问题: {result.get('original_question', 'N/A')}\n")
        f.write(f"回答:\n{clean_output}\n")

    print(f"\n[保存] 结果已保存: {result_file}")


def main():
    """命令行接口"""
    import sys

    if len(sys.argv) < 2:
        print("NotebookLM 编码修复工具")
        print("\n用法:")
        print("  python notebooklm_wrapper.py demo           # 演示安全查询")
        print("  python notebooklm_wrapper.py ask <问题>    # 安全提问")
        print("  python notebooklm_wrapper.py list           # 列出笔记本")
        print("  python notebooklm_wrapper.py status         # 查看状态")
        return

    command = sys.argv[1]
    encoder = NotebookLMEncoder()

    if command == 'demo':
        demo_safe_query()

    elif command == 'ask':
        if len(sys.argv) < 3:
            print("用法: python notebooklm_wrapper.py ask <问题>")
            return

        question = ' '.join(sys.argv[2:])
        result = encoder.ask_with_fallback(question)

        if result['success']:
            clean_output = encoder.get_clean_output(result)
            print(f"\n[回答]:\n{clean_output}")
        else:
            print(f"[错误] {result.get('error')}")

    elif command == 'list':
        result = encoder.run_command_safe(['list'])
        if result['success']:
            # 尝试清理输出
            output = encoder._fix_encoding(result['stdout'])
            print(f"\n{output}")
        else:
            print(f"[错误] {result.get('error')}")

    elif command == 'status':
        print("\n[系统状态]")
        print(f"编码: UTF-8")
        print(f"缓存目录: {encoder.cache_dir}")
        print(f"Python版本: {sys.version}")
        print(f"平台: {sys.platform}")


if __name__ == "__main__":
    from datetime import datetime
    main()
