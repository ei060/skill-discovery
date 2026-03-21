# 未跟踪文件分类报告

**生成日期**: 2026-03-21
**未跟踪文件总数**: 738 个
**分类目的**: 清理工作区，建立合理的 .gitignore 规则

---

## A. 未跟踪文件清单

已获取完整清单，共 **738 个未跟踪文件**。主要分布在：
- 根目录：临时脚本、测试文件、安装包
- AI_Roland/：日志、记忆库、临时文件
- .claude/：技能、会话脚本
- 各种测试输出和调试文件

---

## B. 应提交文件（核心配置）

### 1. 项目规则文件
- `AGENT_RULES.md` - ✅ **必须提交**（项目执行规则）

### 2. Git 忽略规则
- `.gitignore` - ⚠️ **需要先完善再提交**（当前只有一行）

### 3. 关键配置文档（可选）
以下文档如果已经稳定，建议提交：
- `QUICK_REFERENCE.md`
- `USAGE_GUIDE.md`
- `README-Installation.md`

---

## C. 应加入 .gitignore 的文件

### 1. Python 相关
```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
*.db
*.sqlite
*.sqlite3
```

**理由**: Python 字节码缓存、编译产物、数据库文件不应提交

### 2. IDE 和编辑器
```
.vscode/
.idea/
*.swp
*.swo
*~
.kiro/
```

**理由**: 个人开发环境配置，不应共享

### 3. Claude Code 相关
```
.agents/
.browser-profile/
.claude/knowledge/
.claude/projects/
.claude/session-*.py
```

**理由**: Claude Code 运行时生成的临时文件和会话数据

### 4. Node.js 相关
```
node_modules/
package-lock.json
.cache/
```

**理由**: 依赖包和缓存，可通过 npm install 恢复

### 5. 日志和临时文件
```
*.log
*.txt
logs/
AI_Roland/logs/*.log
AI_Roland/logs/*.txt
AI_Roland/memory_injection.log
AI_Roland/memory_save.log
pinchtab_server*.log
```

**理由**: 日志文件会持续增长，不应纳入版本控制

### 6. 测试和调试文件
```
*_test_*.png
*_screenshot.png
debug_*.png
debug_*.html
error*.png
*_result.json
test_*.py
*_test*.json
*_test*.txt
```

**理由**: 测试输出和调试截图，不应提交

### 7. 数据和状态文件
```
*.json
!package.json
accounts.db
artifact_*.json
status_*.json
api_requests.json
source_info.json
web_result.json
ai_memory_projects.json
memory_*.json
```

**理由**: 运行时状态、临时数据，需排除但保留必要的配置文件

### 8. 下载的安装包和二进制
```
*.msi
*.zip
*.exe
*.tar.gz
DockerDesktopInstaller.exe
go1.23.6.windows-amd64.*
pinchtab-windows-amd64.zip
```

**理由**: 安装包占用空间大，应从官方下载

### 9. 浏览器和自动化相关
```
browser-automation/
browser-control-*
.browser-profile/
playwright-bot-bypass-test/
```

**理由**: 浏览器用户数据、临时下载

### 10. 外部克隆项目
```
everything-claude-code/
learn-claude-code/
awesome-openclaw-skills/
github-publish-test/
skill-discovery-release/
```

**理由**: 外部仓库应使用 git submodule 或单独管理

### 11. 临时脚本和输出
```
nul
*_output.txt
*_result.*
temp_skills/
cache/
.slides/
video_frames/
tweet_images/
```

**理由**: 临时文件和输出目录

### 12. AI Roland 特定
```
AI_Roland/memory/
AI_Roland/技术库/
AI_Roland/记录库/
AI_Roland/AI_Roland/
AI_Roland/current_task.json
AI_Roland/proxy_config.json
AI_Roland/sessions/
```

**理由**: 运行时记忆、会话数据、配置文件

### 13. 媒体文件
```
*.wav
*.mp3
*.mp4
*.avi
*.png
*.jpg
*.jpeg
!AI_Roland/system/skills/**/images/
```

**理由**: 媒体文件通常很大，除非是项目必要的图标/文档

---

## D. 暂时保留但不提交的文件

### 1. 技能文档（待整理）
```
.claude/skills/**/README.md
.claude/skills/**/CHANGELOG.md
AI_Roland/*/安装指南.md
AI_Roland/*/使用指南.md
```

**理由**: 技能文档可能还在频繁更新，建议稳定后再提交

### 2. 安装和启动脚本
```
启动*.bat
检查*.bat
安装*.bat
修复*.bat
*.bat
```

**理由**: Windows 批处理脚本，个人使用，建议改为跨平台脚本后再提交

### 3. 分析报告（临时）
```
*_ANALYSIS.md
*_REPORT.md
*_报告.md
*_完成报告.md
```

**理由**: 临时分析报告，建议整理后归档到 docs/ 目录

---

## E. 可删除的文件

### 1. 重复和过时的测试脚本
```
test_*.py (30+ 个测试文件)
fix_*.py (10+ 个修复脚本)
diagnose_*.py
verify_*.py
```

**理由**: 临时调试脚本，功能已集成或问题已解决

### 2. 重复的发布脚本
```
publish_*.py (10+ 个版本)
*_poster.py (多个版本)
```

**理由**: 多次迭代留下的旧版本，保留最新即可

### 3. 临时提取的文件
```
extract_*.py (10+ 个)
transcribe_*.py (8个)
fetch_*.py (多个)
create_*.py (多个)
```

**理由**: 功能已整合到主系统或技能中

