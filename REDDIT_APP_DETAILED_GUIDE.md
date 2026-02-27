# 📱 Reddit App创建详细步骤 - 图文说明

## 第1步：访问App页面

**链接**: https://www.reddit.com/prefs/apps

1. 登录你的Reddit账号
2. 访问上述链接
3. **如果看到政策提示**：
   - 这是正常的政策说明页面
   - 阅读后可以继续
   - 不会阻止你创建应用

---

## 第2步：创建应用

### 滚动到页面底部

在页面最底部，你会看到：

```
┌─────────────────────────────────────────┐
│ create app                               │
│ create another app                       │
└─────────────────────────────────────────┘
```

点击 **"create app"** 或 **"create another app"**

---

## 第3步：填写应用信息

你会看到一个表单，填写如下：

### name（应用名称）
```
Skill Discovery
```

### app type（应用类型）
```
✅ script
```
**重要**: 必须选择 "script"，不是 "web"

### description（描述）
```
Auto-posting tool for open-source Skill Discovery project
```

### about url（关于网址）
```
https://github.com/ei060/skill-discovery
```

### redirect uri（重定向地址）
```
http://localhost:8080
```

**注意**: 对于script类型，这个字段只是占位，不会真的用到

---

## 第4步：创建并获取凭证

1. 点击表单底部的 **"create app"** 按钮
2. 页面会滚动到顶部，显示你刚创建的app

### 获取凭证

在app信息中找到：

**1. client_id**
- 位置: app名称正下方
- 标签: 就在app name下面，14个字符的字符串
- 示例: `p1ctr2andomString3z`
- **注意**: 不要括号中的 `(personal use script)` 部分，只复制14位字符串

**2. client_secret**
- 位置: 大约在app名称下方几行
- 标签: `secret` 或 `client secret`
- 长度: 约27-30个字符
- 示例: `abcDEF123456ghiJKL789mnoPQR`

**3. username**
- 你的Reddit用户名
- 例如: `your_reddit_username`

**4. password**
- 你的Reddit密码
- 用于OAuth认证

---

## 第5步：告诉我凭证

把4个信息告诉我，格式可以是：

```
username: myusername
password: mypassword123
client_id: p1ctr2andomString3z
client_secret: abcDEF123456ghiJKL789mnoPQR
```

或者随便什么格式都行，我能识别！

---

## ⚠️ 常见问题

### Q: 看到"Responsible Builder Policy"怎么办？
**A**: 这是正常的政策说明，阅读后继续即可。我们的项目完全符合政策。

### Q: client_id是包括括号吗？
**A**: 不包括。只复制14位字符串，不包括 `(personal use script)`。

### Q: redirect uri一定要填吗？
**A**: script类型必须填一个，但不会真的使用。填 `http://localhost:8080` 即可。

### Q: 创建后可以修改吗？
**A**: 可以。随时可以回来删除或修改app。

---

## 🔐 安全提示

- ✅ 这些凭证只保存在本地 `.env` 文件
- ✅ `.env` 已在 `.gitignore` 中，不会上传
- ✅ 可以随时删除app撤销访问
- ✅ script类型只有基础权限

---

**准备好了吗？** 继续创建吧！

🔗 **链接**: https://www.reddit.com/prefs/apps

⏱️ **预计耗时**: 3分钟
