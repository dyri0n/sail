param(
    [switch]$Help
)

if ($Help) {
    Write-Host "Uso: .\start-frontend.ps1" -ForegroundColor Yellow
    return
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$frontendRoot = Split-Path -Parent $scriptDir
$pidFile = Join-Path $scriptDir 'frontend.pid'
$logsDir = Join-Path $frontendRoot 'logs'
$logFile = Join-Path $logsDir 'frontend.log'
$errorFile = Join-Path $logsDir 'frontend.error.log'

# Verificar Node.js
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "Node.js no está instalado. Ejecuta .\setup-frontend.ps1 primero." -ForegroundColor Red
    exit 1
}

# Verificar node_modules
$nodeModules = Join-Path $frontendRoot 'node_modules'
if (-Not (Test-Path $nodeModules)) {
    Write-Host "node_modules no encontrado. Ejecuta .\setup-frontend.ps1 primero." -ForegroundColor Red
    exit 1
}

# Asegurar que el directorio de logs exista
if (-Not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
}

# Verificar si ya está corriendo
if (Test-Path $pidFile) {
    $existing = Get-Content $pidFile | Select-Object -First 1
    if ($existing -and (Get-Process -Id $existing -ErrorAction SilentlyContinue)) {
        Write-Host "Frontend ya está corriendo (pid: $existing)." -ForegroundColor Yellow
        Write-Host "URL: http://localhost:5173" -ForegroundColor Cyan
        Write-Host "Logs: $logFile"
        exit 0
    } else {
        Remove-Item $pidFile -ErrorAction SilentlyContinue
    }
}

Write-Host "Iniciando frontend (Vite dev server)..." -ForegroundColor Cyan

# Crear script temporal para ejecutar npm
$tempScript = Join-Path $scriptDir "temp_start.ps1"
@"
Set-Location '$frontendRoot'
npm run dev *>&1 | Out-File -FilePath '$logFile' -Append
"@ | Out-File -FilePath $tempScript -Encoding utf8

# Ejecutar el script en segundo plano
$proc = Start-Process powershell -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $tempScript -WindowStyle Hidden -PassThru

$proc.Id | Out-File -FilePath $pidFile -Encoding ascii
Write-Host "Iniciado con pid $($proc.Id)" -ForegroundColor Green
Write-Host "URL: http://localhost:5173" -ForegroundColor Cyan
Write-Host "Logs: $logFile" -ForegroundColor Gray
Write-Host "Nota: Espera unos segundos para que el servidor inicie completamente" -ForegroundColor Yellow
