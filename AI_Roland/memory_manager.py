#!/usr/bin/env python3
"""
Memory Manager - AI Roland 记忆管理系统

功能：
1. 自动扫描和索引对话历史
2. 提取关键信息更新用户记忆
3. 生成记忆使用报告
4. 执行记忆清理和归档
5. 搜索和检索记忆
"""

import os
import re
import json
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
from collections import defaultdict
import argparse

# ==================== 配置 ====================

BASE_DIR = Path(__file__).parent
CONVERSATION_HISTORY = BASE_DIR / "对话历史.md"
USER_MEMORY = BASE_DIR / "USER_MEMORY.md"
TASK_LIST = BASE_DIR / "任务清单.md"
SYSTEM_STATE = BASE_DIR / "system_state.json"

MEMORY_DIRS = {
    "episodic": BASE_DIR / "记忆库/情景记忆",
    "semantic": BASE_DIR / "记忆库/语义记忆",
    "rules": BASE_DIR / "记忆库/强制规则"
}

# ==================== 工具函数 ====================

def log(message, level="INFO"):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def read_file(file_path):
    """读取文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        log(f"文件不存在: {file_path}", "WARNING")
        return None
    except Exception as e:
        log(f"读取文件失败: {e}", "ERROR")
        return None

def write_file(file_path, content):
    """写入文件内容"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        log(f"文件已保存: {file_path}")
        return True
    except Exception as e:
        log(f"写入文件失败: {e}", "ERROR")
        return False

def get_file_hash(file_path):
    """获取文件哈希值（用于检测变化）"""
    content = read_file(file_path)
    if content:
        return hashlib.md5(content.encode()).hexdigest()
    return None

# ==================== 对话历史解析 ====================

class ConversationParser:
    """对话历史解析器"""

    def __init__(self, history_file):
        self.history_file = history_file
        self.conversations = []

    def parse(self):
        """解析对话历史"""
        content = read_file(self.history_file)
        if not content:
            return []

        # 分割会话
        pattern = r'---\n### 会话：(\d{4}-\d{2}-\d{2}(?: \d{2}:\d{2})?)'
        sections = re.split(pattern, content)

        conversations = []
        for i in range(1, len(sections), 2):
            if i+1 < len(sections):
                date_str = sections[i]
                body = sections[i+1]

                conv = {
                    'date': date_str,
                    'user': self._extract_field(body, '用户'),
                    'ai': self._extract_field(body, 'AI Roland'),
                    'tasks': self._extract_tasks(body),
                    'outputs': self._extract_outputs(body),
                    'achievements': self._extract_achievements(body)
                }
                conversations.append(conv)

        return conversations

    def _extract_field(self, text, field_name):
        """提取字段内容"""
        # 使用更简单的匹配方式避免编码问题
        lines = text.split('\n')
        for line in lines:
            if f'**{field_name}**：' in line:
                return line.split(f'**{field_name}**：')[1].strip()
        return ""

    def _extract_tasks(self, text):
        """提取任务列表"""
        tasks = []
        in_task_section = False

        for line in text.split('\n'):
            if '**任务**：' in line:
                in_task_section = True
                continue
            if in_task_section:
                if line.startswith('**') or line.startswith('---'):
                    break
                if line.strip().startswith('- ['):
                    tasks.append(line.strip())
                elif line.strip().startswith('-') and not line.startswith('---'):
                    tasks.append(line.strip())

        return tasks

    def _extract_outputs(self, text):
        """提取产出文件"""
        outputs = []
        in_output_section = False

        for line in text.split('\n'):
            if '**产出**：' in line or '**关键成果**：' in line:
                in_output_section = True
                continue
            if in_output_section:
                if line.startswith('**') or line.startswith('---'):
                    break
                if line.strip().startswith('-') or line.strip().startswith('*'):
                    outputs.append(line.strip())

        return outputs

    def _extract_achievements(self, text):
        """提取关键成果"""
        achievements = []
        lines = text.split('\n')
        in_achievement_section = False

        for line in lines:
            if '**关键成果**：' in line:
                in_achievement_section = True
                continue
            if in_achievement_section:
                if line.startswith('**') or line.startswith('---'):
                    break
                if line.strip().startswith('-'):
                    achievements.append(line.strip())

        return achievements

