# Data Preprocessing Platform - Setup Script for Windows
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Data Preprocessing Platform Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.9 or higher." -ForegroundColor Red
    Write-Host "Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Check Node.js installation
Write-Host "Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found. Please install Node.js 18 or higher." -ForegroundColor Red
    Write-Host "Download from: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setting up Backend" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Setup Backend
Set-Location -Path "backend"

Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Backend setup completed!" -ForegroundColor Green
} else {
    Write-Host "✗ Backend setup failed!" -ForegroundColor Red
    exit 1
}

Set-Location -Path ".."

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setting up Frontend" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Setup Frontend
Set-Location -Path "frontend"

Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
npm install

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Frontend setup completed!" -ForegroundColor Green
} else {
    Write-Host "✗ Frontend setup failed!" -ForegroundColor Red
    exit 1
}

Set-Location -Path ".."

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Start backend:  cd backend && venv\Scripts\Activate.ps1 && uvicorn app.main:app --reload" -ForegroundColor White
Write-Host "2. Start frontend: cd frontend && npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "Then open http://localhost:3000 in your browser" -ForegroundColor Yellow
Write-Host ""
