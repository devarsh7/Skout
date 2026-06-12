@echo off
REM Kills anything holding port 8000, then starts FastAPI fresh with reload.
cd /d "%~dp0.."

echo Killing any process on port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo   killing PID %%a
    taskkill /F /PID %%a >nul 2>&1
)

if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

echo Starting FastAPI on :8000 ...
uvicorn backend.main:app --reload --port 8000
