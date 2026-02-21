@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8

echo ============================================================
echo AI Roland 知识库查询（编码修复版）
echo ============================================================
echo.

if "%~1"=="" (
    echo 使用方法:
    echo   查询AI_Roland\system\查询AI_Roland知识库.bat "你的问题"
    echo.
    echo 示例:
    echo   查询AI_Roland\system\查询AI_Roland知识库.bat "浏览器控制器如何使用？"
    echo   查询AI_Roland\system\查询AI_Roland知识库.bat "AI Roland的核心功能"
    echo.
    pause
    exit /b
)

python AI_Roland\system\notebooklm_wrapper.py ask %*

pause
