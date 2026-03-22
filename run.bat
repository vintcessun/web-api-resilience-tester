@echo off
setlocal
:: ==========================================
:: 配置区域
:: ==========================================
set ENV_NAME=base
set SCRIPT_NAME=main.py

echo [!] 准备启动正义执行任务...
echo [!] 正在激活 Conda 环境: %ENV_NAME%

:: 激活 Conda 环境
call conda activate %ENV_NAME%

:loop
echo.
echo ======================================================
echo [%TIME%] 正在发动新一轮投毒...
echo ======================================================

:: 执行 Python 脚本
python %SCRIPT_NAME%

:: 检查执行结果
if %ERRORLEVEL% NEQ 0 (
    echo [!] 脚本异常退出，错误码: %ERRORLEVEL%
    echo [!] 正在等待 5 秒后重试...
    timeout /t 5 /nobreak
) else (
    echo [!] 本轮投毒圆满完成。
    :: 设置一个随机或者固定的冷却时间，防止本地 IP 被秒封
    echo [!] 冷却 5 秒后开始下一轮...
    timeout /t 5 /nobreak
)

:: 跳回循环起点
goto loop