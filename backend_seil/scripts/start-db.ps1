param(
    [switch]$Help
)

if ($Help) {
    Write-Host "Uso: .\start-db.ps1" -ForegroundColor Yellow
    return
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendRoot = Split-Path -Parent $scriptDir

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Docker no está en PATH" -ForegroundColor Red
    exit 1
}

$ComposeFile = Join-Path $backendRoot 'docker\postgres\docker-compose.yml'

if (-Not (Test-Path $ComposeFile)) {
    Write-Host "docker-compose file not found: $ComposeFile" -ForegroundColor Red
    exit 1
}

Write-Host "Starting Postgres..." -ForegroundColor Cyan
Set-Location $backendRoot
docker compose -f $ComposeFile up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "Postgres started successfully. Run 'docker ps' to check containers." -ForegroundColor Green
} else {
    Write-Host "Error starting Postgres" -ForegroundColor Red
    exit 1
}
