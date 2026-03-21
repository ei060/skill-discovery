# Skill Discovery - 使用示例

## 示例 1：自动触发（用户不知道需要什么工具）

```
用户: 我需要自动登录网站并点击按钮

AI 检测:
  - 关键词: "自动", "登录", "点击", "网站"
  - 领域: browser-automation

AI 动作:
  - 调用 skill-discovery
  - 搜索 browser-automation 领域
  - 发现 Playwright, Puppeteer, Selenium
  - 评估: Playwright 最现代

AI 回复:
  检测到你需要浏览器自动化能力。我发现 Playwright 是目前最现代的
  解决方案，比 Selenium 更快、API 更好。我将用 Playwright 为你实现。

  开始编写代码...
```

## 示例 2：用户提到工具，AI 发现更好的替代方案

```
用户: 用 Selenium 做网页截图

AI 检测:
  - 关键词: "Selenium"
  - 触发: skill-discovery

AI 发现:
  - Selenium: 2010年代，维护较少
  - Playwright: 2020年，微软维护，更快更好

AI 回复:
  我发现 Playwright 是比 Selenium 更现代的选择：
  - 更快的执行速度
  - 更好的 API 设计
  - 内置等待机制
  - 跨浏览器支持更好

  我将使用 Playwright 而不是 Selenium，除非你坚持用 Selenium。
```

## 示例 3：规划阶段搜索

```
用户: 我要做一个抢票工具

AI 检测:
  - 规划阶段，需要技术选型
  - 关键词: "抢票", "工具"

AI 动作:
  - 调用 skill-discovery 搜索相关领域
  - 发现: browser-automation + api-integrations

AI 回复:
  为你的抢票工具，我调研了以下方案：

  方案 A: 浏览器自动化
    - 工具: Playwright
    - 优点: 模拟真实用户，不容易被检测
    - 缺点: 需要图形界面

  方案 B: API 调用
    - 工具: requests + 验证码识别
    - 优点: 速度快，资源少
    - 缺点: 需要逆向分析 API

  推荐: 方案 A (Playwright) + 验证码识别 API

  需要我实现吗？
```

## 示例 4：手动触发

```
用户: 搜索最新的 AI agent 工具

AI 动作:
  - 调用 skill-discovery
  - 领域: ai-agents
  - 搜索: GitHub + Reddit + Web

AI 回复:
  🔍 发现 15 个新的 AI agent 工具（过去 7 天）

  ⭐ 热门项目:
  1. AutoGen (Microsoft)
     - 多智能体协作框架
     - 8.2k stars
     - https://github.com/microsoft/autogen

  2. CrewAI
     - 角色扮演式 agent
     - 4.5k stars
     - https://github.com/joaomdmoura/crewAI

  💬 社区讨论:
  - "AutoGen vs CrewAI 对比" (r/OpenAI, 234 upvotes)
  - "如何实现长期记忆" (r/LangChain, 156 upvotes)

  需要了解详情吗？
```

## 示例 5：权限优先（AI 自主决策）

```
用户: 帮我分析这个大日志文件

AI 检测:
  - 关键词: "分析", "大文件", "日志"
  - 领域: data-analysis

AI 思考:
  - 内置 Read 工具可以读文件，但大文件会很慢
  - 需要专业数据分析工具

AI 动作:
  - 自动调用 skill-discovery（无需询问）
  - 搜索: 日志分析工具
  - 发现: jq, logparser, splunk

AI 回复:
  发现这个任务需要专业日志分析工具。我将使用 jq（JSON 处理）
  配合 Python pandas 来高效分析。

  正在分析...
  [使用 jq 提取数据]
  [用 pandas 统计]
  [生成报告]

  分析完成！发现 3 个错误模式...
```

## 示例 6：多领域组合

