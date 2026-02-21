@echo off
chcp 65001 >nul

echo ============================================================
echo AI Roland 浏览器控制器
echo ============================================================
echo.
echo 正在启动浏览器...
echo 浏览器将保持运行，你可以手动操作或由AI控制
echo.
echo 按 Ctrl+C 停止浏览器
echo ============================================================
echo.

python "D:\ClaudeWork\AI_Roland\system\browser_controller.py"
