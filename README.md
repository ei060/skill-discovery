# 🔍 Skill Discovery

> 自动发现和追踪最新的 AI 技能、工具和框架

**[English](README_EN.md)** | **[日本語](README_JA.md)**

---

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Skill-blue.svg)](https://code.anthropic.com)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)

---

## 🎯 什么是 Skill Discovery？

**Skill Discovery** 是 Claude Code 的一个智能技能，能够**自动发现和推荐**最新的工具、框架和库。与传统的搜索工具不同，它是**主动式**的 - AI 会在你明确请求之前就决定何时搜索。

### 核心特性

✅ **自主检测** - AI 自动检测何时需要外部工具
✅ **多源搜索** - 同时搜索 GitHub、Reddit 和 Web
✅ **智能缓存** - 两级缓存（内存 + 文件）即时获取结果
✅ **智能排序** - 基于多因素的相关性评分
✅ **6 个预配置领域** - 浏览器自动化、AI 智能体、Python、DevOps、API、数据

---

## 🚀 为什么使用 Skill Discovery？

### 传统方式
```
你: "我需要自动化浏览器操作"
 ↓
你: 搜索 "浏览器自动化工具"
 ↓
你: 阅读 10+ 篇对比文章
 ↓
你: 基于有限的知识选择
 ↓
你: 可能选择了过时的工具（Selenium vs Playwright）
```

### 使用 Skill Discovery
```
你: "我需要自动化浏览器操作"
 ↓
AI: [自动检测需求]
 ↓
AI: [搜索 GitHub、Reddit、Web]
 ↓
AI: 发现 Playwright 比 Selenium 更好
 ↓
AI: "我会用 Playwright - 它更快更现代"
 ↓
完成！无需研究，直接获得最佳工具
```

---

## 📊 支持的领域

| 领域 | 关键词 | 数据源 | 缓存时间 |
|------|--------|---------|----------|
| **浏览器自动化** | puppeteer, playwright, selenium | GitHub, Reddit, Web | 12 小时 |
| **AI 智能体** | openclaw, claude, llm, autonomous | GitHub, Reddit, Web | 6 小时 |
| **Python 脚本** | python, automation, scripting | GitHub, Reddit | 12 小时 |
| **API 集成** | api, rest, graphql, webhook | GitHub, Web | 12 小时 |
| **DevOps 工具** | docker, kubernetes, cicd | GitHub, Reddit | 12 小时 |
| **数据分析** | pandas, jupyter, visualization | GitHub, Reddit | 12 小时 |

---

## 🛠️ 安装

### 方法 1：安装为 Claude Code Skill

```bash
# 克隆到 Claude skills 目录
git clone https://github.com/ei060/skill-discovery.git ~/.claude/skills/skill-discovery

# Windows
git clone https://github.com/ei060/skill-discovery.git %USERPROFILE%\.claude\skills\skill-discovery
```

### 方法 2：独立使用

```bash
# 克隆到任何位置
git clone https://github.com/ei060/skill-discovery.git
cd skill-discovery

# 安装依赖（可选）
pip install -r requirements.txt  # 如果有此文件
```

---

## 💻 使用示例

### 自动触发（推荐）

**只需与 Claude 正常对话：**

```
你: "我需要自动化网站"
AI: [Skill Discovery 自动激活]
AI: "发现 Playwright 是最佳选择..."
AI: [使用 Playwright 为你实现]
```

### 手动触发

```
你: "搜索最新的 DevOps 工具"
你: "AI agents 领域有什么新东西？"
你: "skill-discovery: 查找 docker 替代品"
```

---

## 🎨 工作原理

```
用户输入
    ↓
1. 领域检测
   - 关键词："自动化"、"部署"、"api"
   - 上下文分析
    ↓
2. 缓存检查
   - 内存缓存（快速）
   - 文件缓存（持久）
   - TTL 检查
    ↓
3. 并行搜索
   - GitHub API（仓库）
   - Reddit API（社区讨论）
   - WebSearch（文章、教程）
    ↓
4. 合并与排序
   - URL 去重
   - 相关性评分
   - 质量评估
    ↓
5. 更新缓存
    ↓
6. 展示结果
```

---

## 📦 项目结构

```
skill-discovery/
├── README.md              # 主文件（中文版）
├── README_EN.md          # 英文版
├── README_JA.md          # 日文版
├── SKILL.md              # Skill 定义
├── USAGE_GUIDE.md        # 详细使用指南
├── DESIGN.md             # 设计文档
├── QUICK_REFERENCE.md    # 快速参考
├── COMPLETION_REPORT.md  # 完成报告
├── USAGE_EXAMPLES.md     # 使用示例
├── config/
│   ├── domains.json      # 领域配置
│   └── behavior.json     # 行为配置
├── scripts/
│   ├── search_github.py  # GitHub 搜索
│   ├── search_reddit.py  # Reddit 抓取
│   ├── merge_results.py  # 结果合并
│   └── update_cache.py   # 缓存管理
├── references/
│   ├── domains.md        # 领域文档
│   └── api_limits.md     # API 限制
└── cache/
    └── index.json        # 全局缓存索引
```

---

## ⚙️ 配置

### 添加新领域

编辑 `config/domains.json`：

```json
{
  "id": "new-domain",
  "name": "显示名称",
  "enabled": true,
  "keywords": ["关键词1", "关键词2"],
  "github_query": "GitHub 搜索查询",
  "subreddits": ["相关子版块"],
  "sources": ["github", "reddit", "web"],
  "schedule": "weekly",
  "cache_ttl": 43200000,
  "priority": 5
}
```

### 调整行为

编辑 `config/behavior.json`：

```json
{
  "auto_discovery": true,
  "auto_use_skills": true,
  "ask_before_using": false,
  "show_what_i_used": true,
  "max_results_per_source": 20
}
```

---

## 🧪 测试

```bash
# 测试 GitHub 搜索
python scripts/search_github.py

# 测试 Reddit 搜索
python scripts/search_reddit.py

# 测试缓存管理
python scripts/update_cache.py
```

---

## 📈 性能

- **内存缓存**: < 1ms 检索
- **文件缓存**: < 10ms 检索
- **新鲜搜索**: 2-5 秒

---

## 🤝 贡献

欢迎贡献！请：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

---

## 📝 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🙋 致谢

- 为 [Claude Code](https://code.anthropic.com/) 构建
- 灵感来自 [OpenClaw](https://github.com/openclaw/openclaw) skills 生态
- 使用 GitHub、Reddit、Web Search APIs

---

## 📮 联系方式

- **Issues**: [GitHub Issues](https://github.com/ei060/skill-discovery/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ei060/skill-discovery/discussions)

---

## 🌟 给 Star 吗

如果你觉得这个项目有帮助，请给它一个 ⭐ star！

---

<div align="center">

**让 AI 帮你发现和选择最佳工具**

</div>
