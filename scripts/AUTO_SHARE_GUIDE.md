# 🚀 自动化分享工具使用指南

> **一键发布到GitHub + Reddit，生成分享报告**

---

## 📋 功能特性

✅ **自动创建GitHub Release** - 通过API一键创建Release
✅ **自动发布到Reddit** - 支持r/Claude, r/artificial, r/opensource
✅ **自动添加GitHub Topics** - 批量添加仓库标签
✅ **生成分享报告** - JSON格式的发布记录
✅ **内容模板化** - 从RELEASE_NOTES.md和SHARE.md自动加载内容

---

## 🔧 安装配置

### 1. 安装依赖

```bash
cd skill-discovery-release
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制配置模板
cp .env.example .env

# 编辑.env文件，填入你的API凭证
```

### 3. 获取API凭证

#### GitHub Token（必需）
1. 访问: https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 勾选权限: `repo` (full control)
4. 生成并复制token
5. 粘贴到 `.env`: `GITHUB_TOKEN=ghp_xxxxxxxxxxxx`

#### Reddit API（可选）
如果不配置，将跳过Reddit发布

1. 访问: https://www.reddit.com/prefs/apps
2. 点击 "create app" 或 "create another app"
3. 填写信息:
   - **name**: `Skill Discovery`
   - **app type**: `script`
   - **description**: `Auto-posting tool`
   - **about url**: `https://github.com/ei060/skill-discovery`
   - **redirect uri**: `http://localhost:8080`
4. 保存后获取 `client_id` 和 `client_secret`
5. 粘贴到 `.env`:
   ```bash
   REDDIT_CLIENT_ID=your_client_id
   REDDIT_CLIENT_SECRET=your_secret
   REDDIT_USERNAME=your_reddit_username
   REDDIT_PASSWORD=your_reddit_password
   ```

---

## 🚀 使用方法

### 方式1: 全自动（推荐）

```bash
# 确保在scripts目录
cd scripts

# 运行自动化脚本
python auto_share.py
```

**输出示例**:
```
============================================================
🚀 Skill Discovery - 自动化分享工具
============================================================

📋 检查配置...

============================================================
📦 步骤 1/4: 创建GitHub Release
============================================================
📝 正在创建Release...
✅ Release创建成功!
   URL: https://github.com/ei060/skill-discovery/releases/tag/v1.0.0

============================================================
🏷️  步骤 2/4: 添加GitHub Topics
============================================================
📝 请手动添加Topics（见上方说明）

============================================================
📱 步骤 3/4: 发布到Reddit
============================================================

📌 发布到 r/Claude...
✅ 发布成功!
   URL: https://reddit.com/r/Claude/comments/xxxxx

📌 发布到 r/artificial...
✅ 发布成功!
   URL: https://reddit.com/r/artificial/comments/xxxxx

📌 发布到 r/opensource...
✅ 发布成功!
   URL: https://reddit.com/r/opensource/comments/xxxxx

============================================================
📊 步骤 4/4: 生成分享报告
============================================================
✅ 报告已保存: share_report.json

============================================================
🎉 自动化分享完成!
============================================================

📋 后续任务:
   1. 手动添加GitHub Topics
   2. 监控Reddit帖子的upvotes和评论
   3. 回复用户问题和反馈
```

---

### 方式2: 分步执行

如果只想执行部分步骤，可以修改脚本或创建独立脚本：

#### 仅创建GitHub Release

```python
from auto_share import GitHubPublisher, ContentTemplates, Config
import os
from dotenv import load_dotenv

load_dotenv()

config = Config()
github = GitHubPublisher(config.GITHUB_TOKEN, config.GITHUB_REPO)
notes = ContentTemplates.load_release_notes()

result = github.create_release(
    tag="v1.0.0",
    title="🎉 Skill Discovery v1.0.0",
    notes=notes
)

print(result)
```

#### 仅发布到Reddit

```python
from auto_share import RedditPublisher, ContentTemplates, Config
import os
from dotenv import load_dotenv

load_dotenv()

config = Config()
reddit = RedditPublisher(
    config.REDDIT_CLIENT_ID,
    config.REDDIT_CLIENT_SECRET,
    config.REDDIT_USERNAME,
    config.REDDIT_PASSWORD
)

title, content = ContentTemplates.load_reddit_post("claude")
result = reddit.post("Claude", title, content)

print(result)
```

---

## 📊 输出文件

### share_report.json

自动化完成后生成的报告：

