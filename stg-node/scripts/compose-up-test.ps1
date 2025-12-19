param([switch]$Help)

if ($Help) {
    Write-Host "Uso: .\scripts\compose-up-test.ps1" -ForegroundColor Yellow
    Write-Host "Levanta el contenedor staging en modo testing (con datos de prueba)" -ForegroundColor Gray
    return
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $scriptDir "..")

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Docker no está en PATH" -ForegroundColor Red
    exit 1
}

docker compose --profile testing up -d
