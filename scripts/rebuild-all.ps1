# =============================================================================
# SCRIPT DE RECONSTRUCCIÓN COMPLETA - REBUILD FROM SCRATCH
# =============================================================================
# Ejecutar desde la raíz del proyecto: .\scripts\rebuild-all.ps1
# =============================================================================
# ADVERTENCIA: Este script eliminará TODOS los datos de PostgreSQL
# =============================================================================

Write-Host "========================================" -ForegroundColor Yellow
Write-Host " REBUILD COMPLETO - SIN CACHE" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "ADVERTENCIA: Este script:" -ForegroundColor Red
Write-Host "  - Detendrá todos los contenedores" -ForegroundColor Red
Write-Host "  - Eliminará TODOS los datos de PostgreSQL (dwh-node/data)" -ForegroundColor Red
Write-Host "  - Reconstruirá todas las imágenes sin cache" -ForegroundColor Red
Write-Host ""

$confirmation = Read-Host "¿Estás seguro de continuar? (escribe 'SI' para confirmar)"
if ($confirmation -ne "SI") {
    Write-Host "Operación cancelada." -ForegroundColor Yellow
    exit 0
}

$ErrorActionPreference = "Stop"
$ROOT_DIR = Split-Path -Parent $PSScriptRoot

# -----------------------------------------------------------------------------
# 1. Detener toda la infraestructura
# -----------------------------------------------------------------------------
Write-Host "`n[1/4] Deteniendo toda la infraestructura..." -ForegroundColor Green
Set-Location $ROOT_DIR
& .\scripts\stop-all.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Algunos servicios no se pudieron detener correctamente" -ForegroundColor Yellow
}

# -----------------------------------------------------------------------------
# 2. Eliminar datos de PostgreSQL
# -----------------------------------------------------------------------------
Write-Host "`n[2/4] Eliminando datos de PostgreSQL..." -ForegroundColor Green
$DATA_PATH = Join-Path $ROOT_DIR "dwh-node\data"
if (Test-Path $DATA_PATH) {
    Write-Host "  Eliminando: $DATA_PATH" -ForegroundColor Yellow
    Remove-Item -Recurse -Force $DATA_PATH
    Write-Host "  ✓ Datos eliminados" -ForegroundColor Green
} else {
    Write-Host "  ℹ No se encontró carpeta de datos" -ForegroundColor Cyan
}

# -----------------------------------------------------------------------------
# 3. Rebuild DWH Node (con --build --no-cache)
# -----------------------------------------------------------------------------
Write-Host "`n[3/4] Reconstruyendo Data Warehouse (sin cache)..." -ForegroundColor Green
Set-Location (Join-Path $ROOT_DIR "dwh-node")
Write-Host "  Ejecutando: docker compose build --no-cache" -ForegroundColor Cyan
docker compose build --no-cache
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Falló al reconstruir dwh-node" -ForegroundColor Red
    exit 1
}
Write-Host "  Levantando servicios..." -ForegroundColor Cyan
& .\scripts\compose-up.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Falló al levantar dwh-node" -ForegroundColor Red
    exit 1
}

# -----------------------------------------------------------------------------
# 4. Rebuild ETL Node / Airflow (con --build --no-cache)
# -----------------------------------------------------------------------------
Write-Host "`n[4/4] Reconstruyendo Airflow (sin cache)..." -ForegroundColor Green
Set-Location (Join-Path $ROOT_DIR "etl-node\airflow")
Write-Host "  Ejecutando: docker compose build --no-cache" -ForegroundColor Cyan
docker compose build --no-cache
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Falló al reconstruir airflow" -ForegroundColor Red
    exit 1
}
Write-Host "  Levantando servicios..." -ForegroundColor Cyan
& .\scripts\compose-up.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Falló al levantar airflow" -ForegroundColor Red
    exit 1
}

# -----------------------------------------------------------------------------
# Resumen
# -----------------------------------------------------------------------------
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " Rebuild Completo Exitoso!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host @"

✓ Servicios reconstruidos y levantados:
  - Data Warehouse:  localhost:6000 (usuario: dwh_admin, schemas: stg y dwh)
  - Airflow UI:      http://localhost:8080 (admin/admin)

⚠ IMPORTANTE:
  1. La base de datos PostgreSQL se recreó desde cero
  2. Se aplicaron los scripts de inicialización (schemas + permisos)
  3. Espera ~60s para que Airflow inicialice completamente
  4. Los datos de staging/dwh están vacíos - necesitarás ejecutar los DAGs

"@ -ForegroundColor White

Set-Location $ROOT_DIR