```json
{
  "timestamp": "2026-02-27T21:00:00",
  "release_tag": "v1.0.0",
  "tasks": {
    "github_release": true,
    "github_topics": false,
    "reddit_claude": true,
    "reddit_artificial": true,
    "reddit_opensource": true
  },
  "links": {
    "github_repo": "https://github.com/ei060/skill-discovery",
    "github_release": "https://github.com/ei060/skill-discovery/releases/tag/v1.0.0",
    "github_settings": "https://github.com/ei060/skill-discovery/settings"
  }
}
```

---

## ⚠️ 常见问题

### 1. GitHub认证失败

**错误**: `401 Unauthorized`

**解决**:
- 检查token是否正确: `GITHUB_TOKEN=ghp_xxx`
- 确认token有`repo`权限
- 重新生成token

### 2. Reddit认证失败

**错误**: `401 Unauthorized` 或 `invalid_grant`

**解决**:
- 检查client_id和secret是否正确
- 确认username和password正确
- 检查app type是否设置为"script"
- 尝试重新创建Reddit app

### 3. Reddit发布失败

**错误**: `rate limit exceeded`

**解决**:
- Reddit有发布频率限制
- 等待10分钟后重试
- 或手动发布（使用SHARE.md中的模板）

### 4. 内容加载失败

**错误**: `RELEASE_NOTES.md not found`

**解决**:
- 确保在正确的目录运行脚本
- 检查文件是否存在: `ls RELEASE_NOTES.md`
- 或手动提供内容字符串

---

## 🔄 自动化流程说明

### 完整流程图

```
开始
  ↓
检查配置 (.env)
  ↓
创建GitHub Release
  ├─ 成功 → 记录URL
  └─ 失败 → 跳过，继续
  ↓
添加GitHub Topics (手动)
  ↓
发布到Reddit
  ├─ r/Claude
  ├─ r/artificial
  └─ r/opensource
  ↓
生成分享报告 (JSON)
  ↓
结束
```

### 时间线

| 步骤 | 预计时间 | 说明 |
|------|----------|------|
| 检查配置 | 5秒 | 验证环境变量 |
| GitHub Release | 10秒 | API调用 |
| GitHub Topics | 3分钟 | 手动添加 |
| Reddit发布 | 30秒/个 | 3个社区 |
| 生成报告 | 2秒 | 写入JSON |
| **总计** | **~5分钟** | 自动化部分 |

---

## 📝 手动回退方案

如果自动化失败，可以手动执行：

### 手动创建GitHub Release
1. 访问: https://github.com/ei060/skill-discovery/releases/new
2. 复制 `RELEASE_NOTES.md` 内容
3. 点击 "Publish release"

### 手动发布到Reddit
1. 访问对应subreddit
2. 点击 "Create Post"
3. 复制 `SHARE.md` 中的对应内容
4. 点击 "Post"

---

## 🔐 安全建议

1. **永远不要提交 `.env` 文件** 到Git
   ```bash
   # .gitignore 应该包含:
   .env
   share_report.json
   ```

2. **使用受限Token**
   - GitHub Token: 只给 `repo` 权限
   - Reddit Token: 只给 `read,submit` 权限

3. **定期轮换Token**
   - 每月更换一次
   - 如果怀疑泄露，立即撤销

4. **检查日志**
   - 查看 `share_report.json`
   - 确认所有URL正确

---

## 🚀 高级用法

### 自定义发布内容

修改 `ContentTemplates` 类：

```python
@staticmethod
def load_custom_post():
    title = "My Custom Title"
    content = """
    My custom content here...
    """
    return title, content
```

### 发布到更多Subreddit

在 `main()` 函数添加：

```python
# 发布到r/Python
print("\n📌 发布到 r/Python...")
title, content = ContentTemplates.load_reddit_post("python")
result = reddit.post("Python", title, content)
```

### 定时发布

使用cron或Windows Task Scheduler：

```bash
# 每周三晚上21:00运行
0 21 * * 3 cd /path/to/skill-discovery-release/scripts && python auto_share.py
```

---

## 📚 相关文档

- **[SHARE.md](../SHARE.md)** - 分享内容模板
- **[RELEASE_NOTES.md](../RELEASE_NOTES.md)** - Release创建指南
- **[SHARING_CHECKLIST.md](../SHARING_CHECKLIST.md)** - 完整检查清单
- **[README.md](../README.md)** - 项目说明

---

## 💪 下一步

1. ✅ 完成首次自动化发布
2. 📊 监控发布效果（stars, upvotes）
3. 💬 回复社区反馈
4. 🔄 根据反馈准备v1.0.1

---

**创建时间**: 2026-02-27
**版本**: 1.0.0
**作者**: ei060
