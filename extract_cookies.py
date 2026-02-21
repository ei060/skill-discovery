"""
从已登录的 Chrome 提取 cookies
通过 Chrome DevTools Protocol
"""

import json
from pathlib import Path

print("="*60)
print("Cookie 提取助手")
print("="*60)
print()
print("请按以下步骤操作：")
print()
print("1. 在已登录 NotebookLM 的 Chrome 浏览器中，按 F12 打开开发者工具")
print("2. 切换到「Console」（控制台）标签")
print("3. 复制并运行以下代码：")
print()
print("-" * 60)
print("""
// 复制所有 cookies
document.cookie.split(';').forEach(c => {
    const [name, value] = c.trim().split('=');
    console.log(name + '=' + value);
});

// 或者使用 Chrome API
chrome.cookies.getAll({domain: '.google.com'}, (cookies) => {
    console.log(JSON.stringify(cookies, null, 2));
});
""")
print("-" * 60)
print()
print("4. 将输出的 cookies 内容发送给我")
print()
print("="*60)
print()
print("或者，更简单的方法：")
print()
print("1. 在 Chrome 中按 F12")
print("2. 切换到「Application」（应用）标签")
print("3. 左侧找到「Cookies」")
print("4. 展开 https://notebooklm.google.com")
print("5. 找到名为 'SID' 的 cookie，复制它的值")
print()
print("="*60)

# 等待用户输入
print("\n如果你已经复制了 SID cookie 的值，请粘贴到这里：")
sid_value = input("SID cookie 值（留空跳过）: ")

if sid_value:
    print(f"\n你输入的 SID: {sid_value[:20]}...")
    print("\n正在保存到 storage_state.json...")

    # 读取现有的 storage_state
    storage_file = Path("C:/Users/DELL/.notebooklm/storage_state.json")

    storage_state = {
        "cookies": [
            {
                "name": "SID",
                "value": sid_value,
                "domain": ".google.com",
                "path": "/",
                "expires": -1,
                "httpOnly": True,
                "secure": True,
                "sameSite": "None"
            }
        ],
        "origins": []
    }

    with open(storage_file, 'w', encoding='utf-8') as f:
        json.dump(storage_state, f, ensure_ascii=False, indent=2)

    print(f"已保存到: {storage_file}")
    print("\n现在运行: notebooklm list")
else:
    print("\n已跳过。请手动完成登录。")
