# =============================================================================
# SCRIPT MAESTRO - LEVANTAR TODA LA INFRAESTRUCTURA
# =============================================================================
# Ejecutar desde la raíz del proyecto: .\scripts\start-all.ps1
# =============================================================================

# -----------------------------------------------------------------------------
# CONFIGURACIÓN: Elige el modo de Staging
# -----------------------------------------------------------------------------
# Opciones: "STG-PROD" (sin datos) o "STG-TEST" (con datos de prueba)
$STG_MODE = "STG-TEST"
# $STG_MODE = "STG-PROD"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Levantando Infraestructura Completa" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Modo Staging: $STG_MODE" -ForegroundColor Yellow
Write-Host ""

$ErrorActionPreference = "Stop"
$ROOT_DIR = Split-Path -Parent $PSScriptRoot

# -----------------------------------------------------------------------------
# 1. DWH Node (Data Warehouse)
# -----------------------------------------------------------------------------
Write-Host "[1/3] Levantando Data Warehouse (puerto 6000)..." -ForegroundColor Green
Set-Location (Join-Path $ROOT_DIR "dwh-node")
& .\scripts\compose-up.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Falló al levantar dwh-node" -ForegroundColor Red
    exit 1
}

# -----------------------------------------------------------------------------
# 2. STG Node (Staging Database)
# -----------------------------------------------------------------------------
Write-Host "`n[2/3] Levantando Staging Database..." -ForegroundColor Green
Set-Location (Join-Path $ROOT_DIR "stg-node")

if ($STG_MODE -eq "STG-TEST") {
    Write-Host "  -> Modo: Testing con datos de prueba (puerto 6002)" -ForegroundColor Gray
    & .\scripts\compose-up-test.ps1
} else {
    Write-Host "  -> Modo: Producción sin datos (puerto 6001)" -ForegroundColor Gray
    & .\scripts\compose-up-prod.ps1
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Falló al levantar stg-node" -ForegroundColor Red
    exit 1
}

# -----------------------------------------------------------------------------
# 3. ETL Node (Airflow)
# -----------------------------------------------------------------------------
Write-Host "`n[3/3] Levantando Airflow (puerto 8080)..." -ForegroundColor Green
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
  - Data Warehouse:  localhost:6000 (usuario: dwh_admin)
  - Staging $STG_MODE`:  localhost:$( if ($STG_MODE -eq "STG-TEST") { "6002" } else { "6001" } ) (usuario: stg_admin)
  - Airflow UI:      http://localhost:8080 (admin/admin)

Próximos pasos:
  1. Verifica que .env esté configurado correctamente en etl-node/airflow/
  2. Espera ~60s para que Airflow inicialice completamente
  3. Accede a http://localhost:8080 para ver los DAGs

"@ -ForegroundColor White

Set-Location $ROOT_DIR
