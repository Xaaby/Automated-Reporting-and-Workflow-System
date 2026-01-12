# How to Restart the Server

## The Problem
The server is running old code and needs to be restarted to pick up the latest fixes.

## Solution: Restart the Server

### Step 1: Stop the Current Server
1. Find the terminal/command prompt where the server is running
2. Press `Ctrl+C` to stop it
3. Or close that terminal window

### Step 2: Start the Server Again

**Option A: Using the restart script (PowerShell)**
```powershell
.\restart_server.ps1
```

**Option B: Manual restart**
```bash
cd "C:\Z UTD\OneDrive - The University of Texas at Dallas\Documents\Automated Reporting and Workflow System"
python run_local.py
```

**Option C: Direct uvicorn command**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 3: Wait for Startup Messages
You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
Database initialized
Scheduler started
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 4: Test in Browser
1. Open `http://localhost:8000` in your browser
2. Press `Ctrl+F5` (hard refresh) to reload the frontend
3. Try creating a report again

## Why This Happens
The server process was started before the code changes were saved. Restarting loads the new code with all the fixes:
- SQLite database support
- UUID string handling
- Better error handling
- Scheduler auto-start

## Verification
After restarting, you can verify the server is working by:
1. Creating a report through the UI
2. Checking `http://localhost:8000/api/reports` in your browser
3. Running `python view_db.py` to see the database contents
