@echo off
REM Windows Hook Script - Save Memory
REM
REM 这个脚本在Task tool执行后执行
REM 自动保存执行经验到AI Roland记忆

setlocal enabledelayedexpansion

REM 设置路径
set SAVE_MEMORY=%~dp0..\save_memory.py

REM 检查参数
if "%1"=="" (
    exit /b 0
)

REM 调用Python脚本保存记忆
python "%SAVE_MEMORY%" %* 2>nul

endlocal
