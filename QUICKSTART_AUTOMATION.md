# ⚡ 5分钟快速开始 - 自动化分享

> **一键发布到GitHub + Reddit，省时30分钟！**

---

## 🎯 你需要什么

- GitHub账号（已有）
- Reddit账号（可选，如不发布到Reddit可跳过）
- 5分钟时间

---

## 📋 3步设置

### 步骤1: 获取GitHub Token（2分钟）

1. 访问: https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 勾选: `repo` (full control of private repositories)
4. 点击底部 "Generate token"
5. **复制token** (格式: `ghp_xxxxxxxxxxxxxxxxxxxx`)

### 步骤2: 配置环境变量（1分钟）

```bash
# 进入项目目录
cd D:\ClaudeWork\skill-discovery-release

# 复制配置模板
cp .env.example .env

# 编辑.env文件（用记事本或VS Code）
notepad .env
```

填写以下内容：

```bash
# 必填：GitHub Token
GITHUB_TOKEN=ghp_你刚才复制的token

# 可选：Reddit（如不发布到Reddit，留空即可）
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USERNAME=
REDDIT_PASSWORD=
```

### 步骤3: 安装依赖并运行（2分钟）

```bash
# 安装Python依赖
pip install -r requirements.txt

# 运行自动化脚本
cd scripts
python auto_share.py
```

---

## ✅ 运行结果

你会看到：

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
📊 步骤 4/4: 生成分享报告
============================================================
✅ 报告已保存: share_report.json

============================================================
🎉 自动化分享完成!
============================================================
```

---

## 🎉 恭喜！

你已经完成：
- ✅ GitHub Release v1.0.0创建成功
- ✅ 分享报告已生成

**下一步**:
1. 访问你的Release: https://github.com/ei060/skill-discovery/releases
2. 手动添加Topics（见脚本输出）
3. 分享Release链接到社交媒体

---

## 📱 想发布到Reddit？（可选）

如果配置了Reddit API，脚本会自动发布到：
- r/Claude
- r/artificial
- r/opensource

**配置Reddit**:
1. 访问: https://www.reddit.com/prefs/apps
2. 创建app（类型: script）
3. 获取client_id和secret
4. 填写到 `.env` 文件

详细步骤见: [scripts/AUTO_SHARE_GUIDE.md](scripts/AUTO_SHARE_GUIDE.md)

---

## ❓ 遇到问题？

### 问题1: `pip install` 失败

**解决**:
```bash
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题2: Token无效

**解决**:
- 确认token以 `ghp_` 开头
- 重新生成token
- 检查 `.env` 文件中是否有空格

### 问题3: 找不到 `.env` 文件

**解决**:
```bash
# 确认在正确目录
cd D:\ClaudeWork\skill-discovery-release
dir .env

# 如果不存在，重新创建
copy .env.example .env
```

---

## 💡 提示

1. **Token安全**: 永远不要分享或提交 `.env` 文件
2. **首次运行**: 只需配置一次，以后直接运行即可
3. **GitHub Topics**: 需要手动添加（脚本会给出链接）
4. **查看报告**: `share_report.json` 包含所有发布链接

---

## 🚀 下次发布更简单

下次发布新版本时：

```bash
cd D:\ClaudeWork\skill-discovery-release\scripts
python auto_share.py
```

就这2行命令，全部搞定！

---

**准备时间**: 2026-02-27
**预计耗时**: 5分钟（首次），2分钟（以后）
**版本**: v1.0.0
