@echo off
chcp 65001 >nul
echo ========================================
echo   医疗智能问答系统 - 生产构建
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
echo [2/2] 构建生产版本...
call npm run build
if errorlevel 1 (
    echo.
    echo [错误] 构建失败
    cd ..
    pause
    exit /b 1
)

cd ..

echo.
echo ========================================
echo   构建完成！
echo ========================================
echo.
echo   构建文件位置: frontend\dist\
echo.
echo   部署说明:
echo   1. 将 frontend\dist\ 目录部署到 Web 服务器
echo   2. 配置 Nginx 或其他 Web 服务器
echo   3. 确保后端 API 服务正常运行
echo.
pause
