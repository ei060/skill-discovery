@echo off
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8

echo ============================================================
echo   AI Roland 系统测试
echo ============================================================
echo.

echo [1/3] 测试 Hooks 系统...
echo.
cd AI_Roland\system
python hooks_manager.py

echo.
echo [2/3] 测试 Skills 系统...
echo.
python skills_manager.py

echo.
echo [3/3] 测试记忆搜索...
echo.
python memory_search.py

echo.
echo ============================================================
echo   所有测试完成！
echo ============================================================
pause
