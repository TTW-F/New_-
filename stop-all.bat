@echo off
chcp 65001 >nul
title Medical QA System - Shutdown

echo.
echo ========================================================
echo        医疗智能问答系统 - 停止所有服务
echo ========================================================
echo.

echo [1/3] 停止后端服务 (Python/Uvicorn)...
taskkill /F /FI "WINDOWTITLE eq 医疗问答系统-后端*" >nul 2>&1
if errorlevel 1 (
    echo [提示] 未找到运行中的后端服务
) else (
    echo [成功] 后端服务已停止
)

echo.
echo [2/3] 停止前端服务 (Node.js/Vite)...
taskkill /F /FI "WINDOWTITLE eq 医疗问答系统-前端*" >nul 2>&1
if errorlevel 1 (
    echo [提示] 未找到运行中的前端服务
) else (
    echo [成功] 前端服务已停止
)

echo.
echo [3/3] 停止 Neo4j 数据库...
taskkill /F /FI "WINDOWTITLE eq Neo4j Database*" >nul 2>&1
if errorlevel 1 (
    echo [提示] 未找到由脚本启动的 Neo4j 服务
    echo [提示] 如果使用 Neo4j Desktop，请手动停止
) else (
    echo [成功] Neo4j 数据库已停止
)

echo.
echo ========================================================
echo   所有服务已停止
echo ========================================================
echo.
echo 注意: MySQL 和 Redis 服务未停止
echo 如需停止这些服务，请手动执行:
echo   - MySQL: net stop MySQL80
echo   - Redis: docker stop redis-medical-qa
echo.
pause
