# 防御性编程指南 - 系统资源访问

## 问题根源分析

### 原始错误
```python
# ❌ 不安全的代码
headless = not sys.stdin.isatty() or not hasattr(sys.stdout, 'isatty')
```

**错误原因**：
- `sys.stdin` 在守护进程中可能为 `None`
- `None.isatty()` → `'NoneType' object has no attribute 'isatty'`
- 常见于：守护进程、Windows 服务、pythonw.exe、重定向输入

### 为什么会发生？

1. **守护进程环境**
   - stdin 被重定向到 `/dev/null` 或关闭
   - Python 设置 `sys.stdin = None`

2. **Windows 服务**
   - 没有控制台，所有标准流可能为 `None`

3. **pythonw.exe**
   - 无控制台的 Python 解释器
   - 标准流通常为 `None`

4. **进程重定向**
   - 输入被重定向到文件或管道
   - TTY 属性不可用

## 解决方案

### 1. 使用 sys_utils 模块

```python
# ✅ 安全的代码
from system.sys_utils import is_interactive, is_daemon, safe_read_stdin

# 检测环境
if is_daemon():
    headless = True
else:
    headless = False

# 安全读取
data = safe_read_stdin()
if data:
    process(data)
```

### 2. 三层防御

#### 第一层：None 检查
```python
if sys.stdin is not None:
    data = sys.stdin.read()
```

#### 第二层：属性检查
```python
if hasattr(sys.stdin, 'isatty'):
    is_tty = sys.stdin.isatty()
```

#### 第三层：异常捕获
```python
try:
    is_tty = sys.stdin.isatty()
except (AttributeError, OSError):
    is_tty = False
```

### 3. 完整的安全模式

```python
# 最佳实践：三层防御
def safe_is_interactive():
    try:
        if sys.stdin is None or not hasattr(sys.stdin, 'isatty'):
            return False
        return sys.stdin.isatty()
    except (AttributeError, OSError, ValueError):
        return False
```

## 代码审查检查清单

### ✅ 访问 sys.stdin 前必须检查
- [ ] 检查 `sys.stdin is not None`
- [ ] 使用 `hasattr(sys.stdin, 'method')` 验证方法存在
- [ ] 捕获可能的异常

### ✅ 访问 sys.stdout/stderr 前必须检查
- [ ] 检查 `sys.stdout is not None` / `sys.stderr is not None`
- [ ] 使用 try-except 包装写入操作

### ✅ 文件描述符操作前必须检查
- [ ] 检查 `hasattr(file, 'fileno')`
- [ ] 捕获 `OSError` 和 `ValueError`

## 常见模式

### 模式 1: 读取用户输入
```python
# ❌ 错误
user_input = sys.stdin.read().strip()

# ✅ 正确
from system.sys_utils import safe_read_stdin
user_input = safe_read_stdin()
if user_input:
    user_input = user_input.strip()
```

### 模式 2: 检测交互模式
```python
# ❌ 错误
if sys.stdin.isatty():
    run_interactive()

# ✅ 正确
from system.sys_utils import is_interactive
if is_interactive():
    run_interactive()
```

### 模式 3: 写入日志
```python
# ❌ 错误
print("Log message", file=sys.stdout)

# ✅ 正确
from system.sys_utils import safe_write_stdout
if not safe_write_stdout("Log message"):
    # 降级到文件日志
    log_to_file("Log message")
```

## 测试策略

### 单元测试必须覆盖的场景

1. **正常环境**
   - sys.stdin.isatty() = True
   - sys.stdout.isatty() = True

2. **守护进程**
   - sys.stdin = None
   - sys.stdout = None

3. **重定向环境**
   - sys.stdin.isatty() = False
   - sys.stdout.isatty() = False

4. **异常环境**
   - isatty() 抛出 OSError
   - fileno() 抛出 ValueError

### 测试示例
```python
def test_safe_stdin_with_none():
    original = sys.stdin
    try:
        sys.stdin = None
        result = safe_read_stdin()
        assert result is None
    finally:
        sys.stdin = original
```

## 最佳实践总结

1. **永远不信任环境**
   - 假设任何系统资源都可能不可用
   - 使用防御性检查

2. **优雅降级**
   - 无法访问 stdin 时，使用命令行参数或配置文件
   - 无法写入 stdout 时，降级到文件日志

3. **明确异常处理**
   - 捕获特定的异常类型，不使用裸 `except:`
   - 记录异常用于调试

4. **使用 sys_utils**
   - 所有系统资源访问都通过 sys_utils
   - 保持代码一致性和可维护性

5. **文档化假设**
   - 在代码注释中说明环境要求
   - 在文档中列出测试过的环境

## 相关文件

- `system/sys_utils.py` - 安全的系统资源访问工具
- `system/test_sys_utils.py` - 测试套件
- `system/browser_controller.py` - 修复示例
- `system/task_dispatcher.py` - 修复示例
- `system/agents/consult_agents.py` - 修复示例

## 更新日志

- 2026-03-27: 创建指南，修复 isatty() 相关错误
- 添加 sys_utils 模块提供统一的安全接口
- 更新所有直接访问 sys.stdin 的代码
