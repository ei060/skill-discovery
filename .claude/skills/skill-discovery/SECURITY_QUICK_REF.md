# Security Quick Reference Card
# 安全快速参考卡

> **Print this. Keep it on your desk. Use it every day.**
> **打印此卡片。放在桌上。每天使用。**

---

## 🚨 CRITICAL RULES / 关键规则

### ✅ ALWAYS DO / 始终要做

1. **Use environment variables / 使用环境变量**
   ```bash
   export API_KEY="xxx"
   # or in Python:
   import os
   key = os.getenv('API_KEY')
   ```

2. **Check .gitignore / 检查.gitignore**
   ```bash
   cat .gitignore | grep "\.env"
   # Should see: .env
   ```

3. **Sanitize logs / 清理日志**
   ```python
   # Never log:
   # print(f"Token: {token}")

   # Always do:
   print(f"Token: {'*' * 10}")
   ```

4. **Scan before commit / 提交前扫描**
   ```bash
   git diff | grep -i "api_key\|secret\|token"
   # If results found: DON'T COMMIT
   ```

### ❌ NEVER DO / 永不不做

1. **Hardcode credentials / 硬编码凭据**
   ```python
   # ❌ NEVER:
   API_KEY = "sk-1234567890"
   ```

2. **Commit .env files / 提交.env文件**
   ```bash
   # ❌ NEVER:
   git add .env
   ```

3. **Log sensitive data / 记录敏感数据**
   ```python
   # ❌ NEVER:
   logger.info(f"User: {email}, Pass: {password}")
   ```

4. **Ignore security warnings / 忽略安全警告**
   ```bash
   # ❌ NEVER:
   # npm audit fix --force  # DANGEROUS!
   ```

---

## 🔍 PRE-COMMIT CHECKLIST / 提交前清单

### Run these every time / 每次都运行这些

```bash
# 1. Check for secrets / 检查密钥
git diff --cached | grep -iE "(api_key|secret|token|password).{0,20}=.*['\"]"

# 2. Run security audit / 运行安全审计
npm audit  # Node.js
# or
pip-audit  # Python

# 3. Check .env in .gitignore / 检查.gitignore中的.env
git check-ignore -v .env

# 4. Verify no credentials in code / 验证代码中无凭据
git ls-files | xargs grep -l "sk_\|ghp_\|api_key" 2>/dev/null
```

**If ANY of the above show results: STOP AND FIX.**
**如果以上任何一项显示结果：停止并修复。**

---

## 📋 COMMON MISTAKES / 常见错误

### ❌ Mistake #1: Testing with real credentials / 错误#1：使用真实凭据测试

```python
# ❌ BAD:
def test_api():
    client = APIClient(api_key="sk-real-key-here")

# ✅ GOOD:
def test_api():
    client = APIClient(api_key=os.getenv('TEST_API_KEY'))
```

### ❌ Mistake #2: Debugging with secrets / 错误#2：使用密钥调试

```javascript
// ❌ BAD:
console.log(`Using token: ${apiToken}`);

// ✅ GOOD:
console.log(`Using token: ${apiToken.slice(0, 4)}...`);
```

### ❌ Mistake #3: Error messages leak info / 错误#3：错误消息泄露信息

```python
# ❌ BAD:
except Exception as e:
    return f"Error connecting to {db_user}@{db_host}: {e}"

# ✅ GOOD:
except Exception as e:
    logger.error(f"DB error: {e}")  # Logged securely
    return "Database connection failed"  # Generic for user
```

---

## 🚨 EMERGENCY PROCEDURES / 紧急程序

### If you accidentally commit a secret / 如果您意外提交了密钥

#### Step 1: IMMEDIATE ACTION (5 minutes) / 立即行动（5分钟）

```bash
# 1. Revoke the exposed credential
# Go to GitHub/Reddit/wherever and revoke the key
# IMMEDIATELY!

# 2. Remove from git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch FILE_WITH_SECRET" \
  --prune-empty --tag-name-filter cat -- --all

# 3. Force push (CAUTION: only if you know what you're doing)
git push origin --force --all
```

#### Step 2: DAMAGE CONTROL (30 minutes) / 损害控制（30分钟）

