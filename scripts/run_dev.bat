@echo off
REM Dev runner for Windows.
REM Launches FastAPI in a new window, then Streamlit in the current one.

cd /d "%~dp0.."

if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

echo 🚀 Starting FastAPI on :8000
start "Skout API" cmd /k "uvicorn backend.main:app --reload --port 8000"

timeout /t 3 /nobreak >nul

echo 🎨 Starting Streamlit on :8501
set PYTHONPATH=%CD%
streamlit run frontend\streamlit_app.py
