# Server Restart Instructions

## The Problem
The old server process is still running with old code. You need to stop it completely before starting a new one.

## Solution

### Step 1: Stop the Old Server
**Option A: Using Task Manager**
1. Press `Ctrl+Shift+Esc` to open Task Manager
2. Find the Python process (python.exe or uvicorn)
3. Right-click and select "End Task"

**Option B: Using PowerShell (Run as Administrator)**
```powershell
# Find and stop processes on port 8000
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | 
    Select-Object -ExpandProperty OwningProcess -Unique | 
    ForEach-Object { Stop-Process -Id $_ -Force }
```

**Option C: Find the terminal where server is running**
- If you see a terminal window with server output, press `Ctrl+C` to stop it

### Step 2: Verify Port 8000 is Free
```powershell
netstat -ano | findstr :8000
```
This should return nothing (or only TIME_WAIT connections that will clear in a few seconds)

### Step 3: Start the New Server
```powershell
cd "C:\Z UTD\OneDrive - The University of Texas at Dallas\Documents\Automated Reporting and Workflow System"
python run_local.py
```

### Step 4: Wait for Startup Messages
You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
Database initialized
Scheduler started
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 5: Test in Browser
1. Open `http://localhost:8000`
2. Press `Ctrl+F5` (hard refresh)
3. Try creating a report

## Using the Restart Script
You can also use the provided PowerShell script:
```powershell
.\restart_server.ps1
```

This will automatically stop any processes on port 8000 and restart the server.
