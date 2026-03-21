@echo off
REM AI Roland PreToolUse Hook
REM 捕获工具调用前事件

cd /d D:\ClaudeWork
python AI_Roland\system\hooks\observe.py --event pre_tool_use --data "{\"tool_name\": \"%1\", \"session_id\": \"%2\"}"
