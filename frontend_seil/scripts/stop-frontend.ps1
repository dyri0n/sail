param(
    [switch]$Help
)

if ($Help) {
    Write-Host "Uso: .\stop-frontend.ps1" -ForegroundColor Yellow
    return
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pidFile = Join-Path $scriptDir 'frontend.pid'
$tempScript = Join-Path $scriptDir 'temp_start.ps1'

if (-Not (Test-Path $pidFile)) {
    Write-Host "No se encontró archivo pid ($pidFile). Nada que detener." -ForegroundColor Yellow
    exit 0
}

$processId = Get-Content $pidFile | Select-Object -First 1

if ($processId -and (Get-Process -Id $processId -ErrorAction SilentlyContinue)) {
    # Detener el proceso PowerShell y sus hijos (node/vite)
    Write-Host "Deteniendo frontend (pid: $processId)..." -ForegroundColor Cyan
    
    # Obtener procesos hijos usando Get-CimInstance (compatible con PowerShell Core)
    $children = Get-CimInstance -ClassName Win32_Process -Filter "ParentProcessId=$processId" -ErrorAction SilentlyContinue
    
    # Detener procesos hijos primero
    foreach ($child in $children) {
        # También obtener los hijos del hijo (node -> vite)
        $grandchildren = Get-CimInstance -ClassName Win32_Process -Filter "ParentProcessId=$($child.ProcessId)" -ErrorAction SilentlyContinue
        foreach ($gc in $grandchildren) {
            Stop-Process -Id $gc.ProcessId -Force -ErrorAction SilentlyContinue
        }
        Stop-Process -Id $child.ProcessId -Force -ErrorAction SilentlyContinue
    }
    
    # Detener proceso principal
    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    
    Write-Host "Frontend detenido (proceso $processId)" -ForegroundColor Green
} else {
    Write-Host "Proceso $processId no está corriendo. Eliminando archivo pid." -ForegroundColor Gray
}

Remove-Item $pidFile -ErrorAction SilentlyContinue
Remove-Item $tempScript -ErrorAction SilentlyContinue
