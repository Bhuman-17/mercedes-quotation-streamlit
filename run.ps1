$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "Starting Streamlit with the compatible Python 3.13 runtime..." -ForegroundColor Cyan
if (Get-Command uv -ErrorAction SilentlyContinue) {
    uv run --python 3.13 streamlit run app.py --server.headless true --server.port 8501
} else {
    py -m uv run --python 3.13 streamlit run app.py --server.headless true --server.port 8501
}
