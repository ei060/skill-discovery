# 🔑 获取Reddit API凭证 - 快速指南

## 📋 步骤（5分钟）

### 1. 打开Reddit App设置页面

**点击这里**: https://www.reddit.com/prefs/apps

或者：
1. 登录 Reddit
2. 访问：https://www.reddit.com/prefs/apps
3. 滚动到页面底部

---

### 2. 创建新App

点击 **"create app"** 或 **"create another app"** 按钮

---

### 3. 填写App信息

填写以下字段：

**name**:
```
Skill Discovery
```

**app type**:
```
选择: ✅ script
```

**description**:
```
Auto-posting tool for Skill Discovery project
```

**about url**:
```
https://github.com/ei060/skill-discovery
```

**redirect uri**:
```
http://localhost:8080
```

---

### 4. 保存并获取凭证

1. 点击 **"create app"** 按钮
2. 在页面顶部找到你刚创建的app
3. 复制以下信息：

   **client_id** (在app名称下方，14位字符串):
   ```
   例如: p1ctr2andomString3z
   ```

   **client_secret** (标为"secret", 约30位字符串):
   ```
   例如: abcDEF123456ghiJKL789mnoPQR
   ```

4. 你的Reddit **username** 和 **password** (登录凭据)

---

### 5. 告诉我凭证

把4个信息告诉我，格式：

```
username: your_reddit_username
password: your_reddit_password
client_id: your_14_char_client_id
client_secret: your_30_char_client_secret
```

我会帮你配置到 `.env` 文件并自动发布！

---

## 🔐 安全提示

✅ **安全的做法**:
- Script类型的app只有基础权限
- 凭证只在本地使用
- 不会上传到Git（已在.gitignore中）
- 可以随时删除app

❌ **不要做的**:
- 不要分享给他人
- 不要提交到Git
- 不要在公开地方发布

---

## 📝 完成后

告诉我你的凭证，我会：
1. 配置到 `.env` 文件
2. 测试Reddit连接
3. 自动发布到3个subreddit:
   - r/Claude
   - r/artificial
   - r/opensource

---

**准备好了吗？** 去获取凭证吧！

🔗 **快速链接**: https://www.reddit.com/prefs/apps

⏱️ **预计耗时**: 3分钟
