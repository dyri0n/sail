# =============================================================================
# Script de Setup para Desarrollo Local - Windows PowerShell
# =============================================================================
# Ejecutar desde la carpeta airflow/
# PowerShell: .\scripts\setup-dev.ps1
# =============================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Setup de Entorno de Desarrollo Local" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$ErrorActionPreference = "Stop"

# Verificar que estamos en la carpeta correcta
if (-not (Test-Path ".\docker-compose.yaml")) {
    Write-Host "ERROR: Ejecuta este script desde la carpeta 'airflow/'" -ForegroundColor Red
    exit 1
}

# Verificar que 'uv' esté instalado
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Necesitas instalar 'uv' antes de continuar." -ForegroundColor Red
    Write-Host "Instálalo siguiendo: https://docs.astral.sh/uv/" -ForegroundColor Yellow
    exit 1
}

# 1. Crear entorno virtual
Write-Host "`n[1/4] Creando entorno virtual Python..." -ForegroundColor Yellow
if (Test-Path ".\.venv") {
    Write-Host "  -> Entorno virtual ya existe, saltando..." -ForegroundColor Gray
} else {
    uv venv .venv --python 3.13
    Write-Host "  -> Entorno virtual creado en .venv/ (uv venv)" -ForegroundColor Green
}

# 2. Activar e instalar dependencias
Write-Host "`n[2/4] Instalando dependencias para desarrollo..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1
uv pip install -r requirements-dev.txt -q
Write-Host "  -> Dependencias instaladas correctamente" -ForegroundColor Green

# 3. Copiar .env si no existe
Write-Host "`n[3/4] Configurando variables de entorno..." -ForegroundColor Yellow
if (-not (Test-Path ".\.env")) {
    Copy-Item ".\.env.example" ".\.env"
    Write-Host "  -> Archivo .env creado desde .env.example" -ForegroundColor Green
    Write-Host "  -> IMPORTANTE: Revisa y ajusta los valores en .env" -ForegroundColor Magenta
} else {
    Write-Host "  -> Archivo .env ya existe" -ForegroundColor Gray
}

# 4. Crear carpeta de logs si no existe
Write-Host "`n[4/4] Creando estructura de carpetas..." -ForegroundColor Yellow
if (-not (Test-Path ".\logs")) {
    New-Item -ItemType Directory -Path ".\logs" | Out-Null
}
if (-not (Test-Path ".\test_data")) {
    New-Item -ItemType Directory -Path ".\test_data" | Out-Null
}
Write-Host "  -> Carpetas creadas" -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " Setup Completado!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host @"

Próximos pasos:
  1. Abre VS Code en esta carpeta
  2. Selecciona el intérprete Python: .venv\Scripts\python.exe
  3. Los errores de lint deberían desaparecer

Para levantar Airflow en modo testing:
  docker-compose --profile testing up -d

Para ver la UI de Airflow:
  http://localhost:8080 (admin/admin)

"@ -ForegroundColor White
