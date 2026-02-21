@echo off
REM 一键启动 Claude 和 AI Roland
REM 每次启动 Claude 前运行此脚本

echo ============================================================
echo   AI Roland + Claude 自动启动
echo ============================================================
echo.
echo [1/2] 启动 AI Roland 系统...
echo.

cd /d "%~dp0"
cd AI_Roland\system
python session_start.py

echo.
echo ============================================================
echo [2/2] AI Roland 已就绪
echo ============================================================
echo.
echo 现在可以启动 Claude Code CLI
echo.
echo 提示:
echo - 守护进程会在后台持续运行
echo - 每次会话都会自动记录到对话历史
echo - 任务统计会自动更新
echo.
pause
