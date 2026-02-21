@echo off
chcp 65001 >nul

echo ============================================================
echo NotebookLM Google 登录助手
echo ============================================================
echo.
echo 正在启动浏览器...
echo 请在浏览器中完成 Google 账号登录
echo.
echo 登录成功后，Session 会自动保存
echo 后续使用 notebooklm 命令无需重复登录
echo.
echo 按 Ctrl+C 停止
echo ============================================================
echo.

python "D:\ClaudeWork\AI_Roland\system\notebooklm_login.py"
