@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8

echo ============================================================
echo AI Roland x NotebookLM - 编码包装器演示
echo ============================================================
echo.

echo 正在演示编码包装器的三种功能...
echo.

echo [功能1] 自动乱码检测和修复
echo --------------------------------------
python AI_Roland\system\notebooklm_wrapper.py demo

echo.
echo [功能2] 中文查询（自动转换）
echo --------------------------------------
echo 查询："浏览器控制器的核心功能"
python AI_Roland\system\notebooklm_wrapper.py ask "浏览器控制器的核心功能有哪些？"

echo.
echo [功能3] 记忆搜索
echo --------------------------------------
echo 搜索关键词："记忆 系统"
python AI_Roland\system\notebooklm_wrapper.py search "记忆,系统"

echo.
echo ============================================================
echo 演示完成！
echo ============================================================
echo.
echo 日常使用:
echo   1. 双击：查询AI_Roland知识库.bat "你的问题"
echo   2. 双击：启动第二大脑.bat "你的问题"
echo   3. 或直接使用: python AI_Roland\system\notebooklm_wrapper.py ask "问题"
echo.
pause
