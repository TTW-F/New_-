@echo off
chcp 65001 >nul
echo ========================================
echo Neo4j知识图谱导入系统
echo ========================================
echo.

echo 激活虚拟环境...
call .venv\Scripts\activate.bat

echo.
echo 开始导入数据...
python demo_import.py

echo.
echo ========================================
pause
