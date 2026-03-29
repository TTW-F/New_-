@echo off
chcp 65001 >nul
echo 重置管理员密码...
echo.

.venv\Scripts\python.exe reset_admin_password.py

echo.
pause
