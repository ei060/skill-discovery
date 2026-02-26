# Domain Documentation

Detailed documentation for each monitored domain.

## Browser Automation

**Purpose**: Tools for programmatic browser control and web automation

**Key Technologies**:
- **Puppeteer**: Chrome DevTools Protocol, maintained by Google
- **Playwright**: Microsoft's successor to Puppeteer, cross-browser
- **Selenium**: Legacy but widely supported, WebDriver-based
- **Chrome DevTools Recorder**: Google's official low-code solution

**Use Cases**:
- Web scraping
- Automated testing
- Screenshot generation
- PDF generation
- Form submission
- Single-page app navigation

**Keyword Triggers**: puppeteer, playwright, selenium, browser, 爬虫, scraping, headless, automation

**Recommended for New Projects**: Playwright (most modern, best API)

---

## AI Agents

**Purpose**: Autonomous AI systems that can perform complex tasks

**Key Technologies**:
- **OpenClaw**: Telegram-based AI agent with skills ecosystem
- **AutoGPT**: Autonomous GPT-4 agent
- **BabyAGI**: Task management AI
- **CrewAI**: Multi-agent collaboration framework
- **LangChain**: Framework for LLM applications

**Use Cases**:
- Task automation
- Research assistants
- Code generation
- Workflow automation
- Decision making

**Keyword Triggers**: openclaw, claude, ai agent, chatbot, 智能体, autonomous, llm

**Trending**: Multi-agent systems, tool-using agents, memory-augmented agents

---

## Python Scripts

**Purpose**: Reusable Python automation scripts

**Categories**:
- File operations
- Data processing
- Web scraping
- API integrations
- System automation

**Popular Libraries**:
- requests (HTTP)
- BeautifulSoup/Parsel (HTML parsing)
- pandas (data)
- click/typer (CLI)
- pydantic (validation)

**Keyword Triggers**: python, 脚本, py, automation, python script

---

## API Integrations

**Purpose**: Connecting to external services and APIs

**Types**:
- REST APIs
- GraphQL
- Webhooks
- gRPC

**Common Patterns**:
- Rate limiting
- Retry logic
- Authentication (OAuth, API keys)
- Pagination
- Error handling

**Keyword Triggers**: api, rest, graphql, webhook, integration

---

## DevOps Tools

**Purpose**: Infrastructure and deployment automation

**Key Technologies**:
- **Docker**: Containerization
- **Kubernetes**: Container orchestration
- **GitHub Actions**: CI/CD
- **Terraform**: Infrastructure as Code
- **Ansible**: Configuration management

**Keyword Triggers**: docker, kubernetes, ci/cd, 部署, deploy, devops

---

## Data Analysis

**Purpose**: Tools for data processing and visualization

**Stack**:
- **Jupyter**: Interactive notebooks
- **pandas**: Data manipulation
- **polars**: Fast dataframe library
- **matplotlib/plotly**: Visualization
- **scikit-learn**: Machine learning

**Keyword Triggers**: 数据分析, pandas, jupyter, visualization, 图表

---

## Adding New Domains

To add a new domain, edit `config/domains.json`:

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

**Schedule options**: daily, weekly, monthly

**Priority**: Lower number = higher priority (0 is highest)

**Cache TTL** (milliseconds):
- Hot domains: 21600000 (6 hours)
- Medium: 43200000 (12 hours)
- Cold: 86400000 (24 hours)
