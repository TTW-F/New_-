@echo off
chcp 65001 >nul
echo ========================================
echo 安装优雅的日志系统
echo ========================================
echo.

echo [1/2] 安装 Loguru 和 Rich...
pip install -r requirements-logger.txt

echo.
echo [2/2] 创建日志目录...
if not exist "logs" mkdir logs

echo.
echo ========================================
echo ✓ 安装完成！
echo ========================================
echo.
echo 现在你可以使用新的日志系统了
echo 日志文件位置: logs/app.log 和 logs/error.log
echo.
pause
