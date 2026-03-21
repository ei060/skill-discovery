# 未跟踪文件下一步审查指南

**生成日期**: 2026-03-21
**当前状态**: 已应用保守版 .gitignore
**剩余未跟踪文件**: 667 个

---

## ✅ 已完成

### 步骤 1: 应用保守版 .gitignore
- ✅ 备份了原 .gitignore 为 `.gitignore.backup_*`
- ✅ 应用了保守版 .gitignore（仅低风险项）
- ✅ 验证效果：从 738 个减少到 667 个（已忽略 71 个）

### 已忽略的文件类别
- ✅ Python 缓存文件（`__pycache__/`, `*.pyc`）
- ✅ Python 编译产物（`dist/`, `build/`, `*.egg-info/`）
- ✅ 数据库文件（`*.db`, `*.sqlite`）
- ✅ IDE 配置（`.vscode/`, `.idea/`）
- ✅ Claude Code 运行时文件（`.agents/`, `.browser-profile/`）
- ✅ Node.js 依赖（`node_modules/`）
- ✅ 日志文件（`*.log`, `logs/`）
- ✅ 下载的安装包（`*.msi`, `*.zip`, `*.exe`）
- ✅ 浏览器自动化临时文件
- ✅ 外部克隆项目（`everything-claude-code/`, `learn-claude-code/`）
- ✅ 临时目录（`temp_skills/`, `cache/`, `video_frames/`）
- ✅ AI Roland 运行时数据（`AI_Roland/memory/`, `AI_Roland/sessions/`）
- ✅ 音视频文件（`*.wav`, `*.mp3`, `*.mp4`）
- ✅ Windows 系统文件

---

## 📊 剩余未跟踪文件分类统计

| 类别 | 数量 | 优先级 | 建议操作 |
|-----|------|-------|---------|
| **JSON 文件** | 39 个 | 🔴 高 | 单独审查后决定 |
| **图片文件** | 49 个 | 🟡 中 | 人工分类审查 |
| **测试脚本** | 33 个 | 🟡 中 | 保留核心，删除临时 |
| **批处理脚本** | 28 个 | 🟢 低 | 保留启动脚本 |
| **文本文件** | 18 个 | 🟢 低 | 保留文档 |
| **其他文件** | ~500 个 | 🟢 低 | 逐步清理 |

---

## 1️⃣ JSON 文件审查（39 个）

### 示例文件
```
6551_github_info.json                    # GitHub API 数据
6551_github_search_results.json          # GitHub 搜索结果
AI_Roland/current_task.json              # 当前任务状态
AI_Roland/proxy_config.json              # 代理配置（可能含敏感信息）
AI_Roland/system/agents/capabilities.json # Agent 能力注册表
AI_Roland/system/agents/test_results.json # 测试结果
AI_Roland/system/skills/skills_registry.json # 技能注册表（重要）
```

### 审查步骤

#### 步骤 1: 列出所有 JSON 文件
```bash
git status --porcelain | grep '^??' | grep '\.json$' | sed 's/^?? //' > untracked_jsons.txt
cat untracked_jsons.txt
```

#### 步骤 2: 按类别分类

**A. 配置类 JSON（可能需要保留）**
```bash
# 查看配置文件
cat AI_Roland/proxy_config.json          # 代理配置
cat AI_Roland/system/skills/skills_registry.json  # 技能注册表
cat package.json                         # Node.js 配置
```

**建议**:
- `skills_registry.json` - ✅ **应提交**（技能系统核心配置）
- `proxy_config.json` - ⚠️ **审查后决定**（可能含敏感信息）
- `package.json` - ✅ **应提交**（如果有 Node.js 项目）

---

**B. 运行时状态 JSON（应忽略）**
```bash
# 查看状态文件
cat AI_Roland/current_task.json          # 当前任务状态
cat AI_Roland/system/agents/test_results.json  # 测试结果
cat status_final.json                    # 最终状态
```

**建议**: 添加到 .gitignore
```bash
echo "AI_Roland/current_task.json" >> .gitignore
echo "AI_Roland/system/agents/test_results.json" >> .gitignore
echo "status_*.json" >> .gitignore
echo "artifact_*.json" >> .gitignore
```

---

**C. 测试数据 JSON（应忽略）**
```bash
# 查看测试数据
cat 6551_github_info.json                # GitHub API 数据
cat 6551_github_search_results.json      # 搜索结果
cat api_requests.json                    # API 请求记录
cat source_info.json                     # 来源信息
```

**建议**: 添加到 .gitignore
```bash
echo "*_github_info.json" >> .gitignore
echo "*_search_results.json" >> .gitignore
echo "api_requests.json" >> .gitignore
echo "source_info.json" >> .gitignore
echo "web_result.json" >> .gitignore
```

---

