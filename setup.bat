@echo off
REM ─────────────────────────────────────────────────────────
REM  Enterprise Knowledge Assistant — First-Time Setup
REM ─────────────────────────────────────────────────────────

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║      Enterprise Knowledge Assistant — Setup              ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

REM Step 1: Check .env
if not exist ".env" (
    echo [Step 1/4] Creating .env from template...
    copy .env.example .env
    echo.
    echo ⚠️  IMPORTANT: Open .env and add your OPENAI_API_KEY before continuing!
    echo    File location: %CD%\.env
    echo.
    pause
) else (
    echo [Step 1/4] .env already exists. ✓
)

REM Step 2: Create venv
if not exist "venv" (
    echo [Step 2/4] Creating virtual environment...
    python -m venv venv
    echo    Virtual environment created. ✓
) else (
    echo [Step 2/4] Virtual environment already exists. ✓
)

REM Step 3: Install deps
echo [Step 3/4] Installing dependencies (this may take a few minutes)...
call venv\Scripts\pip install -r requirements.txt
echo    Dependencies installed. ✓

REM Step 4: Seed users
echo [Step 4/4] Creating database and seeding default users...
call venv\Scripts\python scripts\seed_users.py
echo    Database seeded. ✓

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                  ✅ Setup Complete!                       ║
echo ║                                                          ║
echo ║  Now run: start.bat                                      ║
echo ║  Or manually:                                            ║
echo ║    Terminal 1: uvicorn app.api.main:app --reload         ║
echo ║    Terminal 2: streamlit run app\ui\streamlit_app.py     ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
pause
