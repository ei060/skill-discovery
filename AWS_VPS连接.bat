@echo off
chcp 65001 >nul

echo ============================================================
echo AWS VPS - SSH 连接
echo ============================================================
echo.
echo 服务器: aws-uqiha (3.86.220.54)
echo 用户: ubuntu
echo 密钥: uqiha1.pem
echo.
echo 正在连接...
echo.

REM 使用 Windows SSH 客户端连接
ssh -i "C:\Users\DELL\.ssh\uqiha1.pem" ubuntu@3.86.220.54

echo.
echo 连接已关闭
pause
