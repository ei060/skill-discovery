# Skill Discovery - Security Checklist
# Skill Discovery - 安全检查清单

> **Last Updated / 最后更新:** 2026-02-27
> **Version / 版本:** 1.0.0

---

## Quick Links / 快速链接

- [Pre-Development Checklist / 开发前检查](#pre-development-checklist--开发前检查)
- [Pre-Publish Checklist / 发布前检查](#pre-publish-checklist--发布前检查)
- [Code Review Checklist / 代码审查清单](#code-review-checklist--代码审查清单)
- [Maintenance Checklist / 维护清单](#maintenance-checklist--维护清单)

---

## Pre-Development Checklist / 开发前检查

### Phase 1: Planning / 规划阶段

#### ✅ Requirements Analysis / 需求分析

- [ ] **Security Requirements / 安全需求**
  - [ ] Identify sensitive data handling requirements / 识别敏感数据处理需求
  - [ ] Define authentication needs / 定义身份验证需求
  - [ ] Determine compliance requirements (GDPR, CCPA, etc.) / 确定合规需求
  - [ ] Document threat model / 记录威胁模型

- [ ] **Dependencies / 依赖项**
  - [ ] List all required dependencies / 列出所有必需依赖
  - [ ] Research alternative libraries / 研究替代库
  - [ ] Check library security reputation / 检查库的安全声誉
  - [ ] Verify maintenance status / 验证维护状态

#### ✅ Environment Setup / 环境设置

- [ ] **Development Environment / 开发环境**
  - [ ] Create .env.example file (no real secrets) / 创建.env.example文件（无真实密钥）
  - [ ] Set up environment variables / 设置环境变量
  - [ ] Configure local secrets manager / 配置本地密钥管理器
  - [ ] Enable security linting rules / 启用安全lint规则

- [ ] **Version Control / 版本控制**
  - [ ] Initialize .gitignore / 初始化.gitignore
  - [ ] Add pre-commit hooks / 添加pre-commit钩子
  - [ ] Set up branch protection rules / 设置分支保护规则
  - [ ] Configure secret scanning / 配置密钥扫描

---

## Pre-Publish Checklist / 发布前检查

### Phase 2: Development Security / 开发安全

#### ✅ Code Security / 代码安全

- [ ] **Credential Management / 凭据管理**
  - [ ] No hardcoded secrets in code / 代码中无硬编码密钥
  - [ ] All secrets use environment variables / 所有密钥使用环境变量
  - [ ] API tokens properly scoped / API令牌正确限定范围
  - [ ] Secrets rotation plan documented / 记录密钥轮换计划

```bash
# ✅ Verify no secrets in code
git grep -iE "(api_key|secret|token|password)\s*[:=]\s*['\"][^'\"]{8,}"
```

- [ ] **Input Validation / 输入验证**
  - [ ] All user inputs sanitized / 清理所有用户输入
  - [ ] Type checking implemented / 实现类型检查
  - [ ] Length limits enforced / 强制长度限制
  - [ ] Special characters escaped / 转义特殊字符

```python
# ✅ Input validation checklist
def validate_input(user_input, max_length=1000):
    if not isinstance(user_input, str):
        raise TypeError("Input must be string")
    if len(user_input) > max_length:
        raise ValueError(f"Input exceeds max length of {max_length}")
    # Add more validation as needed
    return user_input
```

- [ ] **Output Encoding / 输出编码**
  - [ ] HTML output escaped / HTML输出转义
  - [ ] JSON output sanitized / JSON输出清理
  - [ ] File paths validated / 文件路径验证
  - [ ] Error messages don't leak info / 错误消息不泄露信息

#### ✅ API Security / API安全

- [ ] **Rate Limiting / 速率限制**
  - [ ] Implement request throttling / 实现请求节流
  - [ ] Add retry logic with exponential backoff / 添加指数退避重试逻辑
  - [ ] Configure timeout values / 配置超时值
  - [ ] Monitor API usage / 监控API使用情况

```python
# ✅ Rate limiting example
from functools import wraps
import time

def rate_limit(max_calls=10, period=60):
    """Rate limiting decorator"""
    calls = []
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            calls[:] = [c for c in calls if c > now - period]
            if len(calls) >= max_calls:
                raise Exception("Rate limit exceeded")
            calls.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

- [ ] **HTTPS / TLS**
  - [ ] All API calls use HTTPS / 所有API调用使用HTTPS
  - [ ] Certificate validation enabled / 启用证书验证
  - [ ] No insecure HTTP requests / 无不安全的HTTP请求
  - [ ] TLS version >= 1.2 / TLS版本>= 1.2

- [ ] **Error Handling / 错误处理**
  - [ ] Catch specific exceptions / 捕获特定异常
  - [ ] Log errors without sensitive data / 记录错误时不包含敏感数据
  - [ ] Return generic error messages to users / 向用户返回通用错误消息
  - [ ] Detailed errors logged securely / 详细错误安全记录

```python
# ✅ Safe error handling
try:
    result = api_call()
except APIError as e:
    logger.error(f"API call failed: {e.code}")  # Safe: no sensitive data
    raise UserFacingError("Operation failed, please try again")  # Generic
```

#### ✅ Data Protection / 数据保护

- [ ] **Sensitive Data / 敏感数据**
  - [ ] No PII in logs / 日志中无个人身份信息
  - [ ] Secrets never in debug output / 密钥绝不出现在调试输出中
  - [ ] Temporary files encrypted / 临时文件加密
  - [ ] Memory cleared after use / 使用后清除内存

```python
# ✅ Safe logging
import logging

def safe_log(data):
    """Remove sensitive fields before logging"""
    sensitive_keys = ['password', 'token', 'api_key', 'secret', 'credit_card']
    safe_data = {k: '***' if k in sensitive_keys else v for k, v in data.items()}
    logging.info(f"Data: {safe_data}")
```

- [ ] **File Operations / 文件操作**
  - [ ] File paths validated / 文件路径验证
  - [ ] File permissions set correctly / 正确设置文件权限
  - [ ] Temporary files cleaned up / 清理临时文件
  - [ ] No directory traversal vulnerabilities / 无目录遍历漏洞

```python
# ✅ Safe file operations
from pathlib import Path

def safe_read_file(filename, base_dir='/app/data'):
    """Safely read file with path validation"""
    base = Path(base_dir).resolve()
    file_path = (base / filename).resolve()

    # Prevent directory traversal
    if not file_path.is_relative_to(base):
        raise ValueError("Invalid file path")

    return file_path.read_text()
```

---

## Code Review Checklist / 代码审查清单

### Phase 3: Review Process / 审查流程

#### ✅ Automated Checks / 自动检查

- [ ] **Security Scanning / 安全扫描**
  ```bash
  # ✅ Run all security scans
  npm audit                # JavaScript/Node.js
  pip-audit                # Python
  bandit -r ./             # Python security linter
  safety check             # Python dependency check
  trufflehog git .         # Secret scanner
  ```

- [ ] **Code Quality / 代码质量**
  ```bash
  # ✅ Run linters and formatters
  eslint --plugin security src/    # JavaScript
  flake8 .                         # Python
  mypy .                           # Python type checking
  ```

- [ ] **Dependency Check / 依赖检查**
  ```bash
  # ✅ Check for vulnerabilities
  npm outdated              # Check for updates
  npm ls                    # View dependency tree
  pip list --outdated      # Python outdated packages
  ```

#### ✅ Manual Review / 手动审查

- [ ] **Credential Security / 凭据安全**
  - [ ] Search for hardcoded secrets / 搜索硬编码密钥
  - [ ] Verify .env.example exists / 验证.env.example存在
  - [ ] Check .gitignore coverage / 检查.gitignore覆盖范围
  - [ ] Confirm no test credentials / 确认无测试凭据

```bash
# ✅ Manual secret search patterns
git grep -i "sk_"                     # OpenAI keys
git grep -i "ghp_"                    # GitHub tokens
git grep -i "api_key\|apikey"         # Generic API keys
git grep -iE "(password|secret).{0,20}=.*['\"]" # Passwords/secrets
```

- [ ] **Logic Security / 逻辑安全**
  - [ ] Authentication flow correct / 身份验证流程正确
  - [ ] Authorization checks present / 存在授权检查
  - [ ] Race conditions prevented / 防止竞态条件
  - [ ] Edge cases handled / 处理边缘情况

- [ ] **Error Handling / 错误处理**
  - [ ] No bare except clauses / 无裸except子句
  - [ ] Specific exceptions caught / 捕获特定异常
  - [ ] Errors logged appropriately / 适当记录错误
  - [ ] User messages are generic / 用户消息通用

```python
# ❌ BAD: Bare except
try:
    risky_operation()
except:
    pass  # Hides all errors

# ✅ GOOD: Specific exceptions
try:
    risky_operation()
except ValueError as e:
    logger.warning(f"Invalid value: {e}")
except APIError as e:
    logger.error(f"API error: {e.code}")
    raise
```

- [ ] **Logging Security / 日志安全**
  - [ ] No sensitive data in logs / 日志中无敏感数据
  - [ ] Log level appropriate / 日志级别适当
  - [ ] Sensitive operations audited / 审计敏感操作
  - [ ] Log rotation configured / 配置日志轮换

```python
# ❌ BAD: Logging sensitive data
logger.info(f"User {email} logged in with {password}")

# ✅ GOOD: Safe logging
user_hash = hashlib.sha256(email.encode()).hexdigest()[:8]
logger.info(f"User {user_hash} logged in successfully")
```

---

## Maintenance Checklist / 维护清单

### Phase 4: Ongoing Security / 持续安全

#### ✅ Regular Updates / 定期更新

- [ ] **Weekly / 每周**
  - [ ] Check for security advisories / 检查安全公告
  - [ ] Review GitHub security alerts / 审查GitHub安全警报
  - [ ] Update dependencies if needed / 需要时更新依赖
  - [ ] Review access logs / 审查访问日志

- [ ] **Monthly / 每月**
  - [ ] Run full security audit / 运行完整安全审计
  - [ ] Rotate API keys / 轮换API密钥
  - [ ] Review and update .gitignore / 审查和更新.gitignore
  - [ ] Check dependency health / 检查依赖健康状况

- [ ] **Quarterly / 每季度**
  - [ ] Comprehensive security review / 全面安全审查
  - [ ] Penetration testing / 渗透测试
  - [ ] Update documentation / 更新文档
  - [ ] Security training / 安全培训

#### ✅ Monitoring / 监控

- [ ] **Set Up Alerts / 设置告警**
  - [ ] GitHub Dependabot alerts / GitHub Dependabot警报
  - [ ] Dependency update notifications / 依赖更新通知
  - [ ] Unusual activity detection / 异常活动检测
  - [ ] API usage monitoring / API使用监控

- [ ] **Log Management / 日志管理**
  - [ ] Centralized logging / 集中式日志
  - [ ] Log analysis tools / 日志分析工具
  - [ ] Automated log review / 自动化日志审查
  - [ ] Secure log storage / 安全日志存储

---

## Specialized Checklists / 专门清单

### Web Scraping Skills / 网页抓取技能

```python
# ✅ Web scraping security checklist
- [ ] Respect robots.txt
- [ ] Rate limiting implemented
- [ ] User-Agent header set
- [ ] Error handling for network issues
- [ ] No scraping of sensitive data
- [ ] Legal compliance verified
```

### API Integration Skills / API集成技能

```python
# ✅ API integration security checklist
- [ ] API keys stored in environment variables
- [ ] HTTPS only
- [ ] Retry logic with exponential backoff
- [ ] Request/response size limits
- [ ] API rate limits respected
- [ ] Sensitive data filtered from logs
```

### File Processing Skills / 文件处理技能

```python
# ✅ File processing security checklist
- [ ] File type validation
- [ ] File size limits
- [ ] Path traversal prevention
- [ ] Virus scanning for uploads
- [ ] Temporary file cleanup
- [ ] Secure file permissions
```

---

## Quick Reference / 快速参考

### Critical Checks / 关键检查

```bash
# 🚨 MUST CHECK before every commit
# 1. No secrets committed
git diff --cached | grep -iE "(api_key|secret|token|password)"

# 2. Dependencies secure
npm audit  # or pip-audit for Python

# 3. Linting passes
npm run lint  # or flake8 for Python

# 4. Tests pass
npm test  # or pytest for Python
```

### Pre-Commit Hook / 提交前钩子

```bash
# ✅ Add to .git/hooks/pre-commit
#!/bin/bash

echo "🔒 Running security checks..."

# Check for secrets
if git diff --cached | grep -iE "(api_key|secret|token|password).{0,20}=.*['\"]"; then
    echo "❌ Possible secret detected in commit!"
    exit 1
fi

# Run security audit
if command -v npm &> /dev/null; then
    npm audit --audit-level=moderate || exit 1
fi

echo "✅ Security checks passed!"
exit 0
```

### GitHub Actions Template / GitHub Actions模板

```yaml
# ✅ .github/workflows/security-checks.yml
name: Security Checks
on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run npm audit
        run: npm audit --audit-level=moderate

      - name: Check for secrets
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./

      - name: Run CodeQL
        uses: github/codeql-action/analyze@v2
```

---

## Emergency Checklist / 紧急清单

### 🚨 If Secret is Leaked / 如果密钥泄露

```bash
# 1. IMMEDIATE ACTION (within minutes)
# Revoke exposed credentials
- Revoke API keys
- Rotate tokens
- Change passwords

# 2. CONTAINMENT (within hour)
- Check commit history for additional secrets
- Search codebase for related secrets
- Review recent access logs

# 3. CLEANUP (within day)
- Remove secrets from all branches
- Force push to remove from history (if needed)
- Update all affected systems

# 4. PREVENTION (within week)
- Add pre-commit hooks
- Enable secret scanning
- Update security documentation
- Team training on secret management
```

### 🔄 Secret Rotation Procedure / 密钥轮换流程

```python
# ✅ Systematic rotation process
# 1. Generate new credentials
new_key = generate_api_key()

# 2. Update configuration
update_environment_variable('API_KEY', new_key)

# 3. Test new credentials
test_api_connection(new_key)

# 4. Deploy to production
deploy_changes()

# 5. Revoke old credentials
revoke_api_key(old_key)

# 6. Update documentation
update_api_key_documentation()
```

---

## Scoring System / 评分系统

### Security Maturity Model / 安全成熟度模型

**Level 1 - Basic / 基础 (0-25%):**
- .gitignore configured / 已配置.gitignore
- Environment variables used / 使用环境变量
- Basic error handling / 基本错误处理

**Level 2 - Intermediate / 中级 (25-50%):**
- Dependency scanning / 依赖扫描
- Input validation / 输入验证
- Secure logging / 安全日志
- HTTPS enforced / 强制HTTPS

**Level 3 - Advanced / 高级 (50-75%):**
- Automated security tests / 自动化安全测试
- Secret rotation / 密钥轮换
- Security monitoring / 安全监控
- Regular audits / 定期审计

**Level 4 - Expert / 专家 (75-100%):**
- Comprehensive threat model / 全面威胁模型
- Penetration testing / 渗透测试
- Security training / 安全培训
- Incident response plan / 事件响应计划

---

**Remember / 记住:**

> Use this checklist every time. Consistency is key to security.
> 每次都使用此清单。一致性是安全的关键。

> When in doubt, choose security over convenience.
> 有疑问时，选择安全而非便利。

> A checklist is only as good as its execution.
> 清单的价值在于执行。

---

**For questions or suggestions, open an issue or submit a pull request.**
**如有疑问或建议，请创建issue或提交pull request。**
