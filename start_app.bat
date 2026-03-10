@echo off
echo ===================================================
echo       Starting OCR Batch Processing System (Debug Mode)
echo ===================================================

REM 设置 Node.js 和 Python 的路径，确保新窗口能找到它们
REM 请根据实际情况确认这些路径
set "NODE_PATH=C:\Program Files\nodejs"
set "PATH=%NODE_PATH%;%PATH%"

echo.
echo [1/4] Checking and Starting Database & Redis...
docker compose up -d db redis
if %errorlevel% neq 0 (
    echo [WARNING] Docker command failed. Please ensure Docker Desktop is running.
) else (
    echo [SUCCESS] Database and Redis containers command executed.
)

echo.
echo [2/4] Starting Backend API Server...
REM 使用 call 确保环境变量传递
start "OCR Backend" cmd /k "set PATH=%PATH% && cd backend && echo Starting Uvicorn... && uvicorn app.main:app --reload"

echo.
echo [3/4] Starting Celery Worker...
start "OCR Worker" cmd /k "set PATH=%PATH% && cd backend && echo Starting Celery... && celery -A app.core.celery_app worker --loglevel=info -P eventlet"

echo.
echo [4/4] Starting Frontend Dev Server...
start "OCR Frontend" cmd /k "set PATH=%PATH% && cd frontend && echo Starting Vite... && npm run dev"

echo.
echo ===================================================
echo       All services launch commands issued.
echo       Please check the popped-up windows for errors.
echo ===================================================
echo Backend API: http://localhost:8000
echo Frontend:    http://localhost:5173
echo.
pause
