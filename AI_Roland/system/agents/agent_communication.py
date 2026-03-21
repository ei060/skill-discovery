#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI Roland Agent 协作通信协议

实现Agent间的请求/响应协作机制
"""

import sys
import os
import json
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import threading
import queue

# 修复Windows编码
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass


class MessageType(Enum):
    """消息类型"""

    # 请求类
    HELP_REQUEST = "help_request"           # 请求帮助
    QUERY = "query"                         # 查询信息
    SHARE_EXPERIENCE = "share_experience"   # 分享经验
    TASK_DELEGATION = "task_delegation"     # 任务委托

    # 响应类
    ACCEPT = "accept"                       # 接受请求
    DECLINE = "decline"                     # 拒绝请求
    PROVIDE_ANSWER = "provide_answer"       # 提供答案
    ACKNOWLEDGEMENT = "acknowledgement"     # 确认收到

    # 系统类
    BROADCAST = "broadcast"                 # 广播消息
    NOTIFICATION = "notification"           # 通知


class MessageStatus(Enum):
    """消息状态"""
    PENDING = "pending"         # 待处理
    DELIVERED = "delivered"     # 已送达
    ACCEPTED = "accepted"       # 已接受
    IN_PROGRESS = "in_progress" # 处理中
    COMPLETED = "completed"     # 已完成
    FAILED = "failed"          # 失败
    EXPIRED = "expired"         # 已过期


@dataclass
class AgentMessage:
    """Agent间通信消息"""

    # 基本信息
    msg_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    msg_type: str = MessageType.HELP_REQUEST.value
    status: str = MessageStatus.PENDING.value

    # 参与者
    from_agent: str = ""
    to_agent: Optional[str] = None  # None表示广播/请求所有人

    # 内容
    subject: str = ""               # 消息主题
    content: Dict = field(default_factory=dict)
    context: Dict = field(default_factory=dict)  # 上下文信息

    # 能力要求（用于匹配）
    required_capabilities: List[str] = field(default_factory=list)
    required_expertise: List[str] = field(default_factory=list)

    # 时间戳
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    expires_at: Optional[str] = None

    # 响应
    response_from: Optional[str] = None
    response_content: Optional[Dict] = None

    # 优先级
    priority: int = 5  # 1-10, 10最高

    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'AgentMessage':
        """从字典创建"""
        return cls(**data)

    def is_expired(self) -> bool:
        """检查是否过期"""
        if not self.expires_at:
            return False
        try:
            expires = datetime.fromisoformat(self.expires_at)
            return datetime.now(timezone.utc) > expires
        except:
            return False

    def add_context(self, key: str, value: Any):
        """添加上下文"""
        self.context[key] = value
        return self


@dataclass
class AgentCapability:
    """Agent能力描述"""

    agent_name: str
    agent_type: str

    # 专业领域
    expertise: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)

    # 技能水平（0-100）
    skill_level: int = 50

    # 可用性
    availability: float = 1.0  # 0.0-1.0, 1.0完全可用

    # 当前负载
    current_load: int = 0
    max_capacity: int = 10

    # 统计
    tasks_completed: int = 0
    avg_response_time: float = 0.0  # 秒
    success_rate: float = 1.0

    # 更新时间
    last_updated: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def can_handle(self, required_capabilities: List[str], required_expertise: List[str]) -> float:
        """计算是否能处理请求，返回匹配分数（0-1）"""

        score = 0.0

        # 能力匹配
        if required_capabilities:
            matched = sum(1 for cap in required_capabilities if cap in self.capabilities)
            score += (matched / len(required_capabilities)) * 0.5

        # 专业领域匹配
        if required_expertise:
            matched = sum(1 for exp in required_expertise if exp in self.expertise)
            score += (matched / len(required_expertise)) * 0.3

        # 技能水平
        score += (self.skill_level / 100) * 0.1

        # 可用性
        score += self.availability * 0.1

        return min(score, 1.0)

    def is_available(self) -> bool:
        """检查是否可用"""
        return (self.availability > 0.3 and
                self.current_load < self.max_capacity)


class CollaborationMatcher:
    """协作匹配器 - 选择最合适的Agent响应请求"""

    def __init__(self):
        self.match_history: List[Dict] = []

    def find_best_match(
        self,
        message: AgentMessage,
        capabilities: Dict[str, AgentCapability]
    ) -> Optional[str]:
        """找到最匹配的Agent"""

        candidates = []

        for agent_name, cap in capabilities.items():
            # 跳过发送者自己
            if agent_name == message.from_agent:
                continue

            # 跳过指定的接收者（如果有）
            if message.to_agent and agent_name != message.to_agent:
                continue

            # 检查可用性
            if not cap.is_available():
                continue

            # 计算匹配分数
            score = cap.can_handle(message.required_capabilities, message.required_expertise)

            if score > 0.3:  # 最低匹配阈值
                candidates.append((agent_name, score))

        if not candidates:
            return None

        # 按分数排序
        candidates.sort(key=lambda x: x[1], reverse=True)

        # 记录匹配历史
        best_match = candidates[0][0]
        self.match_history.append({
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'from': message.from_agent,
            'to': best_match,
            'subject': message.subject,
            'score': candidates[0][1],
            'candidates': len(candidates)
        })

        return best_match

    def get_statistics(self) -> Dict:
        """获取匹配统计"""
        if not self.match_history:
            return {'total_matches': 0}

        return {
            'total_matches': len(self.match_history),
            'recent_matches': self.match_history[-10:],
            'avg_score': sum(m['score'] for m in self.match_history) / len(self.match_history)
        }


class CollaborationHub:
    """协作中心 - 管理Agent间的所有通信"""

    def __init__(self, workspace: Optional[Path] = None):
        if workspace is None:
            workspace = Path(__file__).parent.parent.parent

        self.workspace = Path(workspace)
        self.agents_dir = self.workspace / "system" / "agents"
        self.agents_dir.mkdir(parents=True, exist_ok=True)

        # 能力注册表
        self.capabilities_file = self.agents_dir / "capabilities.json"
        self.capabilities: Dict[str, AgentCapability] = {}
        self._load_capabilities()

        # 消息队列
        self.message_queue: queue.Queue = queue.Queue()

        # 消息历史
        self.messages_file = self.agents_dir / "messages.json"
        self.message_history: List[AgentMessage] = []
        self._load_messages()

        # 匹配器
        self.matcher = CollaborationMatcher()

        # 消息处理器注册
        self.message_handlers: Dict[str, List[Callable]] = {}

        # 后台处理线程
        self._running = False
        self._process_thread: Optional[threading.Thread] = None

    def _load_capabilities(self):
        """加载能力注册表"""
        if self.capabilities_file.exists():
            try:
                with open(self.capabilities_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for agent_name, cap_data in data.items():
                        self.capabilities[agent_name] = AgentCapability(**cap_data)
            except Exception as e:
                print(f"[WARN] 加载能力表失败: {e}")

    def _save_capabilities(self):
        """保存能力注册表"""
        with open(self.capabilities_file, 'w', encoding='utf-8') as f:
            data = {
                name: asdict(cap)
                for name, cap in self.capabilities.items()
            }
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

    def _load_messages(self):
        """加载消息历史"""
        if self.messages_file.exists():
            try:
                with open(self.messages_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.message_history = [
                        AgentMessage.from_dict(msg) for msg in data
                    ]
            except Exception as e:
                print(f"[WARN] 加载消息历史失败: {e}")

    def _save_messages(self):
        """保存消息历史"""
        # 只保留最近1000条
        messages_to_save = self.message_history[-1000:]
        with open(self.messages_file, 'w', encoding='utf-8') as f:
            data = [msg.to_dict() for msg in messages_to_save]
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

    def register_capability(self, capability: AgentCapability):
        """注册Agent能力"""
        capability.last_updated = datetime.now(timezone.utc).isoformat()
        self.capabilities[capability.agent_name] = capability
        self._save_capabilities()
        print(f"[INFO] 注册能力: {capability.agent_name} ({capability.agent_type})")

    def update_capability(self, agent_name: str, **updates):
        """更新Agent能力"""
        if agent_name in self.capabilities:
            cap = self.capabilities[agent_name]
            for key, value in updates.items():
                if hasattr(cap, key):
                    setattr(cap, key, value)
            cap.last_updated = datetime.now(timezone.utc).isoformat()
            self._save_capabilities()

    def send_message(self, message: AgentMessage) -> bool:
        """发送消息"""

        # 检查发送者是否已注册
        if message.from_agent not in self.capabilities:
            print(f"[WARN] 未注册的Agent: {message.from_agent}")
            return False

        # 如果没有指定接收者，自动匹配
        if not message.to_agent:
            best_match = self.matcher.find_best_match(message, self.capabilities)
            if not best_match:
                print(f"[WARN] 找不到合适的Agent响应: {message.subject}")
                return False
            message.to_agent = best_match

        # 更新状态
        message.status = MessageStatus.DELIVERED.value

        # 添加到历史
        self.message_history.append(message)
        self._save_messages()

        # 放入队列
        self.message_queue.put(message)

        print(f"[INFO] 消息发送: {message.from_agent} → {message.to_agent}: {message.subject}")
        return True

    def respond_to_message(self, msg_id: str, response_from: str, response_content: Dict) -> bool:
        """响应消息"""

        # 找到原消息
        original_msg = None
        for msg in self.message_history:
            if msg.msg_id == msg_id:
                original_msg = msg
                break

        if not original_msg:
            print(f"[WARN] 找不到消息: {msg_id}")
            return False

        # 更新原消息
        original_msg.response_from = response_from
        original_msg.response_content = response_content
        original_msg.status = MessageStatus.COMPLETED.value

        # 创建响应消息
        response = AgentMessage(
            msg_type=MessageType.PROVIDE_ANSWER.value,
            from_agent=response_from,
            to_agent=original_msg.from_agent,
            subject=f"RE: {original_msg.subject}",
            content=response_content,
            context={'original_msg_id': msg_id}
        )

        self.message_history.append(response)
        self._save_messages()

        print(f"[INFO] 响应发送: {response_from} → {original_msg.from_agent}")
        return True

    def broadcast_experience(self, from_agent: str, experience: Dict) -> int:
        """广播经验分享"""

        if from_agent not in self.capabilities:
            print(f"[WARN] 未注册的Agent: {from_agent}")
            return 0

        # 创建广播消息
        message = AgentMessage(
            msg_type=MessageType.SHARE_EXPERIENCE.value,
            from_agent=from_agent,
            to_agent=None,  # 广播
            subject=f"经验分享: {experience.get('title', '')}",
            content=experience,
            priority=3
        )

        # 发送给所有相关Agent
        sent_count = 0
        for agent_name in self.capabilities:
            if agent_name == from_agent:
                continue

            msg_copy = AgentMessage(**message.to_dict())
            msg_copy.to_agent = agent_name
            if self.send_message(msg_copy):
                sent_count += 1

        return sent_count

    def get_pending_messages(self, agent_name: str) -> List[AgentMessage]:
        """获取Agent的待处理消息"""

        pending = []
        for msg in self.message_history:
            if (msg.to_agent == agent_name and
                msg.status in [MessageStatus.DELIVERED.value, MessageStatus.PENDING.value]):
                pending.append(msg)

        return pending

    def get_conversation(self, agent1: str, agent2: str) -> List[AgentMessage]:
        """获取两个Agent的对话历史"""

        conversation = []
        for msg in self.message_history:
            if ((msg.from_agent == agent1 and msg.to_agent == agent2) or
                (msg.from_agent == agent2 and msg.to_agent == agent1)):
                conversation.append(msg)

        return conversation

    def get_statistics(self) -> Dict:
        """获取统计信息"""

        # 消息统计
        total_messages = len(self.message_history)
        by_type = {}
        by_status = {}

        for msg in self.message_history:
            by_type[msg.msg_type] = by_type.get(msg.msg_type, 0) + 1
            by_status[msg.status] = by_status.get(msg.status, 0) + 1

        # Agent统计
        agent_stats = {}
        for agent_name, cap in self.capabilities.items():
            agent_stats[agent_name] = {
                'type': cap.agent_type,
                'skill_level': cap.skill_level,
                'availability': cap.availability,
                'tasks_completed': cap.tasks_completed,
                'success_rate': cap.success_rate
            }

        return {
            'total_messages': total_messages,
            'by_type': by_type,
            'by_status': by_status,
            'registered_agents': len(self.capabilities),
            'agent_stats': agent_stats,
            'matcher_stats': self.matcher.get_statistics()
        }

    def start_background_processor(self):
        """启动后台消息处理器"""
        if self._running:
            return

        self._running = True
        self._process_thread = threading.Thread(target=self._process_messages, daemon=True)
        self._process_thread.start()
        print("[INFO] 协作中心后台处理器已启动")

    def _process_messages(self):
        """后台处理消息"""
        while self._running:
            try:
                # 从队列获取消息（超时1秒）
                message = self.message_queue.get(timeout=1)

                # 触发注册的处理器
                msg_type = message.msg_type
                if msg_type in self.message_handlers:
                    for handler in self.message_handlers[msg_type]:
                        try:
                            handler(message)
                        except Exception as e:
                            print(f"[ERROR] 处理消息失败: {e}")

            except queue.Empty:
                continue
            except Exception as e:
                print(f"[ERROR] 消息处理错误: {e}")

    def stop_background_processor(self):
        """停止后台处理器"""
        self._running = False
        if self._process_thread:
            self._process_thread.join(timeout=5)
        print("[INFO] 协作中心后台处理器已停止")

    def register_handler(self, msg_type: str, handler: Callable):
        """注册消息处理器"""
        if msg_type not in self.message_handlers:
            self.message_handlers[msg_type] = []
        self.message_handlers[msg_type].append(handler)


# 模块级单例
_instance = None

def get_collaboration_hub() -> CollaborationHub:
    """获取协作中心单例"""
    global _instance
    if _instance is None:
        _instance = CollaborationHub()
    return _instance


# 测试
if __name__ == "__main__":
    print("\n" + "="*60)
    print("Agent 协作通信协议测试")
    print("="*60)

    hub = get_collaboration_hub()

    # 注册Agent能力
    print("\n1. 注册Agent能力")
    hub.register_capability(AgentCapability(
        agent_name="python_reviewer",
        agent_type="language_reviewer",
        expertise=["python", "django", "flask", "async"],
        capabilities=["code_review", "type_checking", "pep8_check"],
        skill_level=85
    ))

    hub.register_capability(AgentCapability(
        agent_name="database_reviewer",
        agent_type="specialist",
        expertise=["sql", "postgres", "mysql", "optimization"],
        capabilities=["query_review", "index_optimization", "schema_design"],
        skill_level=90
    ))

    # 发送请求消息
    print("\n2. 发送协作请求")
    help_request = AgentMessage(
        from_agent="code_reviewer",
        subject="需要数据库专家帮助",
        content={
            "problem": "发现慢查询，需要优化建议",
            "query": "SELECT * FROM users WHERE...",
            "context": "Web应用，用户表100万行"
        },
        required_capabilities=["query_review"],
        required_expertise=["sql", "optimization"],
        priority=8
    )

    hub.send_message(help_request)

    # 查看统计
    print("\n3. 系统统计")
    stats = hub.get_statistics()
    print(f"  注册Agent: {stats['registered_agents']}")
    print(f"  总消息数: {stats['total_messages']}")
    print(f"  消息类型: {stats['by_type']}")
    print(f"  匹配统计: {stats['matcher_stats']}")

    # 查看待处理消息
    print("\n4. 待处理消息")
    pending = hub.get_pending_messages("database_reviewer")
    for msg in pending:
        print(f"  来自: {msg.from_agent}")
        print(f"  主题: {msg.subject}")
        print(f"  优先级: {msg.priority}")

    print("\n✓ 测试完成")
