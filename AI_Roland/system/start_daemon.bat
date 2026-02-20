@echo off
chcp 65001 >nul

echo ============================================================
echo AI Roland 守护进程启动
echo ============================================================
echo.

cd /d %~dp0

echo [INFO] 守护进程将在后台持续运行
echo [INFO] 日志文件: AI_Roland/logs/daemon_YYYYMMDD.log
echo [INFO] 按 Ctrl+C 可停止
echo.

python daemon.py

pause
