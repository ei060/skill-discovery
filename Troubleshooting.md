# Browser Control Skill - Quick Installation Guide

## Prerequisites

- Windows 10/11
- Node.js 16.x or later (Get it from https://nodejs.org/)

## Installation (3-5 minutes)

### Option 1: Automated Installation

1. Double-click: `启动BrowserControl本地安装-修复版.bat`
2. Wait for installation to complete
3. Run test: `node test-12306-local.js`

### Option 2: English Version (No encoding issues)

1. Double-click: `Installer-English.bat`
2. Wait for installation to complete
3. Run test: `node test-12306-local.js`

### Option 3: Manual Installation

```bash
# 1. Check Node.js
node --version

# 2. Navigate to directory
cd %USERPROFILE%\AI_Roland\system\skills\browser-control

# 3. Install dependencies
npm install playwright

# 4. Install browser
npx playwright install chromium

# 5. Test
npm test
```

## Verification

After installation, run:

```bash
node test-12306-local.js
```

**Expected Result:**
- Browser window opens automatically
- Visits 12306 website
- Screenshot saved to C:\Users\Public\12306-demo.png

## Usage

### Run 12306 Demo

```bash
cd C:\Users\[YourUsername]\AI_Roland\system\skills\browser-control
node test-12306-local.js
```

### Create Custom Script

```javascript
// my-script.js
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  await page.goto('https://www.12306.cn/');

  // Add your custom code here

  // Keep browser open
  await new Promise(() => {});
})();
```

Run: `node my-script.js`

## Troubleshooting

### Issue: Console shows garbled text
**Solution**: The script still works, just display issue. Check actual files for correct content.

### Issue: Installation fails
**Solutions**:
- Run as Administrator
- Disable antivirus temporarily
- Check network connection
- Ensure 500MB+ disk space

### Issue: Browser won't launch
**Solution**:
```bash
npx playwright install chromium --force
```

### Issue: Test timeout
**Solution**:
```bash
# Reinstall dependencies
rm -rf node_modules
npm install
```

## Files

After installation, you should have:

```
C:\Users\[YourUsername]\AI_Roland\system\skills\browser-control\
├── index.js                 # Core controller
├── test.js                  # Basic tests
├── test-12306-local.js     # 12306 demo
├── roland-integration.js   # Integration layer
├── package.json             # Dependencies
└── node_modules\            # Installed packages
```

## Features

- Open websites automatically
- Fill forms
- Click buttons
- Take screenshots
- Extract data (links, text, images)
- Save login credentials (encrypted)

## Examples

### Example 1: Search on Baidu
```javascript
await page.goto('https://www.baidu.com');
await page.fill('#kw', 'AI Roland');
await page.click('#su');
```

### Example 2: Extract Links
```javascript
const links = await page.evaluate(() =>
  Array.from(document.querySelectorAll('a')).map(a => ({
    text: a.textContent,
    href: a.href
  }))
);
console.log(links);
```

### Example 3: Take Screenshot
```javascript
await page.screenshot({ path: 'screenshot.png' });
```

---

**Installation Guide** - Read this for detailed instructions

**Status Checker** - Run `检查状态修复版.bat` to check installation status