#### 步骤 3: 应用 JSON 忽略规则
```bash
# 备份 .gitignore
cp .gitignore .gitignore.backup_json

# 添加 JSON 忽略规则
cat >> .gitignore << 'EOF'

# ========================================
# 运行时状态 JSON（安全忽略）
# ========================================
AI_Roland/current_task.json
AI_Roland/proxy_config.json
status_*.json
artifact_*.json

# ========================================
# 测试数据 JSON（安全忽略）
# ========================================
*_github_info.json
*_search_results.json
*_links_*.json
*_test_result.json
api_requests.json
source_info.json
web_result.json
ai_memory_projects.json
memory_*.json
EOF

# 验证效果
git status --porcelain | grep '\.json$' | wc -l
```

---

## 2️⃣ 图片文件审查（49 个）

### 示例文件
```
AI_Roland/12306_homepage.png             # 项目截图
AI_Roland_Directory_Structure.png        # 系统架构图（重要）
AI_Roland_System_Flowchart.png           # 系统流程图（重要）
debug_screenshot.png                     # 调试截图
error.png                                # 错误截图
chrome_devtools_mcp_repo.png             # 文档截图
```

### 审查步骤

#### 步骤 1: 列出所有图片
```bash
git status --porcelain | grep '^??' | grep -E '\.(png|jpg|jpeg)$' | sed 's/^?? //' > untracked_images.txt
cat untracked_images.txt
```

#### 步骤 2: 按用途分类

**A. 文档图片（应保留）**
```bash
# 查看可能的文档图片
ls -lh AI_Roland_Directory_Structure.png
ls -lh AI_Roland_System_Flowchart.png
ls -lh AI_Roland_*.png
```

**建议**:
- 系统架构图、流程图 - ✅ **应提交**（放在 `docs/images/` 目录）
- 使用说明截图 - ✅ **应提交**（放在相应文档目录）

---

**B. 调试截图（应删除）**
```bash
# 查看调试截图
ls -lh debug_*.png
ls -lh error*.png
ls -lh *_screenshot.png
```

**建议**: 添加到 .gitignore 并删除
```bash
# 添加到 .gitignore
echo "debug_*.png" >> .gitignore
echo "error*.png" >> .gitignore
echo "*_screenshot.png" >> .gitignore
echo "*_test_*.png" >> .gitignore

# 删除调试截图（谨慎！）
rm debug_*.png
rm error*.png
```

---

**C. 爬虫/测试截图（应删除）**
```bash
# 查看测试截图
ls -lh reddit_*.png
ls -lh twitter_*.png
ls -lh xiaohongshu_*.png
ls -lh youtube_*.png
```

**建议**: 删除或添加到 .gitignore
```bash
# 添加到 .gitignore
echo "reddit_*.png" >> .gitignore
echo "twitter_*.png" >> .gitignore
echo "*_nitter_*.png" >> .gitignore

# 删除测试截图
rm reddit_*.png
rm twitter_*.png
```

---

#### 步骤 3: 整理文档图片
```bash
# 创建 docs/images 目录
mkdir -p docs/images

# 移动文档图片
mv AI_Roland_Directory_Structure.png docs/images/
mv AI_Roland_System_Flowchart.png docs/images/
mv AI_Roland_*.png docs/images/ 2>/dev/null

# 提交文档图片
git add docs/images/
git commit -m "docs: 添加系统架构图和流程图"
```

---

## 3️⃣ 测试脚本审查（33 个）

### 示例文件
```
test_6551_integration.py                # 6551 集成测试
test_ai_roland_simple.py                # AI Roland 简单测试
test_hooks_real.py                      # Hooks 测试
fix_hooks.py                            # Hooks 修复脚本
diagnose_hooks.py                       # Hooks 诊断脚本
```

### 审查步骤

#### 步骤 1: 列出所有测试脚本
```bash
git status --porcelain | grep '^??' | grep -E 'test_.*\.py$|fix_.*\.py$|diagnose_.*\.py$|verify_.*\.py$' | sed 's/^?? //' > untracked_tests.txt
cat untracked_tests.txt
```

#### 步骤 2: 按功能分类

**A. 核心测试脚本（应保留）**
```bash
# 查看可能的测试脚本
cat test_ai_roland_system.py | head -20
cat test_hooks_real.py | head -20
```

**建议**:
- 创建 `tests/` 目录
- 移动核心测试脚本到 `tests/`
- 删除临时调试脚本

---

**B. 临时调试脚本（应删除）**
```bash
# 查看临时脚本
ls -lh fix_*.py
ls -lh diagnose_*.py
ls -lh verify_*.py
```

**建议**: 删除临时脚本
```bash
# 删除前先确认
# rm fix_*.py
# rm diagnose_*.py
# rm verify_*.py
```

---

**C. 功能整合脚本（需审查）**
```bash
# 查看功能脚本
cat extract_video*.py | head -10
cat transcribe_*.py | head -10
```

**建议**:
- 如果功能已整合到技能中 → 删除
- 如果是独立工具 → 移到 `tools/` 目录

---

#### 步骤 3: 整理测试脚本
```bash
# 创建 tests 目录
mkdir -p tests

# 移动核心测试脚本
mv test_ai_roland_system.py tests/
mv test_hooks_real.py tests/

# 提交测试脚本
git add tests/
git commit -m "test: 添加核心测试脚本"
```