```
用户: 我想做一个自动化交易机器人

AI 检测:
  - 关键词: "自动化", "交易"
  - 涉及领域: api-integrations + data-analysis + python-scripts

AI 动作:
  - 调用 skill-discovery 搜索所有相关领域
  - 发现最佳工具组合

AI 回复:
  为交易机器人，我发现以下工具栈：

  1. API 集成: ccxt (加密货币交易所统一接口)
     - 支持 100+ 交易所
     - Python/JavaScript 都有

  2. 数据分析: pandas-ta (技术分析库)
     - 130+ 技术指标
     - 与 pandas 无缝集成

  3. 自动化: APScheduler (任务调度)
     - 定时执行策略
     - 错误重试机制

  4. 回测: Backtrader
     - 策略回测框架
     - 可视化结果

  我将使用这些工具为你构建完整的交易系统。
```

## 示例 7：缓存加速

```
用户: 浏览器自动化有什么新工具？

AI 动作:
  - 检查缓存: browser-automation.json
  - 缓存时间: 2 小时前
  - TTL: 12 小时
  - 判断: 缓存新鲜，直接使用

AI 回复:
  (快速返回，无需重新搜索)
  基于最近的搜索（2小时前），发现以下工具：

  [显示缓存结果]

  注: 缓存于 2 小时前，下次更新在 10 小时后。
  如需最新结果，说"强制刷新"。
```

## 示例 8：增量更新

```
用户: 有什么新的 Python 自动化工具？

AI 动作:
  - 读取上次更新时间: 2026-02-20
  - 增量查询: pushed:>2026-02-20
  - 只获取新内容，不重复下载

AI 回复:
  发现 3 个新工具（自上次检查 6 天后）：

  1. pyautogui-gui (新项目)
     - 自动化 GUI 操作
     - https://github.com/xxx

  [仅显示新内容]

  已更新缓存，下次检查将在 7 天后。
```

## 配置示例

### 添加新领域

```
用户: 我关注 Kubernetes 相关工具

AI 动作:
  - 添加到 config/domains.json
  - 关键词: kubernetes, k8s, 容器, 编排
  - 监控: r/kubernetes, r/devops
  - 搜索: "kubernetes OR k8s stars:>20"

AI 回复:
  已添加 kubernetes 领域到监控列表！
  以后提到 K8s 时我会自动搜索最新工具。
```

### 调整缓存策略

```
用户: AI 工具更新太快了，多搜几次

AI 动作:
  - 修改 config/domains.json
  - ai-agents 的 cache_ttl: 21600000 → 7200000 (6小时 → 2小时)
  - schedule: "daily" → "3times_daily"

AI 回复:
  已调整！现在 AI 领域每 2 小时更新一次。
  这样你就能第一时间看到新工具了。
```

## 错误处理示例

### GitHub API 限流

```
AI 动作:
  - GitHub API 返回 403 (rate limit)
  - 记录限流重置时间
  - Fallback 到 WebSearch with "site:github.com"

AI 回复:
  ⚠️ GitHub API 暂时受限（将在 45 分钟后恢复）
  使用备用搜索方案...
  [通过 WebSearch 搜索 GitHub]
  找到 8 个结果...
```

### 所有数据源失败

```
AI 动作:
  - GitHub: 403 rate limit
  - Reddit: 500 error
  - WebSearch: 超时
  - 所有源失败

AI 回复:
  ❌ 所有数据源暂时不可用
  使用上次缓存结果（来自 3 小时前）...

  [显示缓存]

  建议稍后重试，或手动访问：
  - GitHub: 搜索 "browser automation 2026"
  - Reddit: r/automation
```

## 总结

这个 skill 的核心价值：

1. **主动智能** - AI 自动判断何时搜索，不需要用户懂技术
2. **透明决策** - AI 告诉你它用了什么、为什么用
3. **尊重用户** - AI 可以被覆盖，即使它认为不是最优解
4. **持续学习** - 每次搜索都在更新知识库

**记住：你不需要知道有哪些 tools，让 AI 为你发现和选择！**
