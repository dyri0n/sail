# =============================================================================
# SCRIPT MAESTRO - LEVANTAR TODA LA INFRAESTRUCTURA
# =============================================================================
# Ejecutar desde la raíz del proyecto: .\scripts\start-all.ps1
# =============================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Levantando Infraestructura Completa" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"
$ROOT_DIR = Split-Path -Parent $PSScriptRoot

# -----------------------------------------------------------------------------
# 1. DWH Node (Data Warehouse + Staging)
# -----------------------------------------------------------------------------
Write-Host "[1/2] Levantando Data Warehouse (puerto 6000)..." -ForegroundColor Green
Set-Location (Join-Path $ROOT_DIR "dwh-node")
& .\scripts\compose-up.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Falló al levantar dwh-node" -ForegroundColor Red
    exit 1
}

# -----------------------------------------------------------------------------
# 2. ETL Node (Airflow)
# -----------------------------------------------------------------------------
Write-Host "`n[2/2] Levantando Airflow (puerto 8080)..." -ForegroundColor Green
Set-Location (Join-Path $ROOT_DIR "etl-node\airflow")
& .\scripts\compose-up.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Falló al levantar airflow" -ForegroundColor Red
    exit 1
}

# -----------------------------------------------------------------------------
# Resumen
# -----------------------------------------------------------------------------
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " Infraestructura Levantada!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host @"

Servicios disponibles:
  - Data Warehouse:  localhost:6000 (usuario: dwh_admin, schemas: stg y dwh)
  - Airflow UI:      http://localhost:8080 (admin/admin)

Próximos pasos:
  1. Verifica que .env esté configurado correctamente en etl-node/airflow/
  2. Espera ~60s para que Airflow inicialice completamente
  3. Accede a http://localhost:8080 para ver los DAGs

"@ -ForegroundColor White

Set-Location $ROOT_DIR
