$ErrorActionPreference = "Stop"

Write-Host "CivilConnect - MODE PRESENTATION (SQLite + Vite)" -ForegroundColor Cyan

# Backend en SQLite (évite Postgres/Docker)
$env:DJANGO_USE_SQLITE = "1"
$env:DEMO_SKIP_MFA = "1"
# Si tu passes DEMO_SKIP_MFA à 0 pour tester l’écran MFA, tu peux saisir ce code à la place du TOTP :
$env:DEMO_MFA_BYPASS_CODE = "888888"

$backendCmd = @"
`$env:DJANGO_USE_SQLITE='1';
`$env:DEMO_SKIP_MFA='1';
`$env:DEMO_MFA_BYPASS_CODE='888888';
Set-Location 'E:\Projet Dut\backend_django';
python manage.py migrate;
python create_default_login.py;
python manage.py runserver 127.0.0.1:8000
"@

Start-Process powershell -ArgumentList @("-NoProfile", "-Command", $backendCmd)

Start-Process powershell -ArgumentList @(
  "-NoProfile",
  "-Command",
  "cd `\"E:\Projet Dut\frontend`\"; npm run dev -- --host 127.0.0.1 --port 5174"
)

Start-Sleep -Seconds 2
Start-Process "http://127.0.0.1:5174/"
Start-Process "http://127.0.0.1:8000/api/docs/"

Write-Host "Ouvre UI: http://127.0.0.1:5174/  | Swagger: http://127.0.0.1:8000/api/docs/" -ForegroundColor Green

