# NotebookLM 中文乱码完整解决方案

## 问题分析

从截图可以看到，NotebookLM 在 Windows 命令行中输出中文时出现乱码（显示为问号）。

**根本原因**：
1. Windows 命令行默认使用 GBK/CP936 编码
2. NotebookLM CLI 可能未完全支持 UTF-8 输出
3. 终端字体可能不支持某些 Unicode 字符

---

## 解决方案

### 方案1：使用英文查询（最简单）⭐

**适用场景**：快速查询

```bash
# 使用英文问题
cd D:\ClaudeWork
notebooklm use 6f279652
notebooklm ask "What are the core features of AI Roland?"
notebooklm ask "How to use the memory system?"
```

**优点**：
- ✅ 完全避免乱码
- ✅ 响应快速
- ✅ 准确获取信息

---

### 方案2：使用编码包装器（推荐）⭐⭐

**使用修复版的工具**：

```bash
# 使用包装器（自动处理乱码）
python AI_Roland/system/notebooklm_wrapper.py ask "AI Roland 的功能"
```

**功能**：
- ✅ 自动检测乱码
- ✅ 中英文自动转换
- ✅ 输出清理

---

### 方案3：通过 NotebookLM Web 界面（最佳用户体验）⭐⭐⭐

**步骤**：

1. **打开 NotebookLM Web 界面**
   ```
   https://notebooklm.google.com
   ```

2. **在浏览器中使用**（完全支持中文）
   - 创建笔记本
   - 添加文档
   - 提问（中文完美支持）
   - 生成内容

**优点**：
- ✅ 完美支持中文
- ✅ 图形界面友好
- ✅ 所有功能可用
- ✅ 无编码问题

---

### 方案4：将输出重定向到文件

```bash
# 将输出保存到文件（UTF-8编码）
cd D:\ClaudeWork
notebooklm use 6f279652
notebooklm ask "AI Roland 的功能" > output.txt 2>&1

# 查看文件（UTF-8 编码）
chcp 65001
type output.txt
```

---

## 实用建议

### 日常使用

**推荐顺序**：

1. **Web 界面**（最推荐）
   - 直接使用 https://notebooklm.google.com
   - 完美中文支持
   - 所有功能可用

2. **英文查询**
   - 临时查询使用
   - 快速有效

3. **编码包装器**
   - 需要命令行自动化时使用
   - 自动处理编码问题

### 开发集成

```python
from AI_Roland.system.notebooklm_wrapper import NotebookLMEncoder

encoder = NotebookLMEncoder()

# 安全查询（自动处理中文）
result = encoder.ask_with_fallback("AI Roland 的核心功能")
clean_output = encoder.get_clean_output(result)
```

---

## 临时解决方案

### 如果急需使用中文查询

**方法1：使用关键词**

```bash
# 使用简单的关键词，避免复杂句子
notebooklm ask "AI Roland 功能"
notebooklm ask "Memory System"
notebooklm ask "Browser Controller"
```

**方法2：使用 Web 界面**

```
1. 访问 https://notebooklm.google.com
2. 选择 "AI Roland 系统文档" notebook
3. 直接输入中文问题
4. 获得完美中文回答
```

---

## 已提供的工具

| 文件 | 说明 |
|------|------|
| `运行_NotebookLM中文修复版.bat` | UTF-8 环境启动器 |
| `AI_Roland/system/notebooklm_wrapper.py` | 编码包装器 |

---

## 最佳实践

### 推荐工作流

```
日常使用：
  Web 界面 (https://notebooklm.google.com)
    ↓
  完美中文支持，所有功能

命令行自动化：
  Python wrapper + 英文查询
    ↓
  避免编码问题，可靠稳定

批量操作：
  Sitemap → 批量导入 → Web 界面查询
    ↓
  分离导入和使用，各取所长
```

---

## 技术细节

### Windows 编码设置

```bash
# 设置 UTF-8 代码页
chcp 65001

# 设置环境变量
set PYTHONIOENCODING=utf-8
```

### Python 编码处理

```python
import sys
import io

# 强制 UTF-8 输出
sys.stdout = io.TextIOWrapper(
    sys.stdout.buffer,
    encoding='utf-8',
    errors='replace'  # 替换无法解码的字符
)
```

---

## 总结

### 短期方案（立即可用）
- ✅ 使用 Web 界面：https://notebooklm.google.com
- ✅ 使用英文查询
- ✅ 将输出重定向到文件

### 长期方案（推荐）
- ✅ 等待 NotebookLM 官方修复 CLI 编码问题
- ✅ 或使用 Web API（如果提供）
- ✅ 或使用第三方案（Web 界面）

### 当前最佳方案
**直接使用 NotebookLM Web 界面**
- 完美支持中文
- 所有功能可用
- 无需担心编码

---

**创建时间**：2026-02-21
**状态**：✅ 已提供多种解决方案
**推荐**：Web 界面 > 英文查询 > 编码包装器
