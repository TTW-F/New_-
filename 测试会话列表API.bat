@echo off
chcp 65001 >nul
echo ========================================
echo 测试会话列表API返回的数据格式
echo ========================================
echo.

set /p TOKEN="请输入你的 JWT Token: "
echo.

echo 调用 API: GET /api/v1/history/sessions?page=1^&page_size=5
echo ----------------------------------------
curl -X GET "http://localhost:8000/api/v1/history/sessions?page=1&page_size=5" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" | python -m json.tool

echo.
echo ========================================
echo 请检查返回的 updated_at 字段格式
echo 应该是 ISO 格式，例如: 2026-03-25T22:11:54.596000
echo ========================================
pause