### 4. 调试输出文件
```
debug_*.png
debug_*.html
error*.png
*_screenshot.png (50+ 个)
```

**理由**: 调试过程中生成的截图，不再需要

### 5. 音视频处理临时文件
```
RPReplay_Final1772232768_*
video_audio.wav
youtube_podcast.mp3
```

**理由**: 处理过程中的临时文件

### 6. JSON 测试数据
```
*_test_result.json
*_search_results.json
*_links_*.json
*_info.json
```

**理由**: 测试和抓取的临时数据

### 7. Windows 特殊文件
```
nul
.ps1
.bat (根目录下的启动脚本)
```

**理由**: Windows 空设备文件、个人启动脚本

---

## F. 建议的下一步命令

### ⚠️ 重要：这些命令仅供参考，请先审查再执行！

### 步骤 1：备份当前状态（推荐）
```bash
# 创建备份分支
git branch backup-before-cleanup-$(date +%Y%m%d)

# 或创建压缩备份
tar -czf D:/ClaudeWork/backup_$(date +%Y%m%d_%H%M%S).tar.gz .
```

### 步骤 2：更新 .gitignore（建议先执行）
```bash
# 创建完善的 .gitignore（见下方完整内容）
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST
*.db
*.sqlite
*.sqlite3

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.kiro/

# Claude Code
.agents/
.browser-profile/
.claude/knowledge/
.claude/projects/
.claude/session-*.py

# Node
node_modules/
package-lock.json
.cache/

# Logs
*.log
logs/
AI_Roland/logs/*.log
AI_Roland/logs/*.txt
pinchtab_server*.log

# Test outputs
*_test_*.png
*_screenshot.png
debug_*.png
debug_*.html
error*.png
*_result.json
*_test_result.json

# Data files
*.json
!package.json
!AI_Roland/system/skills/skills_registry.json
accounts.db
artifact_*.json
status_*.json
api_requests.json
source_info.json
web_result.json
ai_memory_projects.json
AI_Roland/current_task.json
AI_Roland/proxy_config.json

# Downloads
*.msi
*.zip
*.exe
*.tar.gz
DockerDesktopInstaller.exe
go1.23.6.windows-amd64.*
pinchtab-windows-amd64.zip

# Browser
browser-automation/
browser-control-*
.browser-profile/
playwright-bot-bypass-test/

# External repos
everything-claude-code/
learn-claude-code/
awesome-openclaw-skills/
github-publish-test/
skill-discovery-release/

# Temp files
nul
temp_skills/
cache/
.slides/
video_frames/
tweet_images/
investment_report_charts/

# AI Roland runtime
AI_Roland/memory/
AI_Roland/技术库/
AI_Roland/记录库/
AI_Roland/AI_Roland/
AI_Roland/sessions/
AI_Roland/system/sessions/
AI_Roland/system/agents/memory/
AI_Roland/system/agents/monitor/
AI_Roland/system/agents/meta/
AI_Roland/system/logs/
AI_Roland/system/improvement_data/
AI_Roland/system/memory_tree/

# Media
*.wav
*.mp3
*.mp4
*.avi
!AI_Roland/system/skills/**/images/

# Windows
.DS_Store?
Thumbs.db
ehthumbs.db
Desktop.ini
EOF
```

### 步骤 3：提交核心文件
```bash
# 添加 AGENT_RULES.md
git add AGENT_RULES.md

# 添加更新后的 .gitignore
git add .gitignore

# 提交
git commit -m "chore: 添加项目规则和完善的 .gitignore"
```

### 步骤 4：清理可删除文件（⚠️ 谨慎操作）
```bash
# 删除测试脚本（仅示例，请根据实际情况调整）
# rm test_*.py
# rm fix_*.py
# rm diagnose_*.py

# 删除调试截图
# rm *_screenshot.png
# rm debug_*.png
# rm error*.png

# 删除临时 JSON 数据
# rm *_test_result.json
# rm *_search_results.json

# 删除音视频临时文件
# rm RPReplay_Final1772232768_*
# rm video_audio.wav
# rm youtube_podcast.mp3

# 删除 Windows 特殊文件
# rm nul
```

### 步骤 5：检查清理后的状态
```bash
# 查看剩余未跟踪文件
git status --short

# 统计未跟踪文件数量
git status --porcelain | grep '^??' | wc -l
```

### 步骤 6：分批提交（如有需要）
```bash
# 如果有其他需要提交的文件，分批添加
# git add <特定文件>
# git commit -m "描述"
```

---

## 总结

| 分类 | 数量估计 | 优先级 | 建议操作 |
|-----|---------|-------|---------|
| **应提交** | 1-5 个 | 🔴 高 | 立即提交 |
| **应忽略** | ~600 个 | 🔴 高 | 更新 .gitignore |
| **暂保留** | ~50 个 | 🟡 中 | 定期审查 |
| **可删除** | ~80 个 | 🟢 低 | 谨慎清理 |

### 风险提示
1. ⚠️ 删除前请确认文件确实不再需要
2. ⚠️ 建议先在备份分支或测试目录执行清理命令
3. ⚠️ 某些 .json 文件可能是配置文件，请仔细审查
4. ⚠️ 媒体文件中可能有必要的文档图片，请逐个确认

### 下一步建议
1. ✅ 先更新 .gitignore（最安全）
2. ✅ 提交 AGENT_RULES.md 和 .gitignore
3. ⚠️ 审查"可删除"文件列表，确认后再删除
4. ⚠️ 定期（每周）清理临时文件和日志

---

**报告生成完毕**。以上命令仅供参考，请根据实际情况调整后再执行。
