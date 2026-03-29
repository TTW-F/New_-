@echo off
chcp 65001 >nul
echo ========================================
echo 医疗数据预处理系统
echo ========================================
echo.

echo 激活虚拟环境...
call .venv\Scripts\activate.bat

echo.
echo 开始预处理数据...
python demo_preprocess.py

echo.
echo ========================================
pause
