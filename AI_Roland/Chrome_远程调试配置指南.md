# Chrome 远程调试配置指南

## 📋 配置步骤

### 步骤 1: 打开远程调试设置

Chrome 已经启动并打开了配置页面。你应该看到一个标题为 **"Remote Debugging"** 的页面。

### 步骤 2: 启用远程调试

在页面上找到并勾选：
```
☑️ Allow remote debugging for this browser instance
```

**位置**：通常在页面的顶部或右侧

### 步骤 3: 重启 Chrome（如果需要）

如果勾选后提示需要重启，请：
1. 关闭所有 Chrome 窗口
2. 重新启动 Chrome
3. Chrome 会记住你的设置

### 步骤 4: 验证配置

配置完成后，点击页面底部的 **"Inspect"** 按钮或类似按钮，应该能看到当前浏览器的调试信息。

## 🧪 自动验证

运行以下命令验证配置：

```bash
bash ~/.claude/skills/web-access/scripts/check-deps.sh
```

**预期输出**：
```
node: ok (v24.12.0)
chrome: connected ✅
```

如果看到 `chrome: connected`，说明配置成功！

## 🎯 配置成功后

web-access skill 将能够：
- ✅ 直连你的 Chrome 浏览器
- ✅ 使用你的登录态（已登录的网站）
- ✅ 操作动态页面
- ✅ 执行点击、滚动等交互操作
- ✅ 截取页面截图

## 🔧 故障排除

### 问题 1: 端口被占用

**错误**：`Error: listen EADDRINUSE: address already in use :::9222`

**解决**：
```bash
# 查找占用端口的进程
netstat -ano | findstr :9222

# 结束进程（如果需要）
taskkill /F /PID <进程ID>
```

### 问题 2: 无法连接

**症状**：`chrome: not connected`

**解决**：
1. 确保 Chrome 已启动
2. 确认已勾选 "Allow remote debugging"
3. 尝试重启 Chrome
4. 检查防火墙设置

### 问题 3: 权限问题

**症状**：无法访问某些页面

**解决**：
- 以管理员身份运行 Chrome
- 或在 CDP Proxy 启动时使用 `--user-data-dir` 参数

## 📚 相关资源

- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [web-access Skill 文档](https://github.com/eze-is/web-access)
- [AI Roland 安装说明](./web-access_skill_安装说明.md)

---
**创建时间**: 2026-03-28
**Chrome 版本**: 146.0.7680.154