- [ ] Rotate all related credentials / 轮换所有相关凭据
- [ ] Check for other exposed secrets / 检查其他暴露的密钥
- [ ] Review recent access logs / 审查最近的访问日志
- [ ] Notify team members / 通知团队成员
- [ ] Document the incident / 记录事件

#### Step 3: PREVENTION (1 week) / 预防（1周）

- [ ] Install pre-commit hooks / 安装提交前钩子
- [ ] Enable secret scanning / 启用密钥扫描
- [ ] Add security training / 添加安全培训
- [ ] Review all commits in history / 审查历史中的所有提交

---

## 🔧 TOOLS TO INSTALL / 要安装的工具

### Essential / 必需工具

```bash
# 1. Secret scanning / 密钥扫描
npm install -g trufflehog
# or
pip install truffleHog

# 2. Dependency checking / 依赖检查
npm install -g npm-audit-resolver
# or
pip install safety

# 3. Pre-commit hooks / 提交前钩子
pip install pre-commit
# or
npm install -g husky

# 4. Git secret scanning / Git密钥扫描
pip install git-secrets
git secrets --install
git secrets --register-aws
```

### Configure pre-commit / 配置提交前钩子

```bash
# .git/hooks/pre-commit
#!/bin/bash
echo "🔒 Checking for secrets..."

# Check for common secret patterns
if git diff --cached | grep -iE "(api_key|secret|token|password).{0,20}=.*['\"]"; then
    echo "❌ SECRET DETECTED! Commit blocked."
    echo "Please remove sensitive data before committing."
    exit 1
fi

echo "✅ No secrets found. Proceeding with commit."
exit 0
```

```bash
# Make it executable
chmod +x .git/hooks/pre-commit
```

---

## 📊 SECURITY MATURITY MODEL / 安全成熟度模型

### Level 1 - Beginner / 初学者 (You are here / 你在这里)

- ✅ Using .env files / 使用.env文件
- ✅ Basic .gitignore / 基本的.gitignore
- ⚠️ No automated checks / 无自动检查

**Next step / 下一步:** Install pre-commit hooks
**命令:** `pip install pre-commit`

### Level 2 - Intermediate / 中级

- ✅ Pre-commit hooks / 提交前钩子
- ✅ Regular dependency updates / 定期依赖更新
- ⚠️ No security scanning / 无安全扫描

**Next step / 下一步:** Enable secret scanning
**命令:** `npm install -g trufflehog`

### Level 3 - Advanced / 高级

- ✅ Automated security scans / 自动安全扫描
- ✅ Security CI/CD pipeline / 安全CI/CD管道
- ✅ Regular security audits / 定期安全审计

**Next step / 下一步:** Penetration testing
**工具:** OWASP ZAP

### Level 4 - Expert / 专家

- ✅ Comprehensive threat model / 全面威胁模型
- ✅ Incident response plan / 事件响应计划
- ✅ Security training program / 安全培训计划

**You're here! Congrats! 🎉**
**你在这里！恭喜！🎉**

---

## 🎯 DAILY CHECKLIST / 每日清单

### Morning / 早上

- [ ] Check for security updates / 检查安全更新
  ```bash
  npm audit  # or pip-audit
  ```

- [ ] Review GitHub security alerts / 审查GitHub安全警报
  ```bash
  # Visit: https://github.com/your-repo/security/alerts
  ```

### Before Committing / 提交前

- [ ] Run secret scan / 运行密钥扫描
  ```bash
  git diff | grep -iE "(api_key|secret|token)"
  ```

- [ ] Check .gitignore / 检查.gitignore
  ```bash
  git status  # Should not show .env
  ```

### Weekly / 每周

- [ ] Update dependencies / 更新依赖
  ```bash
  npm update  # or pip install --upgrade
  ```

- [ ] Review access logs / 审查访问日志
  ```bash
  # Check API usage for anomalies
  ```

- [ ] Rotate sensitive credentials / 轮换敏感凭据
  ```bash
  # Generate new API keys, update services
  ```

---

## 📱 EMERGENCY CONTACTS / 紧急联系人

### Security Incident Response Team / 安全事件响应团队

| Role / 角色 | Contact / 联系方式 | Availability / 可用时间 |
|------------|------------------|---------------------|
| Security Lead / 安全负责人 | security@example.com | 24/7 |
| DevOps Lead / DevOps负责人 | devops@example.com | Business hours / 工作时间 |
| GitHub Support / GitHub支持 | https://github.com/contact | 24/7 |

