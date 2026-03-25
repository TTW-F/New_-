@echo off
chcp 65001 >nul
echo ========================================
echo   医疗智能问答系统 - 启动前端服务
echo ========================================
echo.

REM 检查 Node.js 是否安装
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Node.js，请先安装 Node.js
    pause
    exit /b 1
)

echo [1/2] 检查前端依赖...
cd frontend
if not exist "node_modules" (
    echo [提示] 正在安装前端依赖...
    call npm install
    if errorlevel 1 (
        echo [错误] 安装前端依赖失败
        cd ..
        pause
        exit /b 1
    )
    echo [成功] 前端依赖安装完成
) else (
    echo [提示] 前端依赖已安装
)

echo.
echo [2/2] 启动前端服务...
echo.
echo ========================================
echo   前端服务地址: http://localhost:3000
echo ========================================
echo.
echo   按 Ctrl+C 停止服务
echo.

call npm run dev
