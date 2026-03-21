#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI Roland Agent 桥接层

连接ECC执行和AI Roland记忆系统，让无记忆的ECC agent获得记忆能力
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

# 修复Windows编码
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

# 添加系统路径
system_path = Path(__file__).parent
sys.path.insert(0, str(system_path))

from agent_memory import get_agent_memory_manager, AgentMemory
from agent_communication import get_collaboration_hub, AgentMessage


class AgentBridge:
    """桥接ECC执行和AI Roland记忆"""

    def __init__(self, workspace: Optional[Path] = None):
        if workspace is None:
            workspace = Path(__file__).parent.parent.parent

        self.workspace = Path(workspace)
        self.memory_manager = get_agent_memory_manager()
        self.collab_hub = get_collaboration_hub()

        # ECC agents配置路径
        self.ecc_agents_dir = Path.home() / ".claude" / "agents"

        # 统计信息
        self.stats = {
            'total_executions': 0,
            'memory_hits': 0,
            'experiences_saved': 0,
            'collaborations_triggered': 0
        }

    def map_ecc_to_roland(self, ecc_agent_name: str) -> str:
        """将ECC agent名称映射到AI Roland agent名称"""

        mapping = {
            'code-reviewer': 'code_reviewer',
            'planner': 'planner',
            'architect': 'architect',
            'security-reviewer': 'security_reviewer',
            'doc-updater': 'doc_writer',
            'tdd-guide': 'tdd_guide',
            'e2e-runner': 'e2e_runner',
            'refactor-cleaner': 'refactor_cleaner',
            'verification-before-completion': 'verification_before_completion',
            'python-reviewer': 'python_reviewer',
            'go-reviewer': 'go_reviewer',
            'kotlin-reviewer': 'kotlin_reviewer',
            'database-reviewer': 'database_reviewer',
            'build-error-resolver': 'engineer',
            'chief-of-staff': 'planner',
            'harness-optimizer': 'tdd_guide',
            'loop-operator': 'planner',
            'go-build-resolver': 'go_reviewer',
            'kotlin-build-resolver': 'kotlin_reviewer'
        }

        return mapping.get(ecc_agent_name, ecc_agent_name.replace('-', '_'))

    def prepare_execution_context(
        self,
        agent_name: str,
        task: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """准备执行上下文（加载记忆和协作消息）"""

        # 映射agent名称
        roland_agent_name = self.map_ecc_to_roland(agent_name)

        # 获取agent记忆
        memory = self.memory_manager.get_agent_memory(roland_agent_name)

        # 准备上下文
        execution_context = {
            'agent_name': agent_name,
            'roland_agent_name': roland_agent_name,
            'task': task,
            'user_context': context or {},
            'memory_context': {},
            'collaboration_context': []
        }

        # 1. 加载专业记忆（最近5条）
        recent_professional = memory.professional_memory[-5:]
        if recent_professional:
            execution_context['memory_context']['recent_experiences'] = [
                {
                    'type': exp.get('type'),
                    'content': exp.get('content', exp.get('task', ''))[:200],
                    'timestamp': exp.get('timestamp')
                }
                for exp in recent_professional
            ]
            self.stats['memory_hits'] += 1

        # 2. 加载相关模式（前5条）
        relevant_patterns = memory.patterns[-5:]
        if relevant_patterns:
            execution_context['memory_context']['best_practices'] = [
                {
                    'name': pattern.get('name'),
                    'description': pattern.get('description'),
                    'example': pattern.get('example', '')[:100]
                }
                for pattern in relevant_patterns
            ]

        # 3. 加载偏好设置
        if memory.preferences:
            execution_context['memory_context']['preferences'] = memory.preferences

        # 4. 检查待处理的协作消息
        pending_messages = self.collab_hub.get_pending_messages(roland_agent_name)
        if pending_messages:
            execution_context['collaboration_context'] = [
                {
                    'from': msg.from_agent,
                    'subject': msg.subject,
                    'content': msg.content,
                    'priority': msg.priority,
                    'msg_id': msg.msg_id
                }
                for msg in pending_messages[:3]  # 只取前3条
            ]
            self.stats['collaborations_triggered'] += len(pending_messages)

        # 5. 统计信息
        execution_context['memory_context']['stats'] = memory.get_summary()

        return execution_context

    def format_memory_prompt(self, execution_context: Dict) -> str:
        """将记忆上下文格式化为提示词补充"""

        memory_ctx = execution_context['memory_context']
        prompt_parts = []

        # 经验部分
        if 'recent_experiences' in memory_ctx:
            prompt_parts.append("\n## 相关经验（来自你的记忆）\n")
            for i, exp in enumerate(memory_ctx['recent_experiences'], 1):
                prompt_parts.append(f"{i}. {exp['content']}")

        # 最佳实践
        if 'best_practices' in memory_ctx:
            prompt_parts.append("\n## 最佳实践（来自你的记忆）\n")
            for pattern in memory_ctx['best_practices']:
                prompt_parts.append(f"- **{pattern['name']}**: {pattern['description']}")
                if pattern.get('example'):
                    prompt_parts.append(f"  示例: {pattern['example']}")

        # 偏好设置
        if 'preferences' in memory_ctx:
            prompt_parts.append("\n## 你的工作偏好\n")
            for key, value in memory_ctx['preferences'].items():
                prompt_parts.append(f"- {key}: {value}")

        # 协作消息
        if execution_context.get('collaboration_context'):
            prompt_parts.append("\n## 待处理的协作请求\n")
            for msg in execution_context['collaboration_context']:
                priority_mark = "🔴" if msg['priority'] >= 8 else "🟡" if msg['priority'] >= 5 else "🟢"
                prompt_parts.append(
                    f"{priority_mark} **来自{msg['from']}**: {msg['subject']}\n"
                    f"   内容: {str(msg['content'])[:150]}"
                )

        if prompt_parts:
            return "\n".join(prompt_parts) + "\n"
        return ""

    def execute_with_memory(
        self,
        agent_name: str,
        task: str,
        context: Optional[Dict] = None,
        execution_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """使用记忆增强执行agent"""

        self.stats['total_executions'] += 1

        # 1. 准备执行上下文
        exec_ctx = self.prepare_execution_context(agent_name, task, context)

        # 2. 格式化记忆提示词
        memory_prompt = self.format_memory_prompt(exec_ctx)

        # 3. 构建增强的任务描述
        enhanced_task = task
        if memory_prompt:
            enhanced_task = f"{task}\n\n{memory_prompt}"

        # 4. 记录开始时间
        start_time = datetime.now(timezone.utc)

        # 5. 执行（如果有回调，使用回调；否则返回增强任务供手动执行）
        if execution_callback:
            result = execution_callback(agent_name, enhanced_task, exec_ctx)
        else:
            # 返回增强任务，供外部调用ECC
            result = {
                'success': True,
                'enhanced_task': enhanced_task,
                'execution_context': exec_ctx,
                'message': '任务已增强记忆上下文，请使用enhanced_task调用ECC agent'
            }

        # 6. 记录执行时间
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()

        # 7. 如果有实际执行结果，保存到记忆
        if result.get('success') and 'output' in result:
            self._save_experience(
                exec_ctx['roland_agent_name'],
                task,
                result,
                duration
            )

        return result

    def _save_experience(
        self,
        roland_agent_name: str,
        task: str,
        result: Dict,
        duration: float
    ):
        """保存执行经验到记忆"""

        memory = self.memory_manager.get_agent_memory(roland_agent_name)

        # 判断是否有价值保存
        output = result.get('output', '')
        if not output or len(output) < 50:
            return

        # 提取经验
        experience = {
            'type': 'task_execution',
            'task': task,
            'output_summary': output[:500],
            'duration_seconds': duration,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'success': result.get('success', True)
        }

        # 保存到专业记忆
        memory.add_professional_memory(experience)
        self.memory_manager._save_agent_memory(roland_agent_name)
        self.stats['experiences_saved'] += 1

    def share_experience(
        self,
        agent_name: str,
        experience: Dict
    ) -> int:
        """分享经验给其他agent"""

        roland_agent_name = self.map_ecc_to_roland(agent_name)

        # 通过协作中心广播
        sent_count = self.collab_hub.broadcast_experience(
            roland_agent_name,
            experience
        )

        return sent_count

    def request_collaboration(
        self,
        from_agent: str,
        subject: str,
        problem: Dict,
        required_capabilities: List[str] = None,
        required_expertise: List[str] = None,
        priority: int = 5
    ) -> Optional[str]:
        """请求其他agent协作"""

        roland_agent_name = self.map_ecc_to_roland(from_agent)

        # 创建协作请求
        message = AgentMessage(
            from_agent=roland_agent_name,
            subject=subject,
            content=problem,
            required_capabilities=required_capabilities or [],
            required_expertise=required_expertise or [],
            priority=priority
        )

        # 发送请求
        success = self.collab_hub.send_message(message)

        if success:
            return message.to_agent
        return None

    def respond_to_collaboration(
        self,
        agent_name: str,
        msg_id: str,
        response: Dict
    ) -> bool:
        """响应协作请求"""

        roland_agent_name = self.map_ecc_to_roland(agent_name)

        return self.collab_hub.respond_to_message(
            msg_id,
            roland_agent_name,
            response
        )

    def get_agent_stats(self, agent_name: str) -> Dict:
        """获取agent统计信息"""

        roland_agent_name = self.map_ecc_to_roland(agent_name)
        memory = self.memory_manager.get_agent_memory(roland_agent_name)

        return {
            'memory': memory.get_summary(),
            'bridge': self.stats
        }

    def get_system_stats(self) -> Dict:
        """获取桥接系统统计"""

        return {
            'bridge': self.stats,
            'memory_system': self.memory_manager.get_status_report(),
            'collaboration_system': self.collab_hub.get_statistics()
        }


# 模块级单例
_instance = None

def get_agent_bridge() -> AgentBridge:
    """获取桥接层单例"""
    global _instance
    if _instance is None:
        _instance = AgentBridge()
    return _instance


# 使用示例
if __name__ == "__main__":
    print("\n" + "="*70)
    print("Agent 桥接层测试")
    print("="*70)

    bridge = get_agent_bridge()

    # 测试1: 准备执行上下文
    print("\n1. 测试：准备code-reviewer的执行上下文")
    exec_ctx = bridge.prepare_execution_context(
        "code-reviewer",
        "审查用户认证代码",
        {"language": "python"}
    )

    print(f"  Agent: {exec_ctx['agent_name']} → {exec_ctx['roland_agent_name']}")
    print(f"  任务: {exec_ctx['task']}")
    print(f"  经验数: {len(exec_ctx['memory_context'].get('recent_experiences', []))}")
    print(f"  模式数: {len(exec_ctx['memory_context'].get('best_practices', []))}")
    print(f"  协作消息: {len(exec_ctx['collaboration_context'])}")

    # 测试2: 格式化记忆提示词
    print("\n2. 测试：格式化记忆提示词")
    memory_prompt = bridge.format_memory_prompt(exec_ctx)
    print(f"  提示词长度: {len(memory_prompt)} 字符")
    print(f"  前200字符:\n{memory_prompt[:200]}...")

    # 测试3: 执行with记忆
    print("\n3. 测试：增强任务")
    result = bridge.execute_with_memory(
        "code-reviewer",
        "审查这段Django代码的安全性"
    )

    if result['success']:
        print(f"  ✓ 任务已增强")
        print(f"  原始任务长度: {len('审查这段Django代码的安全性')}")
        print(f"  增强任务长度: {len(result['enhanced_task'])}")
        print(f"  增加了 {len(result['enhanced_task']) - len('审查这段Django代码的安全性')} 字符")

    # 测试4: 统计信息
    print("\n4. 系统统计")
    stats = bridge.get_system_stats()
    print(f"  总执行次数: {stats['bridge']['total_executions']}")
    print(f"  记忆命中: {stats['bridge']['memory_hits']}")
    print(f"  协作触发: {stats['bridge']['collaborations_triggered']}")
    print(f"  注册agent数: {stats['memory_system']['total_agents']}")
    print(f"  共享记忆数: {stats['memory_system']['shared_memory_count']}")

    print("\n✓ 测试完成")
