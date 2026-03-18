#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI Roland 代理独立记忆系统

分层架构：
- 全局共享记忆 (用户偏好、项目状态、跨代理知识)
- 代理独立记忆 (各代理的专业经验、工作记忆)
- 记忆同步机制
"""

import sys
import os
import io
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
import copy

# 修复 Windows 编码
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

# 添加系统路径
system_path = Path(__file__).parent
sys.path.insert(0, str(system_path))


@dataclass
class AgentMemory:
    """单个代理的记忆"""

    agent_name: str
    agent_type: str  # architect, planner, code_reviewer, etc.

    # 短期工作记忆 (当前会话)
    working_memory: List[Dict] = field(default_factory=list)

    # 长期专业记忆 (经验积累)
    professional_memory: List[Dict] = field(default_factory=list)

    # 常见模式和最佳实践
    patterns: List[Dict] = field(default_factory=list)

    # 代理偏好设置
    preferences: Dict = field(default_factory=dict)

    # 统计信息
    stats: Dict = field(default_factory=lambda: {
        'tasks_completed': 0,
        'tasks_created': datetime.now(timezone.utc).isoformat(),
        'last_active': None
    })

    def add_work_item(self, item: Dict):
        """添加工作记忆项"""
        item['timestamp'] = datetime.now(timezone.utc).isoformat()
        self.working_memory.append(item)

        # 限制工作记忆大小（最近50项）
        if len(self.working_memory) > 50:
            self.working_memory = self.working_memory[-50:]

    def add_professional_memory(self, item: Dict):
        """添加专业记忆（长期经验）"""
        item['timestamp'] = datetime.now(timezone.utc).isoformat()
        item['agent'] = self.agent_name
        self.professional_memory.append(item)

        # 限制专业记忆大小（最近200项）
        if len(self.professional_memory) > 200:
            self.professional_memory = self.professional_memory[-200:]

    def add_pattern(self, pattern: Dict):
        """添加模式或最佳实践"""
        pattern['timestamp'] = datetime.now(timezone.utc).isoformat()
        pattern['agent'] = self.agent_name
        self.patterns.append(pattern)

        # 限制模式数量（最近100项）
        if len(self.patterns) > 100:
            self.patterns = self.patterns[-100:]

    def search(self, query: str, category: str = 'all') -> List[Dict]:
        """搜索代理记忆"""
        query_lower = query.lower()
        results = []

        # 搜索工作记忆
        if category in ['all', 'work']:
            for item in self.working_memory:
                if self._matches(item, query_lower):
                    results.append({**item, 'source': 'work', 'score': self._score(item, query_lower)})

        # 搜索专业记忆
        if category in ['all', 'professional']:
            for item in self.professional_memory:
                if self._matches(item, query_lower):
                    results.append({**item, 'source': 'professional', 'score': self._score(item, query_lower)})

        # 搜索模式
        if category in ['all', 'patterns']:
            for item in self.patterns:
                if self._matches(item, query_lower):
                    results.append({**item, 'source': 'pattern', 'score': self._score(item, query_lower) + 0.2})

        # 按分数排序
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:20]

    def _matches(self, item: Dict, query: str) -> bool:
        """检查项是否匹配查询"""
        searchable = str(item).lower()
        return query in searchable

    def _score(self, item: Dict, query: str) -> float:
        """计算匹配分数"""
        searchable = str(item).lower()
        # 简单的频率匹配
        count = searchable.count(query)
        return count * 0.1

    def clear_working_memory(self):
        """清除工作记忆（会话结束）"""
        # 将重要的工作记忆转移到专业记忆
        for item in self.working_memory:
            if item.get('important', False):
                self.add_professional_memory({
                    'type': 'lesson_learned',
                    'content': item.get('content', ''),
                    'context': item.get('context', '')
                })

        self.working_memory = []

    def get_summary(self) -> Dict:
        """获取记忆摘要"""
        return {
            'agent': self.agent_name,
            'type': self.agent_type,
            'working_memory_count': len(self.working_memory),
            'professional_memory_count': len(self.professional_memory),
            'patterns_count': len(self.patterns),
            'tasks_completed': self.stats['tasks_completed'],
            'last_active': self.stats['last_active']
        }

    def to_dict(self) -> Dict:
        """转换为字典（用于保存）"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'AgentMemory':
        """从字典创建（用于加载）"""
        return cls(**data)


