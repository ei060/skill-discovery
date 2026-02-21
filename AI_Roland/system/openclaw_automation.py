"""
OpenClaw 式自动化工具集
实现 sitemap 抓取、批量导入、智能清洗、完整性审计
"""

import xml.etree.ElementTree as ET
import requests
import subprocess
import json
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Set
from datetime import datetime
import re


class SitemapParser:
    """Sitemap 解析器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def fetch_sitemap(self, sitemap_url: str) -> List[str]:
        """
        获取 sitemap 中的所有 URL

        Args:
            sitemap_url: sitemap.xml URL

        Returns:
            URL 列表
        """
        urls = []

        try:
            print(f"[抓取] 正在获取 sitemap: {sitemap_url}")
            response = self.session.get(sitemap_url, timeout=30)
            response.raise_for_status()

            # 解析 XML
            root = ET.fromstring(response.content)

            # 命名空间
            ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

            # 检查是否有 sitemap index
            sitemap_tags = root.findall('ns:sitemap/ns:loc', ns)
            if sitemap_tags:
                # Sitemap index，递归获取
                print(f"[发现] Sitemap index，包含 {len(sitemap_tags)} 个子 sitemap")
                for sitemap in sitemap_tags:
                    sub_urls = self.fetch_sitemap(sitemap.text)
                    urls.extend(sub_urls)
            else:
                # 直接的 urlset
                url_tags = root.findall('ns:url/ns:loc', ns)
                urls = [tag.text for tag in url_tags]
                print(f"[解析] 从 sitemap 提取 {len(urls)} 个 URL")

        except Exception as e:
            print(f"[错误] 解析 sitemap 失败: {e}")

        return urls

    def fetch_sitemap_from_url(self, base_url: str) -> List[str]:
        """
        从给定 URL 自动发现并获取 sitemap

        Args:
            base_url: 网站 URL

        Returns:
            URL 列表
        """
        parsed = urlparse(base_url)
        base_domain = f"{parsed.scheme}://{parsed.netloc}"

        # 尝试常见的 sitemap 位置
        sitemap_locations = [
            f"{base_domain}/sitemap.xml",
            f"{base_domain}/sitemap_index.xml",
            f"{base_domain}/wp-sitemap.xml",
            f"{base_domain}/sitemap.txt",
        ]

        # 尝试 robots.txt
        try:
            robots_url = f"{base_domain}/robots.txt"
            response = self.session.get(robots_url, timeout=10)
            if response.status_code == 200:
                # 查找 Sitemap 行
                for line in response.text.split('\n'):
                    line = line.strip()
                    if line.lower().startswith('sitemap:'):
                        sitemap_url = line.split(':', 1)[1].strip()
                        sitemap_locations.insert(0, sitemap_url)
                        print(f"[发现] robots.txt 中的 sitemap: {sitemap_url}")
        except:
            pass

        # 尝试每个位置
        for sitemap_url in sitemap_locations:
            try:
                print(f"[尝试] {sitemap_url}")
                urls = self.fetch_sitemap(sitemap_url)
                if urls:
                    return urls
            except:
                continue

        print(f"[警告] 未能找到 sitemap")
        return []


class NotebookLMAutomator:
    """NotebookLM 自动化操作"""

    def __init__(self):
        self.cache_dir = Path("D:/ClaudeWork/AI_Roland/cache/notebooklm")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def run_command(self, args: List[str]) -> Dict:
        """运行 notebooklm 命令"""
        try:
            result = subprocess.run(
                ['notebooklm'] + args,
                capture_output=True,
                text=True,
                timeout=60,
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
            return {'success': False, 'error': 'Timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def list_notebooks(self) -> List[Dict]:
        """列出所有笔记本"""
        result = self.run_command(['list'])
        if not result['success']:
            return []

        notebooks = []
        lines = result['stdout'].split('\n')
        for line in lines:
            if '|' in line and 'ID' not in line and '---' not in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 2 and parts[0]:
                    notebooks.append({
                        'id': parts[0],
                        'title': parts[1] if len(parts) > 1 else ''
                    })
        return notebooks

    def use_notebook(self, notebook_id: str) -> bool:
        """选择笔记本"""
        result = self.run_command(['use', notebook_id])
        return result['success']

    def create_notebook(self, title: str) -> bool:
        """创建笔记本"""
        result = self.run_command(['create', title])
        time.sleep(1)  # 等待创建完成
        return result['success']

    def batch_add_sources(self, urls: List[str], delay: float = 2.0) -> Dict:
        """
        批量添加 source

        Args:
            urls: URL 列表
            delay: 每次添加之间的延迟（秒）

        Returns:
            导入结果统计
        """
        results = {
            'total': len(urls),
            'success': 0,
            'failed': 0,
            'errors': []
        }

        print(f"\n[批量导入] 开始导入 {len(urls)} 个 source")
        print(f"[进度] {'='*50}")

        for i, url in enumerate(urls, 1):
            try:
                print(f"\r[{i}/{len(urls)}] {url[:60]}", end='', flush=True)

                result = self.run_command(['source', 'add', url])

                if result['success']:
                    results['success'] += 1
                else:
                    results['failed'] += 1
                    error_msg = result.get('stderr', 'Unknown error')
                    if 'already exists' not in error_msg.lower():
                        results['errors'].append({'url': url, 'error': error_msg})

                time.sleep(delay)

            except Exception as e:
                results['failed'] += 1
                results['errors'].append({'url': url, 'error': str(e)})

        print(f"\n\n[完成] 成功: {results['success']}, 失败: {results['failed']}")

        # 保存结果
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        result_file = self.cache_dir / f"import_results_{timestamp}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"[保存] 结果已保存: {result_file}")

        return results


class SourceCleaner:
    """Source 清洗工具"""

    def __init__(self):
        self.automator = NotebookLMAutomator()

    def detect_translations(self, sources: List[Dict]) -> List[Dict]:
        """
        检测翻译重复（中英文）

        Args:
            sources: source 列表，每个包含 id 和 title

        Returns:
            重复组列表
        """
        print("\n[检测] 翻译重复（中英文）")

        duplicates = []
        seen = {}

        for source in sources:
            # 简化标题用于比较
            title = source.get('title', '')
            # 移除常见翻译标识
            simplified = re.sub(r'\s*\((中文|Chinese|English|EN|CN)\)', '', title)
            simplified = re.sub(r'\s*-\s*(中文版|英文版|CN|EN)$', '', simplified, flags=re.IGNORECASE)
            simplified = simplified.strip().lower()

            if simplified in seen:
                duplicates.append({
                    'original': seen[simplified],
                    'duplicate': source,
                    'type': 'translation',
                    'pattern': simplified
                })
                print(f"  [发现] {simplified}")
            else:
                seen[simplified] = source

        print(f"[结果] 发现 {len(duplicates)} 组翻译重复")
        return duplicates

    def detect_url_duplicates(self, sources: List[Dict]) -> List[Dict]:
        """
        检测 URL 重复

        Args:
            sources: source 列表

        Returns:
            重复组列表
        """
        print("\n[检测] URL 重复")

        # 按路径分组
        path_groups = {}
        for source in sources:
            url = source.get('url', '')
            parsed = urlparse(url)
            # 移除尾部斜杠和常见参数
            path = parsed.path.rstrip('/').lower()

            if path not in path_groups:
                path_groups[path] = []
            path_groups[path].append(source)

        # 找出重复
        duplicates = []
        for path, group in path_groups.items():
            if len(group) > 1:
                duplicates.append({
                    'type': 'url',
                    'path': path,
                    'sources': group
                })
                print(f"  [发现] {path}: {len(group)} 个")

        print(f"[结果] 发现 {len(duplicates)} 组 URL 重复")
        return duplicates

    def batch_delete_sources(self, source_ids: List[str]) -> int:
        """
        批量删除 source

        Args:
            source_ids: source ID 列表

        Returns:
            删除数量
        """
        print(f"\n[批量删除] 开始删除 {len(source_ids)} 个 source")

        deleted = 0
        for i, source_id in enumerate(source_ids, 1):
            # notebooklm 没有 source delete 命令
            # 这里只是占位，实际需要通过 GUI 操作或其他方式
            pass

        print(f"[完成] 删除了 {deleted} 个 source")
        return deleted


class SourceAuditor:
    """Source 完整性审计"""

    def __init__(self):
        self.automator = NotebookLMAutomator()

    def audit_completeness(self, expected_urls: List[str], actual_sources: List[Dict]) -> Dict:
        """
        审计完整性

        Args:
            expected_urls: 预期的 URL 列表
            actual_sources: 实际的 source 列表

        Returns:
            审计报告
        """
        print("\n[审计] 完整性检查")

        # 提取实际的 URL
        actual_urls = set()
        for source in actual_sources:
            url = source.get('url', '')
            # 规范化 URL
            normalized = url.rstrip('/').lower()
            actual_urls.add(normalized)

        # 规范化预期 URL
        expected_normalized = set()
        for url in expected_urls:
            normalized = url.rstrip('/').lower()
            expected_normalized.add(normalized)

        # 计算差异
        missing = expected_normalized - actual_urls
        extra = actual_urls - expected_normalized
        duplicate = len(expected_urls) - len(expected_normalized)

        report = {
            'expected': len(expected_normalized),
            'actual': len(actual_urls),
            'missing': len(missing),
            'extra': len(extra),
            'duplicate': duplicate,
            'missing_urls': list(missing)[:10],  # 只显示前10个
            'extra_urls': list(extra)[:10]
        }

        print(f"\n[审计报告]")
        print(f"  预期: {report['expected']}")
        print(f"  实际: {report['actual']}")
        print(f"  缺失: {report['missing']}")
        print(f"  多余: {report['extra']}")
        print(f"  重复: {report['duplicate']}")

        if missing:
            print(f"\n  缺失示例（前10个）:")
            for url in list(missing)[:10]:
                print(f"    - {url}")

        if extra:
            print(f"\n  多余示例（前10个）:")
            for url in list(extra)[:10]:
                print(f"    - {url}")

        # 保存报告
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.automator.cache_dir / f"audit_report_{timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n[保存] 审计报告已保存: {report_file}")

        return report


def main():
    """命令行接口"""
    import sys

    if len(sys.argv) < 2:
        print("OpenClaw 式自动化工具")
        print("\n用法:")
        print("  python openclaw_automation.py sitemap <url>     # 抓取 sitemap")
        print("  python openclaw_automation.py import <urls.txt>  # 批量导入")
        print("  python openclaw_automation.py clean            # 清洗重复")
        print("  python openclaw_automation.py audit            # 完整性审计")
        return

    command = sys.argv[1]

    if command == 'sitemap':
        parser = SitemapParser()
        if len(sys.argv) < 3:
            print("用法: python openclaw_automation.py sitemap <url>")
            return

        url = sys.argv[2]
        urls = parser.fetch_sitemap_from_url(url)

        # 保存 URL 列表
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        url_file = Path("D:/ClaudeWork/AI_Roland/cache/notebooklm") / f"urls_{timestamp}.txt"
        with open(url_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(urls))

        print(f"\n[保存] URL 列表已保存: {url_file}")
        print(f"[总计] {len(urls)} 个 URL")

    elif command == 'import':
        automator = NotebookLMAutomator()

        # 从文件读取 URL
        if len(sys.argv) >= 3:
            url_file = Path(sys.argv[2])
        else:
            # 使用最新的 URL 文件
            cache_dir = Path("D:/ClaudeWork/AI_Roland/cache/notebooklm")
            url_files = list(cache_dir.glob("urls_*.txt"))
            if not url_files:
                print("[错误] 未找到 URL 文件")
                return
            url_file = max(url_files, key=lambda p: p.stat().st_mtime)

        with open(url_file, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]

        results = automator.batch_add_sources(urls)

    elif command == 'clean':
        print("[清洗] Source 清洗功能")
        print("注意：当前需要通过 NotebookLM GUI 手动删除")

    elif command == 'audit':
        print("[审计] 完整性审计功能")
        print("需要提供预期和实际的 source 列表")


if __name__ == "__main__":
    main()
