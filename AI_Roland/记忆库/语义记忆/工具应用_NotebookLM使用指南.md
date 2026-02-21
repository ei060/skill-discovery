# NotebookLM 使用指南

## 状态

✅ **已安装并登录**（2026-02-21）
- 版本：notebooklm-py v0.3.2
- 认证：Google 账号已完成
- 可用笔记本：7 个

## 基本功能

### 1. 查看笔记本列表

```bash
notebooklm list
```

**您的笔记本**：
| ID | 标题 | 创建日期 |
|----|------|----------|
| f2fa7bab | Hogwarts Chronicles: Personalized Magic Fusion Guide | 2026-02-19 |
| 7c2430e2 | （无标题） | 2026-02-08 |
| 903e361e | The Great Plague and the Fall of the Ming Dynasty | 2026-01-17 |
| ac30228f | LunaTV GitHub Repository and Source Documentation | 2026-01-14 |
| ... | ... | ... |

### 2. 选择笔记本

```bash
# 使用完整 ID
notebooklm use f2fa7bab-c4b7-4bdf-90df-2xxx

# 或使用部分 ID（自动匹配）
notebooklm use f2fa7bab
```

### 3. 对话提问

```bash
# 向当前笔记本提问
notebooklm ask "请总结这个笔记本的主要内容"

# 英文提问
notebooklm ask "What are the key points?"

# 继续对话
notebooklm ask "可以详细解释第一点吗？"
```

### 4. 创建新笔记本

```bash
notebooklm create "我的新笔记本"
```

### 5. 添加源文档

```bash
# 添加本地文件
notebooklm source add path/to/document.pdf

# 添加网页
notebooklm source add https://example.com/article

# 添加 Google Drive 文件
notebooklm source add-drive "文档ID"

# 查看源列表
notebooklm source list
```

### 6. 生成内容

```bash
# 生成摘要
notebooklm summary

# 生成音频概述
notebooklm generate audio

# 生成思维导图
notebooklm generate mind-map

# 生成幻灯片
notebooklm generate slide-deck

# 生成测验
notebooklm generate quiz

# 生成报告
notebooklm generate report
```

### 7. 查看对话历史

```bash
notebooklm history
```

### 8. 查看当前状态

```bash
notebooklm status
```

## 高级功能

### Artifact 管理

```bash
# 列出所有生成的 artifacts
notebooklm artifact list

# 获取特定 artifact
notebooklm artifact get <artifact-id>

# 导出 artifact
notebooklm artifact export <artifact-id> output.pdf

# 删除 artifact
notebooklm artifact delete <artifact-id>
```

### 笔记本管理

```bash
# 重命名笔记本
notebooklm rename "新标题"

# 删除笔记本
notebooklm delete

# 共享笔记本
notebooklm share add user@example.com

# 设置公开访问
notebooklm share public
```

### 便签管理

```bash
# 创建便签
notebooklm note create --title "我的笔记" "内容"

# 列出便签
notebooklm note list

# 保存便签
notebooklm note save <note-id>
```

## 实际应用场景

### 场景1：研究论文分析

```bash
# 1. 创建研究笔记本
notebooklm create "LLM 研究论文"

# 2. 添加多篇论文
notebooklm source add papers/paper1.pdf
notebooklm source add papers/paper2.pdf

# 3. 询问关键问题
notebooklm ask "这些论文的主要贡献是什么？"
notebooklm ask "比较它们的方法论差异"

# 4. 生成思维导图
notebooklm generate mind-map

# 5. 生成音频概述
notebooklm generate audio
```

### 场景2：代码文档学习

```bash
# 1. 创建代码学习笔记本
notebooklm source add https://github.com/user/repo

# 2. 询问代码结构
notebooklm ask "这个项目的主要模块有哪些？"
notebooklm ask "解释核心算法的实现"

# 3. 生成测验测试理解
notebooklm generate quiz
```

### 场景3：内容创作助手

```bash
# 1. 添加参考资料
notebooklm source add research.docx
notebooklm source add interview.pdf

# 2. 生成大纲
notebooklm ask "基于这些材料，生成一份详细的大纲"

# 3. 深入特定主题
notebooklm ask "大纲中的第三点可以补充哪些细节？"

# 4. 生成最终报告
notebooklm generate report
```

## 注意事项

1. **编码问题**：命令行输出中文可能乱码，建议使用英文提问
2. **源文档限制**：单个笔记本最多 50 个源
3. **Token 限制**：每个对话有上下文长度限制
4. **网络要求**：需要稳定的网络连接

## 与 AI Roland 集成

### 自动化脚本

```python
import subprocess
import json

def ask_notebooklm(question, notebook_id=None):
    """通过 Python 调用 NotebookLM"""
    if notebook_id:
        subprocess.run(['notebooklm', 'use', notebook_id])

    result = subprocess.run(
        ['notebooklm', 'ask', question],
        capture_output=True,
        text=True
    )
    return result.stdout

# 使用示例
answer = ask_notebooklm("总结主要内容", "f2fa7bab")
print(answer)
```

### 技能集成（Skills）

可以在 AI Roland 的 Skills 框架中创建 NotebookLM 技能：

```yaml
name: notebooklm
description: 使用 NotebookLM 进行文档分析和问答
commands:
  - name: ask
    description: 向笔记本提问
    usage: notebooklm ask <question>
  - name: summary
    description: 生成摘要
    usage: notebooklm summary
```

## 配置文件

位置：`C:\Users\DELL\.notebooklm\`

```
~/.notebooklm/
├── storage_state.json    # 登录 session
├── browser_profile/       # 浏览器配置
└── config.json           # 配置文件
```

## 常见问题

### Q: 重新登录

```bash
notebooklm login
```

### Q: 切换笔记本

```bash
notebooklm use <notebook-id>
```

### Q: 清除当前上下文

```bash
notebooklm clear
```

### Q: 查看帮助

```bash
notebooklm --help
notebooklm <command> --help
```

## 相关链接

- 官网：https://notebooklm.google.com
- GitHub：https://github.com/google/notebooklm-py
- 文档：https://github.com/google/notebooklm-py/blob/main/README.md

---

**更新时间**：2026-02-21
**状态**：✅ 已测试可用