class AgentMemoryManager:
    """代理记忆管理器 - 管理所有代理的记忆"""

    def __init__(self, workspace: Optional[Path] = None):
        if workspace is None:
            # 默认使用 AI_Roland/system 作为工作空间
            workspace = Path(__file__).parent.parent

        self.workspace = Path(workspace)
        # 记忆目录在 agents 下的 memory 子目录
        self.memory_dir = self.workspace / "agents" / "memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        # 代理记忆存储
        self.agent_memories: Dict[str, AgentMemory] = {}

        # 全局共享记忆
        self.shared_memory: List[Dict] = []

        # 加载现有记忆
        self._load_memories()

    def _load_memories(self):
        """加载所有代理记忆"""
        # 检查每个代理的记忆文件（跳过 shared.json，它是共享记忆列表）
        for memory_file in self.memory_dir.glob("*.json"):
            agent_name = memory_file.stem

            # 跳过共享记忆文件（它是列表，不是 AgentMemory 对象）
            if agent_name == "shared":
                continue

            try:
                with open(memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 确保数据是字典格式
                    if isinstance(data, dict):
                        self.agent_memories[agent_name] = AgentMemory.from_dict(data)
                    else:
                        print(f"[WARN] 代理记忆格式错误 {agent_name}: 期望字典，得到 {type(data).__name__}")
            except Exception as e:
                print(f"[WARN] 加载代理记忆失败 {agent_name}: {e}")

        # 加载全局共享记忆
        shared_file = self.memory_dir / "shared.json"
        if shared_file.exists():
            try:
                with open(shared_file, 'r', encoding='utf-8') as f:
                    self.shared_memory = json.load(f)
            except Exception as e:
                print(f"[WARN] 加载共享记忆失败: {e}")

    def get_agent_memory(self, agent_name: str) -> AgentMemory:
        """获取代理记忆"""
        if agent_name not in self.agent_memories:
            # 创建新代理记忆
            self.agent_memories[agent_name] = AgentMemory(
                agent_name=agent_name,
                agent_type=self._get_agent_type(agent_name)
            )
            self._save_agent_memory(agent_name)

        return self.agent_memories[agent_name]

    def _get_agent_type(self, agent_name: str) -> str:
        """获取代理类型"""
        # 根据代理名称推断类型
        type_map = {
            'architect': 'design',
            'planner': 'planning',
            'code_reviewer': 'review',
            'security_reviewer': 'security',
            'doc_writer': 'documentation',
            'engineer': 'implementation'
        }
        return type_map.get(agent_name, 'general')

    def _save_agent_memory(self, agent_name: str):
        """保存代理记忆"""
        if agent_name not in self.agent_memories:
            return

        memory_file = self.memory_dir / f"{agent_name}.json"
        with open(memory_file, 'w', encoding='utf-8', errors='replace') as f:
            json.dump(self.agent_memories[agent_name].to_dict(), f, ensure_ascii=False, indent=2, default=str)

    def save_shared_memory(self):
        """保存共享记忆"""
        shared_file = self.memory_dir / "shared.json"
        # 只保留最近1000条共享记忆
        memory_to_save = self.shared_memory[-1000:] if len(self.shared_memory) > 1000 else self.shared_memory
        with open(shared_file, 'w', encoding='utf-8', errors='replace') as f:
            json.dump(memory_to_save, f, ensure_ascii=False, indent=2, default=str)

    def add_to_shared(self, item: Dict):
        """添加到共享记忆"""
        item['timestamp'] = datetime.now(timezone.utc).isoformat()
        self.shared_memory.append(item)
        self.save_shared_memory()

    def search_shared(self, query: str) -> List[Dict]:
        """搜索共享记忆"""
        query_lower = query.lower()
        results = []

        for item in self.shared_memory:
            if query_lower in str(item).lower():
                score = str(item).lower().count(query_lower) * 0.1
                results.append({**item, 'score': score})

        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:20]

    def record_task_completion(self, agent_name: str, task: str, result: Dict):
        """记录任务完成"""
        memory = self.get_agent_memory(agent_name)
        memory.stats['tasks_completed'] += 1
        memory.stats['last_active'] = datetime.now(timezone.utc).isoformat()

        # 添加到工作记忆
        memory.add_work_item({
            'type': 'task_completed',
            'task': task,
            'result': result,
            'important': result.get('success', True)
        })

        # 添加到专业记忆（成功经验）
        if result.get('success', True):
            memory.add_professional_memory({
                'type': 'successful_task',
                'task': task,
                'approach': result.get('approach', ''),
                'lessons': result.get('lessons', '')
            })

        # 添加到共享记忆（跨代理可见）
        self.add_to_shared({
            'type': 'agent_task',
            'agent': agent_name,
            'task': task,
            'success': result.get('success', True)
        })

        self._save_agent_memory(agent_name)

    def sync_to_global(self):
        """将代理重要记忆同步到全局系统"""
        # 这会与 HomunculusMemory 同步
        from homunculus_memory import HomunculusMemory
        from homunculus_memory import Observation

        global_memory = HomunculusMemory(self.workspace)

        # 同步各代理的专业记忆到全局
        for agent_name, memory in self.agent_memories.items():
            # 只同步最近的重要记忆
            for item in memory.professional_memory[-10:]:
                if item.get('type') == 'successful_task':
                    obs = Observation(
                        timestamp=item['timestamp'],
                        event='agent_experience',
                        tool=f'agent:{agent_name}',
                        session='',
                        project_id=global_memory.project['id'],
                        project_name=global_memory.project['name'],
                        input=item.get('task', '')[:200],
                        output=item.get('approach', '')[:500],
                        cwd=str(self.workspace)
                    )
                    global_memory.add_observation(obs)

    def get_status_report(self) -> Dict:
        """获取所有代理记忆的状态报告"""
        report = {
            'total_agents': len(self.agent_memories),
            'shared_memory_count': len(self.shared_memory),
            'agents': {}
        }

        for agent_name, memory in self.agent_memories.items():
            report['agents'][agent_name] = memory.get_summary()

        return report

    def clear_all_working_memory(self):
        """清除所有代理的工作记忆（会话结束时调用）"""
        for memory in self.agent_memories.values():
            memory.clear_working_memory()
            self._save_agent_memory(memory.agent_name)