### External Resources / 外部资源

- **GitHub Security:** https://github.com/security
- **OWASP:** https://owasp.org
- **CVE Database:** https://cve.mitre.org

---

## 🔐 PASSWORD & TOKEN HYGIENE / 密码和令牌卫生

### Password Rules / 密码规则

- ✅ Minimum 16 characters / 最少16个字符
- ✅ Mix of upper/lower case, numbers, symbols / 大小写字母、数字、符号混合
- ✅ Unique for each service / 每个服务唯一
- ✅ Use password manager / 使用密码管理器

### Token Rules / 令牌规则

- ✅ Rotate every 90 days / 每90天轮换
- ✅ Use minimum required scope / 使用最小所需范围
- ✅ Revoke immediately if leaked / 如果泄露立即撤销
- ✅ Monitor usage regularly / 定期监控使用情况

### Storage Rules / 存储规则

- ✅ Use password manager (1Password, Bitwarden) / 使用密码管理器
- ✅ Enable 2FA everywhere / 到处启用2FA
- ✅ Never store in plaintext / 永不以明文存储
- ✅ Encrypt backup files / 加密备份文件

---

## 🎓 LEARNING RESOURCES / 学习资源

### Must Read / 必读

1. **OWASP Top 10** / OWASP十大
   https://owasp.org/www-project-top-ten/

2. **GitHub Security Guide** / GitHub安全指南
   https://docs.github.com/en/security

3. **OpenAI Security Best Practices** / OpenAI安全最佳实践
   https://platform.openai.com/docs/guides/security

### Courses / 课程

- **Coursera:** Cybersecurity Specialization
- **Udemy:** Web Application Security & Penetration Testing
- **Pluralsight:** Application Security Fundamentals

### Tools Practice / 工具练习

1. **TryHackMe** - Hands-on security labs
2. **OWASP Juice Shop** - Vulnerable app for practice
3. **DVWA** - Damn Vulnerable Web Application

---

## 📝 QUICK TIPS / 快速提示

### Git Safety / Git安全

```bash
# Remove file from history / 从历史记录中删除文件
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/file" \
  --prune-empty --tag-name-filter cat -- --all

# Prevent future commits / 防止未来的提交
git update-index --assume-unchanged path/to/file
```

### Environment Variables / 环境变量

```python
# Python best practice / Python最佳实践
from dotenv import load_dotenv
load_dotenv()  # Loads .env file
api_key = os.getenv('API_KEY')
if not api_key:
    raise ValueError("API_KEY not set")
```

### Log Safety / 日志安全

```python
# Safe logging function / 安全的日志函数
import re

def sanitize_log(message):
    """Remove potential secrets from log message"""
    # Pattern matches common secret formats
    secret_pattern = r'(sk_|ghp_|api_key|token)[a-zA-Z0-9_-]{20,}'
    return re.sub(secret_pattern, '[REDACTED]', str(message))
```

---

## ✅ FINAL REMINDERS / 最后提醒

### Before You Leave Today / 今天离开前

- [ ] Did you run security scans? / 你运行安全扫描了吗？
- [ ] Is your .env file in .gitignore? / 你的.env文件在.gitignore中吗？
- [ ] Are your secrets rotated? / 你的密钥轮换了吗？
- [ ] Did you lock your computer? / 你锁电脑了吗？

### Before You Push Code / 推送代码前

- [ ] No secrets in code? / 代码中没有密钥？
- [ ] Security tests pass? / 安全测试通过了吗？
- [ ] Dependencies updated? / 依赖更新了吗？
- [ ] Peer review completed? / 同行审查完成了吗？

---

**Remember / 记住:**

> Security is a habit, not a one-time setup.
> 安全是一种习惯，而不是一次性设置。

> It only takes one mistake to compromise everything.
> 只需要一个错误就能危及一切。

> When in doubt, ask. Better safe than sorry.
> 有疑问就问。安全总比后悔好。

---

**Print this. Share it. Use it.**
**打印这个。分享它。使用它。**

**Last Updated / 最后更新:** 2026-02-27
**Version / 版本:** 1.0.0
