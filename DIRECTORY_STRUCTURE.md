# ClaudeWork 目录结构

**生成日期**: 2026-03-21
**工作目录**: D:\ClaudeWork
**最后更新**: 完成三阶段文件清理（449个未跟踪文件）

---

## 目录树结构（简化版）

```
ClaudeWork/
│
├── .claude/                          # Claude Code 配置目录
│   ├── session-start.py               # ✨ Session Start Hook（每个会话开始时执行）
│   ├── settings.json                 # Claude Code 默认配置
│   ├── settings.local.json           # ✨ 本地配置（含 Hooks 配置）
│   ├── skills/                       # 技能目录
│   │   ├── ai-roland-secretary/      # AI Roland 秘书技能
│   │   ├── ask-search/               # 搜索技能
│   │   └── network-scraping/         # 网络爬虫技能
│   └── knowledge/                    # 知识库目录
│
├── AI_Roland/                       # ✨ AI Roland 主系统
│   │
│   ├── system/                       # 系统核心
│   │   ├── task_executor.py         # ✨ 统一任务执行接口（新）
│   │   ├── engine.py                 # 引擎核心
│   │   ├── daemon.py                # 守护进程
│   │   ├── browser_controller.py    # 浏览器控制
│   │   ├── youtube_adapter.py        # YouTube 适配器
│   │   └── [其他核心模块]
│   │
│   ├── system/agents/               # ✨ Agent 协作系统（新）
│   │   ├── auto_agent_suggester.py      # ✨ 智能任务推荐
│   │   ├── agent_activity_monitor.py    # ✨ 活跃度监控
│   │   ├── agent_enforcer.py            # ✨ 强制规则系统
│   │   ├── agent_orchestrator_integrated.py  # 集成系统
│   │   ├── agent_manager.py            # Agent 管理器
│   │   ├── agent_bridge.py              # 桥接层
│   │   ├── agent_memory.py              # 记忆管理
│   │   │
│   │   ├── hooks/                      # Hooks 脚本
│   │   │   ├── inject_memory.py        # ✨ 记忆注入 Hook
│   │   │   ├── save_memory.py          # ✨ 经验保存 Hook
│   │   │   ├── memory_injection.log    # 注入日志
│   │   │   ├── memory_save.log         # 保存日志
│   │   │   └── memory_errors.log       # 错误日志
│   │   │
│   │   ├── memory/                     # Agent 记忆存储
│   │   │   ├── architect.json         # architect 记忆
│   │   │   ├── planner.json           # planner 记忆
│   │   │   ├── code_reviewer.json     # code_reviewer 记忆
│   │   │   ├── security_reviewer.json # security_reviewer 记忆
│   │   │   ├── [其他 agent 记忆...]
│   │   │
│   │   └── monitor/                   # 监控数据
│   │       ├── activity_log.json     # 活动日志
│   │       ├── activity_stats.json   # 统计信息
│   │       └── alerts.json           # 警报
│   │
│   ├── system/skills/                # 技能目录
│   │   ├── browser-control/           # 浏览器控制技能
│   │   ├── network-scraping/          # 网络爬虫技能
│   │   ├── short-drama-script/        # 短剧剧本创作
│   │   └── ai-roland-secretary/      # AI Roland 秘书技能
│   │
│   ├── 日记/                         # 系统日记
│   ├── 记忆库/                       # 记忆存储
│   ├── 技术库/                       # 技术文档
│   └── 日志/                         # 运行日志
│
├── .git/                            # Git 仓库
│
├── 测试文件/                         # 各种测试文件
│   ├── test_ai_roland_simple.py      # ✨ 完整测试套件（新）
│   ├── test_hooks_real.py             # Hooks 真实测试
│   └── [其他测试文件...]
│
├── 文档文件/                        # 项目文档
│   ├── FIX_COMPLETION_REPORT.md     # ✨ 修复完成报告（新）
│   ├── USAGE_GUIDE.md               # ✨ 使用指南（新）
│   ├── TRUTH_INVESTIGATION_REPORT.md # ✨ 真相调查报告（新）
│   └── [其他文档...]
│
├── [其他项目目录和文件...]
```

---

## 核心文件说明

### 🔑 关键系统文件（新创建/修复）

#### 1. Session Start Hook
- **路径**: `.claude/session-start.py`
- **功能**: 每个 Claude Code 会话开始时自动执行
- **作用**:
  - 验证系统配置
  - 初始化 Agent 协作系统
  - 显示系统状态和使用指南

#### 2. 统一任务执行接口
- **路径**: `AI_Roland/system/task_executor.py`
- **功能**: 提供统一的任务执行接口
- **API**:
  ```python
  from AI_Roland.system.task_executor import analyze_task, execute_with_agent

  # 分析任务
  analysis = analyze_task("检查 SQL 注入")

  # 执行任务（记录）
  result = execute_with_agent("检查 SQL 注入", record=True)
  ```

#### 3. 智能任务推荐系统
- **路径**: `AI_Roland/system/agents/auto_agent_suggester.py`
- **功能**: 自动分析任务类型并推荐合适的 Agent
- **支持的 Agent**: 9 种专业 Agent

