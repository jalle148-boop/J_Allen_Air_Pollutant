$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$venvActivate = Join-Path $repoRoot ".venv\Scripts\Activate.ps1"

if (-Not (Test-Path $venvActivate)) {
    Write-Host "No .venv found. Run: python .\scripts\setup_venv.py" -ForegroundColor Yellow
    return
}

& $venvActivate
Write-Host "Activated .venv at $repoRoot\.venv" -ForegroundColor Green