# ==================== 记忆统计 ====================

class MemoryStatistics:
    """记忆统计器"""

    def __init__(self):
        self.stats = {
            'total_conversations': 0,
            'total_tasks': 0,
            'completed_tasks': 0,
            'total_files': 0,
            'memory_files': {
                'episodic': 0,
                'semantic': 0,
                'rules': 0
            },
            'recent_activity': [],
            'top_keywords': [],
            'projects': []
        }

    def calculate(self, conversations, memory_dirs):
        """计算统计信息"""
        # 对话统计
        self.stats['total_conversations'] = len(conversations)

        # 任务统计
        for conv in conversations:
            self.stats['total_tasks'] += len([t for t in conv.get('tasks', []) if '✅' in t])

        # 记忆文件统计
        for mem_type, mem_dir in memory_dirs.items():
            if mem_dir.exists():
                self.stats['memory_files'][mem_type] = len(list(mem_dir.rglob('*.md')))

        # 最近活动
        if conversations:
            self.stats['recent_activity'] = [
                {
                    'date': conv['date'],
                    'summary': conv['user'][:50] + '...' if len(conv['user']) > 50 else conv['user']
                }
                for conv in conversations[-5:]
            ]

        # 项目提取
        self.stats['projects'] = self._extract_projects(conversations)

        return self.stats

    def _extract_projects(self, conversations):
        """提取项目列表"""
        projects = defaultdict(list)

        for conv in conversations:
            for task in conv.get('tasks', []):
                # 识别项目关键词
                if 'Skill' in task or '技能' in task:
                    projects['技能开发'].append({
                        'date': conv['date'],
                        'task': task
                    })
                elif 'AWS' in task or '服务器' in task:
                    projects['服务器运维'].append({
                        'date': conv['date'],
                        'task': task
                    })
                elif '集成' in task or '整合' in task:
                    projects['系统集成'].append({
                        'date': conv['date'],
                        'task': task
                    })

        return dict(projects)

    def generate_report(self):
        """生成统计报告"""
        report = []
        report.append("# 记忆系统统计报告")
        report.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        report.append("## 📊 整体统计")
        report.append(f"- 对话总数: {self.stats['total_conversations']}")
        report.append(f"- 任务总数: {self.stats['total_tasks']}")
        report.append(f"- 已完成任务: {self.stats['completed_tasks']}")

        report.append("\n## 🗂️ 记忆文件")
        report.append(f"- 情景记忆: {self.stats['memory_files']['episodic']} 个")
        report.append(f"- 语义记忆: {self.stats['memory_files']['semantic']} 个")
        report.append(f"- 强制规则: {self.stats['memory_files']['rules']} 个")

        report.append("\n## 🚀 最近活动")
        for activity in self.stats['recent_activity']:
            report.append(f"- {activity['date']}: {activity['summary']}")

        if self.stats['projects']:
            report.append("\n## 📁 项目分类")
            for project, tasks in self.stats['projects'].items():
                report.append(f"\n### {project} ({len(tasks)} 个任务)")
                for task in tasks[-5:]:  # 最近5个
                    report.append(f"- {task['date']}: {task['task']}")

        return '\n'.join(report)

# ==================== 记忆搜索 ====================

