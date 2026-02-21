@echo off
chcp 65001 >nul

echo ============================================================
echo OpenClaw 控制面板 - SSH隧道
echo ============================================================
echo.
echo 正在建立SSH隧道到AWS服务器...
echo.
echo 隧道建立后，请在浏览器中访问:
echo.
echo    http://localhost:18789
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 提示:
echo - 请保持此窗口打开
echo - 按 Ctrl+C 可停止隧道
echo - 关闭窗口也会停止隧道
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

ssh -i "C:\Users\DELL\.ssh\uqiha1.pem" -L 18789:127.0.0.1:18789 -N ubuntu@3.86.220.54

if errorlevel 1 (
    echo.
    echo [错误] SSH隧道建立失败
    echo 请检查:
    echo 1. SSH密钥文件是否存在: C:\Users\DELL\.ssh\uqiha1.pem
    echo 2. 网络连接是否正常
    echo.
    pause
)
