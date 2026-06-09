$ErrorActionPreference = "Stop"

Write-Host "CivilConnect - démarrage local (PostgreSQL + Vite)" -ForegroundColor Cyan

# ====== CONFIG POSTGRES LOCAL ======
# Adapter si besoin
$env:DJANGO_USE_SQLITE = "0"
$env:DEMO_SKIP_MFA = "1"
$env:DEMO_MFA_BYPASS_CODE = "888888"
$env:DATABASE_URL = "postgresql://postgres:Prince2018@127.0.0.1:5432/Projet%20DUT"
$env:POSTGRES_HOST = "127.0.0.1"   # fallback si DATABASE_URL absent
$env:POSTGRES_PORT = "5432"
$env:POSTGRES_DB = "Projet DUT"
$env:POSTGRES_USER = "postgres"
$env:POSTGRES_PASSWORD = "Prince2018"

# Frontend -> backend local
$env:VITE_API_URL = "http://127.0.0.1:8000"

$backendCmd = @"
`$env:DJANGO_USE_SQLITE='0';
`$env:DEMO_SKIP_MFA='1';
`$env:DEMO_MFA_BYPASS_CODE='888888';
`$env:DATABASE_URL='postgresql://postgres:Prince2018@127.0.0.1:5432/Projet%20DUT';
Set-Location 'E:\Projet Dut\backend_django';
python manage.py migrate;
python create_default_login.py;
python manage.py runserver 127.0.0.1:8000
"@

Start-Process powershell -ArgumentList @("-NoProfile", "-Command", $backendCmd)

Start-Process powershell -ArgumentList @(
  "-NoProfile",
  "-Command",
  "Set-Location 'E:\\Projet Dut\\frontend'; npm run dev -- --host 127.0.0.1 --port 5174"
)

Start-Sleep -Seconds 2
Start-Process "http://127.0.0.1:5174/"
Start-Process "http://127.0.0.1:8000/api/docs/"

Write-Host "Ouvert: UI + Swagger" -ForegroundColor Green

