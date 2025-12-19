param(
    [switch]$Testing,
    [switch]$Help
)

if ($Help) {
    Write-Host "Uso: .\\scripts\\compose-up.ps1 [-Testing]" -ForegroundColor Yellow
    return
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $scriptDir "..")

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Docker no está en PATH" -ForegroundColor Red
    exit 1
}

$profile = $null
if ($Testing) { $profile = "testing" }

$composeArgs = @("compose")
if ($profile) { $composeArgs += @("--profile", $profile) }

docker @composeArgs up -d
