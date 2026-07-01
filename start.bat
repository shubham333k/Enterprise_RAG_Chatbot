@echo off
REM ─────────────────────────────────────────────────────────
REM  Enterprise Knowledge Assistant — Quick Start Script
REM  Run this after initial setup (pip install + seed_users)
REM ─────────────────────────────────────────────────────────

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║     Enterprise Knowledge Assistant — Starting up         ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

REM Check .env exists
if not exist ".env" (
    echo [ERROR] .env file not found!
    echo Please copy .env.example to .env and add your OPENAI_API_KEY
    pause
    exit /b 1
)

REM Activate venv
call venv\Scripts\activate.bat

REM Start FastAPI in a new window
echo [1/2] Starting FastAPI backend on http://localhost:8000 ...
start "RAG API" cmd /k "venv\Scripts\uvicorn app.api.main:app --reload --port 8000"

REM Wait a moment for API to start
timeout /t 4 /nobreak > nul

REM Start Streamlit in a new window
echo [2/2] Starting Streamlit UI on http://localhost:8501 ...
start "RAG UI" cmd /k "venv\Scripts\streamlit run app\ui\streamlit_app.py"

echo.
echo ✅ Both services started in separate windows!
echo.
echo   API:     http://localhost:8000
echo   Swagger: http://localhost:8000/docs
echo   UI:      http://localhost:8501
echo.
echo Opening browser...
timeout /t 3 /nobreak > nul
start http://localhost:8501

pause
