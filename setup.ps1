$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "Ensuring uv is available..." -ForegroundColor Cyan
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    py -m pip install --user uv
}

Write-Host "Installing Python dependencies with a compatible Python 3.13 runtime..." -ForegroundColor Cyan
if (Get-Command uv -ErrorAction SilentlyContinue) {
    uv sync --python 3.13
} else {
    py -m uv sync --python 3.13
}

Write-Host "Setup complete. Run .\run.ps1" -ForegroundColor Green