---

## 4️⃣ 批处理脚本审查（28 个）

### 示例文件
```
启动AI_Roland_自动.bat                  # 启动脚本
检查配置状态.bat                       # 检查脚本
安装Perplexica.bat                     # 安装脚本
```

### 建议
- ✅ 保留个人使用的启动脚本
- ⚠️ 考虑转换为跨平台脚本（Python/shell）
- ❌ 不提交到版本控制（个人配置）

---

## 5️⃣ 文本文件审查（18 个）

### 示例文件
```
START-HERE.txt                          # 项目说明
QUICK_REFERENCE.md                      # 快速参考（实际是 .md）
lang_check.txt                          # 语言检查结果
```

### 建议
- ✅ 保留文档类文件
- ✅ 删除临时输出文件
- ⚠️ 将 .txt 文档转换为 .md

---

## 🎯 推荐执行顺序

### 第一阶段：审查 JSON 文件（最安全）
```bash
# 1. 列出所有 JSON 文件
git status --porcelain | grep '^??' | grep '\.json$' | sed 's/^?? //' > untracked_jsons.txt

# 2. 人工审查每个 JSON 文件
for file in $(cat untracked_jsons.txt); do
    echo "=== $file ==="
    head -20 "$file"
    read -p "保留/忽略/删除? [r/i/d] " choice
done

# 3. 应用 JSON 忽略规则
# (见上文 JSON 文件审查步骤)
```

---

### 第二阶段：审查图片文件（需人工判断）
```bash
# 1. 列出所有图片文件
git status --porcelain | grep '^??' | grep -E '\.(png|jpg|jpeg)$' | sed 's/^?? //' > untracked_images.txt

# 2. 人工分类（打开图片查看器）
# - 文档图片 → 移到 docs/images/
# - 调试截图 → 删除
# - 测试截图 → 删除

# 3. 应用图片忽略规则
# (见上文图片文件审查步骤)
```

---

### 第三阶段：审查测试脚本（中等风险）
```bash
# 1. 列出所有测试脚本
git status --porcelain | grep '^??' | grep -E 'test_.*\.py$|fix_.*\.py$' | sed 's/^?? //' > untracked_tests.txt

# 2. 人工审查
# - 核心测试 → 移到 tests/
# - 临时调试 → 删除
# - 功能脚本 → 移到 tools/ 或整合到技能

# 3. 清理临时脚本
# (见上文测试脚本审查步骤)
```

---

## 📋 完整检查清单

### JSON 文件审查清单
- [ ] 列出所有 JSON 文件
- [ ] 识别配置类 JSON（skills_registry.json, package.json）
- [ ] 识别状态类 JSON（current_task.json, test_results.json）
- [ ] 识别测试数据 JSON（*_search_results.json, api_requests.json）
- [ ] 决定哪些提交、哪些忽略
- [ ] 应用 JSON 忽略规则到 .gitignore
- [ ] 提交必要的配置文件

### 图片文件审查清单
- [ ] 列出所有图片文件
- [ ] 创建 docs/images/ 目录
- [ ] 移动文档图片（架构图、流程图）
- [ ] 删除调试截图（debug_*.png, error*.png）
- [ ] 删除测试截图（reddit_*.png, twitter_*.png）
- [ ] 应用图片忽略规则到 .gitignore
- [ ] 提交文档图片

### 测试脚本审查清单
- [ ] 列出所有测试脚本
- [ ] 创建 tests/ 目录
- [ ] 移动核心测试脚本
- [ ] 删除临时调试脚本
- [ ] 整合功能脚本到技能或 tools/
- [ ] 提交核心测试脚本

### 最终清理清单
- [ ] 验证剩余未跟踪文件数量（应 < 100 个）
- [ ] 提交 AGENT_RULES.md
- [ ] 提交更新后的 .gitignore
- [ ] 创建清理完成报告
- [ ] 通知相关人员

---

## 🚀 立即执行的命令（复制粘贴）

### 步骤 1: 审查 JSON 文件
```bash
# 列出所有 JSON 文件
git status --porcelain | grep '^??' | grep '\.json$' | sed 's/^?? //' | tee untracked_jsons.txt
```

### 步骤 2: 添加 JSON 忽略规则
```bash
cat >> .gitignore << 'EOF'

# 运行时状态 JSON
AI_Roland/current_task.json
AI_Roland/proxy_config.json
status_*.json
artifact_*.json

# 测试数据 JSON
*_github_info.json
*_search_results.json
*_links_*.json
*_test_result.json
api_requests.json
source_info.json
web_result.json
ai_memory_projects.json
EOF
```

### 步骤 3: 验证效果
```bash
echo "应用前: 667 个未跟踪文件"
echo "应用后: $(git status --porcelain | grep '^??' | wc -l) 个未跟踪文件"
echo "已忽略: $((667 - $(git status --porcelain | grep '^??' | wc -l))) 个 JSON 文件"
```

---

**审查指南生成完毕**。建议按照推荐顺序执行：先 JSON（最安全），再图片（需人工判断），最后测试脚本（中等风险）。
