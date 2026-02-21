"""
AI Roland x NotebookLM 深度集成系统
本地 AI 直接操作 NotebookLM，实现自动化知识管理
"""

import subprocess
import json
import time
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
import re

# 设置 UTF-8 输出（解决 Windows 中文乱码）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    os.environ['PYTHONIOENCODING'] = 'utf-8'


class AIRolandKnowledgeManager:
    """AI Roland 知识管理系统"""

    def __init__(self):
        self.cache_dir = Path("D:/ClaudeWork/AI_Roland/cache/knowledge")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.current_notebook = None

    def run_notebooklm(self, args: List[str], timeout: int = 60) -> Dict:
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
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': '命令超时'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ==================== Notebook 管理 ====================

    def create_knowledge_base(self, name: str) -> Optional[str]:
        """
        创建知识库（notebook）

        Args:
            name: 知识库名称

        Returns:
            notebook ID
        """
        print(f"\n[创建] 知识库: {name}")
        result = self.run_notebooklm(['create', name])
        time.sleep(2)

        if result['success']:
            # 直接从 create 命令输出中提取 ID
            # 格式: "Created notebook: {id} - {name}"
            stdout = result.get('stdout', '')
            match = re.search(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', stdout, re.IGNORECASE)

            if match:
                notebook_id = match.group(0)
                self.current_notebook = notebook_id
                print(f"[成功] Notebook ID: {notebook_id}")
                return notebook_id
            else:
                print(f"[失败] 无法从输出中提取 ID")
                print(f"[输出] {stdout[:200]}")
                return None

        print(f"[失败] {result.get('stderr', '未知错误')}")
        return None

    def list_knowledge_bases(self) -> List[Dict]:
        """列出所有知识库"""
        result = self.run_notebooklm(['list'])
        if not result['success']:
            return []

        notebooks = []
        lines = result['stdout'].split('\n')
        for line in lines:
            if '|' in line and 'ID' not in line and '---' not in line and line.strip():
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 2 and parts[0] and parts[0] != 'ID':
                    notebooks.append({
                        'id': parts[0][:20],
                        'title': parts[1] if len(parts) > 1 else '',
                        'owner': parts[2] if len(parts) > 2 else '',
                        'created': parts[3] if len(parts) > 3 else ''
                    })
        return notebooks

    def switch_knowledge_base(self, notebook_id: str) -> bool:
        """切换知识库"""
        result = self.run_notebooklm(['use', notebook_id])
        if result['success']:
            self.current_notebook = notebook_id
            print(f"[切换] 当前知识库: {notebook_id}")
            return True
        return False

    # ==================== Source 管理 ====================

    def add_source(self, url_or_path: str) -> bool:
        """添加单个 source"""
        result = self.run_notebooklm(['source', 'add', url_or_path], timeout=120)
        return result['success']

    def batch_add_sources(self, sources: List[str], delay: float = 3.0) -> Dict:
        """
        批量添加 sources

        Args:
            sources: URL 或文件路径列表
            delay: 每次添加之间的延迟

        Returns:
            导入结果统计
        """
        results = {
            'total': len(sources),
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'errors': [],
            'timestamp': datetime.now().isoformat()
        }

        print(f"\n{'='*60}")
        print(f"[批量导入] 开始导入 {len(sources)} 个 source")
        print(f"{'='*60}")

        for i, source in enumerate(sources, 1):
            try:
                # 显示进度
                print(f"[{i}/{len(sources)}] {source[:70]}...", end='', flush=True)

                result = self.run_notebooklm(['source', 'add', source], timeout=120)

                if result['success']:
                    results['success'] += 1
                    print(" ✓")
                else:
                    error = result.get('stderr', result.get('stdout', ''))
                    if 'already exists' in error.lower() or 'duplicate' in error.lower():
                        results['skipped'] += 1
                        print(" ⊙ (已存在)")
                    else:
                        results['failed'] += 1
                        results['errors'].append({'source': source, 'error': error})
                        print(f" ✗\n    错误: {error[:100]}")

                time.sleep(delay)

            except Exception as e:
                results['failed'] += 1
                results['errors'].append({'source': source, 'error': str(e)})
                print(f" ✗\n    异常: {str(e)}")

        # 打印汇总
        print(f"\n{'='*60}")
        print(f"[导入完成]")
        print(f"  总计: {results['total']}")
        print(f"  成功: {results['success']}")
        print(f"  跳过: {results['skipped']}")
        print(f"  失败: {results['failed']}")
        print(f"{'='*60}\n")

        # 保存结果
        self._save_results('batch_import', results)

        return results

    def list_sources(self) -> List[Dict]:
        """列出当前知识库的所有 sources"""
        result = self.run_notebooklm(['source', 'list'])
        if not result['success']:
            return []

        sources = []
        # 解析输出（需要根据实际格式调整）
        lines = result['stdout'].split('\n')
        for line in lines:
            # 这里需要根据 notebooklm source list 的实际输出格式来解析
            if line.strip():
                sources.append({'raw': line})

        return sources

    # ==================== Sitemap 抓取 ====================

    def fetch_sitemap(self, sitemap_url: str) -> List[str]:
        """
        从 sitemap 抓取所有 URL

        Args:
            sitemap_url: sitemap.xml URL

        Returns:
            URL 列表
        """
        print(f"\n[抓取 Sitemap] {sitemap_url}")

        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        try:
            response = session.get(sitemap_url, timeout=30)
            response.raise_for_status()

            # 解析 XML
            root = ET.fromstring(response.content)
            ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

            urls = []

            # 检查是否是 sitemap index
            sitemap_tags = root.findall('ns:sitemap/ns:loc', ns)
            if sitemap_tags:
                print(f"[发现] Sitemap index，包含 {len(sitemap_tags)} 个子 sitemap")
                for sitemap in sitemap_tags:
                    sub_urls = self.fetch_sitemap(sitemap.text)
                    urls.extend(sub_urls)
            else:
                # 直接的 urlset
                url_tags = root.findall('ns:url/ns:loc', ns)
                urls = [tag.text for tag in url_tags]
                print(f"[解析] 提取 {len(urls)} 个 URL")

            return urls

        except Exception as e:
            print(f"[错误] 抓取 sitemap 失败: {e}")
            return []

    def discover_and_fetch_sitemap(self, base_url: str) -> List[str]:
        """
        自动发现并抓取 sitemap

        Args:
            base_url: 网站 URL

        Returns:
            URL 列表
        """
        print(f"\n[自动发现] {base_url} 的 sitemap")

        parsed = urlparse(base_url)
        base_domain = f"{parsed.scheme}://{parsed.netloc}"

        # 常见的 sitemap 位置
        sitemap_locations = [
            f"{base_domain}/sitemap.xml",
            f"{base_domain}/sitemap_index.xml",
            f"{base_domain}/sitemap/sitemap.xml",
        ]

        # 尝试 robots.txt
        try:
            robots_url = f"{base_domain}/robots.txt"
            response = requests.get(robots_url, timeout=10)
            if response.status_code == 200:
                for line in response.text.split('\n'):
                    if line.strip().lower().startswith('sitemap:'):
                        sitemap = line.split(':', 1)[1].strip()
                        sitemap_locations.insert(0, sitemap)
                        print(f"[发现] robots.txt 中的 sitemap: {sitemap}")
        except:
            pass

        # 尝试每个位置
        for sitemap_url in sitemap_locations:
            try:
                urls = self.fetch_sitemap(sitemap_url)
                if urls:
                    return urls
            except:
                continue

        print(f"[警告] 未能找到 sitemap")
        return []

    # ==================== 智能清洗 ====================

    def detect_duplicates(self, sources: List[Dict]) -> Dict:
        """
        检测重复 sources

        Args:
            sources: source 列表

        Returns:
            重复检测结果
        """
        print(f"\n[检测重复] 分析 {len(sources)} 个 sources")

        duplicates = {
            'translation': [],  # 翻译重复
            'url': [],          # URL 重复
            'total': 0
        }

        # 按标题分组检测翻译重复
        title_groups = {}
        for source in sources:
            title = source.get('title', '').lower()
            # 简化标题
            simplified = re.sub(r'\s*\((中文|english|cn|en)\)', '', title, flags=re.IGNORECASE)
            simplified = re.sub(r'\s*-\s*(中文版|英文版)', '', simplified, flags=re.IGNORECASE)
            simplified = simplified.strip()

            if simplified not in title_groups:
                title_groups[simplified] = []
            title_groups[simplified].append(source)

        for title, group in title_groups.items():
            if len(group) > 1:
                duplicates['translation'].append({
                    'pattern': title,
                    'count': len(group),
                    'sources': group
                })
                print(f"  [翻译重复] '{title}': {len(group)} 个")
                duplicates['total'] += len(group) - 1

        return duplicates

    # ==================== 查询和生成 ====================

    def query(self, question: str, notebook_id: str = None) -> Optional[str]:
        """
        向知识库提问

        Args:
            question: 问题
            notebook_id: 指定 notebook（可选）

        Returns:
            回答内容
        """
        if notebook_id:
            self.switch_knowledge_base(notebook_id)

        print(f"\n[查询] {question}")
        result = self.run_notebooklm(['ask', question], timeout=180)

        if result['success']:
            # 提取回答
            output = result['stdout']
            if 'Answer:' in output:
                answer = output.split('Answer:')[1].split('Conversation:')[0].strip()
                return answer
            return output

        print(f"[错误] {result.get('stderr', '未知错误')}")
        return None

    def generate_artifact(self, artifact_type: str, notebook_id: str = None) -> bool:
        """
        生成内容（音频、视频、思维导图等）

        Args:
            artifact_type: 类型（audio, video, mind-map, quiz, etc.）
            notebook_id: 指定 notebook

        Returns:
            是否成功
        """
        if notebook_id:
            self.switch_knowledge_base(notebook_id)

        print(f"\n[生成] {artifact_type}")
        result = self.run_notebooklm(['generate', artifact_type], timeout=300)
        return result['success']

    def summary(self, notebook_id: str = None) -> Optional[str]:
        """生成摘要"""
        if self.switch_knowledge_base(notebook_id) if notebook_id else True:
            result = self.run_notebooklm(['summary'], timeout=180)
            if result['success']:
                return result['stdout']
        return None

    # ==================== 工具方法 ====================

    def _save_results(self, action: str, results: Dict):
        """保存操作结果"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        result_file = self.cache_dir / f"{action}_{timestamp}.json"

        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"[保存] 结果已保存: {result_file}")

    def get_status(self) -> Dict:
        """获取系统状态"""
        notebooks = self.list_knowledge_bases()

        return {
            'total_notebooks': len(notebooks),
            'current_notebook': self.current_notebook,
            'notebooks': notebooks[:5],  # 只返回前5个
            'cache_dir': str(self.cache_dir),
            'timestamp': datetime.now().isoformat()
        }


# ==================== 高级工作流 ====================

class AIRolandWorkflow:
    """AI Roland 高级工作流"""

    def __init__(self):
        self.manager = AIRolandKnowledgeManager()

    def create_ai_roland_knowledge_base(self) -> Optional[str]:
        """创建 AI Roland 专用知识库"""
        return self.manager.create_knowledge_base("AI Roland 系统文档")

    def import_ai_roland_docs(self) -> Dict:
        """导入 AI Roland 所有文档"""
        print("\n" + "="*60)
        print("AI Roland 文档导入工作流")
        print("="*60)

        # 1. 创建知识库
        notebook_id = self.create_ai_roland_knowledge_base()
        if not notebook_id:
            return {'error': '创建知识库失败'}

        # 2. 收集所有文档
        ai_roland_dir = Path("D:/ClaudeWork/AI_Roland")
        doc_files = []

        print("\n[扫描] AI Roland 文档...")

        # 扫描 Markdown 文件
        for md_file in ai_roland_dir.rglob("*.md"):
            # 排除缓存和临时文件
            if 'cache' not in str(md_file) and '__pycache__' not in str(md_file):
                doc_files.append(str(md_file))

        print(f"[发现] {len(doc_files)} 个 Markdown 文件")

        # 3. 批量导入
        results = self.manager.batch_add_sources(doc_files, delay=2.0)

        # 4. 生成报告
        results['notebook_id'] = notebook_id
        results['ai_roland_docs'] = len(doc_files)

        return results

    def setup_second_brain(self) -> Dict:
        """
        设置第二大脑

        将 AI Roland 的记忆系统整合到 NotebookLM
        """
        print("\n" + "="*60)
        print("设置 AI Roland 的第二大脑")
        print("="*60)

        # 1. 创建记忆知识库
        notebook_id = self.manager.create_knowledge_base("AI Roland 记忆系统")
        if not notebook_id:
            return {'error': '创建知识库失败'}

        # 2. 导入对话历史
        history_file = Path("D:/ClaudeWork/AI_Roland/对话历史.md")
        if history_file.exists():
            print(f"\n[导入] 对话历史...")
            self.manager.add_source(str(history_file))

        # 3. 导入语义记忆
        memory_dir = Path("D:/ClaudeWork/AI_Roland/记忆库/语义记忆")
        if memory_dir.exists():
            print(f"\n[导入] 语义记忆...")
            memory_files = list(memory_dir.glob("*.md"))
            for mem_file in memory_files[:10]:  # 先导入10个作为示例
                self.manager.add_source(str(mem_file))
                time.sleep(1)

        # 4. 导入日记
        diary_dir = Path("D:/ClaudeWork/AI_Roland/日记")
        if diary_dir.exists():
            print(f"\n[导入] 日记...")
            diary_files = list(diary_dir.glob("*.md"))
            for diary_file in diary_files[:10]:
                self.manager.add_source(str(diary_file))
                time.sleep(1)

        return {
            'notebook_id': notebook_id,
            'status': '第二大脑设置完成'
        }


# ==================== CLI 接口 ====================

def main():
    """命令行接口"""
    import sys

    manager = AIRolandKnowledgeManager()
    workflow = AIRolandWorkflow()

    if len(sys.argv) < 2:
        print("AI Roland x NotebookLM 集成系统")
        print("\n命令:")
        print("  知识库管理:")
        print("    python ai_roland_notebook.py create <name>          # 创建知识库")
        print("    python ai_roland_notebook.py list                # 列出知识库")
        print("    python ai_roland_notebook.py use <id>             # 切换知识库")
        print("\n  Source 管理:")
        print("    python ai_roland_notebook.py add <url/file>      # 添加 source")
        print("    python ai_roland_notebook.py batch <file.txt>    # 批量导入")
        print("    python ai_roland_notebook.py sitemap <url>       # 抓取 sitemap")
        print("\n  查询和生成:")
        print("    python ai_roland_notebook.py query <question>    # 提问")
        print("    python ai_roland_notebook.py summary            # 生成摘要")
        print("    python ai_roland_notebook.py generate <type>     # 生成内容")
        print("\n  工作流:")
        print("    python ai_roland_notebook.py import-ai-roland    # 导入 AI Roland 文档")
        print("    python ai_roland_notebook.py setup-second-brain # 设置第二大脑")
        print("    python ai_roland_notebook.py status              # 查看状态")
        return

    command = sys.argv[1]

    if command == 'create':
        if len(sys.argv) < 3:
            print("用法: python ai_roland_notebook.py create <name>")
            return
        manager.create_knowledge_base(sys.argv[2])

    elif command == 'list':
        notebooks = manager.list_knowledge_bases()
        print(f"\n共有 {len(notebooks)} 个知识库:\n")
        for nb in notebooks:
            print(f"  {nb['id'][:20]}... | {nb['title']}")

    elif command == 'use':
        if len(sys.argv) < 3:
            print("用法: python ai_roland_notebook.py use <notebook-id>")
            return
        manager.switch_knowledge_base(sys.argv[2])

    elif command == 'add':
        if len(sys.argv) < 3:
            print("用法: python ai_roland_notebook.py add <url-or-file>")
            return
        success = manager.add_source(sys.argv[2])
        print(f"[{'成功' if success else '失败'}] Source 已添加")

    elif command == 'batch':
        if len(sys.argv) < 3:
            print("用法: python ai_roland_notebook.py batch <urls-file>")
            return
        with open(sys.argv[2], 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
        manager.batch_add_sources(urls)

    elif command == 'sitemap':
        if len(sys.argv) < 3:
            print("用法: python ai_roland_notebook.py sitemap <url>")
            return
        urls = manager.discover_and_fetch_sitemap(sys.argv[2])

        # 保存 URL
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        url_file = manager.cache_dir / f"urls_{timestamp}.txt"
        with open(url_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(urls))

        print(f"\n[保存] {len(urls)} 个 URL 已保存到: {url_file}")

    elif command == 'query':
        if len(sys.argv) < 3:
            print("用法: python ai_roland_notebook.py query <question>")
            return
        question = ' '.join(sys.argv[2:])
        answer = manager.query(question)
        if answer:
            print(f"\n{answer}")

    elif command == 'summary':
        summary = manager.summary()
        if summary:
            print(f"\n{summary}")

    elif command == 'generate':
        if len(sys.argv) < 3:
            print("用法: python ai_roland_notebook.py generate <type>")
            print("类型: audio, video, mind-map, quiz, report, etc.")
            return
        success = manager.generate_artifact(sys.argv[2])
        print(f"[{'成功' if success else '失败'}] {sys.argv[2]} 已生成")

    elif command == 'import-ai-roland':
        results = workflow.import_ai_roland_docs()
        print(f"\n[完成] 导入结果:")
        print(f"  Notebook ID: {results.get('notebook_id')}")
        print(f"  文档数量: {results.get('ai_roland_docs', 0)}")
        print(f"  成功导入: {results.get('success', 0)}")

    elif command == 'setup-second-brain':
        results = workflow.setup_second_brain()
        print(f"\n[完成] 第二大脑设置:")
        print(f"  Notebook ID: {results.get('notebook_id')}")
        print(f"  状态: {results.get('status')}")

    elif command == 'status':
        status = manager.get_status()
        print(f"\n系统状态:")
        print(f"  知识库总数: {status['total_notebooks']}")
        print(f"  当前知识库: {status['current_notebook']}")
        print(f"  缓存目录: {status['cache_dir']}")


if __name__ == "__main__":
    main()
