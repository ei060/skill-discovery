# 🔐 安全设置说明

## ⚠️ 重要：API Token 已移除

硬编码的 API token 已从配置文件中移除。需要通过环境变量设置。

## Windows 设置方法

### 方法 1: 系统环境变量（推荐）

1. 按 `Win + X`，选择"系统"
2. 点击"高级系统设置"
3. 点击"环境变量"
4. 在"用户变量"中点击"新建"
5. 变量名：`ANTHROPIC_AUTH_TOKEN`
6. 变量值：你的 API token
7. 点击"确定"保存

### 方法 2: PowerShell 会话级别（临时）

```powershell
$env:ANTHROPIC_AUTH_TOKEN = "your-api-token-here"
```

### 方法 3: CMD 会话级别（临时）

```cmd
set ANTHROPIC_AUTH_TOKEN=your-api-token-here
```

### 方法 4: PowerShell Profile（持久）

编辑 PowerShell Profile：
```powershell
notepad $PROFILE
```

添加：
```powershell
$env:ANTHROPIC_AUTH_TOKEN = "your-api-token-here"
```

## 验证设置

重启 Claude Code 后，运行：
```bash
echo $env:ANTHROPIC_AUTH_TOKEN
```

## 已修复的安全问题

✅ **移除硬编码 token** - 配置文件中不再包含敏感信息
✅ **添加超时保护** - 每个 hook 限制为 5 秒执行时间
✅ **防止会话挂起** - 超时的 hook 会被自动终止

## 下一步建议

1. 如果之前的 token 已经暴露，建议到 API 提供商处撤销并重新生成
2. 将 token 添加到环境变量
3. 重启 Claude Code 使配置生效
