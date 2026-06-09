$ErrorActionPreference = "Stop"

Write-Host "CivilConnect - démarrage local (SQLite + Vite)" -ForegroundColor Cyan

# Backend
Start-Process powershell -ArgumentList @(
  "-NoProfile",
  "-Command",
  "cd `\"E:\Projet Dut\backend_django`\"; python manage.py migrate; python manage.py runserver 127.0.0.1:8000"
)

# Frontend (port fixe pour éviter le fallback silencieux)
Start-Process powershell -ArgumentList @(
  "-NoProfile",
  "-Command",
  "cd `\"E:\Projet Dut\frontend`\"; npm run dev -- --host 127.0.0.1 --port 5174"
)

Start-Sleep -Seconds 2
Start-Process "http://127.0.0.1:5174/"
Start-Process "http://127.0.0.1:8000/api/docs/"

Write-Host "Ouvert: UI + Swagger" -ForegroundColor Green

