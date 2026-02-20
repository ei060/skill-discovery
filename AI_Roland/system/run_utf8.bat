@echo off
REM 设置控制台为 UTF-8 编码
chcp 65001 >nul 2>&1

REM 设置 Python 使用 UTF-8 编码
set PYTHONIOENCODING=utf-8

REM 执行传入的命令
python %*