class MemorySearch:
    """记忆搜索引擎"""

    def __init__(self, memory_dirs):
        self.memory_dirs = memory_dirs
        self.index = {}

    def build_index(self):
        """构建记忆索引"""
        log("正在构建记忆索引...")

        for mem_type, mem_dir in self.memory_dirs.items():
            if not mem_dir.exists():
                continue

            for file_path in mem_dir.rglob('*.md'):
                content = read_file(file_path)
                if content:
                    # 提取关键词
                    keywords = self._extract_keywords(content)
                    file_key = str(file_path.relative_to(BASE_DIR))

                    for keyword in keywords:
                        if keyword not in self.index:
                            self.index[keyword] = []
                        self.index[keyword].append({
                            'file': file_key,
                            'type': mem_type,
                            'relevance': self._calculate_relevance(keyword, content)
                        })

        log(f"索引构建完成，共 {len(self.index)} 个关键词")

    def _extract_keywords(self, text):
        """提取关键词"""
        # 简单的关键词提取（可以用jieba优化）
        keywords = []

        # 提取中文词组（2-4个字）
        chinese_words = re.findall(r'[\u4e00-\u9fa5]{2,4}', text)

        # 提取英文单词
        english_words = re.findall(r'\b[a-zA-Z]{3,}\b', text)

        # 过滤常见词
        stop_words = {'这个', '那个', '可以', '需要', '应该', '系统', '文件', '功能',
                     'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all'}

        keywords = [w for w in chinese_words + english_words if w not in stop_words]

        # 统计词频
        word_freq = defaultdict(int)
        for word in keywords:
            word_freq[word] += 1

        # 返回高频词
        return [k for k, v in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:50]]

    def _calculate_relevance(self, keyword, content):
        """计算相关性分数"""
        count = content.count(keyword)
        length = len(content)
        return count / length * 1000

    def search(self, query):
        """搜索记忆"""
        results = []

        # 直接匹配
        if query in self.index:
            results.extend(self.index[query])

        # 模糊匹配
        for keyword, files in self.index.items():
            if query in keyword or keyword in query:
                results.extend(files)

        # 去重和排序
        unique_results = {}
        for result in results:
            file_key = result['file']
            if file_key not in unique_results or result['relevance'] > unique_results[file_key]['relevance']:
                unique_results[file_key] = result

        return sorted(unique_results.values(), key=lambda x: x['relevance'], reverse=True)

# ==================== 记忆清理 ====================

class MemoryCleaner:
    """记忆清理器"""

    def __init__(self):
        self.cleanup_report = {
            'duplicates': [],
            'empty_files': [],
            'old_files': [],
            'orphaned_files': []
        }

    def find_duplicates(self, memory_dirs):
        """查找重复文件"""
        log("正在查找重复文件...")

        file_hashes = defaultdict(list)

        for mem_dir in memory_dirs.values():
            if not mem_dir.exists():
                continue

            for file_path in mem_dir.rglob('*.md'):
                file_hash = get_file_hash(file_path)
                if file_hash:
                    file_hashes[file_hash].append(file_path)

        # 找出重复的文件
        for file_hash, files in file_hashes.items():
            if len(files) > 1:
                self.cleanup_report['duplicates'].append(files)

        log(f"发现 {len(self.cleanup_report['duplicates'])} 组重复文件")

    def find_empty_files(self, memory_dirs):
        """查找空文件"""
        log("正在查找空文件...")

        for mem_dir in memory_dirs.values():
            if not mem_dir.exists():
                continue

            for file_path in mem_dir.rglob('*.md'):
                content = read_file(file_path)
                if content and len(content.strip()) < 10:
                    self.cleanup_report['empty_files'].append(file_path)

        log(f"发现 {len(self.cleanup_report['empty_files'])} 个空文件")

    def find_old_files(self, memory_dirs, days=180):
        """查找旧文件（超过指定天数未修改）"""
        log(f"正在查找 {days} 天未修改的文件...")

        cutoff_date = datetime.now() - timedelta(days=days)

        for mem_dir in memory_dirs.values():
            if not mem_dir.exists():
                continue

            for file_path in mem_dir.rglob('*.md'):
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if mtime < cutoff_date:
                    self.cleanup_report['old_files'].append({
                        'file': file_path,
                        'last_modified': mtime
                    })

        log(f"发现 {len(self.cleanup_report['old_files'])} 个旧文件")

    def generate_cleanup_report(self):
        """生成清理报告"""
        report = []
        report.append("# 记忆清理报告")
        report.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        if self.cleanup_report['duplicates']:
            report.append("## 🔄 重复文件")
            for files in self.cleanup_report['duplicates']:
                report.append(f"\n发现重复:")
                for file in files:
                    report.append(f"  - {file}")

        if self.cleanup_report['empty_files']:
            report.append("\n## 📭 空文件")
            for file in self.cleanup_report['empty_files']:
                report.append(f"- {file}")

        if self.cleanup_report['old_files']:
            report.append("\n## 📅 旧文件（超过180天未修改）")
            for item in self.cleanup_report['old_files']:
                report.append(f"- {item['file']} (最后修改: {item['last_modified'].strftime('%Y-%m-%d')})")

        if not any([self.cleanup_report['duplicates'], self.cleanup_report['empty_files'], self.cleanup_report['old_files']]):
            report.append("\n✅ 记忆库状态良好，无需清理")

        return '\n'.join(report)

