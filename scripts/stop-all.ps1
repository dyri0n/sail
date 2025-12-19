# =============================================================================
# SCRIPT MAESTRO - DETENER TODA LA INFRAESTRUCTURA
# =============================================================================
# Ejecutar desde la raíz del proyecto: .\scripts\stop-all.ps1
# =============================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Deteniendo Infraestructura Completa" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Continue"
$ROOT_DIR = Split-Path -Parent $PSScriptRoot

# -----------------------------------------------------------------------------
# 1. Airflow (detener primero para liberar conexiones)
# -----------------------------------------------------------------------------
Write-Host "[1/3] Deteniendo Airflow..." -ForegroundColor Yellow
Set-Location (Join-Path $ROOT_DIR "etl-node\airflow")
& .\scripts\compose-down.ps1

# -----------------------------------------------------------------------------
# 2. Staging Database (ambos modos si están activos)
# -----------------------------------------------------------------------------
Write-Host "`n[2/3] Deteniendo Staging Database..." -ForegroundColor Yellow
Set-Location (Join-Path $ROOT_DIR "stg-node")
& .\scripts\compose-down.ps1

# -----------------------------------------------------------------------------
# 3. Data Warehouse
# -----------------------------------------------------------------------------
Write-Host "`n[3/3] Deteniendo Data Warehouse..." -ForegroundColor Yellow
Set-Location (Join-Path $ROOT_DIR "dwh-node")
& .\scripts\compose-down.ps1

# -----------------------------------------------------------------------------
# Resumen
# -----------------------------------------------------------------------------
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " Infraestructura Detenida!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $ROOT_DIR
