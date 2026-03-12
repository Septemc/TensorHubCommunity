$ErrorActionPreference = 'Stop'

if (-not (Test-Path '.env')) {
  Write-Host 'No backend/.env found; using environment variables or defaults.'
}

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