# ==================== 主程序 ====================

def main():
    """主程序"""
    parser = argparse.ArgumentParser(description='AI Roland 记忆管理系统')
    parser.add_argument('--scan', action='store_true', help='扫描对话历史')
    parser.add_argument('--stats', action='store_true', help='生成统计报告')
    parser.add_argument('--search', type=str, help='搜索记忆')
    parser.add_argument('--cleanup', action='store_true', help='清理记忆')
    parser.add_argument('--update', action='store_true', help='更新用户记忆')
    parser.add_argument('--all', action='store_true', help='执行所有操作')

    args = parser.parse_args()

    # 如果没有参数，显示帮助
    if not any(vars(args).values()):
        parser.print_help()
        return

    log("=" * 60)
    log("AI Roland 记忆管理系统启动")
    log("=" * 60)

    # 扫描对话历史
    if args.scan or args.all:
        log("\n[1/5] 扫描对话历史...")
        parser = ConversationParser(CONVERSATION_HISTORY)
        conversations = parser.parse()
        log(f"扫描完成，共发现 {len(conversations)} 次会话")

    # 生成统计报告
    if args.stats or args.all:
        log("\n[2/5] 生成统计报告...")
        if 'conversations' not in locals():
            parser = ConversationParser(CONVERSATION_HISTORY)
            conversations = parser.parse()

        stats = MemoryStatistics()
        stats.calculate(conversations, MEMORY_DIRS)

        report = stats.generate_report()
        report_file = BASE_DIR / "记忆库" / f"记忆统计报告_{datetime.now().strftime('%Y%m%d')}.md"
        write_file(report_file, report)
        log(f"统计报告已保存: {report_file}")

    # 搜索记忆
    if args.search:
        log(f"\n[3/5] 搜索记忆: {args.search}")
        search = MemorySearch(MEMORY_DIRS)
        search.build_index()

        results = search.search(args.search)
        log(f"找到 {len(results)} 个相关结果")

        for i, result in enumerate(results[:10], 1):
            log(f"{i}. [{result['type']}] {result['file']} (相关性: {result['relevance']:.2f})")

    # 清理记忆
    if args.cleanup or args.all:
        log("\n[4/5] 清理记忆...")
        cleaner = MemoryCleaner()
        cleaner.find_duplicates(MEMORY_DIRS)
        cleaner.find_empty_files(MEMORY_DIRS)
        cleaner.find_old_files(MEMORY_DIRS)

        cleanup_report = cleaner.generate_cleanup_report()
        cleanup_file = BASE_DIR / "记忆库" / f"记忆清理报告_{datetime.now().strftime('%Y%m%d')}.md"
        write_file(cleanup_file, cleanup_report)
        log(f"清理报告已保存: {cleanup_file}")

    # 更新用户记忆
    if args.update or args.all:
        log("\n[5/5] 更新用户记忆...")
        log("注意: USER_MEMORY.md 需要手动更新，以确保准确性")
        log(f"当前文件: {USER_MEMORY}")

    log("\n" + "=" * 60)
    log("记忆管理系统完成")
    log("=" * 60)

if __name__ == "__main__":
    main()
