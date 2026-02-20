@echo off
chcp 65001 >nul
echo ============================================================
echo AI Roland v2.0 - 一键启动所有服务
echo ============================================================
echo.

cd /d %~dp0

echo [1/4] 启动引擎（带 Heartbeat）
start "AI Roland Engine" python engine_v2.py
timeout /t 2 >nul

echo [2/4] 启动 HTTP API 服务器（端口 3000）
start "AI Roland API" python http_api.py
timeout /t 2 >nul

echo [3/4] 启动 MCP 服务器（端口 3010）
start "AI Roland MCP" python mcp_server.py
timeout /t 2 >nul

echo [4/4] 启动增强版 CLI
start "AI Roland CLI" python cli_v2.py

echo.
echo ============================================================
echo 全部服务已启动！
echo ============================================================
echo.
echo 服务地址：
echo   - HTTP API:   http://localhost:3000
echo   - MCP:        http://localhost:3010
echo   - API 文档:   http://localhost:3000/
echo.
echo 按任意键关闭此窗口...
pause >nul
