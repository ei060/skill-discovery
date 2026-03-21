# Browser Control Skill - 本地版

**快速开始**：双击运行 `启动BrowserControl本地安装.bat`

## 已完成

✅ 本地安装脚本已创建：`启动BrowserControl本地安装.bat`
✅ 12306演示脚本已创建：`test-12306-local.js`

## 一键安装步骤

### 方式1：自动安装（推荐）

1. **双击运行** `启动BrowserControl本地安装.bat`
2. 等待安装完成（约3-5分钟）
3. 测试运行：`node test.js`

### 方式2：手动安装

```bash
# 1. 检查Node.js（如果没安装请先安装）
node --version

# 2. 进入目录
cd %USERPROFILE%\AI_Roland\system\skills\browser-control

# 3. 安装依赖
npm install playwright

# 4. 安装浏览器
npx playwright install chromium

# 5. 测试
npm test
```

## 使用12306查询

### 方法1：运行演示脚本

```bash
# 进入目录
cd %USERPROFILE%\AI_Roland\system\skills\browser-control

# 运行12306演示
node test-12306-local.js
```

浏览器会自动打开12306网站，你可以手动查询车票。

### 方法2：创建自定义脚本

创建文件 `my-query.js`：

```javascript
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  // 打开12306
  await page.goto('https://www.12306.cn/');

  // TODO: 在这里添加你的自定义代码
  // 例如：自动填写表单、点击按钮等

  // 保持浏览器打开
  await new Promise(() => {});
})();
```

运行：`node my-query.js`

## 文件说明

| 文件 | 说明 |
|------|------|
| `启动BrowserControl本地安装.bat` | 一键安装脚本 |
| `test-12306-local.js` | 12306演示脚本 |
| `test.js` | 基础测试脚本 |
| `index.js` | 核心控制器 |
| `package.json` | 依赖配置 |

## 系统要求

- Windows 10/11
- Node.js 16.x+ （推荐 20.x LTS）
- 至少 4GB 内存
- 至少 500MB 磁盘空间

## 常见问题

### Q: 安装失败？
A: 确保有管理员权限，或以管理员身份运行脚本

### Q: 浏览器启动失败？
A: 运行 `npx playwright install chromium --force`

### Q: 想要看到浏览器？
A: 将 `headless: false` 改为 `headless: true`

### Q: 如何关闭浏览器？
A: 按 Ctrl+C 或关闭浏览器窗口

## 下一步

安装完成后，你可以：

1. ✅ 运行演示脚本查看效果
2. ✅ 创建自定义脚本
3. ✅ 集成到你的工作流程

## 示例：12306自动查询脚本

```javascript
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  await page.goto('https://www.12306.cn/');

  // TODO: 添加自动化逻辑
  // 1. 点击"购票"
  // 2. 填写出发地、目的地
  // 3. 选择日期
  // 4. 点击查询

  console.log('✓ 12306已打开，请手动查询');

  await new Promise(() => {});
})();
```

---

**准备好了吗？双击运行 `启动BrowserControl本地安装.bat` 开始安装！**
