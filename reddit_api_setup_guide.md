# Reddit API 设置指南

## 问题
当前无法使用Playwright自动化登录Reddit发布帖子。

## 解决方案：使用Reddit官方API (PRAW)

### 步骤1: 创建Reddit API应用

1. **登录Reddit**
   - 访问: https://www.reddit.com/login
   - 使用账号: s03ei060@gmail.com

2. **创建应用**
   - 访问: https://www.reddit.com/prefs/apps
   - 滚动到页面底部
   - 点击 "create app" 或 "create another app"

3. **填写应用信息**
   ```
   name: SkillDiscovery
   type: script (选择"script")
   description: Auto-poster for Skill Discovery releases
   about url: https://github.com/ei060/skill-discovery
   redirect uri: http://localhost:8080
   ```

4. **获取凭证**
   创建后会显示：
   - **client_id**: 14个字符的字符串（在应用名称下方）
   - **client_secret**: 密钥（在client_id旁边）

   示例：
   ```
   client_id: pVBCNoK2DvRJBQ
   client_secret: Gx7iKjKl8mN3oP4qR5sT6uV7wX8yZ9a
   ```

### 步骤2: 配置环境变量

创建文件 `D:\ClaudeWork\.env`:
```bash
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USERNAME=s03ei060@gmail.com
REDDIT_PASSWORD=m4jJF83AesrR*
```

### 步骤3: 测试API连接

运行测试脚本:
```bash
python test_reddit_api.py
```

### 步骤4: 发布帖子

运行发布脚本:
```bash
python reddit_post_with_api.py
```

## 优势

✅ 官方API，稳定可靠
✅ 无需处理浏览器自动化
✅ 无需登录Cookie
✅ 不会被反爬虫检测
✅ 符合Reddit使用条款

## 注意事项

- Reddit API有速率限制：60次请求/分钟
- 发布相同内容到多个subreddit可能被当作spam
- 建议间隔至少15分钟发布每个帖子
- 检查每个subreddit的发布规则

## 如果仍想用浏览器自动化

如果坚持使用Playwright，需要：

1. **手动登录获取Cookies**:
   - 打开Chrome浏览器
   - 登录Reddit
   - 安装"Get cookies.txt LOCALLY"扩展
   - 导出cookies保存到 `reddit_cookies.json`

2. **修改脚本使用Cookies**:
   - 使用已保存的cookies
   - 跳过登录步骤
   - 直接访问submit页面

但**强烈建议使用API方案**，更稳定可靠！
