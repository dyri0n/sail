# =============================================================================
# Script de Setup para backend - Windows PowerShell (usa "uv")
# =============================================================================
# Ejecutar desde la carpeta backend_seil/scripts o desde la raíz con la ruta completa
# PowerShell: .\setup-backend.ps1
# =============================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Setup backend environment (uv)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$ErrorActionPreference = "Stop"

# Paths
$ScriptsDir = $PSScriptRoot
$BackendRoot = Split-Path -Parent $PSScriptRoot    # backend_seil
$BackendDir = Join-Path $BackendRoot 'app'
$VenvDir = Join-Path $BackendDir '.venv'
$Requirements = Join-Path $BackendDir 'requirements.txt'

# Validaciones
if (-not (Test-Path $Requirements)) {
    Write-Host "ERROR: No se encontró 'requirements.txt' en $BackendDir. Ejecuta este script desde 'backend_seil/scripts' o revisa la estructura." -ForegroundColor Red
    exit 1
}

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: 'uv' no está instalado o no está en PATH." -ForegroundColor Red
    Write-Host "Instálalo siguiendo: https://docs.astral.sh/uv/" -ForegroundColor Yellow
    exit 1
}

# 1. Crear entorno virtual si no existe
Write-Host "`n[1/3] Creando entorno virtual Python con uv (si no existe)..." -ForegroundColor Yellow
if (Test-Path $VenvDir) {
    Write-Host "  -> Entorno virtual ya existe en $VenvDir, saltando..." -ForegroundColor Gray
} else {
    Push-Location $BackendDir
    uv venv .venv --python 3.11
    Pop-Location
    Write-Host "  -> Entorno virtual creado en $VenvDir" -ForegroundColor Green
}

# 2. Activar e instalar dependencias
Write-Host "`n[2/3] Instalando dependencias..." -ForegroundColor Yellow
& "$VenvDir\Scripts\Activate.ps1"
# Usamos uv pip para asegurarnos de usar el pip del entorno
Push-Location $BackendDir
uv pip install -r requirements.txt -q
Pop-Location
Write-Host "  -> Dependencias instaladas correctamente" -ForegroundColor Green

# 3. Crear carpeta de logs si no existe
Write-Host "`n[3/3] Creando carpetas útiles si faltan..." -ForegroundColor Yellow
$Logs = Join-Path $BackendRoot 'logs'
if (-not (Test-Path $Logs)) {
    New-Item -ItemType Directory -Path $Logs | Out-Null
    Write-Host "  -> Carpeta de logs creada: $Logs" -ForegroundColor Green
} else {
    Write-Host "  -> Carpeta de logs ya existe: $Logs" -ForegroundColor Gray
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " Setup backend completado!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host @"
Próximos pasos:
  1. Selecciona el intérprete Python: .venv\Scripts\python.exe
  2. Para arrancar la app: .\start-backend.ps1
  3. Para la BD: .\start-db.ps1 (usa docker compose en backend_seil/docker/postgres)
"@ -ForegroundColor White
