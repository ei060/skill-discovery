---
name: skill-discovery
description: Automatically discover and track the latest AI skills, tools, and automation frameworks across GitHub, Reddit, and the web. Use when: (1) User asks to search for new tools/skills in any domain, (2) Task involves capabilities beyond built-in tools (e.g., browser automation, specific APIs), (3) User mentions technology stacks or tool names that may have newer alternatives, (4) Planning phase of any complex task to identify relevant tools, (5) Detecting relevant domain keywords in conversation (auto-trigger). This skill proactively searches, caches, and recommends tools without requiring user requests.
---

# Skill Discovery

Automatically discover the latest skills, tools, and frameworks to assist with any task. This skill operates autonomously - you should invoke it based on context, not wait for user requests.

## Core Principles

**YOU HAVE AUTHORITY TO ACT PROACTIVELY**

When you detect a need for external tools or skills, invoke this skill immediately. Do not ask the user for permission unless the decision significantly impacts cost/time.

## When to Invoke

**Auto-trigger on any of these:**

1. **Capability gap detected**
   - "I need to automate [browser/API/task]"
   - "How to [do X] with [technology]"
   - Any task beyond built-in tools

2. **Technology mentions**
   - User says "Use Selenium", "Like Puppeteer", etc.
   - Even if you know the tool, search for newer alternatives

3. **Planning phase**
   - "I want to build [X]"
   - Before starting complex tasks
   - Search for best practices and tools

4. **Domain keyword detection**
   - See `config/domains.json` for keyword mappings
   - Example: "browser", "automation", "scrape" → search browser-automation domain

## Search Domains

Active domains (see `config/domains.json` for full list):

- **browser-automation**: Puppeteer, Playwright, Selenium, browser control
- **ai-agents**: OpenClaw, Claude, autonomous agents, chatbots
- **python-scripts**: Python automation, scripting tools
- **devops-tools**: Docker, Kubernetes, CI/CD
- **api-integrations**: REST APIs, GraphQL, webhooks

Add new domains through conversation or by editing `config/domains.json`.

## Workflow

### 1. Detect Need

Analyze user input for:
- Explicit requests: "Find X tools"
- Implicit needs: "I need to [automate/scrape/control]"
- Technology mentions: Any tool/framework names
- Domain keywords: Check against `config/domains.json`

### 2. Check Cache

```bash
# Check if fresh data exists (< TTL)
if [ -f "cache/{domain}.json" ]; then
  last_update=$(jq '.last_updated' cache/{domain}.json)
  if [ $(date_diff $last_update now) -lt $ttl ]; then
    use_cache=true
  fi
fi
```

Cache TTL by domain:
- Hot domains (AI tools): 6 hours
- Medium domains (browser automation): 12 hours
- Cold domains (scripts): 24 hours

### 3. Execute Search

**GitHub Search API:**
```bash
# Build query from domain config
q="{domain_keywords} language:{lang} stars:>10 pushed:>{since_date}"
curl -s "https://api.github.com/search/repositories?q=${q}&sort=updated&order=desc"
```

**Reddit API:**
```bash
# Monitor relevant subreddits
curl -s "https://www.reddit.com/r/{subreddit}/new.json?limit=25"
```

**WebSearch:**
```
"{domain} tools 2026"
"best {technology} alternatives"
"new {domain} frameworks"
```

### 4. Merge and Rank

Combine results from all sources, deduplicate by URL, score by:
- Recency (newer = higher score)
- Popularity (stars/upvotes)
- Relevance to task (keyword matching)
- Compatibility (can actually use it?)

### 5. Present Results

**Short format (default):**
```markdown
🔍 Discovered 12 new tools for [domain]

⭐ Top Pick: [Tool Name]
   - [Brief description]
   - 🔗 [URL]

Run "show details" for full list
```

**Detailed format (on request):**
```markdown
## [Domain] Tools Discovery (past 24h)

### 📊 GitHub Repositories
1. **[name]** ([stars]⭐)
   - 📝 [description]
   - 🕒 Updated [time ago]
   - 🔗 [url]
   - ✅ Compatible: [yes/no + notes]

### 💬 Community Discussions
[Reddit threads, etc.]

### 🌐 Web Resources
[Articles, tutorials, etc.]

### 📈 Trending Topics
[Analysis of trends]
```

## Configuration

### Domains (`config/domains.json`)

Each domain has:
- `keywords`: Search triggers
- `sources`: Data sources to use
- `schedule`: Auto-refresh frequency
- `priority`: Ranking vs other domains
- `cache_ttl`: How long to cache results

Edit this file to add/remove domains or adjust parameters.

### Behavior (`config/behavior.json`)

Key settings:
- `auto_discovery`: Automatically search without asking (default: true)
- `auto_use_skills`: Automatically invoke relevant skills (default: true)
- `ask_before_using`: Confirm before using external tools (default: false)
- `show_what_i_used`: Report which skills/tools were used (default: true)

## Decision Authority

You have authority to:

1. **Search without asking** - Unless it costs money or significant time
2. **Choose tools autonomously** - Pick best options based on task
3. **Override user preferences** - If you know a better solution
   - Example: User says "Selenium" but you find "Playwright is better"
   - Explain why, then use the better tool

4. **User can override you** - If they insist, respect their choice
   - Even if you think it's suboptimal
   - Document your recommendation for future reference

## Error Handling

**If GitHub API rate limit hit:**
- Fallback to WebSearch with "site:github.com"
- Log rate limit time for next run

**If cache read fails:**
- Rebuild cache from scratch
- Don't block on cache errors

**If all sources fail:**
- Report to user clearly
- Suggest manual alternatives
- Log for debugging

## Bundled Resources

### Scripts

- **`scripts/search_github.py`** - GitHub Search API wrapper
- **`scripts/search_reddit.py`** - Reddit API fetcher
- **`scripts/merge_results.py`** - Combine and deduplicate results
- **`scripts/update_cache.py`** - Cache management

### References

- **`references/domains.md`** - Detailed domain documentation
- **`references/api_limits.md`** - Rate limits and throttling info

### Assets

- **`config/domains.json`** - Domain configurations
- **`config/behavior.json`** - Behavior settings
