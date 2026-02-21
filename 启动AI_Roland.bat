@echo off
REM AI Roland 自动启动脚本
REM 每次启动 Claude 时运行此脚本

echo Starting AI Roland System...
echo.

cd /d "%~dp0AI_Roland\system"
python session_start.py

echo.
echo Press any key to close...
pause >nul
