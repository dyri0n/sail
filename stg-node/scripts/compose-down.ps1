param(
    [switch]$Prod,
    [switch]$Test,
    [switch]$All,
    [switch]$Help
)

if ($Help) {
    Write-Host "Uso: .\scripts\compose-down.ps1 [-Prod|-Test|-All]" -ForegroundColor Yellow
    Write-Host "  -Prod  Baja solo el perfil prod" -ForegroundColor Gray
    Write-Host "  -Test  Baja solo el perfil testing" -ForegroundColor Gray
    Write-Host "  -All   Baja ambos perfiles (default)" -ForegroundColor Gray
    return
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $scriptDir "..")

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Docker no está en PATH" -ForegroundColor Red
    exit 1
}

if ($Prod) {
    docker compose --profile prod down
} elseif ($Test) {
    docker compose --profile testing down
} else {
    docker compose --profile prod --profile testing down
}
