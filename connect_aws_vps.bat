@echo off
chcp 65001 >nul

echo ============================================================
echo AWS VPS SSH 连接
echo ============================================================
echo.
echo 连接到: aws-uqiha (3.86.220.54)
echo 用户: ubuntu
echo.

REM 使用 Windows 自带的 SSH 客户端
ssh -i "C:\Users\DELL\.ssh\uqiha1.pem" ubuntu@3.86.220.54

pause
