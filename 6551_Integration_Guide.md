# 6551 MCP 集成 AI Roland 指南

**集成日期**: 2026-03-14
**状态**: 🔄 进行中

---

## 一、已完成步骤

### 1. 仓库克隆 ✅

| 仓库 | 路径 | 状态 |
|------|------|------|
| opennews-mcp | `AI_Roland/system/skills/opennews-mcp` | ✅ 已克隆 |
| opentwitter-mcp | `AI_Roland/system/skills/opentwitter-mcp` | ✅ 已克隆 |

### 2. 依赖检查 ✅

**opennews-mcp**:
- mcp[cli] >= 1.25
- httpx >= 0.27
- websockets >= 13

**opentwitter-mcp**:
- mcp[cli] >= 1.25
- httpx >= 0.27

### 3. 可用工具汇总

**opennews-mcp** (72+ 数据源):
- `get_latest_news` - 获取最新新闻
- `search_news` - 关键词搜索
- `search_news_by_coin` - 币种搜索
- `get_news_by_source` - 按来源获取
- `get_news_sources` - 获取所有来源

**opentwitter-mcp**:
- `get_twitter_user` - 获取用户资料
- `get_twitter_user_tweets` - 获取用户推文
- `search_twitter` - 推文搜索
- `search_twitter_advanced` - 高级搜索
- `get_twitter_follower_events` - 粉丝变化
- `get_twitter_deleted_tweets` - 已删除推文
- `get_twitter_kol_followers` - KOL 粉丝
- `get_twitter_watch` / `add_twitter_watch` / `delete_twitter_watch` - 监控功能

---

## 二、待完成步骤

### 步骤 1: 获取 API Token

**方法 A: 自动获取**
```bash
python D:/ClaudeWork/get_6551_token.py
```
这会打开浏览器，导航到 https://6551.io/mcp，你只需：
1. 完成 Cloudflare 验证
2. 注册/登录
3. 获取 Token
4. 粘贴到脚本

**方法 B: 手动获取**
1. 访问: https://6551.io/mcp
2. 注册/登录账户
3. 复制 API Token
4. 创建配置文件:

```json
// D:/ClaudeWork/AI_Roland/system/skills/opennews-mcp/config.json
{
  "api_base_url": "https://ai.6551.io",
  "api_token": "你的Token",
  "max_rows": 100
}
```

```json
// D:/ClaudeWork/AI_Roland/system/skills/opentwitter-mcp/config.json
{
  "api_base_url": "https://ai.6551.io",
  "api_token": "你的Token",
  "max_rows": 100
}
```

### 步骤 2: 测试连接

```bash
python D:/ClaudeWork/test_6551_mcp_connection.py
```

### 步骤 3: 安装依赖

```bash
# 安装 uv (如果还没有)
pip install uv

# 安装 MCP 依赖
cd D:/ClaudeWork/AI_Roland/system/skills/opennews-mcp
uv pip install -e .

cd D:/ClaudeWork/AI_Roland/system/skills/opentwitter-mcp
uv pip install -e .
```

### 步骤 4: 配置 Claude Desktop

找到 Claude Desktop 配置文件:
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

添加以下配置:

```json
{
  "mcpServers": {
    "opennews": {
      "command": "uv",
      "args": [
        "--directory",
        "D:\\ClaudeWork\\AI_Roland\\system\\skills\\opennews-mcp",
        "run",
        "opennews-mcp"
      ],
      "env": {
        "OPENNEWS_TOKEN": "你的Token"
      }
    },
    "twitter": {
      "command": "uv",
      "args": [
        "--directory",
        "D:\\ClaudeWork\\AI_Roland\\system\\skills\\opentwitter-mcp",
        "run",
        "twitter-mcp"
      ],
      "env": {
        "TWITTER_TOKEN": "你的Token"
      }
    }
  }
}
```

### 步骤 5: 重启 Claude 并测试

重启 Claude Desktop，然后在对话中测试:

```
你: 获取最新的加密货币新闻
AI: [调用 get_latest_news]

你: 搜索比特币相关新闻
AI: [调用 search_news]

你: 查看 @elonmusk 的最新推文
AI: [调用 get_twitter_user_tweets]
```

---

## 三、AI Roland 集成方案

### 方案 A: Claude Desktop MCP (推荐)

使用 Claude Desktop 的 MCP 支持，直接连接 6551 MCP 服务器。

**优势**: 原生支持，配置简单

### 方案 B: AI Roland 内部集成

在 AI Roland 的 engine 中直接调用 MCP 工具。

```python
# 在 AI_Roland/system/engine.py 中
from mcp import ClientSession, StdioServerParameters

async def call_6551_mcp(tool_name, **kwargs):
    # 连接到 6551 MCP
    # 调用工具
    # 返回结果
    pass
```

### 方案 C: 混合模式

- 使用 6551 MCP 作为主要数据源
- 保留 network-scraping skill 作为备用
- 根据 Token 余额自动切换

---

## 四、使用示例

### 示例 1: 新闻监控

```
用户: 有什么加密货币新闻？
AI: [调用 get_latest_news]
    根据最新数据...
    [显示新闻列表，包含 AI 评分和交易信号]
```

### 示例 2: Twitter KOL 追踪

```
用户: @VitalikButerin 最近发了什么？
AI: [调用 get_twitter_user_tweets]
    Vitalik Buterin 最近发布了...
    [显示推文列表]
```

### 示例 3: 币种搜索

```
用户: 搜索 ETH 相关新闻
AI: [调用 search_news_by_coin(coin="ETH")]
    找到 ETH 相关新闻...
    [显示新闻，包含链上数据、交易所信息等]
```

---

## 五、故障排除

### 问题 1: Token 无效 (401)

**解决**:
- 检查 Token 是否正确复制
- 访问 https://6551.io/mcp 确认 Token 状态
- 检查 Token 是否过期

### 问题 2: 连接超时

**解决**:
- 检查网络连接
- 确认 https://ai.6551.io 可访问
- 检查防火墙设置

### 问题 3: 工具未显示

**解决**:
- 确认 MCP 配置正确
- 重启 Claude Desktop
- 检查日志文件

---

## 六、成本与限制

| 项目 | 说明 |
|------|------|
| Token 获取 | 需要注册 https://6551.io/mcp |
| 免费额度 | 未知，需注册后查看 |
| 调用限制 | 默认 max_rows=100 |
| 数据源 | 72+ (opennews), Twitter (twitter) |

---

## 七、下一步行动

1. **立即执行**: 获取 API Token
2. **短期**: 测试连接，验证功能
3. **中期**: 集成到 AI Roland workflow
4. **长期**: 构建 24h 监控系统

---

**脚本文件汇总**:

| 脚本 | 功能 |
|------|------|
| `test_6551_integration.py` | 克隆仓库，设置结构 |
| `get_6551_token.py` | 获取 Token 并创建配置 |
| `test_6551_mcp_connection.py` | 测试 MCP 连接 |

**配置文件位置**:
- Token: `D:/ClaudeWork/AI_Roland/6551_tokens.json`
- opennews config: `AI_Roland/system/skills/opennews-mcp/config.json`
- twitter config: `AI_Roland/system/skills/opentwitter-mcp/config.json`
