# 🔍 Skill Discovery

> Automatically discover and track the latest AI skills, tools, and frameworks

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Skill-blue)](https://code.anthropic.com)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)

## 🎯 What is Skill Discovery?

**Skill Discovery** is an intelligent skill for Claude Code that **automatically discovers and recommends** the latest tools, frameworks, and libraries based on your needs. Unlike traditional search tools, it operates **proactively** - AI decides when to search without you explicitly asking.

### Key Features

✅ **Autonomous Detection** - AI automatically detects when you need external tools
✅ **Multi-Source Search** - GitHub, Reddit, and Web simultaneously
✅ **Smart Caching** - Two-level caching (memory + file) for instant results
✅ **Intelligent Ranking** - Relevance scoring based on multiple factors
✅ **6 Pre-configured Domains** - Browser automation, AI agents, Python, DevOps, APIs, Data

---

## 🚀 Why Use Skill Discovery?

### Traditional Way
```
You: "I need to automate browser actions"
 ↓
You: Search Google for "browser automation tools"
 ↓
You: Read 10+ articles comparing tools
 ↓
You: Choose based on limited knowledge
 ↓
You: Might pick an outdated tool (Selenium vs Playwright)
```

### With Skill Discovery
```
You: "I need to automate browser actions"
 ↓
AI: [Automatically detects need]
 ↓
AI: [Searches GitHub, Reddit, Web]
 ↓
AI: Found Playwright is better than Selenium
 ↓
AI: "I'll use Playwright - it's faster and more modern"
 ↓
Done! You get the best tool without researching
```

---

## 📊 Supported Domains

| Domain | Keywords | Sources | Cache TTL |
|--------|----------|---------|-----------|
| **Browser Automation** | puppeteer, playwright, selenium | GitHub, Reddit, Web | 12h |
| **AI Agents** | openclaw, claude, llm, autonomous | GitHub, Reddit, Web | 6h |
| **Python Scripts** | python, automation, scripting | GitHub, Reddit | 12h |
| **API Integrations** | api, rest, graphql, webhook | GitHub, Web | 12h |
| **DevOps Tools** | docker, kubernetes, cicd | GitHub, Reddit | 12h |
| **Data Analysis** | pandas, jupyter, visualization | GitHub, Reddit | 12h |

---

## 🛠️ Installation

### Option 1: Install for Claude Code

```bash
# Clone to your Claude skills directory
git clone https://github.com/YOUR_USERNAME/skill-discovery.git ~/.claude/skills/skill-discovery

# Or on Windows
git clone https://github.com/YOUR_USERNAME/skill-discovery.git %USERPROFILE%\.claude\skills\skill-discovery
```

### Option 2: Install as Standalone

```bash
# Clone anywhere
git clone https://github.com/YOUR_USERNAME/skill-discovery.git
cd skill-discovery

# Install dependencies (optional, for scripts)
pip install -r requirements.txt  # If available
```

---

## 💻 Usage

### Automatic Usage (Recommended)

**Simply talk to Claude normally:**

```
You: "I need to scrape websites"
AI: [Skill Discovery activates automatically]
AI: "I found Playwright is better than Selenium..."
AI: [Uses Playwright for your task]

You: "What's the best tool for data analysis?"
AI: [Searches data-analysis domain]
AI: "Here are the top options..."
```

### Manual Usage

```
You: "Search for latest DevOps tools"
You: "What's new in AI agents?"
You: "skill-discovery: find docker alternatives"
```

---

## 🎨 How It Works

### Architecture

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
   - Save results locally
   - Index for quick search
    ↓
6. Present Results
   - Top recommendations
   - Comparison with alternatives
   - Learning resources
```

### Search Algorithms

**GitHub Search:**
```python
query = "browser automation language:javascript OR python stars:>10 pushed:>2026-02-19"
```

**Reddit Search:**
```python
subreddits = ["Python", "automation", "webdev"]
```

**Scoring Formula:**
```
score = base_score + popularity_bonus + recency_bonus + relevance_match
```

---

## 📦 Project Structure

```
skill-discovery/
├── SKILL.md              # Main skill definition
├── README.md             # This file
├── QUICK_REFERENCE.md    # Quick start guide
├── DESIGN.md             # Design decisions
├── COMPLETION_REPORT.md  # Development report
├── USAGE_EXAMPLES.md     # Usage examples
├── config/
│   ├── domains.json      # Domain configurations
│   └── behavior.json     # Behavior settings
├── scripts/
│   ├── search_github.py  # GitHub API wrapper
│   ├── search_reddit.py  # Reddit API fetcher
│   ├── merge_results.py  # Result merger
│   └── update_cache.py   # Cache manager
├── references/
│   ├── domains.md        # Domain documentation
│   └── api_limits.md     # API rate limits
└── cache/
    └── index.json        # Global cache index
```

---

## 🧪 Testing

### Test GitHub Search
```bash
python scripts/search_github.py
```

### Test Reddit Search
```bash
python scripts/search_reddit.py
```

### Test Cache Manager
```bash
python scripts/update_cache.py
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

### Adjust Behavior

Edit `config/behavior.json`:

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

## 📈 Performance

### Cache Efficiency

- **Memory Cache**: < 1ms retrieval
- **File Cache**: < 10ms retrieval
- **Fresh Search**: 2-5 seconds

### Rate Limits

- **GitHub API**: 60 requests/hour (unauthenticated)
- **Reddit API**: ~30 requests/minute
- **WebSearch**: Unlimited (managed by Claude)

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

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

- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/skill-discovery/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YOUR_USERNAME/skill-discovery/discussions)

---

## 🌟 Star History

If you find this skill helpful, please consider giving it a ⭐ star on GitHub!

---

<div align="center">

**Made with ❤️ by the AI community**

</div>
