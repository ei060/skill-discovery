# web-access Skill 安装完成

## ✅ 安装状态

- ✅ 已克隆到 `~/.claude/skills/web-access`
- ✅ 已复制到 `AI_Roland/system/skills/web-access`
- ✅ 已更新技能注册表
- ✅ 临时目录已清理

## 📊 Skill 信息

| 项目 | 内容 |
|------|------|
| **名称** | web-access |
| **版本** | v2.4.1 |
| **作者** | 一泽Eze |
| **GitHub** | https://github.com/eze-is/web-access |
| **分类** | network |
| **优先级** | 10（高） |

## 🚀 核心能力

### 1. 联网工具自动选择
- WebSearch - 搜索摘要或关键词结果
- WebFetch - 定向提取特定信息
- curl - 获取原始 HTML 源码
- Jina - 网页转 Markdown（节省 token）
- CDP - 浏览器操作（支持动态页面、登录态）

### 2. CDP 浏览器操作
- 直连用户日常 Chrome
- 天然携带登录态
- 支持动态页面、交互操作
- 视频截帧分析

### 3. 三种点击方式
- `/click` - JS 点击
- `/clickAt` - 真实鼠标事件
- `/setFiles` - 文件上传

### 4. 并行分治
- 多目标时子 Agent 并行执行
- 共享一个 Proxy
- tab 级隔离

### 5. 站点经验积累
- 按域名存储操作经验
- URL 模式、平台特征、已知陷阱
- 跨 session 复用

## ⚙️ 前置配置

### CDP 模式依赖

**已满足：**
- ✅ Node.js v24.12.0（要求 22+）

**需要配置：**
- ⚠️ Chrome 远程调试未启用

### 启用 Chrome 远程调试

1. 打开 Chrome
2. 地址栏输入：`chrome://inspect/#remote-debugging`
3. 勾选 **"Allow remote debugging for this browser instance"**
4. 可能需要重启浏览器

### 验证配置

```bash
bash ~/.claude/skills/web-access/scripts/check-deps.sh
```

预期输出：
```
node: ok (v24.12.0)
chrome: connected ✅
```

## 🔧 使用方法

### 自动触发场景

Claude 会自动在以下场景使用此 skill：
- 搜索信息
- 查看网页内容
- 访问需要登录的网站
- 操作网页界面
- 抓取社交媒体内容（小红书、微博、推特等）
- 读取动态渲染页面
- 需要真实浏览器环境的网络任务

### 手动检查依赖

```bash
cd AI_Roland/system/skills/web-access
bash scripts/check-deps.sh
```

### 启动 CDP Proxy

```bash
node ~/.claude/skills/web-access/scripts/cdp-proxy.mjs &
```

Proxy 默认运行在 `http://localhost:3456`

## 📖 浏览哲学

**像人一样思考**，兼顾高效与适应性：

1. **拿到请求** — 明确目标，定义成功标准
2. **选择起点** — 根据任务性质选择最佳方式
3. **过程校验** — 用结果对照目标，动态调整
4. **完成判断** — 达成目标后停止，避免过度操作

## 🔗 相关资源

- **GitHub**: https://github.com/eze-is/web-access
- **推荐阅读**: [Web Access：一个 Skill，拉满 Agent 联网和浏览器能力](https://mp.weixin.qq.com/s/rps5YVB6TchT9npAaIWKCw)
- **完整文档**: `~/.claude/skills/web-access/README.md`

## 📝 技能统计

- 当前系统总技能数：12
- 网络相关技能：2（web-access, ask-search）
- 浏览器相关技能：3（web-access, browser-control, network-scraping）

---
**安装时间**: 2026-03-28
**状态**: ✅ 已安装，待配置 Chrome 远程调试
