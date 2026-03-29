@echo off
chcp 65001 >nul
echo ========================================
echo 测试 Neo4j 数据库
echo ========================================
echo.

call .venv\Scripts\activate && python 测试Neo4j数据.py

echo.
pause
