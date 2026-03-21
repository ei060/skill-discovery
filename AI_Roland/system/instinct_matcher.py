#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI Roland v2.0 - 本能匹配器

将 Claude 的决策与 AI Roland 的本能系统连接起来
实现真正的智能技能选择
"""

import sys
import os
import io
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse

# 修复 Windows 编码
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

# 添加系统路径
system_path = Path(__file__).parent
sys.path.insert(0, str(system_path))

from homunculus_memory import HomunculusMemory, Observation, Instinct
from datetime import datetime
from skills.skill_manager import SkillManager
from agents.agent_manager import AgentManager


# 模块级单例
_instance = None


def get_instinct_matcher():
    """获取本能匹配器单例"""
    global _instance
    if _instance is None:
        _instance = InstinctMatcher()
    return _instance


class InstinctMatcher:
    """本能匹配器 - 连接决策与本能"""

    def __init__(self):
        self.memory = HomunculusMemory()
        self.skill_manager = SkillManager()
        self.agent_manager = AgentManager()
        self.workspace = Path(__file__).parent.parent

    def match_for_context(self, context: Dict) -> List[Dict]:
        """根据上下文匹配相关本能"""
        user_input = context.get('user_input', '')
        current_url = context.get('url', '')
        mentioned_tools = context.get('mentioned_tools', [])

        results = []

        # 1. 直接关键词匹配
        keywords = self._extract_keywords(user_input + ' ' + current_url)
        for keyword in keywords:
            instincts = self.memory.search(keyword, top_k=3)
            for r in instincts:
                results.append({
                    'instinct': r['instinct'],
                    'score': r['score'],
                    'source': 'keyword_match',
                    'keyword': keyword
                })

        # 2. URL 模式匹配
        if current_url:
            domain = urlparse(current_url).netloc
            url_instincts = self._match_url_patterns(current_url, domain)
            results.extend(url_instincts)

        # 3. 工具使用模式匹配
        for tool in mentioned_tools:
            tool_instincts = self._match_tool_patterns(tool)
            results.extend(tool_instincts)

        # 去重并排序
        seen = set()
        unique_results = []
        for r in results:
            instinct_id = r['instinct'].id
            if instinct_id not in seen:
                seen.add(instinct_id)
                unique_results.append(r)

        unique_results.sort(key=lambda x: x['score'], reverse=True)
        return unique_results

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        keywords = []

        # URL 检测
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, text)
        keywords.extend(urls)

        # 域名检测
        domain_pattern = r'(?:https?://)?(?:www\.)?([a-z0-9-]+\.[a-z]{2,})'
        domains = re.findall(domain_pattern, text, re.IGNORECASE)
        keywords.extend([d[0] for d in domains])

        # 平台关键词
        platform_keywords = {
            'twitter': ['twitter', 'x.com', '推文', 'tweet'],
            'reddit': ['reddit', 'reddit.com'],
            'youtube': ['youtube', 'youtu.be', '视频'],
            '小红书': ['小红书', 'xiaohongshu'],
            '抖音': ['抖音', 'douyin'],
            'bilibili': ['b站', 'bilibili', 'bili'],
            '知乎': ['知乎'],
        }

        text_lower = text.lower()
        for platform, terms in platform_keywords.items():
            if any(term in text_lower for term in terms):
                keywords.append(platform)

        # 提取有意义的中文和英文词汇（至少2个字符）
        # 英文词汇
        english_words = re.findall(r'[a-z]{2,}', text_lower)
        keywords.extend(english_words)

        # 中文词汇（简单的连续汉字提取）
        chinese_words = re.findall(r'[\u4e00-\u9fff]{2,}', text)
        keywords.extend(chinese_words)

        # 额外：提取单个汉字（用于更细粒度的搜索）
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
        keywords.extend(chinese_chars)

        # 去重
        keywords = list(set(keywords))
        return keywords

    def _match_url_patterns(self, url: str, domain: str) -> List[Dict]:
        """匹配 URL 模式"""
        results = []

        # 域名 → 技能映射
        domain_skill_mapping = {
            'twitter.com': 'network-scraping',
            'x.com': 'network-scraping',
            'reddit.com': 'network-scraping',
            'youtube.com': 'network-scraping',
            'xiaohongshu.com': 'network-scraping',
            'douyin.com': 'network-scraping',
            'bilibili.com': 'network-scraping',
        }

        if domain in domain_skill_mapping:
            skill_name = domain_skill_mapping[domain]
            skills = self.skill_manager.search_skills(skill_name)

            for skill in skills:
                # 创建临时本能用于返回
                temp_instinct = type('Instinct', (), {
                    'id': f'use-{skill.name}',
                    'trigger': f'当遇到 {domain} 链接时',
                    'action': f'使用 {skill.name} 技能处理',
                    'confidence': 0.8,
                    'domain': skill.name
                })()
                results.append({
                    'instinct': temp_instinct,
                    'score': 0.8,
                    'source': 'domain_mapping',
                    'skill': skill
                })

        return results

    def _match_tool_patterns(self, tool: str) -> List[Dict]:
        """匹配工具使用模式"""
        results = []
        本能 = self.memory.search(tool, top_k=3)

        for r in 本能:
            r['tool'] = tool
            r['source'] = 'tool_match'
            results.append(r)

        return results

    def match_agents(self, context: Dict) -> List[Dict]:
        """匹配相关代理

        Args:
            context: 包含 user_input 的上下文

        Returns:
            匹配的代理列表，按优先级排序
        """
        user_input = context.get('user_input', '')
        user_input_lower = user_input.lower()

        # 1. 基于本能搜索（如果有代理使用本能）
        agent_instincts = []
        instincts = self.match_for_context(context)
        for i in instincts:
            instinct_id = i['instinct'].id
            # 检查是否是代理使用本能（支持带空格和不带空格的格式）
            if 'use-agent-' in instinct_id.lower():
                # 提取代理名并规范化（去除空格和前缀）
                agent_name = instinct_id.replace('use-agent-', '').replace('use-Agent-', '').strip()
                # 如果有其他前缀，也去除
                if agent_name.startswith('-'):
                    agent_name = agent_name[1:].strip()
                agent_instincts.append({
                    'agent': agent_name,
                    'score': i['score'],
                    'source': 'instinct'
                })

        # 2. 基于关键词匹配（静态规则）
        keyword_matches = self.agent_manager.suggest_agent(user_input)
        for agent_name in keyword_matches:
            # 避免重复（比较规范化后的名字）
            normalized_agent = agent_name.strip().lower()
            if not any(a['agent'].strip().lower() == normalized_agent for a in agent_instincts):
                agent_instincts.append({
                    'agent': agent_name,
                    'score': 0.6,  # 静态关键词匹配的基础分数
                    'source': 'keyword'
                })

        # 3. 去重（同一个代理可能匹配多次）
        seen = {}
        unique_agents = []
        for a in agent_instincts:
            normalized = a['agent'].strip().lower()
            if normalized not in seen:
                seen[normalized] = a
                unique_agents.append(a)

        # 4. 按分数排序
        unique_agents.sort(key=lambda x: x['score'], reverse=True)
        return unique_agents

    def suggest_action(self, context: Dict) -> Dict:
        """建议行动"""
        user_input = context.get('user_input', '')
        url = context.get('url', '')

        # 1. 检查现有本能
        matched_instincts = self.match_for_context(context)

        # 2. 搜索相关技能
        skills = []
        if url:
            domain = urlparse(url).netloc.lower()
            # 域名 -> 搜索关键词映射
            domain_keywords = {
                'twitter.com': 'twitter',
                'x.com': 'twitter',
                'reddit.com': 'reddit',
                'youtube.com': 'youtube',
                'youtu.be': 'youtube',
                'bilibili.com': 'bilibili',
                'xiaohongshu.com': 'xiaohongshu',
                'douyin.com': 'douyin',
                'weibo.com': 'weibo',
            }
            # 查找匹配的域名
            search_term = None
            for d, keyword in domain_keywords.items():
                if d in domain:
                    search_term = keyword
                    break
            # 如果没有匹配到具体域名，搜索 general scraping
            if search_term:
                skills = self.skill_manager.search_skills(search_term)
            else:
                # 通用搜索，尝试多个关键词
                skills = self.skill_manager.search_skills('scraping')
                if not skills:
                    skills = self.skill_manager.search_skills('web')
        else:
            skills = self.skill_manager.search_skills(user_input[:50])

        # 3. 生成建议
        suggestion = {
            'user_input': user_input,
            'url': url,
            'matched_instincts': matched_instincts,
            'available_skills': skills,
            'recommended_action': None
        }

        # 4. 匹配代理
        matched_agents = self.match_agents(context)
        suggestion['suggested_agents'] = matched_agents

        # 5. 确定推荐行动
        # 优先级：代理本能 > 技能本能 > 技能 > 通用本能
        relevant_instinct = None

        # 检查是否有代理使用本能（最高优先级）
        for instinct_result in matched_instincts:
            instinct_id = instinct_result['instinct'].id
            if instinct_id.startswith('use-agent-'):
                relevant_instinct = instinct_result
                break

        # 如果没有代理本能，检查其他领域相关本能
        if not relevant_instinct:
            for instinct_result in matched_instincts:
                instinct = instinct_result['instinct']
                source = instinct_result.get('source', '')
                # 优先考虑基于工具或序列匹配的本能
                if source in ['tool_match', 'sequence_match'] and instinct_result['score'] > 0.5:
                    relevant_instinct = instinct_result
                    break

        # 如果有相关本能，优先使用
        if relevant_instinct:
            instinct_id = relevant_instinct['instinct'].id
            if instinct_id.startswith('use-agent-'):
                # 代理本能
                agent_name = instinct_id.replace('use-agent-', '')
                suggestion['recommended_action'] = {
                    'type': 'use_agent',
                    'agent': agent_name,
                    'reason': f'根据学习到的本能',
                    'confidence': relevant_instinct['score']
                }
            else:
                # 其他本能
                suggestion['recommended_action'] = {
                    'type': 'follow_instinct',
                    'instinct': instinct_id,
                    'action': relevant_instinct['instinct'].action,
                    'confidence': relevant_instinct['score']
                }
        # 否则，如果有技能，推荐技能
        elif skills and len(skills) > 0:
            top_skill = skills[0]
            suggestion['recommended_action'] = {
                'type': 'use_skill',
                'skill': top_skill.name,
                'reason': f'根据关键词/域名匹配',
                'confidence': 0.8
            }
        # 最后，如果有任何本能（即使是通用的），也可以考虑
        elif matched_instincts and len(matched_instincts) > 0:
            top_instinct = matched_instincts[0]
            # 只有当置信度较高时才推荐通用本能
            if top_instinct['score'] > 0.6:
                suggestion['recommended_action'] = {
                    'type': 'follow_instinct',
                    'instinct': top_instinct['instinct'].id,
                    'action': top_instinct['instinct'].action,
                    'confidence': top_instinct['score']
                }

        return suggestion

    def learn_from_decision(self, context: Dict, decision: str):
        """从决策中学习"""
        obs = Observation(
            timestamp=datetime.now().isoformat(),
            event='decision',
            tool=decision,
            session=context.get('session_id', ''),
            project_id=self.memory.project['id'],
            project_name=self.memory.project['name'],
            input=str(context.get('user_input', ''))[:200],
            output=f'决策: {decision}',
            cwd=str(self.workspace)
        )

        self.memory.add_observation(obs)


# 便捷函数
def get_suggested_action(user_input: str, url: str = None) -> Dict:
    """获取建议行动（便捷函数）"""
    matcher = get_instinct_matcher()

    context = {
        'user_input': user_input,
        'url': url or '',
        'session_id': ''
    }

    return matcher.suggest_action(context)


# 测试
if __name__ == "__main__":
    matcher = InstinctMatcher()

    # 测试1: Twitter 链接
    context = {
        'user_input': '帮我抓取这个推文',
        'url': 'https://twitter.com/user/status/123',
        'session_id': 'test'
    }

    print("=" * 60)
    print("测试：Twitter 链接")
    print("=" * 60)

    suggestion = matcher.suggest_action(context)
    print(f"用户输入: {suggestion['user_input']}")
    print(f"URL: {suggestion['url']}")
    print(f"匹配本能数: {len(suggestion['matched_instincts'])}")
    print(f"可用技能数: {len(suggestion['available_skills'])}")
    print(f"推荐行动: {suggestion['recommended_action']}")

    print()
    print("结论: 当前使用静态规则匹配")
