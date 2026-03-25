@echo off
chcp 65001 >nul
echo ========================================
echo 通过API创建管理员账号
echo ========================================
echo.
echo 注意: 请确保后端服务正在运行
echo.

call .venv\Scripts\activate.bat

pip install requests >nul 2>&1

python test_create_admin.py

echo.
echo ========================================
pause
