@echo off
REM Windows Hook Script - Inject Memory
REM
REM 这个脚本在Task tool调用前执行
REM 自动加载AI Roland的记忆并注入到agent

setlocal enabledelayedexpansion

REM 设置路径
set AGENT_BRIDGE=%~dp0..\agent_bridge.py
set HOOK_LOG=%~dp0memory_injection.log

REM 检查参数
if "%1"=="" (
    exit /b 0
)

REM 提取agent名称（简化版）
set AGENT_NAME=%1

REM 检查是否是Task tool
echo %1 | findstr /i "task" >nul
if errorlevel 1 (
    exit /b 0
)

REM 调用Python脚本注入记忆
python "%AGENT_BRIDGE%" %* 2>nul

endlocal
