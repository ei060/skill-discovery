# 🔍 Skill Discovery

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Skill-blue.svg)](https://code.anthropic.com)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)

> Automatically discover and track the latest AI skills, tools, and frameworks

[English](README_EN.md) | [日本語](README_JA.md) | [中文](README.md)

---

## ✨ Features

- 🤖 **Autonomous Detection** - AI automatically detects when you need external tools
- 🔍 **Multi-Source Search** - GitHub, Reddit, and Web simultaneously
- 💾 **Smart Caching** - Two-level caching for instant results
- 📊 **Intelligent Ranking** - Relevance-based recommendation
- 🌍 **6 Pre-configured Domains** - Browser automation, AI agents, Python, DevOps, APIs, Data

---

## 🚀 Quick Start

### Installation

```bash
# Clone to Claude skills directory
git clone https://github.com/ei060/skill-discovery.git ~/.claude/skills/skill-discovery

# On Windows
git clone https://github.com/ei060/skill-discovery.git %USERPROFILE%\.claude\skills\skill-discovery
```

### Usage

Just talk to Claude normally:

```
You: "I need to scrape websites"
AI: [Skill Discovery activates automatically]
AI: "I found Playwright is better than Selenium..."
AI: [Uses Playwright for your task]
```

---

## 📚 Supported Domains

| Domain | Keywords | Sources | Cache TTL |
|--------|----------|---------|-----------|
| Browser Automation | puppeteer, playwright, selenium | GitHub, Reddit, Web | 12h |
| AI Agents | openclaw, claude, llm, autonomous | GitHub, Reddit, Web | 6h |
| Python Scripts | python, automation, scripting | GitHub, Reddit | 12h |
| API Integrations | api, rest, graphql, webhook | GitHub, Web | 12h |
| DevOps Tools | docker, kubernetes, cicd | GitHub, Reddit | 12h |
| Data Analysis | pandas, jupyter, visualization | GitHub, Reddit | 12h |

---

## 🛠️ How It Works

```
User Input
    ↓
1. Domain Detection
   - Keywords: "automation", "deploy", "api"
   - Context Analysis
    ↓
2. Cache Check
   - Memory cache (fast)
   - File cache (persistent)
   - TTL check
    ↓
3. Parallel Search
   - GitHub API (repositories)
   - Reddit API (community discussions)
   - WebSearch (articles, tutorials)
    ↓
4. Merge & Rank
   - URL deduplication
   - Relevance scoring
   - Quality assessment
    ↓
5. Update Cache
    ↓
6. Present Results
```

---

## 📦 Project Structure

```
skill-discovery/
├── SKILL.md              # Main skill definition
├── README.md             # This file
├── README_EN.md          # English version
├── README_JA.md          # Japanese version
├── USAGE_GUIDE.md        # Detailed usage guide
├── config/
│   ├── domains.json      # Domain configurations
│   └── behavior.json     # Behavior settings
├── scripts/
│   ├── search_github.py  # GitHub API wrapper
│   ├── search_reddit.py  # Reddit API fetcher
│   ├── merge_results.py  # Result merger
│   └── update_cache.py   # Cache manager
└── references/
    ├── domains.md        # Domain documentation
    └── api_limits.md     # API rate limits
```

---

## ⚙️ Configuration

### Add New Domain

Edit `config/domains.json`:

```json
{
  "id": "new-domain",
  "name": "Display Name",
  "enabled": true,
  "keywords": ["keyword1", "keyword2"],
  "github_query": "search query",
  "subreddits": ["relevant_subreddits"],
  "sources": ["github", "reddit", "web"],
  "schedule": "weekly",
  "cache_ttl": 43200000,
  "priority": 5
}
```

---

## 🧪 Testing

```bash
# Test GitHub search
python scripts/search_github.py

# Test Reddit search
python scripts/search_reddit.py

# Test cache manager
python scripts/update_cache.py
```

---

## 📈 Performance

- **Memory Cache**: < 1ms retrieval
- **File Cache**: < 10ms retrieval
- **Fresh Search**: 2-5 seconds

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built for [Claude Code](https://code.anthropic.com/)
- Inspired by [OpenClaw](https://github.com/openclaw/openclaw) skills ecosystem
- Powered by GitHub, Reddit, and Web Search APIs

---

## 📮 Contact

- **Issues**: [GitHub Issues](https://github.com/ei060/skill-discovery/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ei060/skill-discovery/discussions)

---

<div align="center">

**Made with ❤️ by [ei060](https://github.com/ei060)**

</div>