#### 4. Agent 活跃度监控
- **路径**: `AI_Roland/system/agents/agent_activity_monitor.py`
- **功能**: 跟踪所有 Agent 的使用情况
- **监控指标**: 活跃度、成功率、任务分布

#### 5. Agent 强制规则系统
- **路径**: `AI_Roland/system/agents/agent_enforcer.py`
- **功能**: 确保关键任务由专业 Agent 处理
- **强制规则**: 9 条（安全、测试、架构等）

#### 6. Hooks 脚本
- **路径**: `AI_Roland/system/agents/hooks/`
- **文件**:
  - `inject_memory.py` - 记忆注入 Hook
  - `save_memory.py` - 经验保存 Hook

---

## 配置文件

### Claude Code 配置
- **路径**: `.claude/settings.local.json`
- **内容**: Hooks 配置
- **状态**: ✅ 已配置

### Hooks 配置结构
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Task",
      "hooks": [{
        "type": "command",
        "command": "python \"D:\\ClaudeWork\\AI_Roland\\system\\agents\\hooks\\inject_memory.py\""
      }]
    }],
    "PostToolUse": [{
      "matcher": "Task",
      "hooks": [{
        "type": "command",
        "command": "python \"D:\\ClaudeWork\\AI_Roland\\system\\agents\\hooks\\save_memory.py\""
      }]
    }]
  }
}
```

---

## 测试文件

### 完整测试套件
- **路径**: `test_ai_roland_simple.py`
- **功能**: 测试所有核心功能
- **结果**: ✅ 6/6 测试通过 (100%)

### Hooks 测试
- **路径**: `test_hooks_real.py`
- **功能**: 测试 Hooks 脚本执行
- **结果**: ✅ Hooks 脚本可正常执行

---

## 文档文件

### 修复完成报告
- **路径**: `FIX_COMPLETION_REPORT.md`
- **内容**: 问题诊断、解决方案、测试结果

### 使用指南
- **路径**: `USAGE_GUIDE.md`
- **内容**: 快速开始、API 文档、故障排除

### 真相调查报告
- **路径**: `TRUTH_INVESTIGATION_REPORT.md`
- **内容**: 问题根本原因分析、教训总结

---

## 数据存储

### Agent 记忆
- **路径**: `AI_Roland/system/agents/memory/`
- **内容**: 每个 Agent 的独立记忆文件

### 监控数据
- **路径**: `AI_Roland/system/agents/monitor/`
- **内容**: 活动日志、统计信息、警报

### Hooks 日志
- **路径**: `AI_Roland/system/agents/hooks/`
- **内容**: 注入日志、保存日志、错误日志

---

## 系统状态

| 组件 | 状态 | 说明 |
|------|------|------|
| Session Start Hook | ✅ 可用 | 自动初始化系统 |
| Task Executor | ✅ 可用 | 统一任务执行接口 |
| Agent 推荐系统 | ✅ 可用 | 智能任务分析 |
| 活跃度监控 | ✅ 可用 | 跟踪 Agent 使用 |
| 强制规则 | ✅ 可用 | 确保 Agent 参与 |
| Hooks 脚本 | ✅ 可用 | 手动可执行 |
| 测试套件 | ✅ 通过 | 6/6 测试通过 |

---

## 使用流程

```
1. 会话开始
   ↓
2. session-start.py 自动执行
   ↓
3. 系统初始化完成
   ↓
4. 用户提出任务
   ↓
5. analyze_task() 分析任务
   ↓
6. 推荐合适的 Agent
   ↓
7. execute_with_agent() 执行并记录
   ↓
8. 任务完成，经验保存
```

---

## 快速验证命令

```bash
# 1. 运行测试套件
python D:\ClaudeWork\test_ai_roland_simple.py

# 2. 查看系统报告
python -c "from AI_Roland.system.task_executor import get_system_report; print(get_system_report())"

# 3. 测试 Session Start Hook
python D:\ClaudeWork\.claude\session-start.py
```

---

**生成时间**: 2026-03-19 19:49:56
**系统状态**: ✅ 所有测试通过，系统已就绪

---

## 📊 文件清理统计（2026-03-21更新）

### 清理前后对比
| 类别 | 清理前 | 清理后 | 减少率 |
|-----|-------|-------|--------|
| JSON 文件 | 36 | 2 | ↓ 94% |
| 图片文件 | 18 | 0 | ↓ 100% |
| Python 脚本 | 192 | 55 | ↓ 71% |
| **未跟踪文件总数** | 738 | 449 | ↓ 39% |

### 新增目录
- `docs/images/` - 文档图片目录（174 KB）
  - AI_Roland_Directory_Structure.png (90 KB)
  - AI_Roland_System_Flowchart.png (84 KB)

### 更新的 .gitignore 规则
- JSON 文件规则（15条）
- 调试截图规则（12条）
- Python 脚本规则（50+条）

### 清理报告
- `untracked_files_classification_report.md` - 分类报告
- `json_cleanup_report.md` - JSON 清理报告
- `images_cleanup_report.md` - 图片清理报告
- `scripts_cleanup_report.md` - 脚本清理报告
- `workspace_summary.md` - 工作区总结

---

**文档版本**: 2.0
**最后更新**: 2026-03-21
