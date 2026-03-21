# Reddit 自动发布 - 快速执行清单

## ⚡ 5分钟快速开始

### 步骤1: 创建Reddit API应用（必须）

1. **登录Reddit**
   - 网址: https://www.reddit.com/login
   - 账号: s03ei060@gmail.com
   - 密码: m4jJF83AesrR*

2. **创建应用**
   - 访问: https://www.reddit.com/prefs/apps
   - 滚动到底部
   - 点击 "create app" 或 "create another app"

3. **填写表单**
   ```
   name:          SkillDiscovery
   type:          script (选择"script")
   description:   Auto-poster for Skill Discovery releases
   about url:     https://github.com/ei060/skill-discovery
   redirect uri:  http://localhost:8080
   ```

4. **点击 "create app"**

5. **复制凭证**（重要！）
   - `client_id`: 14个字符（在应用名称下方）
   - `client_secret`: 一串密钥

### 步骤2: 配置脚本（1分钟）

编辑文件: `D:\ClaudeWork\reddit_post_with_api.py`

找到这一部分（在文件开头）:
```python
REDDIT_CONFIG = {
    "client_id": "YOUR_CLIENT_ID",  # ← 替换这里
    "client_secret": "YOUR_CLIENT_SECRET",  # ← 替换这里
    "user_agent": "SkillDiscovery/1.0 by ei060",
    "username": "s03ei060@gmail.com",  # ← 可能需要改成Reddit用户名
    "password": "m4jJF83AesrR*"
}
```

替换:
- `YOUR_CLIENT_ID` → 你复制的client_id（保留引号）
- `YOUR_CLIENT_SECRET` → 你复制的client_secret（保留引号）

**注意**:
- `username` 可能需要改成Reddit用户名（不是邮箱）
- 查看你的用户名: https://www.reddit.com/prefs/profile

### 步骤3: 测试连接（1分钟）

打开命令提示符（CMD）或PowerShell:

```bash
cd D:\ClaudeWork
python test_reddit_api.py
```

**预期输出**:
```
========================================
Reddit API 连接测试
========================================

1. 初始化Reddit客户端...
2. 测试连接...
✅ 连接成功! 用户: YOUR_USERNAME
   Karma: XXXX

3. 测试读取subreddit...
✅ 成功访问 r/Claude

✅ 所有测试通过！API连接正常
```

✅ 如果看到以上输出，继续下一步
❌ 如果看到错误，查看"故障排除"部分

### 步骤4: 自动发布（45分钟，全自动）

```bash
python reddit_post_with_api.py
```

**选择**: `1` (发布所有帖子)

**确认**: `y`

**然后**: 脚本会自动完成所有发布，你只需要等待！

---

## 🎯 帖子内容

脚本会自动发布以下3个帖子:

### 帖子1: r/Claude
- **标题**: [Release] Skill Discovery - Auto Tool Discovery + Security Audit Framework
- **内容**: 项目介绍 + 安全框架特色 + GitHub链接

### 帖子2: r/artificial
- **标题**: Built tool-discovery system for Claude AI with security framework
- **内容**: 问题分析 + 解决方案 + 安全重点

### 帖子3: r/opensource
- **标题**: [OS] Skill Discovery - Auto-discovery tool for AI assistants
- **内容**: 开源介绍 + 技术栈 + 贡献号召

---

## ⚠️ 故障排除

### 问题1: `Unauthorized: incorrect username/password`

**原因**: 用户名填写错误

**解决**:
1. 访问 https://www.reddit.com/prefs/profile
2. 查看"Username"字段（不是邮箱）
3. 使用该用户名更新配置

**示例**:
```python
"username": "my_reddit_username",  # 不是邮箱！
```

### 问题2: `Unauthorized: invalid client_id`

**原因**: client_id 或 secret 错误

**解决**:
1. 重新访问 https://www.reddit.com/prefs/apps
2. 找到你创建的应用
3. 仔细复制（不要有空格）

**正确格式**:
```python
"client_id": "pVBCNoK2DvRJBQ",  # 14个字符，无空格
"client_secret": "Gx7iKjKl8mN3oP4qR5sT6uV7wX8yZ9a",  # 密钥字符串，无空格
```

### 问题3: 测试脚本找不到模块

**症状**: `ModuleNotFoundError: No module named 'praw'`

**解决**:
```bash
pip install praw
```

### 问题4: 发布时出现速率限制

**症状**: `RateLimitExceeded`

**解决**:
- 脚本已包含15分钟延迟
- 如果仍失败，等待30分钟后重试
- 或者手动发布（见下方）

---

## 🔄 备选方案: 手动发布

如果API方案完全失败，可以手动发布:

### 手动发布步骤

1. **访问r/Claude发布页**
   https://www.reddit.com/r/Claude/submit

2. **打开帖子内容文件**
   `D:\ClaudeWork\skill-discovery-release\reddit_1_Claude.txt`

3. **复制标题和内容**
   - 标题: TITLE后面的内容
   - 内容: CONTENT后面的所有文本

4. **填写并发布**
   - 粘贴标题到"Title"字段
   - 粘贴内容到"Text"字段
   - 点击"Post"

5. **重复其他subreddit**
   - r/artificial: https://www.reddit.com/r/artificial/submit
   - r/opensource: https://www.reddit.com/r/opensource/submit

**总耗时**: 约15-20分钟

---

## 📊 预期结果

### 成功发布后

你会在Reddit看到3个新帖子:
- ✅ r/Claude: https://www.reddit.com/r/Claude/comments/[id]/
- ✅ r/artificial: https://www.reddit.com/r/artificial/comments/[id]/
- ✅ r/opensource: https://www.reddit.com/r/opensource/comments/[id]/

每个帖子包含:
- GitHub仓库链接
- v1.0.0 Release链接
- 项目描述
- 安全框架特色
- 号召性用语

### 日志文件

结果会保存到:
`D:\ClaudeWork\reddit_api_results.json`

包含:
- 发布时间
- 帖子URL
- 帖子ID
- 成功/失败状态

---

## ✅ 快速检查清单

发布前检查:
- [ ] Reddit API应用已创建
- [ ] client_id已复制
- [ ] client_secret已复制
- [ ] 配置文件已更新
- [ ] 测试脚本运行成功
- [ ] 帖子内容文件存在

发布后检查:
- [ ] 3个帖子都成功发布
- [ ] 可以访问帖子URL
- [ ] 内容显示正确
- [ ] 保存了发布结果

---

## 📞 需要帮助?

### 详细文档
- **完整解决方案**: `REDDIT_PUBLISHING_SOLUTION.md`
- **流程图**: `REDDIT_PUBLISHING_FLOWCHART.md`
- **API设置**: `reddit_api_setup_guide.md`

### 快速命令
```bash
# 测试连接
python test_reddit_api.py

# 查看日志
type reddit_api_results.json

# 重新发布
python reddit_post_with_api.py
```

---

## 🎯 立即开始

**最简单的方式**:

1. 双击运行: `start_reddit_posting.bat`
2. 按照提示操作
3. 等待自动发布完成

**或手动执行**:

```bash
cd D:\ClaudeWork
python test_reddit_api.py
python reddit_post_with_api.py
```

**总耗时**: ~50分钟（配置5分钟 + 发布45分钟）

---

**准备好了吗？开始吧！** 🚀

```bash
python test_reddit_api.py
```
