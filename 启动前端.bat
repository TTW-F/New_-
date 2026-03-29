@echo off
chcp 65001 >nul
echo ========================================
echo 启动前端开发服务器
echo ========================================
echo.

cd frontend
echo 正在启动 Vite 开发服务器...
npm run dev

pause
