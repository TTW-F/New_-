@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title Medical QA System - Startup

echo.
echo ========================================================
echo        医疗智能问答系统 - 一键启动
echo ========================================================
echo.

cd /d %~dp0

REM 配置变量
set REDIS_CONTAINER=redis-medical-qa
set NEO4J_BIN=
set MYSQL_SERVICE=MySQL80

REM 检查 Python 是否安装
echo [检查] Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    goto ENDSCRIPT
)
echo [成功] Python 已安装

REM 检查 Node.js 是否安装
echo [检查] Node.js 环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Node.js，请先安装 Node.js 16+
    goto ENDSCRIPT
)
echo [成功] Node.js 已安装

echo.
echo ========================================================
echo   第一步：启动数据库服务
echo ========================================================

REM 1. 检查并启动 MySQL
echo.
echo [1/3] 检查 MySQL...
sc query %MYSQL_SERVICE% | find "RUNNING" >nul 2>&1
if not errorlevel 1 (
    echo [成功] MySQL 正在运行
) else (
    echo [提示] MySQL 未运行，正在启动...
    net start %MYSQL_SERVICE% >nul 2>&1
    if errorlevel 1 (
        echo [警告] MySQL 启动失败，请检查服务是否已安装
    ) else (
        echo [成功] MySQL 已启动
    )
)

REM 2. 检查并启动 Redis (Docker)
echo.
echo [2/3] 检查 Redis...
docker info >nul 2>&1
if errorlevel 1 (
    echo [警告] Docker 未运行，跳过 Redis 启动
    echo [提示] Redis 是可选服务，不影响核心功能
) else (
    docker ps --format "{{.Names}}" | findstr /i "%REDIS_CONTAINER%" >nul 2>&1
    if not errorlevel 1 (
        echo [成功] Redis 正在运行
    ) else (
        echo [提示] Redis 未运行，正在启动...
        docker start %REDIS_CONTAINER% >nul 2>&1
        if errorlevel 1 (
            echo [警告] Redis 容器不存在，跳过启动
            echo [提示] 可使用以下命令创建 Redis 容器:
            echo docker run -d --name %REDIS_CONTAINER% -p 6379:6379 redis:latest
        ) else (
            echo [成功] Redis 已启动
        )
    )
)

REM 3. 检查并启动 Neo4j
echo.
echo [3/3] 检查 Neo4j...
netstat -ano | findstr ":7687 " | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo [成功] Neo4j 正在运行
    goto neo4j_done
)

echo [警告] Neo4j 未运行，正在尝试启动...

REM 尝试查找 Neo4j 安装路径
where neo4j >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Neo4j 安装
    echo.
    echo 请选择以下方式之一安装并启动 Neo4j:
    echo.
    echo 方式 1: 使用 Neo4j Desktop (推荐)
    echo   1. 下载: https://neo4j.com/download/
    echo   2. 安装并打开 Neo4j Desktop
    echo   3. 创建数据库实例并点击 "Start"
    echo.
    echo 方式 2: 使用 Docker
    echo   docker run -d --name neo4j-medical -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest
    echo.
    echo 方式 3: 安装 Neo4j Community Edition
    echo   下载地址: https://neo4j.com/download/
    echo.
    if "%1"=="test" (
        echo [测试模式] 自动继续启动
        echo [警告] 继续启动，但问答功能将不可用
    ) else (
        choice /C YN /M "是否继续启动（问答功能将不可用）"
        if errorlevel 2 (
            echo [取消] 启动已取消
            goto ENDSCRIPT
        )
        echo [警告] 继续启动，但问答功能将不可用
    )
    goto neo4j_done
)

echo [提示] 检测到 Neo4j 命令行工具，正在启动...
start "Neo4j Database" cmd /c "neo4j console"
echo [等待] 等待 Neo4j 启动 (最多 30 秒)...

set neo4j_retry=0
:neo4j_wait_loop
timeout /t 1 /nobreak >nul
netstat -ano | findstr ":7687 " | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo [成功] Neo4j 已启动！
    goto neo4j_done
)
set /a neo4j_retry=neo4j_retry+1
if %neo4j_retry% LSS 30 (
    echo [等待] Neo4j 启动中... (%neo4j_retry%/30)
    goto neo4j_wait_loop
)
echo [警告] Neo4j 启动超时，但将继续启动其他服务
echo [提示] 请检查 Neo4j 窗口的启动日志

:neo4j_done

echo.
echo ========================================================
echo   第二步：准备 Python 环境
echo ========================================================

echo [1/4] 检查 Python 虚拟环境...
if not exist ".venv" (
    echo [提示] 虚拟环境不存在，正在创建...
    python -m venv .venv
    if errorlevel 1 (
        echo [错误] 创建虚拟环境失败
        goto ENDSCRIPT
    )
    echo [成功] 虚拟环境创建完成
) else (
    echo [成功] 虚拟环境已存在
)

echo.
echo [2/4] 激活虚拟环境...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [错误] 激活虚拟环境失败
    goto ENDSCRIPT
)
echo [成功] 虚拟环境已激活

echo.
echo [3/4] 检查后端依赖...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装后端依赖...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 安装后端依赖失败
        goto ENDSCRIPT
    )
    echo [成功] 后端依赖安装完成
) else (
    echo [成功] 后端依赖已安装
)

echo.
echo [4/4] 检查前端依赖...
cd frontend
if not exist "node_modules" (
    echo [提示] 正在安装前端依赖...
    call npm install
    if errorlevel 1 (
        echo [错误] 安装前端依赖失败
        cd ..
        goto ENDSCRIPT
    )
    echo [成功] 前端依赖安装完成
) else (
    echo [成功] 前端依赖已安装
)
cd ..

echo.
echo ========================================================
echo   第三步：启动应用服务
echo ========================================================

REM 检查后端是否已运行
echo.
echo [1/2] 启动后端服务...
netstat -ano | findstr ":8000 " | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo [警告] 端口 8000 已被占用，后端可能已在运行
) else (
    start "医疗问答系统-后端" cmd /k "call .venv\Scripts\activate.bat && python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload"
    timeout /t 3 /nobreak >nul
    echo [成功] 后端服务已启动
)

REM 检查前端是否已运行
echo.
echo [2/2] 启动前端服务...
netstat -ano | findstr ":3000 " | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo [警告] 端口 3000 已被占用，前端可能已在运行
) else (
    start "医疗问答系统-前端" cmd /k "cd frontend && npm run dev"
    timeout /t 2 /nobreak >nul
    echo [成功] 前端服务已启动
)

echo.
echo ========================================================
echo   启动完成！
echo ========================================================
echo.
echo   前端应用: http://localhost:3000
echo   后端 API: http://localhost:8000
echo   API 文档: http://localhost:8000/docs
echo   Neo4j:    http://localhost:7474
echo.
echo ========================================================
echo.

if "%1"=="test" (
    echo [测试模式] 跳过打开浏览器
    goto ENDSCRIPT
)

set /p OPEN_APP=是否打开前端页面？(Y/N): 
if /i "%OPEN_APP%"=="Y" start http://localhost:3000

:ENDSCRIPT
echo.
if "%1"=="test" (
    echo [测试模式] 脚本执行完成
) else (
    echo 按任意键关闭此窗口...
    echo (注意: 关闭此窗口不会停止服务)
    pause >nul
)
