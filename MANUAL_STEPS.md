# GitHub CLI - 完全自动化发布步骤

## 前提条件
- GitHub CLI 已安装: `C:\Program Files\GitHub CLI\gh.exe`
- 仓库代码已准备: `skill-discovery-release/`

## 步骤

### 1. 登录 GitHub
```bash
"C:\Program Files\GitHub CLI\gh.exe" auth login
```

**交互过程：**
1. 选择 `GitHub.com`
2. 选择 `HTTPS` (推荐)
3. 选择 `Login with a web browser`
4. 按回车打开浏览器
5. 在浏览器中授权
6. 回到命令行按回车

### 2. 验证登录
```bash
"C:\Program Files\GitHub CLI\gh.exe" auth status
```

应该显示：
```
GitHub.com
  ✓ Logged in as ei060
```

### 3. 创建仓库并推送
```bash
cd skill-discovery-release
"C:\Program Files\GitHub CLI\gh.exe" repo create skill-discovery --public --source=. --remote=origin --push
```

### 4. 访问你的仓库
```
https://github.com/ei060/skill-discovery
```

## 一键脚本

运行 `gh_login_and_push.bat` 自动完成所有步骤。
