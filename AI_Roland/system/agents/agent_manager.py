"""
AI Roland 代理系统

借鉴 ECC 的代理格式，为 AI_Roland 创建标准化的子代理系统
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass


@dataclass
class AgentConfig:
    """代理配置"""
    name: str
    description: str
    tools: List[str]
    model: str = "sonnet"  # haiku/sonnet/opus
    system_prompt: str = ""
    trigger_keywords: List[str] = None
    auto_activate: bool = False
    skill_dependencies: List[str] = None

    def __post_init__(self):
        if self.trigger_keywords is None:
            self.trigger_keywords = []
        if self.skill_dependencies is None:
            self.skill_dependencies = []


class AgentManager:
    """代理管理器"""

    def __init__(self):
        self.agents_dir = Path(__file__).parent.parent / "agents"
        self.agents_dir.mkdir(exist_ok=True)
        self.registry_file = self.agents_dir / "agents_registry.json"
        self.agents: Dict[str, AgentConfig] = {}
        self._load_agents()

        # 注册内置代理
        for name, config in BUILT_IN_AGENTS.items():
            if name not in self.agents:
                self.agents[name] = config

    def _load_agents(self):
        """加载代理配置"""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for name, config in data.items():
                    self.agents[name] = AgentConfig(**config)
            except Exception as e:
                print(f"[WARN] 加载代理注册表失败: {e}")

        # 扫描代理目录
        self._scan_agents()

    def _scan_agents(self):
        """扫描代理目录"""
        # 检查是否有 .md 代理文件
        for agent_file in self.agents_dir.glob("*.md"):
            self._register_agent_from_file(agent_file)

    def _register_agent_from_file(self, agent_file: Path):
        """从 Markdown 文件注册代理"""
        try:
            content = agent_file.read_text(encoding='utf-8')

            # 解析 YAML frontmatter
            import re
            yaml_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if yaml_match:
                yaml_content = yaml_match.group(1)
                import yaml
                frontmatter = yaml.safe_load(yaml_content)

                config = AgentConfig(
                    name=frontmatter.get('name', agent_file.stem),
                    description=frontmatter.get('description', ''),
                    tools=frontmatter.get('tools', []),
                    model=frontmatter.get('model', 'sonnet'),
                    system_prompt=content,  # 剩余内容作为系统提示
                    trigger_keywords=frontmatter.get('trigger_keywords', []),
                    auto_activate=frontmatter.get('auto_activate', False),
                    skill_dependencies=frontmatter.get('skill_dependencies', [])
                )
                self.agents[config.name] = config
        except Exception as e:
            print(f"[WARN] 解析代理文件失败 {agent_file}: {e}")

    def get_agent(self, name: str) -> Optional[AgentConfig]:
        """获取代理配置"""
        return self.agents.get(name)

    def list_agents(self) -> List[AgentConfig]:
        """列出所有代理"""
        return list(self.agents.values())

    def find_agent_by_keywords(self, text: str) -> Optional[AgentConfig]:
        """根据关键词自动选择代理"""
        text_lower = text.lower()

        # 检查触发关键词
        for agent in self.agents.values():
            if agent.auto_activate:
                for keyword in agent.trigger_keywords:
                    if keyword.lower() in text_lower:
                        return agent

        return None

    def suggest_agent(self, task: str) -> List[str]:
        """
        根据任务建议合适的代理

        Args:
            task: 任务描述

        Returns:
            建议的代理名称列表
        """
        task_lower = task.lower()
        suggested = []

        for agent in self.agents.values():
            # 检查触发关键词
            for keyword in agent.trigger_keywords:
                if keyword.lower() in task_lower:
                    suggested.append(agent.name)
                    break

        return suggested

    def delegate(self, agent_name: str, task: str, context: dict = None) -> dict:
        """
        委派任务给代理（简化版本，实际执行由调用者处理）

        Args:
            agent_name: 代理名称
            task: 任务描述
            context: 上下文信息

        Returns:
            代理配置和任务信息
        """
        agent = self.get_agent(agent_name)
        if not agent:
            return {"error": f"Agent {agent_name} not found"}

        return {
            "agent": agent.name,
            "description": agent.description,
            "model": agent.model,
            "tools": agent.tools,
            "task": task,
            "context": context or {},
            "system_prompt": agent.system_prompt
        }

    def save_registry(self):
        """保存代理注册表"""
        data = {}
        for name, config in self.agents.items():
            data[name] = {
                "name": config.name,
                "description": config.description,
                "tools": config.tools,
                "model": config.model,
                "system_prompt": config.system_prompt,
                "trigger_keywords": config.trigger_keywords,
                "auto_activate": config.auto_activate,
                "skill_dependencies": config.skill_dependencies
            }

        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


# 内置代理定义

BUILT_IN_AGENTS = {
    "planner": AgentConfig(
        name="planner",
        description="规划和设计专家，负责任务分解和实施计划",
        tools=["Read", "Grep", "Glob"],
        model="opus",
        auto_activate=True,
        trigger_keywords=["规划", "设计", "重构", "实现", "计划", "架构"],
        system_prompt="""你是一位专家规划师，专注于创建可执行的实施计划。

