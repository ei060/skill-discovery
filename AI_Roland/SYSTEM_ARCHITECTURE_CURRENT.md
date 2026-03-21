# AI Roland 系统运行架构 (2026-03-17 更新)

## 🏗️ 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户（蝎大人）                        │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│             汇报与沟通层 (Claude/汉尼拔)                     │
│  • 接收用户指令                                             │
│  • 协调 AI Roland 系统                                      │
│  • 汇报进度和结果                                           │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│           执行层 (AI Roland System v2.1)                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────┐      │
│  │              核心引擎层                          │      │
│  │  • daemon.py          (守护进程)                 │      │
│  │  • engine.py          (执行引擎)                 │      │
│  │  • agent_memory.py    (记忆管理)                 │      │
│  └──────────────────────────────────────────────────┘      │
│                                                              │
│  ┌────────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  记忆系统      │  │  技能系统    │  │  协作系统    │  │
│  │  Homunculus    │  │  SkillMgr    │  │  CollabHub   │  │
│  │  + MemoryTree  │  │  56+技能     │  │  14个Agent   │  │
│  └────────────────┘  └──────────────┘  └──────────────┘  │
│                                                              │
│  ┌────────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  子代理调度    │  │  观察系统    │  │  自我改进    │  │
│  │  Task Tool     │  │  Observer    │  │  MetaAgent   │  │
│  │  + ECC插件     │  │              │  │              │  │
│  └────────────────┘  └──────────────┘  └──────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧠 记忆系统架构

```
记忆系统 (ECC Homunculus v2.1 + AI Roland Memory Tree)
│
├─ 📁 ~/.claude/homunculus/              (全局统一记忆)
│  ├─ instincts/                         (本能系统)
│  │  ├─ personal/                       (21个习得本能)
│  │  └─ inherited/                      (继承的本能)
│  ├─ memories.json                      (统一记忆存储)
│  └─ projects/3694270db109/             (项目级记忆)
│
├─ 📁 AI_Roland/记忆库/                  (分层记忆)
│  ├─ 情景记忆/                          (日记、具体事件)
│  ├─ 语义记忆/                          (知识库、经验)
│  └─ 强制规则/                          (必须遵守的规则)
│
└─ 📁 AI_Roland/system/agents/memory/   (Agent独立记忆)
   ├─ architect.json                     (6个模式, 11条经验)
   ├─ planner.json                       (5个模式, 11条经验)
   ├─ code_reviewer.json                 (9个模式, 11条经验)
   ├─ security_reviewer.json             (7个模式, 10条经验)
   ├─ doc_writer.json                    (8个模式, 10条经验)
   ├─ engineer.json                      (7个模式, 12条经验)
   ├─ python_reviewer.json               (5个模式) ← 新增
   ├─ database_reviewer.json             (5个模式) ← 新增
   ├─ tdd_guide.json                     (3个模式) ← 新增
   ├─ e2e_runner.json                    (4个模式) ← 新增
   ├─ verification_before_completion.json (4个模式) ← 新增
   ├─ go_reviewer.json                   (4个模式) ← 新增
   ├─ kotlin_reviewer.json               (3个模式) ← 新增
   ├─ refactor_cleaner.json              (3个模式) ← 新增
   └─ shared.json                        (39条共享记忆)
```

---

## 🤖 Agent协作网络

```
┌──────────────────────────────────────────────────────────┐
│         CollaborationHub (协作中心)                      │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ 能力注册表   │  │ 消息队列     │  │ 智能匹配器   │ │
│  │ 14个Agent    │  │ 异步处理     │  │ 分数: 0.84   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└──────────────────────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   ┌────▼────┐      ┌────▼────┐     ┌────▼────┐
   │设计组   │      │审查组   │     │实现组   │
   └─────────┘      └─────────┘     └─────────┘
        │                │                │
   ┌───▼────┐       ┌───▼────┐       ┌───▼────┐
   │architect│      │code_   │       │engineer│
   │planner  │      │reviewer │       │python_ │
   │         │      │security │       │db_     │
   │         │      │doc_     │       │go_     │
   │         │      │tdd_     │       │kotlin_ │
   │         │      │e2e_     │       │refactor│
   │         │      │verif_   │       │        │
   └─────────┘      └─────────┘      └─────────┘
        ↑                ↑                ↑
   独立记忆          独立记忆          独立记忆
        └────────────────┼────────────────┘
                         │
                    [协作协议]
                - help_request
                - share_experience
                - task_delegation
                - provide_answer
```

**14个Agent分组：**
- 🎨 **设计组** (2): architect, planner
- 🔍 **审查组** (8): code_reviewer, security_reviewer, doc_writer, python_reviewer, database_reviewer, go_reviewer, kotlin_reviewer, refactor_cleaner
- ✅ **质量组** (2): tdd_guide, e2e_runner, verification_before_completion
- 🔨 **实现组** (1): engineer

---

## 🔄 协作流程

### 场景1：跨领域协作
```
python_reviewer: "Django查询慢"
    ↓
[CollaborationHub]
    ↓
database_reviewer: "用select_related"
    ↓
python_reviewer: "性能提升3倍 ✓"
```

### 场景2：经验传播
```
security_reviewer: "发现XSS防护新模式"
    ↓
[broadcast_experience]
    ↓
13个Agent全部收到 → 存入专业记忆
```

