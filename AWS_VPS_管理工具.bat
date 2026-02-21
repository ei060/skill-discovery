@echo off
chcp 65001 >nul

:MENU
cls
echo ============================================================
echo AWS VPS 管理工具
echo ============================================================
echo.
echo [服务器信息]
echo   名称: aws-uqiha
echo   IP:   3.86.220.54
echo   用户: ubuntu
echo   系统: Ubuntu 24.04
echo.
echo [快速操作]
echo   1. 打开 SSH 终端
echo   2. 查看服务器状态
echo   3. 查看磁盘使用
echo   4. 查看运行进程
echo   5. 重启服务器
echo   6. 部署 AI Roland
echo   0. 退出
echo.

set /p choice=请选择操作 (0-6):

if "%choice%"=="1" (
    start "" cmd /k "ssh -i C:\Users\DELL\.ssh\uqiha1.pem ubuntu@3.86.220.54"
    goto MENU
)

if "%choice%"=="2" (
    echo.
    echo [查询服务器状态]
    echo.
    ssh -i C:\Users\DELL\.ssh\uqiha1.pem ubuntu@3.86.220.54 "echo '=== 系统信息 ==='; uname -a; echo; echo '=== CPU ===' | head -3; uptime; echo; echo '=== 内存 ===' | head -5; free -h; echo; echo '=== 磁盘 ===' | head -6; df -h"
    echo.
    pause
    goto MENU
)

if "%choice%"=="3" (
    echo.
    echo [磁盘使用详情]
    echo.
    ssh -i C:\Users\DELL\.ssh\uqiha1.pem ubuntu@3.86.220.54 "df -h"
    echo.
    pause
    goto MENU
)

if "%choice%"=="4" (
    echo.
    echo [运行中的进程]
    echo.
    ssh -i C:\Users\DELL\.ssh\uqiha1.pem ubuntu@3.86.220.54 "ps aux | head -20"
    echo.
    pause
    goto MENU
)

if "%choice%"=="5" (
    echo.
    echo [WARNING] 即将重启服务器！
    set /p confirm=确认重启？(y/n):
    if /i "%confirm%"=="y" (
        ssh -i C:\Users\DELL\.ssh\uqiha1.pem ubuntu@3.86.220.54 "sudo reboot"
        echo [OK] 重启命令已发送
    )
    echo.
    pause
    goto MENU
)

if "%choice%"=="6" (
    echo.
    echo [部署 AI Roland 到 VPS]
    echo.
    echo 准备部署...
    echo.
    pause
    call :DEPLOY_ROLAND
    goto MENU
)

if "%choice%"=="0" (
    echo.
    echo 退出
    exit /b 0
)

echo.
echo [ERROR] 无效选择
pause
goto MENU

:DEPLOY_ROLAND
echo.
echo ============================================================
echo 部署 AI Roland 到 AWS VPS
echo ============================================================
echo.

echo [1/5] 创建工作目录...
ssh -i C:\Users\DELL\.ssh\uqiha1.pem ubuntu@3.86.220.54 "mkdir -p ~/AI_Roland/system && cd ~/AI_Roland && pwd"

echo [2/5] 检查 Python 版本...
ssh -i C:\Users\DELL\.ssh\uqiha1.pem ubuntu@3.86.220.54 "python3 --version"

echo [3/5] 上传文件...
scp -i C:\Users\DELL\.ssh\uqiha1.pem -r D:\ClaudeWork\AI_Roland\system\*.py ubuntu@3.86.220.54:~/AI_Roland/system/

echo [4/5] 安装依赖...
ssh -i C:\Users\DELL\.ssh\uqiha1.pem ubuntu@3.86.220.54 "cd ~/AI_Roland && pip3 install -q croniter flask flask-cors requests 2>&1 | grep -v 'already satisfied' || echo '依赖已安装'"

echo [5/5] 创建服务配置...
ssh -i C:\Users\DELL\.ssh\uqiha1.pem ubuntu@3.86.220.54 "cat > ~/AI_Roland/system/daemon.service << 'EOF'
[Unit]
Description=AI Roland Daemon
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/ubuntu/AI_Roland
ExecStart=/usr/bin/python3 system/daemon.py
Restart=always
User=ubuntu

[Install]
WantedBy=multi-user.target
EOF
"

echo.
echo ============================================================
echo [OK] 部署完成！
echo ============================================================
echo.
echo 下一步操作：
echo   1. 启动服务: ssh ubuntu@3.86.220.54 "cd ~/AI_Roland && python3 system/daemon.py"
echo   2. 或注册为系统服务
echo.
pause
goto :EOF
