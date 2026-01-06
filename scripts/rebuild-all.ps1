# =============================================================================
# SCRIPT DE RECONSTRUCCIÓN - REBUILD FROM SCRATCH
# =============================================================================
# Ejecutar desde la raíz del proyecto: .\scripts\rebuild-all.ps1
# =============================================================================
# ADVERTENCIA: Este script puede eliminar datos de PostgreSQL
# =============================================================================

Write-Host "========================================" -ForegroundColor Yellow
Write-Host " REBUILD - SIN CACHE" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "Selecciona qué componentes reconstruir:" -ForegroundColor Cyan
Write-Host "  [1] Todo (DWH Node + ETL Node)" -ForegroundColor White
Write-Host "  [2] Solo DWH Node (Data Warehouse + PostgreSQL)" -ForegroundColor White
Write-Host "  [3] Solo ETL Node (Airflow)" -ForegroundColor White
Write-Host "  [0] Cancelar" -ForegroundColor White
Write-Host ""

$option = Read-Host "Opción"

switch ($option) {
    "1" { $buildDWH = $true; $buildETL = $true }
    "2" { $buildDWH = $true; $buildETL = $false }
    "3" { $buildDWH = $false; $buildETL = $true }
    "0" { 
        Write-Host "Operación cancelada." -ForegroundColor Yellow
        exit 0
    }
    default {
        Write-Host "Opción inválida. Operación cancelada." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "ADVERTENCIA: Este script:" -ForegroundColor Red
Write-Host "  - Detendrá los contenedores seleccionados" -ForegroundColor Red
if ($buildDWH) {
    Write-Host "  - Eliminará TODOS los datos de PostgreSQL (dwh-node/data)" -ForegroundColor Red
}
Write-Host "  - Reconstruirá las imágenes seleccionadas sin cache" -ForegroundColor Red
Write-Host ""

$confirmation = Read-Host "¿Estás seguro de continuar? (escribe 'SI' para confirmar)"
if ($confirmation -ne "SI") {
    Write-Host "Operación cancelada." -ForegroundColor Yellow
    exit 0
}

$ErrorActionPreference = "Stop"
$ROOT_DIR = Split-Path -Parent $PSScriptRoot

# -----------------------------------------------------------------------------
# 1. Detener infraestructura
# -----------------------------------------------------------------------------
Write-Host "`n[1/4] Deteniendo infraestructura..." -ForegroundColor Green
Set-Location $ROOT_DIR

if ($buildDWH -and $buildETL) {
    & .\scripts\stop-all.ps1
} elseif ($buildDWH) {
    Set-Location (Join-Path $ROOT_DIR "dwh-node")
    & .\scripts\compose-down.ps1
    Set-Location $ROOT_DIR
} elseif ($buildETL) {
    Set-Location (Join-Path $ROOT_DIR "etl-node\airflow")
    & .\scripts\compose-down.ps1
    Set-Location $ROOT_DIR
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Algunos servicios no se pudieron detener correctamente" -ForegroundColor Yellow
}

# -----------------------------------------------------------------------------
# 2. Eliminar datos de PostgreSQL (solo si se reconstruye DWH)
# -----------------------------------------------------------------------------
if ($buildDWH) {
    Write-Host "`n[2/4] Eliminando datos de PostgreSQL..." -ForegroundColor Green
    $DATA_PATH = Join-Path $ROOT_DIR "dwh-node\data"
    if (Test-Path $DATA_PATH) {
        Write-Host "  Eliminando: $DATA_PATH" -ForegroundColor Yellow
        Remove-Item -Recurse -Force $DATA_PATH
        Write-Host "  ✓ Datos eliminados" -ForegroundColor Green
    } else {
        Write-Host "  ℹ No se encontró carpeta de datos" -ForegroundColor Cyan
    }
} else {
    Write-Host "`n[2/4] Saltando eliminación de datos PostgreSQL..." -ForegroundColor Cyan
}

# -----------------------------------------------------------------------------
# 3. Rebuild DWH Node (con --build --no-cache)
# -----------------------------------------------------------------------------
if ($buildDWH) {
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
} else {
    Write-Host "`n[3/4] Saltando rebuild de DWH Node..." -ForegroundColor Cyan
}

# -----------------------------------------------------------------------------
# 4. Rebuild ETL Node / Airflow (con --build --no-cache)
# -----------------------------------------------------------------------------
if ($buildETL) {
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
} else {
    Write-Host "`n[4/4] Saltando rebuild de ETL Node..." -ForegroundColor Cyan
}

# -----------------------------------------------------------------------------
# Resumen
# -----------------------------------------------------------------------------
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " Rebuild Exitoso!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

$summary = "`n✓ Servicios reconstruidos y levantados:`n"
if ($buildDWH) {
    $summary += "  - Data Warehouse:  localhost:6000 (usuario: dwh_admin, schemas: stg y dwh)`n"
}
if ($buildETL) {
    $summary += "  - Airflow UI:      http://localhost:8080 (admin/admin)`n"
}
$summary += "`n⚠ IMPORTANTE:`n"
if ($buildDWH) {
    $summary += "  - La base de datos PostgreSQL se recreó desde cero`n"
    $summary += "  - Se aplicaron los scripts de inicialización (schemas + permisos)`n"
    $summary += "  - Los datos de staging/dwh están vacíos - necesitarás ejecutar los DAGs`n"
}
if ($buildETL) {
    $summary += "  - Espera ~60s para que Airflow inicialice completamente`n"
}

Write-Host $summary -ForegroundColor White

Set-Location $ROOT_DIR
