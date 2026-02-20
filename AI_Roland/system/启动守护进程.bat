@echo off
chcp 65001 >nul

echo ============================================================
echo AI Roland 守护进程管理
echo ============================================================
echo.

:MENU
echo 请选择操作:
echo   1. 启动守护进程（后台运行）
echo   2. 查看系统状态
echo   3. 查看实时日志
echo   4. 安装开机自启动
echo   5. 停止守护进程
echo   6. 退出
echo.

set /p choice=请输入选择 (1-6):

cd /d %~dp0

if "%choice%"=="1" (
    echo.
    echo [INFO] 启动守护进程...
    start /MIN pythonw daemon.py
    echo [OK] 守护进程已在后台启动
    echo.
    pause
    goto MENU
)

if "%choice%"=="2" (
    echo.
    python monitor.py
    pause
    goto MENU
)

if "%choice%"=="3" (
    echo.
    echo [INFO] 打开最新日志...
    for /f "delims=" %%i in ('dir /b /o-d ..\logs\daemon_*.log 2^>nul') do (
        set logfile=%%i
        goto :found
    )
    echo [ERROR] 未找到日志文件
    pause
    goto MENU

    :found
    start notepad ..\logs\%logfile%
    goto MENU
)

if "%choice%"=="4" (
    echo.
    python install_service.py
    pause
    goto MENU
)

if "%choice%"=="5" (
    echo.
    echo [INFO] 正在停止守护进程...
    for /f "tokens=2" %%a in ('tasklist /fi "imagename eq pythonw.exe" ^| find "pythonw"') do (
        taskkill /pid %%a /f >nul 2>&1
    )
    echo [OK] 守护进程已停止
    echo.
    pause
    goto MENU
)

if "%choice%"=="6" (
    echo.
    echo 再见！
    exit /b 0
)

echo.
echo [ERROR] 无效选择
pause
goto MENU
