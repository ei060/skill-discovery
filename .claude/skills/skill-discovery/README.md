# Skill Discovery

> **Automatically discover and track the latest AI skills, tools, and automation frameworks**
> **自动发现和跟踪最新的AI技能、工具和自动化框架**

---

## Quick Links / 快速链接

- [Features / 功能](#features--功能)
- [Installation / 安装](#installation--安装)
- [Usage / 使用](#usage--使用)
- [⚠️ Security Notice / 安全警告](#-security-notice--安全警告)
- [Configuration / 配置](#configuration--配置)
- [Development / 开发](#development--开发)
- [Contributing / 贡献](#contributing--贡献)

---

## Features / 功能

Skill Discovery automatically searches GitHub, Reddit, and the web to find relevant tools and skills for any task. It operates autonomously - no manual search required.

Skill Discovery自动搜索GitHub、Reddit和网络以查找与任何任务相关的工具和技能。它自主运行 - 无需手动搜索。

### Key Capabilities / 核心能力

- 🔍 **Automatic Discovery / 自动发现** - Detects tool needs from context
- 🔄 **Multi-Source Search / 多源搜索** - GitHub, Reddit, WebSearch
- 💾 **Smart Caching / 智能缓存** - Avoids redundant API calls
- 🎯 **Domain-Aware / 域感知** - Specialized search by technology domain
- 🚀 **Auto-Integration / 自动集成** - Invokes relevant skills automatically

### Supported Domains / 支持的域

- **browser-automation** - Puppeteer, Playwright, Selenium
- **ai-agents** - OpenClaw, Claude, autonomous agents
- **python-scripts** - Python automation tools
- **devops-tools** - Docker, Kubernetes, CI/CD
- **api-integrations** - REST APIs, GraphQL, webhooks

---

## Installation / 安装

### Prerequisites / 先决条件

- Claude Code with MCP support / 支持MCP的Claude Code
- Python 3.8+ (for search scripts) / Python 3.8+（用于搜索脚本）
- Optional: GitHub API token for higher rate limits / 可选：GitHub API令牌以提高速率限制

### Setup / 设置

1. **Clone or download this skill / 克隆或下载此技能**
   ```bash
   # If in a git repository
   git clone <repository-url>
   ```

2. **Configure environment variables / 配置环境变量**
   ```bash
   # Create .env file (see .env.example)
   cp .env.example .env

   # Add your tokens (optional, for higher rate limits)
   GITHUB_TOKEN=your_token_here
   REDDIT_CLIENT_ID=your_client_id
   REDDIT_CLIENT_SECRET=your_client_secret
   ```

3. **Verify installation / 验证安装**
   ```bash
   # Check configuration
   ls config/
   # Should see: domains.json, behavior.json
   ```

---

## Usage / 使用

### Basic Usage / 基本用法

Skill Discovery activates automatically when you mention relevant keywords or tasks:

当您提及相关关键词或任务时，Skill Discovery会自动激活：

```markdown
User: I need to automate browser testing
[Skill Discovery automatically searches for browser automation tools]
→ Found: Playwright, Puppeteer, Cypress
```

### Manual Invocation / 手动调用

```markdown
User: Search for the latest Docker orchestration tools
[Skill Discovery executes search]
→ Returns: Docker Compose, Kubernetes, Portainer
```

### Configuration / 配置

**Adjust Search Domains / 调整搜索域**

Edit `config/domains.json` to add/remove domains:

编辑 `config/domains.json` 添加/删除域：

```json
{
  "web-automation": {
    "keywords": ["selenium", "playwright", "browser control"],
    "github_query": "browser automation",
    "subreddits": ["Python", "javascript"],
    "cache_ttl": 43200000
  }
}
```

**Adjust Behavior / 调整行为**

Edit `config/behavior.json`:

```json
{
  "auto_discovery": true,
  "auto_use_skills": true,
  "ask_before_using": false,
  "max_results_per_source": 20
}
```

---

## ⚠️ Security Notice / 安全警告

### 🚨 CRITICAL WARNING: Third-Party Skill Security / 🚨 关键警告：第三方Skill安全

**Based on security research: "小心你的私密信息被偷走！OpenClaw Skill 安装教程与安全指南"**
**基于安全研究："小心你的私密信息被偷走！OpenClaw Skill 安装教程与安全指南"**

**⚠️ SKILLS MAY STEAL YOUR API KEYS AND PRIVATE DATA**
**⚠️ Skill可能窃取您的API密钥和私人数据**

**Video Reference / 视频参考:** Chapter 5:47 - Privacy Leak and Security
**章节参考：** 5:47 - 隐私泄露和安全

#### The Danger / 危险

**Malicious skills can:**
**恶意Skill可以：**

- 🔓 **Steal your API keys** from environment variables
  🔓 **从环境变量窃取您的API密钥**
- 📤 **Exfiltrate your data** to external servers
  📤 **将您的数据渗透到外部服务器**
- 📊 **Log your conversations** and private information
  📊 **记录您的对话和私人信息**
- 🎭 **Execute arbitrary code** on your system
  🎭 **在您的系统上执行任意代码**

**Real Example from Video / 视频中的真实示例：**
The OpenClaw Skill demonstration shows how a skill could potentially access environment variables, make network requests to unknown servers, and extract sensitive information from your system without your knowledge.

OpenClaw Skill演示展示了skill如何可能在您不知情的情况下访问环境变量、向未知服务器发出网络请求并从您的系统提取敏感信息。

---

### Critical Security Information / 关键安全信息

**IMPORTANT: Read this before using or contributing to this skill**
**重要：在使用或贡献此技能前请阅读此内容**

#### 🚨 Security Risks / 安全风险

This skill involves:
- **External API calls** to GitHub, Reddit, and web services
- **Third-party code execution** when invoking discovered tools
- **Data transmission** over public networks
- **Caching of search results** that may contain sensitive information
- **Potential exposure to malicious third-party skills** during discovery

此技能涉及：
- **外部API调用**到GitHub、Reddit和网络服务
- **第三方代码执行**当调用发现的工具时
- **公共网络上的数据传输**
- **可能包含敏感信息的搜索结果缓存**
- **发现期间潜在暴露于恶意第三方skill**

#### ✅ Security Best Practices / 安全最佳实践

**For Users / 用户:**

1. **🔍 AUDIT Every Skill Before Installation / 🔍 安装前审计每个Skill**
   - Use the [SKILL_AUDIT_CHECKLIST.md](SKILL_AUDIT_CHECKLIST.md) / 使用Skill审计检查清单
   - Check for credential access patterns / 检查凭据访问模式
   - Review all code manually / 手动审查所有代码
   - NEVER install without auditing / 永不在未审计的情况下安装

2. **🔒 Protect Your API Keys / 🔒 保护您的API密钥**
   - Use separate API keys for different skills / 为不同的skill使用单独的API密钥
   - Limit key permissions to minimum necessary / 将密钥权限限制到最小必要
   - Rotate keys regularly (every 30-90 days) / 定期轮换密钥（每30-90天）
   - Monitor API usage for unusual activity / 监控API使用是否有异常活动
   - Never paste API keys in conversations / 永不在对话中粘贴API密钥

3. **🚫 Recognize Danger Patterns / 🚫 识别危险模式**
   ```bash
   # ❌ IMMEDIATE REJECTION if you find:
   # ❌ 如果发现以下内容立即拒绝：

   grep -r "os.getenv" <skill-dir>    # Steals env vars / 窃取环境变量
   grep -r "process.env" <skill-dir>  # Steals env vars / 窃取环境变量
   grep -r "requests.post" <skill-dir> # Exfiltrates data / 渗透数据
   grep -r "\.claude" <skill-dir>     # Accesses config / 访问配置
   grep -r "exec(" <skill-dir>        # Executes code / 执行代码
   ```

4. **📊 Monitor Usage / 📊 监控使用情况**
   - Review which skills are being invoked / 审查正在调用哪些技能
   - Check cache contents regularly / 定期检查缓存内容
   - Audit access logs / 审计访问日志
   - Monitor network activity / 监控网络活动
   - Review API usage logs / 审查API使用日志

5. **🛡️ Safe Discovery Practices / 🛡️ 安全发现实践**
   - Only use trusted skill sources / 仅使用受信任的skill来源
   - Verify discovered tools before using / 使用前验证发现的工具
   - Test skills in isolated environment / 在隔离环境中测试skill
   - Review discovered tool code / 审查发现的工具代码

**For Developers / 开发者:**

1. **Before adding features / 添加功能前**
   - Review [SECURITY.md](SECURITY.md) / 审查安全指南
   - Complete [SKILL_AUDIT_CHECKLIST.md](SKILL_AUDIT_CHECKLIST.md) / 完成Skill审计检查清单
   - Test for common vulnerabilities / 测试常见漏洞
   - Ensure no credential access / 确保无凭据访问

2. **When handling external data / 处理外部数据时**
   - Sanitize all inputs / 清理所有输入
   - Validate data sources / 验证数据源
   - Filter sensitive information / 过滤敏感信息
   - Never log credentials / 永不记录凭据
   - Don't expose user data / 不暴露用户数据

3. **Before publishing / 发布前**
   - Remove all test credentials / 删除所有测试凭据
   - Run security audits / 运行安全审计
   - Enable secret scanning / 启用密钥扫描
   - Review commit history / 审查提交历史
   - Document all permissions / 记录所有权限

4. **Security by design / 安全设计**
   - Minimal permissions principle / 最小权限原则
   - No unnecessary network calls / 无不必要的网络调用
   - No credential access / 无凭据访问
   - Transparent behavior / 透明行为
   - Clear documentation / 清晰文档

#### 🚨 Emergency Response / 🚨 紧急响应

**If you suspect a skill is malicious:**
**如果您怀疑skill是恶意的：**

```bash
# 1. IMMEDIATE: Revoke all API keys
# 1. 立即：撤销所有API密钥
# Visit your API provider's dashboard
# 访问您的API提供商仪表板

# 2. Remove the skill
# 2. 移除skill
rm -rf ~/.claude/skills/<suspicious-skill>

# 3. Check for compromise
# 3. 检查入侵
# Review API usage logs
# 审查API使用日志
# Look for unauthorized access
# 寻找未授权访问

# 4. Rotate ALL credentials
# 4. 轮换所有凭据
# Assume all keys may be compromised
# 假设所有密钥可能已泄露
```

#### 📋 Security Resources / 安全资源

- **[Complete Security Guide / 完整安全指南](SECURITY.md)** - Comprehensive security documentation with skill-specific threats
- **[Skill Audit Checklist / Skill审计检查清单](SKILL_AUDIT_CHECKLIST.md)** - Step-by-step audit procedure for ANY skill
- **[GitHub Security Guidelines](https://docs.github.com/en/security)** - Official GitHub security documentation
- **[OWASP Top 10](https://owasp.org/www-project-top-ten/)** - Critical web application security risks
- **[Video: OpenClaw Security Guide](https://youtu.be/watch?v=***REMOVED***)** - "小心你的私密信息被偷走！" (Chapter 5:47)

#### 🚨 Reporting Security Issues / 报告安全问题

**If you discover a security vulnerability:**
**如果您发现安全漏洞：**

1. **DO NOT** open a public issue / **不要**创建公共issue
2. **DO** send details via private disclosure / **要**通过私人渠道发送详细信息
3. **DO** include steps to reproduce / **要**包含复现步骤
4. **DO** suggest a fix if possible / **如果可能，要**建议修复方案
5. **IMMEDIATELY** revoke any exposed credentials / **立即**撤销任何暴露的凭据

**Responsible Disclosure Policy / 负责任披露政策:**
- We will respond within 48 hours / 我们将在48小时内响应
- We will provide a timeline for fix / 我们将提供修复时间表
- We will credit you for the discovery / 我们将认可您的发现

---

**Remember / 记住:**

> ⚠️ **Every skill you install has access to your system. Treat it like installing any other software.**
> ⚠️ **您安装的每个skill都有访问您系统的权限。像安装任何其他软件一样对待它。**

> 🔍 **Always audit skills before installation. Your security is worth more than any feature.**
> 🔍 **安装前始终审计skill。您的安全比任何功能都重要。**

> 🚨 **If in doubt, don't install. If something seems wrong, investigate immediately.**
> 🚨 **如果有疑问，不要安装。如果看起来不对，立即调查。**

---

## Configuration / 配置

### Domain Configuration / 域配置

Located in `config/domains.json`:

```json
{
  "browser-automation": {
    "keywords": ["browser", "automation", "scrape", "puppeteer"],
    "sources": ["github", "reddit", "web"],
    "github_query": "browser automation language:javascript OR python",
    "subreddits": ["Python", "javascript", "webdev"],
    "schedule": "0 */6 * * *",
    "priority": 1.0,
    "cache_ttl": 43200000
  }
}
```

### Behavior Configuration / 行为配置

Located in `config/behavior.json`:

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

---

## Development / 开发

### Project Structure / 项目结构

```
skill-discovery/
├── SKILL.md                 # Main skill definition
├── README.md                # This file
├── SECURITY.md              # Security guidelines
├── SECURITY_CHECKLIST.md    # Security checklists
├── DESIGN.md                # Design documentation
├── USAGE_EXAMPLES.md        # Usage examples
├── QUICK_REFERENCE.md       # Quick reference guide
├── config/
│   ├── domains.json         # Domain configurations
│   └── behavior.json        # Behavior settings
├── scripts/
│   ├── search_github.py     # GitHub search
│   ├── search_reddit.py     # Reddit search
│   ├── merge_results.py     # Result merging
│   └── update_cache.py      # Cache management
├── references/
│   ├── domains.md           # Domain documentation
│   └── api_limits.md        # API rate limits
└── cache/
    └── index.json           # Cache index
```

### Running Scripts / 运行脚本

```bash
# Search GitHub for repositories
python scripts/search_github.py

# Search Reddit for discussions
python scripts/search_reddit.py

# Update cache
python scripts/update_cache.py
```

---

## Contributing / 贡献

### Before Contributing / 贡献前

1. **Read Security Documentation / 阅读安全文档**
   - [SECURITY.md](SECURITY.md) - Complete security guide / 完整安全指南
   - [SECURITY_CHECKLIST.md](SECURITY_CHECKLIST.md) - Security checklists / 安全检查清单

2. **Follow Security Best Practices / 遵循安全最佳实践**
   - Never commit sensitive data / 永不提交敏感数据
   - Use environment variables / 使用环境变量
   - Sanitize all inputs / 清理所有输入
   - Review dependencies / 审查依赖

3. **Complete Checklist / 完成清单**
   - Run security scans / 运行安全扫描
   - Test thoroughly / 彻底测试
   - Document changes / 记录更改

### Pull Request Process / 拉取请求流程

1. Fork the repository / 分叉仓库
2. Create a feature branch / 创建功能分支
3. Make your changes / 进行更改
4. Run security checks / 运行安全检查
5. Submit a pull request / 提交拉取请求
6. Address review feedback / 处理审查反馈

---

## Troubleshooting / 故障排除

### Common Issues / 常见问题

**Issue: Rate limit exceeded / 问题：超过速率限制**
- Solution / 解决方案: Wait or use authenticated API requests / 等待或使用经过身份验证的API请求

**Issue: Cache not updating / 问题：缓存未更新**
- Solution / 解决方案: Check cache TTL in config / 检查配置中的缓存TTL

**Issue: No results found / 问题：未找到结果**
- Solution / 解决方案: Adjust domain keywords in config / 调整配置中的域关键字

---

## Performance / 性能

### Caching Strategy / 缓存策略

- **Memory cache / 内存缓存**: 1 hour TTL / 1小时TTL
- **File cache / 文件缓存**: 24 hour TTL / 24小时TTL
- **Domain-specific TTL / 特定域TTL**:
  - Hot domains (AI tools): 6 hours / 热域（AI工具）：6小时
  - Medium domains (browser automation): 12 hours / 中等域（浏览器自动化）：12小时
  - Cold domains (scripts): 24 hours / 冷域（脚本）：24小时

### Rate Limits / 速率限制

- **GitHub API**: 60 requests/hour (unauthenticated) / GitHub API：60请求/小时（未认证）
- **Reddit API**: 60 requests/minute / Reddit API：60请求/分钟
- **WebSearch**: Unlimited / WebSearch：无限

---

## License / 许可证

This project is licensed under the MIT License.

---

## Support / 支持

- **Issues / 问题**: [GitHub Issues](https://github.com/yourusername/skill-discovery/issues)
- **Security / 安全**: See [SECURITY.md](SECURITY.md) for reporting procedures / 查看安全指南了解报告流程
- **Documentation / 文档**: See `references/` folder / 查看 references/ 文件夹

---

## Acknowledgments / 致谢

- GitHub Search API
- Reddit API
- OpenAI for Claude Code
- All contributors and users / 所有贡献者和用户

---

**Remember / 记住:**

> Security is everyone's responsibility.
> 安全是每个人的责任。

> When in doubt, check the security documentation.
> 有疑问时，查看安全文档。

> Use this skill wisely and safely.
> 明智且安全地使用此技能。

---

**Last Updated / 最后更新:** 2026-02-27
**Version / 版本:** 1.0.0
