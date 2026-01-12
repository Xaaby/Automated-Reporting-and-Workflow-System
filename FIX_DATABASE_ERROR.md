# Fix: Database Connection Error

## The Problem
The server is still trying to connect to PostgreSQL even though we've configured SQLite.

## Solution

### Step 1: Stop the Server Completely
1. Find the terminal where the server is running
2. Press `Ctrl+C` to stop it
3. Wait a few seconds

### Step 2: Clear Any Environment Variables
In PowerShell, run:
```powershell
$env:DATABASE_URL = $null
```

Or in Command Prompt:
```cmd
set DATABASE_URL=
```

### Step 3: Restart the Server
```powershell
cd "C:\Z UTD\OneDrive - The University of Texas at Dallas\Documents\Automated Reporting and Workflow System"
python run_local.py
```

### Step 4: Verify SQLite is Being Used
When the server starts, you should see:
```
Using default DATABASE_URL (SQLite): sqlite:///./reporting.db
✓ Database connection successful
Database initialized
```

If you see PostgreSQL connection errors, the server is still using old code.

### Step 5: Test Report Creation
1. Open `http://localhost:8000` in your browser
2. Press `Ctrl+F5` (hard refresh)
3. Try creating a report

## What Was Fixed

1. **`app/db.py`**: Now forces SQLite by default, even if PostgreSQL URL is in environment
2. **`run_local.py`**: Sets SQLite as default DATABASE_URL
3. **Added logging**: Shows which database is being used

## If It Still Doesn't Work

1. **Check for multiple Python processes**:
   ```powershell
   Get-Process python | Where-Object {$_.Path -like "*python*"}
   ```
   Kill any old server processes

2. **Check for .env file**:
   ```powershell
   Get-Content .env
   ```
   If it has `DATABASE_URL=postgresql://...`, either delete it or change it to SQLite

3. **Verify the code changes**:
   - Check `app/db.py` line 13-25 - should show SQLite logic
   - Check `run_local.py` line 60-61 - should set SQLite

4. **Restart your terminal** - Sometimes environment variables persist in the terminal session
