"""
任务统计工具 - 自动更新任务清单的统计数字
"""

import re
from pathlib import Path


class TaskStats:
    """任务统计工具"""

    def __init__(self, workspace_path=None):
        if workspace_path is None:
            current_dir = Path(__file__).parent
            self.workspace = current_dir.parent
        else:
            self.workspace = Path(workspace_path)

        self.tasks_file = self.workspace / "任务清单.md"

    def count_tasks(self):
        """统计任务数量"""
        if not self.tasks_file.exists():
            return {
                "total": 0,
                "done": 0,
                "todo": 0,
                "urgent": 0,
                "important": 0,
                "daily": 0
            }

        content = self.tasks_file.read_text(encoding='utf-8')

        # 统计任务
        total_tasks = len(re.findall(r'- \[ \]', content))
        done_tasks = len(re.findall(r'- \[x\]', content))

        # 分区统计
        urgent_section = re.search(r'## 【紧急重要】.*?(?=##|\Z)', content, re.DOTALL)
        important_section = re.search(r'## 【重要不紧急】.*?(?=##|\Z)', content, re.DOTALL)
        daily_section = re.search(r'## 【日常事项】.*?(?=##|\Z)', content, re.DOTALL)

        urgent_count = len(re.findall(r'- \[ \]', urgent_section.group(0))) if urgent_section else 0
        important_count = len(re.findall(r'- \[ \]', important_section.group(0))) if important_section else 0
        daily_count = len(re.findall(r'- \[ \]', daily_section.group(0))) if daily_section else 0

        return {
            "total": total_tasks,
            "done": done_tasks,
            "todo": total_tasks,
            "urgent": urgent_count,
            "important": important_count,
            "daily": daily_count
        }

    def update_stats(self):
        """更新任务清单中的统计数字"""
        if not self.tasks_file.exists():
            return False

        stats = self.count_tasks()
        content = self.tasks_file.read_text(encoding='utf-8')

        # 新的统计内容
        new_stats = f'''## 统计

- 总任务：{stats["total"]}
- 已完成：{stats["done"]}
- 进行中：0
- 待办：{stats["todo"]}'''

        # 替换旧的统计
        updated_content = re.sub(
            r'## 统计.*?(?=---)',
            new_stats + '\n\n---',
            content,
            flags=re.DOTALL
        )

        self.tasks_file.write_text(updated_content, encoding='utf-8')
        return True

    def get_urgent_tasks(self):
        """获取紧急任务列表"""
        if not self.tasks_file.exists():
            return []

        content = self.tasks_file.read_text(encoding='utf-8')
        urgent_section = re.search(r'## 【紧急重要】.*?(?=##|\Z)', content, re.DOTALL)

        if not urgent_section:
            return []

        # 提取任务文本
        tasks = re.findall(r'- \[ \]\s*(.+)', urgent_section.group(0))
        return tasks


def main():
    """测试"""
    stats = TaskStats()
    result = stats.count_tasks()
    print(f"总任务: {result['total']}")
    print(f"已完成: {result['done']}")
    print(f"紧急: {result['urgent']}")

    stats.update_stats()
    print("统计已更新")


if __name__ == "__main__":
    main()
