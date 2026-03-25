@echo off
chcp 65001 >nul
echo ========================================
echo 创建管理员账号
echo ========================================
echo.

echo 激活虚拟环境...
call .venv\Scripts\activate.bat

echo.
echo 运行创建脚本...
python create_admin.py

echo.
echo ========================================
pause
