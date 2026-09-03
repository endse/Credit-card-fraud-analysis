<#
.SYNOPSIS
    FraudGuard AI - PowerShell Demo Launcher
.DESCRIPTION
    Starts both the FastAPI backend and React 19 frontend, then launches the browser.
#>

Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "                 FRAUDGUARD AI - LIVE DEMO LAUNCHER                          " -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Virtual Environment
if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "[!] Initializing Python environment with uv..." -ForegroundColor Yellow
    uv venv .venv --python 3.11
    uv pip install -r backend\requirements.txt
}

# 2. Check ML Model Artifacts
if (-not (Test-Path ".\backend\ml\artifacts\fraud_model.pkl")) {
    Write-Host "[*] Model artifact not found. Training machine learning models..." -ForegroundColor Yellow
    .\.venv\Scripts\python.exe backend\ml\train.py
}

# 3. Launch Backend in New Process
Write-Host "[*] Starting FastAPI Backend on http://127.0.0.1:8000 ..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& '.\.venv\Scripts\python.exe' -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000"

Start-Sleep -Seconds 3

# 4. Launch Frontend in New Process
Write-Host "[*] Starting React 19 Frontend on http://127.0.0.1:5173 ..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location frontend; npm run dev -- --port 5173 --host 127.0.0.1"

Start-Sleep -Seconds 2

# 5. Open Browser
Write-Host "[*] Opening Dashboard in browser..." -ForegroundColor Cyan
Start-Process "http://localhost:5173"

Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Green
Write-Host " [OK] FraudGuard AI is running!" -ForegroundColor Green
Write-Host " - Web Console:  http://localhost:5173" -ForegroundColor White
Write-Host " - REST Swagger: http://localhost:8000/docs" -ForegroundColor White
Write-Host " - Health Check: http://localhost:8000/api/health" -ForegroundColor White
Write-Host "==============================================================================" -ForegroundColor Green
