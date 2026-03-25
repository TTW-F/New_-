@echo off
chcp 65001 >nul
echo ========================================
echo 测试历史记录功能
echo ========================================
echo.

echo 请确保后端服务已启动...
echo.

set /p TOKEN="请输入你的 JWT Token: "
echo.

echo [1] 测试获取会话列表
echo ----------------------------------------
curl -X GET "http://localhost:8000/api/v1/history/sessions?page=1&page_size=10" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json"
echo.
echo.

echo [2] 测试获取对话历史
echo ----------------------------------------
curl -X GET "http://localhost:8000/api/v1/history?page=1&page_size=20" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json"
echo.
echo.

echo [3] 测试获取用户统计
echo ----------------------------------------
curl -X GET "http://localhost:8000/api/v1/history/stats" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json"
echo.
echo.

echo ========================================
echo 测试完成
echo ========================================
pause
