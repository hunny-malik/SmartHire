# SmartHire Windows Local Dev Runner
$Host.UI.RawUI.WindowTitle = "SmartHire Development Services"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "             STARTING SMART HIRE SERVICES                " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$CurrentDir = Split-Path -Parent $PSScriptRoot
$BackendDir = Join-Path $CurrentDir "backend"
$FrontendDir = Join-Path $CurrentDir "frontend"

Write-Host "`n[1/2] Starting SmartHire FastAPI Backend (Port 8000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$BackendDir'; python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"

Write-Host "[2/2] Starting SmartHire React Frontend (Port 5173)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$FrontendDir'; npm run dev"

Write-Host "`nBoth services launched!" -ForegroundColor Yellow
Write-Host "  Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "  Backend API: http://localhost:8000/api" -ForegroundColor White
Write-Host "  Swagger Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Cyan