### 场景3：任务委托
```
code_reviewer: "需要重构代码"
    ↓
[委托给] refactor_cleaner
    ↓
refactor_cleaner: 完成重构
    ↓
[返回结果] code_reviewer
```

---

## 📊 子代理系统

### ECC 插件 (19个子代理，纯提示词)
```
~/.claude/agents/
├─ planner.md
├─ architect.md
├─ tdd-guide.md
├─ code-reviewer.md
├─ security-reviewer.md
├─ build-error-resolver.md
├─ e2e-runner.md
├─ refactor-cleaner.md
├─ doc-updater.md
├─ go-reviewer.md
├─ python-reviewer.md
├─ kotlin-reviewer.md
├─ database-reviewer.md
├─ chief-of-staff.md
├─ harness-optimizer.md
├─ loop-operator.md
├─ go-build-resolver.md
└─ kotlin-build-resolver.md
```

**特点：**
- ✅ 通过提示词调用
- ❌ 无持久化记忆
- ❌ 无协作能力

### AI Roland 系统 (14个Agent，有记忆+协作)
```
AI_Roland/system/agents/memory/
├─ architect.json                    (有独立记忆)
├─ planner.json                      (有独立记忆)
├─ code_reviewer.json                (有独立记忆)
├─ security_reviewer.json            (有独立记忆)
├─ doc_writer.json                   (有独立记忆)
├─ engineer.json                     (有独立记忆)
├─ python_reviewer.json              (有独立记忆) ← 新增
├─ database_reviewer.json            (有独立记忆) ← 新增
├─ tdd_guide.json                    (有独立记忆) ← 新增
├─ e2e_runner.json                   (有独立记忆) ← 新增
├─ verification_before_completion.json (有独立记忆) ← 新增
├─ go_reviewer.json                  (有独立记忆) ← 新增
├─ kotlin_reviewer.json              (有独立记忆) ← 新增
└─ refactor_cleaner.json             (有独立记忆) ← 新增
```

**特点：**
- ✅ 持久化记忆（working + professional + patterns）
- ✅ 协作能力（请求/响应/分享）
- ✅ 自动匹配
- ✅ 经验积累

---

## ⚙️ 守护进程功能

```python
RolandDaemon (后台持续运行)
│
├─ 💓 心跳监控 (每60秒)
│  └─ 检测紧急任务
│
├─ 🧠 记忆管理 (每2小时)
│  ├─ 索引更新
│  ├─ 衰减检查
│  ├─ 清理过期
│  └─ 观察分析
│
├─ 📚 技能扫描 (自动)
│  └─ 发现新技能
│
├─ 🌐 社交媒体监控 (每6小时)
│  └─ 检查更新
│
└─ 🔍 Skill Discovery (每12小时)
   └─ 自动发现新技能
```

---

## 📈 当前系统状态

| 组件 | 状态 | 数量 | 说明 |
|------|------|------|------|
| 守护进程 | ✅ 运行中 | - | 心跳 #17942+ |
| 记忆系统 | ⚠️ 完整性警告 | - | 7天未记录，覆盖率12% |
| ECC插件 | ✅ 已安装 | 19子代理, 56+技能 | v1.8.0 |
| **有记忆Agent** | ✅ **新增** | **14个** | **独立记忆+协作** |
| **协作中心** | ✅ **新增** | **1个** | **智能匹配0.84** |
| 本能系统 | ✅ 运行中 | 21个 | 🌱0 🌿19 🍂2 |
| 共享记忆 | ✅ 运行中 | 39项 | Agent间共享 |

---

## 🎯 系统能力对比

### 之前 (2026-03-16)
```
有独立记忆: 6个Agent
协作能力: ❌ 无
交流方式: 被动共享记忆
```

### 现在 (2026-03-17)
```
有独立记忆: 14个Agent (+133%)
协作能力: ✅ 完整协作协议
交流方式:
  ✅ 主动请求帮助
  ✅ 自动匹配Agent
  ✅ 经验分享广播
  ✅ 任务委托
  ✅ 对话历史
```

---

## 🔗 关键文件

### 核心系统
- `AI_Roland/system/daemon.py` - 守护进程
- `AI_Roland/system/engine.py` - 执行引擎
- `AI_Roland/system/agents/agent_memory.py` - 记忆管理
- `AI_Roland/system/agents/meta_agent.py` - 元Agent

### 新增协作系统
- `AI_Roland/system/agents/agent_communication.py` - 通信协议
- `AI_Roland/system/agents/register_capabilities.py` - 能力注册
- `AI_Roland/system/agents/COLLABORATION_GUIDE.md` - 使用指南

### 数据文件
- `AI_Roland/system/agents/capabilities.json` - 能力注册表
- `AI_Roland/system/agents/messages.json` - 消息历史
- `AI_Roland/system/agents/memory/*.json` - Agent独立记忆

---

## 📝 系统演进历史

```
v1.0 (2026-02-20)
└─ 基础守护进程

v2.0 (2026-03-04)
└─ 集成ECC Homunculus记忆系统

v2.1 (2026-03-16)
└─ 安装ECC插件（19子代理，56技能）

v3.0 (2026-03-17) ← 当前
├─ 14个Agent独立记忆系统
└─ Agent协作协议
```

---

**这就是当前系统的完整运行结构，蝎大人！** 🎉

一个真正可以：
- 🧠 记住经验（独立记忆）
- 🤝 互相协作（协作协议）
- 📢 分享知识（经验广播）
- 🎯 自我进化（持续学习）

的智能系统！
