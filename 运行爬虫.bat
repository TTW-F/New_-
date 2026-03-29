@echo off
chcp 65001 >nul
echo ========================================
echo 医疗知识图谱数据采集系统
echo ========================================
echo.

echo 激活虚拟环境...
call .venv\Scripts\activate.bat

echo.
echo 开始采集数据...
python demo_spider.py

echo.
echo ========================================
pause
