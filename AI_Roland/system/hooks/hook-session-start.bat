@echo off
REM AI Roland SessionStart Hook
REM 捕获会话开始事件

cd /d D:\ClaudeWork
python AI_Roland\system\hooks\observe.py --event session_start --data "{\"session_id\": \"%1\"}"
