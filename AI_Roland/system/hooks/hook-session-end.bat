@echo off
REM AI Roland SessionEnd Hook
REM 捕获会话结束事件

cd /d D:\ClaudeWork
python AI_Roland\system\hooks\observe.py --event session_end --data "{\"session_id\": \"%1\"}"
