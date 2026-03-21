@echo off
REM AI Roland PostToolUse Hook
REM 捕获工具调用后事件

cd /d D:\ClaudeWork
python AI_Roland\system\hooks\observe.py --event post_tool_use --data "{\"tool_name\": \"%1\", \"session_id\": \"%2\"}"
