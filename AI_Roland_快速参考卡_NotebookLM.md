# AI Roland x NotebookLM - 快速参考卡

## 🚀 三种使用方式

### 方式1：Web 界面（最推荐）⭐⭐⭐

```
1. 访问：https://notebooklm.google.com
2. 选择 "AI Roland 系统文档" notebook
3. 输入中文问题即可
```

**优点**：完美中文支持、图形界面、所有功能

---

### 方式2：编码包装器（自动化集成）⭐⭐⭐

```bash
# 便捷脚本
查询AI_Roland知识库.bat "你的问题"

# 命令行
cd AI_Roland\system
python notebooklm_wrapper.py ask "你的问题"

# 或使用英文（完美支持）
notebooklm use 6f279652
notebooklm ask "What are the core features?"
```

**优点**：自动编码处理、适合脚本集成、批量查询

---

### 方式3：直接命令行（英文查询）

```bash
cd D:\ClaudeWork
notebooklm use 6f279652
notebooklm ask "How to use the memory system?"
```

**优点**：快速直接、无乱码

---

## 📝 常用查询示例

### 系统功能

```bash
# 中文（通过编码包装器）
查询AI_Roland知识库.bat "AI Roland 有哪些核心功能？"

# 英文（直接命令）
notebooklm ask "What are the main capabilities?"
```

### 技术细节

```bash
# 浏览器控制器
查询AI_Roland知识库.bat "浏览器控制器如何使用？"

# 记忆系统
启动第二大脑.bat "记忆系统的工作原理"

# NotebookLM 集成
notebooklm ask "How to integrate with NotebookLM?"
```

### 高级查询

```bash
# 搜索
查询AI_Roland知识库.bat "搜索: 浏览器,NotebookLM,集成"

# 决策背景
启动第二大脑.bat "为什么选择同步API？"

# 最佳实践
notebooklm ask "Best practices for AI Roland?"
```

---

## 🛠️ 便捷脚本

| 脚本 | 功能 |
|------|------|
| `查询AI_Roland知识库.bat` | 中文查询（自动编码处理） |
| `启动第二大脑.bat` | 第二大脑查询 |
| `演示编码包装器.bat` | 功能演示 |
| `运行_NotebookLM中文修复版.bat` | UTF-8 环境启动 |

---

## 💡 使用技巧

### 技巧1：英文查询更快

如果不怕用英文查询，直接用命令行最快：
```bash
cd D:\ClaudeWork
notebooklm use 6f279652
notebooklm ask "How to use browser controller?"
```

### 技巧2：批量查询

创建批处理文件：
```batch
@echo off
call 查询AI_Roland知识库.bat "核心功能1"
call 查询AI_Roland知识库.bat "核心功能2"
call 查询AI_Roland知识库.bat "核心功能3"
```

### 技巧3：保存查询结果

```python
from AI_Roland.system.notebooklm_wrapper import NotebookLMEncoder

encoder = NotebookLMEncoder()
result = encoder.ask_with_fallback("你的问题")

# 保存到文件
with open('answer.txt', 'w', encoding='utf-8') as f:
    f.write(encoder.get_clean_output(result))
```

---

## 🎯 推荐流程

### 日常查询
```
双击：查询AI_Roland知识库.bat
↓
输入问题
↓
获得答案
```

### 开发集成
```
导入 notebooklm_wrapper
↓
调用 ask_with_fallback()
↓
获得 get_clean_output()
↓
集成到你的系统
```

### 批量操作
```
创建问题列表
↓
循环调用编码包装器
↓
收集所有结果
↓
生成报告
```

---

## 📞 需要帮助？

1. 查看 `NotebookLM中文乱码解决方案.md`
2. 运行 `演示编码包装器.bat` 看完整演示
3. 或直接使用 Web 界面：https://notebooklm.google.com

---

**更新时间**：2026-02-21
**状态**：✅ 所有方案已测试可用
