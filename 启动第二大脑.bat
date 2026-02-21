@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8

echo ============================================================
echo AI Roland 第二大脑助手
echo ============================================================
echo.
echo 正在查询第二大脑...
echo.

if "%~1"=="" (
    echo 使用方法:
    echo   启动AI_Roland\system\启动第二大脑.bat "你的问题"
    echo.
    echo 示例:
    echo   启动AI_Roland\system\启动第二大脑.bat "决策背景是什么？"
    echo   启动AI_Roland\system\启动第二大脑.bat "推荐学习路径"
    echo.
    pause
    exit /b
)

python AI_Roland\system\second_brain.py query %*

echo.
echo ============================================================
echo 查询完成！
echo ============================================================
pause
