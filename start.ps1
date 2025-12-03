# Windows PowerShell script to start both backend and frontend
param(
    [switch]$Backend,
    [switch]$Frontend,
    [switch]$Both
)

function Start-Backend {
    Write-Host "Starting Backend Server..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .\venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
}

function Start-Frontend {
    Write-Host "Starting Frontend Server..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"
}

if ($Backend) {
    Start-Backend
}
elseif ($Frontend) {
    Start-Frontend
}
elseif ($Both -or (!$Backend -and !$Frontend)) {
    Write-Host "Starting Data Preprocessing Platform..." -ForegroundColor Green
    Start-Backend
    Start-Sleep -Seconds 2
    Start-Frontend
    Write-Host ""
    Write-Host "Servers are starting in separate windows..." -ForegroundColor Yellow
    Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Press Ctrl+C in each window to stop the servers" -ForegroundColor Yellow
}
