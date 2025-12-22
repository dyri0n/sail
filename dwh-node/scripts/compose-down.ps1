param([switch]$Help)

if ($Help) {
    Write-Host "Uso: .\scripts\compose-down.ps1" -ForegroundColor Yellow
    Write-Host "Baja el contenedor Data Warehouse" -ForegroundColor Gray
    return
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $scriptDir "..")

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Docker no está en PATH" -ForegroundColor Red
    exit 1
}

docker compose down -v
