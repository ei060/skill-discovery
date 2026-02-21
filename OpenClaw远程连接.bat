@echo off
chcp 65001 >nul

echo ============================================================
echo OpenClaw 远程连接
echo ============================================================
echo.
echo 正在建立 SSH 隧道...
echo 本地端口: localhost:18789
echo 远程地址: 127.0.0.1:18789 (AWS VPS)
echo.
echo 连接成功后，请在浏览器打开:
echo http://localhost:18789/#token=308fbd032daa9b1b71297b2bf96d1766c9a5af01de1c799f
echo.
echo 按 Ctrl+C 断开连接
echo.
echo ============================================================

ssh -N -L 18789:127.0.0.1:18789 -i "C:\Users\DELL\.ssh\uqiha1.pem" ubuntu@3.86.220.54
