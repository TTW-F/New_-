@echo off
chcp 65001 >nul
echo ========================================
echo   医疗智能问答系统 - 启动后端服务
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo [1/2] 激活虚拟环境...
if not exist ".venv" (
    echo [错误] 虚拟环境不存在，请先运行 start-all.bat
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [错误] 激活虚拟环境失败
    pause
    exit /b 1
)

echo [成功] 虚拟环境已激活
echo.
echo [2/2] 启动后端服务...
echo.
echo ========================================
echo   后端服务地址: http://localhost:8000
echo   API 文档地址: http://localhost:8000/docs
echo ========================================
echo.
echo   按 Ctrl+C 停止服务
echo.

python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
