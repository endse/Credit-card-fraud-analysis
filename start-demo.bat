@echo off
TITLE FraudGuard AI - Live Demo Launcher
echo ==============================================================================
echo                 FRAUDGUARD AI - LIVE DEMO LAUNCHER
echo ==============================================================================
echo.

REM Verify Python environment
if not exist ".venv\Scripts\python.exe" (
    echo [!] Python virtual environment not found. Setting up with uv...
    call uv venv .venv --python 3.11
    call uv pip install -r backend\requirements.txt
)

REM Verify model artifact exists
if not exist "backend\ml\artifacts\fraud_model.pkl" (
    echo [*] Training machine learning models...
    call .\.venv\Scripts\python.exe backend\ml\train.py
)

REM Start Backend API
echo [*] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "FraudGuard Backend (FastAPI)" cmd /k ".\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000"

REM Wait for backend to initialize
timeout /t 3 /nobreak >nul

REM Start Frontend Dev Server
echo [*] Starting React 19 Frontend on http://127.0.0.1:5173 ...
cd frontend
start "FraudGuard Frontend (Vite)" cmd /k "npm run dev -- --port 5173 --host 127.0.0.1"
cd ..

REM Wait and open browser
timeout /t 2 /nobreak >nul
echo [*] Opening Dashboard in default browser...
start http://localhost:5173

echo.
echo ==============================================================================
echo  [OK] FraudGuard AI is running!
echo  - Web Dashboard: http://localhost:5173
echo  - API Docs:      http://localhost:8000/docs
echo  - Health Check:  http://localhost:8000/api/health
echo ==============================================================================
echo.
pause
