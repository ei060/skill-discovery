"""
编码修复工具 - 解决 Windows 控制台中文乱码
"""

import sys
import os

# 设置标准输出编码为 UTF-8
if sys.platform == 'win32':
    # 方法 1: 设置环境变量
    os.environ['PYTHONIOENCODING'] = 'utf-8'

    # 方法 2: 重新配置标准输出
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 测试输出
def test():
    print("测试中文输出")
    print("✅ Hooks 系统")
    print("🔍 Skills 插件")
    print("📊 记忆搜索")

if __name__ == "__main__":
    test()
