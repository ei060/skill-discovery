@echo off
REM AI Roland Meta-Agent 调度脚本
REM 用于Windows系统

echo ======================================================================
echo AI Roland Meta-Agent Scheduler
echo ======================================================================

SET PYTHONPATH=D:\ClaudeWork\AI_Roland\system
SET SCRIPT_DIR=%~dp0
cd %SCRIPT_DIR%

REM 检查参数
IF "%1"=="daily" GOTO daily_review
IF "%1"=="weekly" GOTO weekly_optimization
IF "%1"=="status" GOTO show_status

REM 默认：显示状态
GOTO show_status

:daily_review
echo.
echo [执行] 每日Agent审查...
python meta_agent.py --review
echo.
echo [完成] 每日审查已执行
GOTO end

:weekly_optimization
echo.
echo [执行] 每周记忆优化...
python meta_agent.py --optimize
echo.
echo [完成] 每周优化已执行
GOTO end

:show_status
echo.
python meta_agent.py --status
GOTO end

:end
echo.
echo ======================================================================
echo Meta-Agent 任务完成
echo ======================================================================
pause
