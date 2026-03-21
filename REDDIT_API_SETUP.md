# Reddit API 设置指南

## 🎯 目标
获取 Reddit API 凭证以自动发布 Skill Discovery

---

## 📖 详细步骤

### 步骤 1: 登录 Reddit
访问: https://www.reddit.com/login

### 步骤 2: 创建应用
1. 访问: https://www.reddit.com/prefs/apps
2. 滚动到页面底部，找到 "create application" 或 "create another app"
3. 点击按钮创建新应用

### 步骤 3: 填写应用信息

填写以下字段:

```
name: SkillDiscovery
type: ✓ script (选择这个选项)
description: Auto-poster for Skill Discovery open source project
about url: https://github.com/ei060/skill-discovery
redirect uri: http://localhost:8080
```

**重要:**
- type 必须选择 **"script"**
- redirect uri 填写 **http://localhost:8080**

### 步骤 4: 获取凭证

创建应用后，你会看到:

```
client_id     (顶部，14个字符的字符串)
client_secret (密钥，大约30个字符)
user_agent    (你自定义的标识符)
```

**示例:**
```
client_id:     p0J7Gx3...14字符
client_secret: aB3dE5f...30字符
```

### 步骤 5: 配置脚本

打开 `scripts/auto_post_reddit.py`

找到这部分:
```python
REDDIT_CREDENTIALS = {
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "user_agent": "SkillDiscovery/1.0 by ei060",
    "username": "YOUR_REDDIT_USERNAME",
    "password": "YOUR_REDDIT_PASSWORD"
}
```

替换为:
```python
REDDIT_CREDENTIALS = {
    "client_id": "p0J7Gx3...",          # 你的 client_id
    "client_secret": "aB3dE5f...",      # 你的 client_secret
    "user_agent": "SkillDiscovery/1.0 by ei060",
    "username": "你的Reddit用户名",
    "password": "你的Reddit密码"
}
```

### 步骤 6: 安装依赖

```bash
pip install praw
```

### 步骤 7: 测试连接

```bash
python scripts/auto_post_reddit.py
```

选择 "3. 测试模式" 检查配置是否正确。

---

## 🔒 安全提示

### 不要暴露凭证
- **不要** 提交包含真实凭证的代码到 GitHub
- **不要** 在公开场合分享 client_secret
- **不要** 在截图时显示敏感信息

### 推荐做法

**方法 1: 环境变量**
```python
import os

REDDIT_CREDENTIALS = {
    "client_id": os.getenv("REDDIT_CLIENT_ID"),
    "client_secret": os.getenv("REDDIT_CLIENT_SECRET"),
    "user_agent": "SkillDiscovery/1.0 by ei060",
    "username": os.getenv("REDDIT_USERNAME"),
    "password": os.getenv("REDDIT_PASSWORD")
}
```

设置环境变量:
```bash
# Windows
set REDDIT_CLIENT_ID=p0J7Gx3...
set REDDIT_CLIENT_SECRET=aB3dE5f...
set REDDIT_USERNAME=你的用户名
set REDDIT_PASSWORD=你的密码

# Linux/Mac
export REDDIT_CLIENT_ID="p0J7Gx3..."
export REDDIT_CLIENT_SECRET="aB3dE5f..."
export REDDIT_USERNAME="你的用户名"
export REDDIT_PASSWORD="你的密码"
```

**方法 2: 配置文件 (不提交到 Git)**

创建 `scripts/reddit_config.json`:
```json
{
  "client_id": "p0J7Gx3...",
  "client_secret": "aB3dE5f...",
  "user_agent": "SkillDiscovery/1.0 by ei060",
  "username": "你的用户名",
  "password": "你的密码"
}
```

添加到 `.gitignore`:
```
scripts/reddit_config.json
```

在 Python 中使用:
```python
import json

with open("scripts/reddit_config.json") as f:
    REDDIT_CREDENTIALS = json.load(f)
```

---

## 🚀 使用脚本

### 模式 1: 发布所有帖子 (自动延迟)

```bash
python scripts/auto_post_reddit.py
```

选择 "1" - 会自动发布所有帖子，每个之间延迟15分钟

### 模式 2: 发布单个帖子

```bash
python scripts/auto_post_reddit.py
```

选择 "2" - 手动选择要发布的子版块

### 模式 3: 测试模式

```bash
python scripts/auto_post_reddit.py
```

选择 "3" - 查看将要发布的内容，不实际发布

---

## 📊 监控发布结果

发布完成后，脚本会生成 `reddit_posts.json`:

```json
{
  "timestamp": "2026-02-26T21:34:00",
  "posts": [
    {
      "success": true,
      "subreddit": "programming",
      "url": "https://reddit.com/r/programming/comments/...",
      "id": "..."
    }
  ]
}
```

---

## ⚠️ 常见问题

### Q1: "401 Unauthorized" 错误
**原因:** 凭证错误
**解决:**
1. 检查 client_id 和 client_secret 是否正确
2. 确认 Reddit 用户名和密码正确
3. 确保应用 type 是 "script"

### Q2: "429 Too Many Requests"
**原因:** Reddit API 速率限制
**解决:**
- 等待几分钟后重试
- 增加帖子之间的延迟时间

### Q3: 帖子发布后立即被删除
**原因:** 可能被 Reddit 的垃圾过滤器识别
**解决:**
1. 检查是否符合子版块规则
2. 联系版主人工审核
3. 等待一段时间后重新发布

### Q4: 某个子版块发布失败
**原因:**
- 可能是子版块限制
- 帖子格式不符合要求
- 账户权限不足

**解决:**
1. 检查子版块规则
2. 手动访问该子版块确认
3. 跳过该子版块，继续发布其他的

---

## 🎯 推荐策略

### 首次发布
1. 先用测试模式验证内容
2. 发布到 1-2 个子版块测试
3. 观察反应和反馈
4. 根据结果调整内容

### 完整发布
1. 选择美国东部时间早上 8-10 点
2. 按推荐顺序发布:
   - r/programming (最大受众)
   - r/Python (针对性)
   - r/MachineLearning (AI/ML)
   - r/opensource (开源社区)
3. 每个帖子间隔 15 分钟
4. 发布后积极回复评论

---

## 📞 需要帮助?

如果遇到问题:
1. 检查 Reddit API 文档: https://praw.readthedocs.io/
2. 查看 PRAW 文档: https://praw.readthedocs.io/
3. 检查 Reddit 应用设置: https://www.reddit.com/prefs/apps

---

## ✅ 完成检查清单

- [ ] 创建 Reddit 应用
- [ ] 复制 client_id
- [ ] 复制 client_secret
- [ ] 填写用户名密码
- [ ] 安装 `pip install praw`
- [ ] 测试连接
- [ ] 运行测试模式
- [ ] 发布第一个帖子
- [ ] 检查发布结果
- [ ] 监控评论反馈

---

祝发布顺利！🚀
