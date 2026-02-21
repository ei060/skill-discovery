@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8

echo ============================================================
echo NotebookLM 中文修复版启动器
echo ============================================================
echo.
echo 正在启动 NotebookLM...
echo 已启用 UTF-8 编码支持
echo.
echo ============================================================

python AI_Roland/system/second_brain.py %*
