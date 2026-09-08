@echo off
chcp 65001 > nul
echo ====================================================================
echo 🚀 Запуск UCust AI Unified Service Gateway (v2.5.0)
echo ====================================================================
echo.
cd /d "%~dp0ai"

set PYTHONIOENCODING=utf-8
set AI_SERVICE_HOST=0.0.0.0
set AI_SERVICE_PORT=8000

echo [1/2] Проверка окружения Python...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Ошибка: Python не найден в PATH.
    pause
    exit /b 1
)

echo [2/2] Запуск Uvicorn шлюза на http://0.0.0.0:8000 ...
echo Swagger UI документация доступна по адресу: http://localhost:8000/docs
echo Единый шлюз оркестратора: POST http://localhost:8000/api/v1/orchestrator/execute
echo.
python api_gateway.py

pause
