# Skill Discovery - 使用指南

## 📚 目录

- [快速开始](#快速开始)
- [安装方法](#安装方法)
- [使用示例](#使用示例)
- [配置说明](#配置说明)
- [常见问题](#常见问题)

---

## 🚀 快速开始

### 你需要什么

- Claude Code (已安装)
- Python 3.8+ (用于脚本功能)
- Git (用于版本控制)

### 30 秒安装

```bash
# 1. 克隆到 Claude skills 目录
git clone https://github.com/ei060/skill-discovery.git ~/.claude/skills/skill-discovery

# 或者在 Windows 上
git clone https://github.com/ei060/skill-discovery.git %USERPROFILE%\.claude\skills\skill-discovery

# 2. 完成！重新启动 Claude Code 即可
```

---

## 📦 安装方法

### 方法 1：Claude Code Skills 目录（推荐）

**Linux/macOS:**
```bash
mkdir -p ~/.claude/skills
cd ~/.claude/skills
git clone https://github.com/ei060/skill-discovery.git
```

**Windows:**
```bash
mkdir %USERPROFILE%\.claude\skills
cd %USERPROFILE%\.claude\skills
git clone https://github.com/ei060/skill-discovery.git
```

### 方法 2：手动安装

1. 下载 ZIP 文件
2. 解压到 `.claude/skills/skill-discovery/`
3. 确保文件结构正确

---

## 💻 使用示例

### 示例 1：自动发现浏览器自动化工具

```
你: "我需要自动化浏览器操作"

AI: [自动触发 skill-discovery]

AI: "发现 3 个主要工具：

⭐ Top Pick: Playwright
   - 最现代的浏览器自动化框架
   - 支持 Chrome, Firefox, Safari
   - API 设计优秀，性能更好

我将使用 Playwright 为你实现..."
```

### 示例 2：搜索最新 AI 工具

```
你: "搜索最新的 AI agents 工具"

AI: [搜索 GitHub, Reddit, Web]

AI: "🔍 发现 1351+ 个 AI agents 项目

Top 3:
1. LangFlow - 145k stars - 可视化构建 AI agents
2. Dify - 130k stars - 生产级 AI 工作流平台
3. LangChain - 127k stars - 可靠的 AI agents 基础平台

需要详细了解某个工具吗？"
```

### 示例 3：DevOps 部署建议

```
你: "我要部署应用到服务器"

AI: [检测到 devops 领域]

AI: "推荐方案：

1. Coolify (51k stars) - 开源自托管 PaaS
   - 类似 Vercel/Heroku 的开源替代
   - 一键部署，无需复杂配置

2. Docker + Compose - 经典方案
   - 容器化部署
   - 易于迁移

我建议用 Coolify，开始部署..."
```

---

## ⚙️ 配置说明

### 领域配置 (config/domains.json)

```json
{
  "id": "your-domain",
  "name": "显示名称",
  "enabled": true,
  "keywords": ["关键词1", "关键词2"],
  "github_query": "GitHub 搜索查询",
  "subreddits": ["相关子版块"],
  "sources": ["github", "reddit", "web"],
  "schedule": "weekly",
  "cache_ttl": 43200000,
  "priority": 1
}
```

### 行为配置 (config/behavior.json)

```json
{
  "auto_discovery": true,
  "auto_use_skills": true,
  "ask_before_using": false,
  "show_what_i_used": true,
  "max_results_per_source": 20,
  "min_relevance_score": 0.3
}
```

**配置说明：**
- `auto_discovery`: 自动搜索相关工具（默认 true）
- `auto_use_skills`: 自动使用发现的技能（默认 true）
- `ask_before_using`: 使用前询问（默认 false）
- `show_what_i_used`: 显示使用的工具（默认 true）

---

## 🔧 支持的领域

| 领域 | 关键词 | 数据源 | 更新频率 |
|------|--------|---------|----------|
| 浏览器自动化 | puppeteer, playwright, selenium | GitHub, Reddit, Web | 12 小时 |
| AI Agents | openclaw, claude, llm, autonomous | GitHub, Reddit, Web | 6 小时 |
| Python 脚本 | python, automation, scripting | GitHub, Reddit | 12 小时 |
| API 集成 | api, rest, graphql, webhook | GitHub, Web | 12 小时 |
| DevOps 工具 | docker, kubernetes, cicd | GitHub, Reddit | 12 小时 |
| 数据分析 | pandas, jupyter, visualization | GitHub, Reddit | 12 小时 |

---

## 🧪 测试脚本

```bash
# 测试 GitHub 搜索
python scripts/search_github.py

# 测试 Reddit 搜索
python scripts/search_reddit.py

# 测试缓存管理
python scripts/update_cache.py

# 测试结果合并
python scripts/merge_results.py
```

---

## 📈 工作原理

### 1. 关键词检测

```
用户输入: "我需要自动化浏览器"
       ↓
AI 分析: 检测到关键词 "自动化", "浏览器"
       ↓
匹配领域: browser-automation
```

### 2. 智能搜索

```
触发搜索
       ↓
检查缓存（是否过期？）
       ↓
并行搜索: GitHub + Reddit + Web
       ↓
合并结果: 去重 + 评分 + 排序
       ↓
更新缓存
```

### 3. 智能推荐

```
分析结果
       ↓
考虑因素:
- Star 数（流行度）
- 更新时间（新鲜度）
- 关键词匹配（相关性）
- 技术栈（兼容性）
       ↓
推荐最佳方案
```

---

## ❓ 常见问题

### Q1: Skill 没有自动触发？

**A:** 检查以下几点：

1. Skill 是否安装在正确目录？
```bash
# 应该在
~/.claude/skills/skill-discovery/
```

2. 关键词是否在配置中？
```bash
# 查看配置
cat config/domains.json | grep keywords
```

3. 重新启动 Claude Code

### Q2: 搜索结果不准确？

**A:** 调整搜索查询：

```json
// config/domains.json
"github_query": "更精确的查询语句"
```

### Q3: 缓存多久更新一次？

**A:** 根据领域热度：

- 热门领域（AI 工具）: 6 小时
- 中频领域（浏览器自动化）: 12 小时
- 冷门领域（脚本工具）: 24 小时

### Q4: 如何添加新领域？

**A:** 编辑 `config/domains.json`：

```bash
# 添加新领域
{
  "id": "new-domain",
  "name": "新领域",
  "enabled": true,
  "keywords": ["关键词1", "关键词2"],
  "github_query": "搜索查询",
  "subreddits": ["相关子版块"],
  "sources": ["github", "reddit", "web"],
  "schedule": "weekly",
  "cache_ttl": 43200000,
  "priority": 5
}
```

### Q5: 如何禁用自动搜索？

**A:** 编辑 `config/behavior.json`：

```json
{
  "auto_discovery": false
}
```

---

## 🤝 贡献指南

欢迎贡献！请：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

---

## 📝 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

- 基于 [Claude Code](https://code.anthropic.com/) 构建
- 灵感来自 [OpenClaw](https://github.com/openclaw/openclaw) skills 生态
- 使用 GitHub, Reddit, Web Search APIs

---

## 📮 联系方式

- **Issues**: [GitHub Issues](https://github.com/ei060/skill-discovery/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ei060/skill-discovery/discussions)

---

## 🌟 Star History

如果这个项目对你有帮助，请给它一个 ⭐ star！

---

<div align="center">

**让 AI 帮你发现和选择最佳工具**

Made with ❤️ by [ei060](https://github.com/ei060)

</div>
