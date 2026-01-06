param(
    [switch]$Help
)

if ($Help) {
    Write-Host "Uso: .\stop-backend.ps1" -ForegroundColor Yellow
    return
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pidFile = Join-Path $scriptDir 'backend.pid'

if (-Not (Test-Path $pidFile)) {
    Write-Host "No pid file ($pidFile) found. Nothing to stop." -ForegroundColor Yellow
    exit 0
}
$processId = Get-Content $pidFile | Select-Object -First 1
if ($processId -and (Get-Process -Id $processId -ErrorAction SilentlyContinue)) {
    Stop-Process -Id $processId -Force
    Write-Host "Stopped process $processId" -ForegroundColor Green
} else {
    Write-Host "Process $processId not running. Removing pid file." -ForegroundColor Gray
}
Remove-Item $pidFile -ErrorAction SilentlyContinue
