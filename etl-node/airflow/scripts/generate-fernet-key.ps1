# Script para generar una clave Fernet para Airflow
# Uso: .\generate-fernet-key.ps1

Write-Host "Generando clave Fernet para Airflow..." -ForegroundColor Cyan

$fernetKey = python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Clave Fernet generada:" -ForegroundColor Green
    Write-Host $fernetKey -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Agrégala a tu archivo .env como:" -ForegroundColor Cyan
    Write-Host "AIRFLOW_FERNET_KEY=$fernetKey" -ForegroundColor White
} else {
    Write-Host "Error: Asegúrate de tener Python y cryptography instalados" -ForegroundColor Red
    Write-Host "Instala con: pip install cryptography" -ForegroundColor Yellow
}
