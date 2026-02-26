# Skill Discovery - Development Notes

## 概述

这个 skill 能够自动发现和追踪最新的 AI 技能、工具和自动化框架。

## 核心特性

1. **主动判断** - AI 自动判断何时需要搜索新工具，无需用户明确请求
2. **多数据源** - GitHub、Reddit、WebSearch
3. **智能缓存** - 内存 + 文件两级缓存，支持增量更新
4. **自动触发** - 根据对话内容自动识别相关领域
5. **权限优先** - AI 有权限自主决定使用哪些工具

## 文件结构

```
skill-discovery/
├── SKILL.md                    # Skill 主文件（必需）
├── DESIGN.md                   # 本文件（开发文档）
├── config/
│   ├── domains.json            # 领域配置
│   └── behavior.json           # 行为配置
├── scripts/
│   ├── search_github.py        # GitHub 搜索
│   ├── search_reddit.py        # Reddit 抓取
│   ├── merge_results.py        # 结果合并去重
│   └── update_cache.py         # 缓存管理
├── references/
│   ├── domains.md              # 领域详细文档
│   └── api_limits.md           # API 限制说明
├── cache/
│   ├── index.json              # 全局索引
│   ├── browser-automation.json # 按领域缓存（使用时生成）
│   └── ...
└── assets/                     # 预留，暂无内容
```

## 使用流程

### AI 自动触发场景

1. **能力缺口检测**
   ```
   用户: "我需要自动化浏览器操作"
   AI: [检测到关键词 "浏览器", "自动化"]
       [自动调用 skill-discovery]
       [搜索 browser-automation 领域]
       [返回 Playwright 作为推荐]
   ```

2. **技术栈提及**
   ```
   用户: "用 Selenium 做爬虫"
   AI: [检测到 "Selenium"]
       [调用 skill-discovery]
       [发现 Playwright 更现代]
       [推荐 Playwright 并解释原因]
   ```

3. **规划阶段**
   ```
   用户: "我要做一个抢票工具"
   AI: [规划阶段，自动搜索相关工具]
       [发现 browser-automation, api-integrations 相关]
       [推荐技术方案]
   ```

### 用户手动触发

```
用户: "搜索最新的 AI 工具"
用户: "有什么新的浏览器自动化框架？"
用户: "skill-discovery: 查找 devops 工具"
```

## 工作原理

### 1. 领域检测

从对话中提取关键词，匹配 `config/domains.json` 中的关键词列表：

```python
# 伪代码
def detect_domain(conversation):
    for domain in domains:
        if any(keyword in conversation for keyword in domain["keywords"]):
            return domain
```

### 2. 缓存检查

```python
# 检查缓存是否新鲜
if cache_exists(domain) and cache_age(domain) < ttl:
    use_cache()
else:
    fresh_search()
```

### 3. 并行搜索

```python
# 同时调用多个数据源
github_results = search_github(domain)
reddit_results = search_reddit(domain)
web_results = web_search(domain)  # 使用 WebSearch 工具
```

### 4. 合并去重

```python
# 按URL归一化去重
# 计算相关性评分
# 按评分排序
```

### 5. 缓存更新

```python
# 更新内存缓存（快速访问）
# 更新文件缓存（持久化）
# 更新索引
```

## 配置说明

### domains.json

- `keywords`: 触发关键词列表
- `github_query`: GitHub 搜索查询语句
- `subreddits`: 监控的子版块
- `sources`: 使用的数据源（github/reddit/web）
- `schedule`: 自动刷新频率
- `cache_ttl`: 缓存过期时间（毫秒）
- `priority`: 优先级（0=最高）

### behavior.json

- `auto_discovery`: 自动搜索（默认 true）
- `auto_use_skills`: 自动使用相关 skills（默认 true）
- `ask_before_using`: 使用前询问（默认 false）
- `show_what_i_used`: 显示使用了什么（默认 true）

## 测试

### 测试 GitHub 搜索

```bash
python .claude/skills/skill-discovery/scripts/search_github.py
```

### 测试 Reddit 搜索

```bash
python .claude/skills/skill-discovery/scripts/search_reddit.py
```

### 测试缓存

```bash
python .claude/skills/skill-discovery/scripts/update_cache.py
```

## 已知限制

1. **GitHub API 限制**
   - 无认证：60次/小时
   - 需要时会fallback到WebSearch

2. **Reddit API 限制**
   - 约30次/分钟
   - 某些子版块可能无法访问

3. **无法浏览器自动化**
   - 这是 Claude Code 的限制
   - 不能像OpenClaw那样操作浏览器
   - 但可以推荐相应工具给用户

## 未来改进

- [ ] 添加更多数据源（Hacker News、Product Hunt）
- [ ] 支持 GitHub API 认证（提高 rate limit）
- [ ] 机器学习排序（更智能的推荐）
- [ ] 历史趋势分析
- [ ] 用户偏好学习
- [ ] 多语言支持

## 设计决策记录

### 为什么 AI 有自主权限？

因为用户通常不知道有哪些 skills 可用，也不知道何时应该用哪个。AI 比用户更了解：
- 自己有什么能力
- 外部有哪些工具
- 哪个工具最适合当前任务

### 为什么用文件缓存而不是数据库？

简单、无依赖、透明：
- JSON 文件人类可读
- 不需要额外依赖
- 易于调试
- 适合小规模数据

### 为什么有多个脚本而不是一个？

模块化、可测试、可重用：
- 每个脚本单一职责
- 可以独立测试
- 其他 skills 也可以重用
