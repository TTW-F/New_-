@echo off
chcp 65001 >nul
echo ========================================
echo   Neo4j 数据库启动脚本
echo ========================================
echo.

REM 检查 Neo4j 是否已安装
where neo4j >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Neo4j 命令行工具
    echo.
    echo 请选择以下方式之一启动 Neo4j:
    echo.
    echo 方式 1: 使用 Neo4j Desktop
    echo   1. 打开 Neo4j Desktop 应用
    echo   2. 选择或创建数据库实例
    echo   3. 点击 "Start" 按钮启动数据库
    echo.
    echo 方式 2: 使用 Docker
    echo   docker run -d ^
    echo     --name neo4j ^
    echo     -p 7474:7474 -p 7687:7687 ^
    echo     -e NEO4J_AUTH=neo4j/password ^
    echo     neo4j:latest
    echo.
    echo 方式 3: 安装 Neo4j Community Edition
    echo   下载地址: https://neo4j.com/download/
    echo.
    pause
    exit /b 1
)

echo [检查] Neo4j 安装路径...
where neo4j

echo.
echo [启动] 正在启动 Neo4j 数据库...
echo.
echo ========================================
echo   Neo4j 控制台模式
echo ========================================
echo.
echo   访问地址: http://localhost:7474
echo   Bolt 端口: 7687
echo   默认用户: neo4j
echo   默认密码: neo4j (首次登录需修改)
echo.
echo ========================================
echo.

REM 启动 Neo4j
neo4j console

pause