## 你的职责
- 分析需求并创建详细的实施计划
- 将复杂功能分解为可管理的步骤
- 识别依赖关系和潜在风险
- 建议最佳实施顺序
- 考虑边界情况和错误场景

## 规划流程

1. **需求分析**
   - 完全理解功能请求
   - 识别成功标准
   - 列出假设和约束

2. **架构审查**
   - 分析现有代码库结构
   - 识别受影响的组件
   - 考虑可重用的模式

3. **步骤分解**
   - 创建详细步骤，包括：
     - 具体操作
     - 文件路径和位置
     - 步骤间的依赖关系
     - 复杂度评估
     - 潜在风险

4. **实施顺序**
   - 按依赖关系排序
   - 分组相关变更
   - 最小化上下文切换
   - 支持增量测试
"""
    ),

    "architect": AgentConfig(
        name="architect",
        description="软件架构专家，负责系统设计、可扩展性和技术决策",
        tools=["Read", "Grep", "Glob"],
        model="opus",
        auto_activate=True,
        trigger_keywords=["架构", "设计", "可扩展", "技术决策", "设计模式"],
        system_prompt="""你是一位高级软件架构师，专注于可扩展、可维护的系统设计。

## 你的职责
- 设计新功能的系统架构
- 评估技术权衡
- 推荐模式和最佳实践
- 识别可扩展性瓶颈
- 为未来增长做规划

## 架构原则

### 1. 模块化 & 关注点分离
- 单一职责原则
- 高内聚、低耦合
- 组件间接口清晰
- 独立可部署

### 2. 可扩展性
- 水平扩展能力
- 无状态设计（尽可能）
- 高效数据库查询
- 缓存策略
- 负载均衡考虑

### 3. 可维护性
- 清晰的代码组织
- 一致的模式
- 全面的文档
- 易于测试
- 简单易懂

### 4. 安全性
- 深度防御
- 最小权限原则
- 边界输入验证
- 默认安全
- 审计跟踪
"""
    ),

    "code_reviewer": AgentConfig(
        name="code_reviewer",
        description="代码审查专家，负责代码质量、最佳实践和潜在问题识别",
        tools=["Read", "Grep"],
        model="sonnet",
        auto_activate=True,
        trigger_keywords=["审查", "review", "代码质量", "bug", "优化"],
        system_prompt="""你是一位代码审查专家，专注于代码质量和最佳实践。

## 审查重点

1. **正确性**
   - 逻辑错误
   - 边界条件处理
   - 错误处理

2. **安全性**
   - 注入漏洞
   - 权限检查
   - 敏感数据处理

3. **性能**
   - 算法效率
   - 资源使用
   - 潜在瓶颈

4. **可维护性**
   - 代码清晰度
   - 命名规范
   - 文档完整性

5. **测试覆盖**
   - 单元测试
   - 边界情况
   - 集成测试
"""
    ),

    "security_reviewer": AgentConfig(
        name="security_reviewer",
        description="安全审查专家，负责识别安全漏洞和风险",
        tools=["Read", "Grep"],
        model="sonnet",
        auto_activate=True,
        trigger_keywords=["安全", "漏洞", "攻击", "权限", "认证"],
        system_prompt="""你是一位安全审查专家，专注于识别安全漏洞和风险。

## 审查重点

1. **常见漏洞**
   - OWASP Top 10
   - SQL 注入
   - XSS
   - CSRF
   - 认证绕过

2. **代码安全**
   - 输入验证
   - 输出编码
   - 加密实践
   - 会话管理

3. **权限控制**
   - 访问控制
   - 权限检查
   - 数据隔离

4. **数据处理**
   - 敏感数据保护
   - 日志记录
   - 数据传输加密
"""
    ),

    "doc_writer": AgentConfig(
        name="doc_writer",
        description="文档写作专家，负责生成技术文档和使用指南",
        tools=["Read", "Grep"],
        model="sonnet",
        auto_activate=True,
        trigger_keywords=["文档", "doc", "README", "指南", "说明"],
        system_prompt="""你是一位技术文档写作专家，专注于创建清晰、完整的技术文档。

## 文档类型

1. **API 文档**
   - 端点说明
   - 请求/响应格式
   - 认证方式
   - 示例代码

2. **架构文档**
   - 系统设计
   - 组件关系
   - 数据流图
   - 部署方案

3. **用户指南**
   - 安装步骤
   - 配置说明
   - 使用示例
   - 故障排除

4. **开发文档**
   - 代码结构
   - 开发规范
   - 测试方法
   - 部署流程

## 写作原则

- 清晰简洁
- 结构化
- 完整性
- 示例驱动
"""
    ),
}


def get_agent_manager() -> AgentManager:
    """获取代理管理器"""
    return AgentManager()


if __name__ == "__main__":
    manager = get_agent_manager()
    manager.save_registry()

    print("=== AI Roland 代理系统 ===")
    print(f"已注册 {len(manager.agents)} 个代理:")
    for agent in manager.list_agents():
        print(f"  - {agent.name}: {agent.description}")