# 模块级单例
_instance = None

def get_agent_memory_manager() -> AgentMemoryManager:
    """获取代理记忆管理器单例"""
    global _instance
    if _instance is None:
        _instance = AgentMemoryManager()
    return _instance


# 测试
if __name__ == "__main__":
    manager = get_agent_memory_manager()

    print("=" * 60)
    print("代理记忆系统测试")
    print("=" * 60)
    print()

    # 测试获取代理记忆
    architect_memory = manager.get_agent_memory('architect')
    print(f"Architect 代理记忆:")
    print(f"  工作记忆: {len(architect_memory.working_memory)} 项")
    print(f"  专业记忆: {len(architect_memory.professional_memory)} 项")
    print()

    # 添加测试记忆
    architect_memory.add_work_item({
        'content': '设计了三层架构',
        'context': 'Web应用项目'
    })

    architect_memory.add_professional_memory({
        'type': 'lesson',
        'content': '微服务架构适合大规模应用',
        'context': '架构设计经验'
    })

    manager._save_agent_memory('architect')

    # 搜索测试
    results = architect_memory.search('架构')
    print(f"搜索 \"架构\" 找到 {len(results)} 条结果")
    for r in results[:3]:
        print(f"  - {r.get('source', 'unknown')}: {r.get('content', r.get('type', 'N/A'))}")
    print()

    # 状态报告
    status = manager.get_status_report()
    print(f"系统状态:")
    print(f"  代理数量: {status['total_agents']}")
    print(f"  共享记忆: {status['shared_memory_count']} 项")
