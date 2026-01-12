# Restart Server Script
Write-Host "Stopping existing server processes..."

# Find and stop Python/uvicorn processes on port 8000
$processes = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($pid in $processes) {
    try {
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        Write-Host "Stopped process $pid"
    } catch {
        Write-Host "Could not stop process $pid"
    }
}

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "Starting server..."
Write-Host ""

# Start the server
python run_local.py
