# 6551 MCP 快速开始指南

## 📋 第一步: 获取 API Token

1. 在浏览器打开: **https://6551.io/mcp**
2. 完成 Cloudflare 验证
3. 注册/登录账户
4. 复制 API Token

## 🔧 第二步: 配置 Token

### 方法 A: 直接编辑配置文件

编辑这两个文件，将 `YOUR_TOKEN_HERE` 替换为你的 Token:

```
D:/ClaudeWork/AI_Roland/system/skills/opennews-mcp/config.json
D:/ClaudeWork/AI_Roland/system/skills/opentwitter-mcp/config.json
```

### 方法 B: 使用脚本

```bash
python D:/ClaudeWork/setup_6551_token.py
```
然后粘贴你的 Token。

## 🧪 第三步: 测试连接

```bash
python D:/ClaudeWork/test_6551_mcp_connection.py
```

## 🔗 第四步: 配置 Claude Desktop

找到 Claude Desktop 配置文件:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

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

## 🚀 第五步: 重启并使用

1. 重启 Claude Desktop
2. 在对话中使用:
   - "获取最新的加密货币新闻"
   - "搜索比特币相关新闻"
   - "查看 @elonmusk 的最新推文"

---

## 📊 可用工具

### opennews-mcp (72+ 数据源)
- `get_latest_news` - 最新新闻
- `search_news` - 关键词搜索
- `search_news_by_coin` - 币种搜索
- `get_news_by_source` - 来源筛选

### opentwitter-mcp
- `get_twitter_user` - 用户资料
- `get_twitter_user_tweets` - 用户推文
- `search_twitter` - 推文搜索
- `get_twitter_follower_events` - 粉丝变化

---

## 📁 文件位置

| 文件 | 位置 |
|------|------|
| opennews-mcp | `AI_Roland/system/skills/opennews-mcp/` |
| opentwitter-mcp | `AI_Roland/system/skills/opentwitter-mcp/` |
| 配置模板 | 上述目录下的 `config.json` |
| 测试脚本 | `D:/ClaudeWork/test_6551_mcp_connection.py` |
| Token 设置 | `D:/ClaudeWork/setup_6551_token.py` |
