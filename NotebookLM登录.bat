@echo off
chcp 65001 >nul

echo ============================================================
echo NotebookLM 远程登录（X11 转发）
echo ============================================================
echo.
echo 正在建立 SSH 连接（支持图形界面）...
echo 连接成功后，Google 登录浏览器将自动打开
echo.
echo 按 Ctrl+C 断开连接
echo ============================================================

ssh -Y -i "C:\Users\DELL\.ssh\uqiha1.pem" ubuntu@3.86.220.54 "/home/ubuntu/.local/bin/notebooklm login"
