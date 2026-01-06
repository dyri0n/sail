param(
    [switch]$Help
)

if ($Help) {
    Write-Host "Uso: .\start-backend.ps1" -ForegroundColor Yellow
    return
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendRoot = Split-Path -Parent $scriptDir
$appDir = Join-Path $backendRoot 'app'
$venvPython = Join-Path $appDir '.venv\Scripts\python.exe'
$pidFile = Join-Path $scriptDir 'backend.pid'
$logsDir = Join-Path $backendRoot 'logs'
$logFile = Join-Path $logsDir 'backend.log'
$errorFile = Join-Path $logsDir 'backend.error.log'

if (-Not (Test-Path $venvPython)) {
    Write-Host "Virtualenv not found. Run .\setup-backend.ps1 first." -ForegroundColor Red
    exit 1
}

# Asegurar que el directorio de logs exista
if (-Not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
}

if (Test-Path $pidFile) {
    $existing = Get-Content $pidFile | Select-Object -First 1
    if ($existing -and (Get-Process -Id $existing -ErrorAction SilentlyContinue)) {
        Write-Host "Backend already running (pid: $existing)." -ForegroundColor Yellow
        Write-Host "Logs: $logFile"
        exit 0
    } else {
        Remove-Item $pidFile -ErrorAction SilentlyContinue
    }
}

Write-Host "Starting backend (uvicorn)..." -ForegroundColor Cyan
$proc = Start-Process -FilePath $venvPython -ArgumentList '-m','uvicorn','app.main:app','--host','0.0.0.0','--port','8000' -WorkingDirectory $backendRoot -NoNewWindow -RedirectStandardOutput $logFile -RedirectStandardError $errorFile -PassThru
$proc.Id | Out-File -FilePath $pidFile -Encoding ascii
Write-Host "Started pid $($proc.Id). Logs: $logFile" -ForegroundColor Green
