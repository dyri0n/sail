param(
    [switch]$Help
)

if ($Help) {
    Write-Host "Uso: .\stop-db.ps1" -ForegroundColor Yellow
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

Write-Host "Stopping Postgres..." -ForegroundColor Cyan
Set-Location $backendRoot
docker compose -f $ComposeFile down -v

if ($LASTEXITCODE -eq 0) {
    Write-Host "Postgres stopped successfully." -ForegroundColor Green
} else {
    Write-Host "Error stopping Postgres" -ForegroundColor Red
    exit 1
}
