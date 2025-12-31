# =============================================================================
# Script de Setup para frontend - Windows PowerShell
# =============================================================================
# Ejecutar desde la carpeta frontend_seil/scripts o desde la raíz con la ruta completa
# PowerShell: .\setup-frontend.ps1
# =============================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Setup frontend environment (SvelteKit)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$ErrorActionPreference = "Stop"

# Paths
$ScriptsDir = $PSScriptRoot
$FrontendRoot = Split-Path -Parent $PSScriptRoot
$PackageJson = Join-Path $FrontendRoot 'package.json'
$NodeModules = Join-Path $FrontendRoot 'node_modules'
$EnvExample = Join-Path $FrontendRoot '.env.example'
$EnvFile = Join-Path $FrontendRoot '.env'

# Validaciones
if (-not (Test-Path $PackageJson)) {
    Write-Host "ERROR: No se encontró 'package.json' en $FrontendRoot. Ejecuta este script desde 'frontend_seil/scripts' o revisa la estructura." -ForegroundColor Red
    exit 1
}

# Verificar Node.js
Write-Host "`n[1/4] Verificando Node.js..." -ForegroundColor Yellow
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Node.js no está instalado o no está en PATH." -ForegroundColor Red
    Write-Host "Instala Node.js desde: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

$nodeVersion = node --version
$nodeMajor = [int]($nodeVersion -replace 'v(\d+)\..*', '$1')
Write-Host "  -> Node.js encontrado: $nodeVersion" -ForegroundColor Green

# Verificar versión de Node compatible
if ($nodeMajor -lt 20 -or $nodeMajor -eq 21 -or $nodeMajor -eq 23) {
    Write-Host "WARNING: Este proyecto requiere Node.js v20, v22 o v24+." -ForegroundColor Yellow
    Write-Host "  Tu versión actual es: $nodeVersion" -ForegroundColor Yellow
    Write-Host "  Recomendación: Instala Node.js v20 LTS o v22 LTS desde https://nodejs.org/" -ForegroundColor Cyan
    Write-Host "`n  Puedes usar 'fnm' o 'nvm' para manejar múltiples versiones de Node." -ForegroundColor Gray
    Write-Host "  Continúa bajo tu propio riesgo..." -ForegroundColor Yellow
    Start-Sleep -Seconds 3
}

# Verificar npm
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: npm no está instalado o no está en PATH." -ForegroundColor Red
    exit 1
}

$npmVersion = npm --version
Write-Host "  -> npm encontrado: v$npmVersion" -ForegroundColor Green

# 2. Crear .env si no existe
Write-Host "`n[2/4] Configurando archivo .env..." -ForegroundColor Yellow
if (Test-Path $EnvFile) {
    Write-Host "  -> Archivo .env ya existe, saltando..." -ForegroundColor Gray
} else {
    if (Test-Path $EnvExample) {
        Copy-Item $EnvExample $EnvFile
        Write-Host "  -> Archivo .env creado desde .env.example" -ForegroundColor Green
    } else {
        Write-Host "  -> Archivo .env.example no encontrado, creando .env básico..." -ForegroundColor Yellow
        "PUBLIC_API_BASE_URL=http://localhost:8000" | Out-File -FilePath $EnvFile -Encoding utf8
        Write-Host "  -> Archivo .env creado" -ForegroundColor Green
    }
}

# 3. Instalar dependencias
Write-Host "`n[3/4] Instalando dependencias con npm..." -ForegroundColor Yellow
Push-Location $FrontendRoot
try {
    $installResult = npm install 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Fallo al instalar dependencias (código de salida: $LASTEXITCODE)" -ForegroundColor Red
        Write-Host $installResult -ForegroundColor Red
        Pop-Location
        exit 1
    }
    Write-Host "  -> Dependencias instaladas correctamente" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Fallo al instalar dependencias" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location

# 4. Crear carpeta de logs si no existe (para consistencia con backend)
Write-Host "`n[4/4] Creando carpetas útiles si faltan..." -ForegroundColor Yellow
$Logs = Join-Path $FrontendRoot 'logs'
if (-not (Test-Path $Logs)) {
    New-Item -ItemType Directory -Path $Logs | Out-Null
    Write-Host "  -> Carpeta de logs creada: $Logs" -ForegroundColor Green
} else {
    Write-Host "  -> Carpeta de logs ya existe: $Logs" -ForegroundColor Gray
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " Setup frontend completado!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host @"
Próximos pasos:
  1. Para arrancar el dev server: .\start-frontend.ps1
  2. La app estará disponible en: http://localhost:5173
  3. Para detener: .\stop-frontend.ps1
"@ -ForegroundColor White
