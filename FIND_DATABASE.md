# Where is the SQLite Database File?

## 📍 Database File Location

**File Name**: `reporting.db`

**Full Path**: 
```
C:\Z UTD\OneDrive - The University of Texas at Dallas\Documents\Automated Reporting and Workflow System\reporting.db
```

**In your project folder**: Same folder as `app/`, `frontend/`, `requirements.txt`, etc.

## ❓ Why Can't I Find It?

The database file **doesn't exist yet** because:

1. ✅ We switched to SQLite (code updated)
2. ⚠️ Server hasn't been restarted yet (still using old config)
3. ⚠️ No reports created yet (database created on first use)

## 🔧 How to Create the Database File

### Step 1: Restart the Server

The server needs to be restarted to use SQLite:

**Stop the current server** (if running), then restart:

```bash
python run_local.py
```

Or:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 2: Create a Report

1. Open http://localhost:8000
2. Click "Create New Report"
3. Fill in the form:
   - Name: "Test Report"
   - SQL Query: `SELECT 'Test' as name, 1 as value`
   - Cron: `0 9 * * *`
4. Click "Create Report"

**The database file will be created automatically!**

## 📂 How to See It in Your Folder Structure

### Option 1: File Explorer
1. Open File Explorer
2. Navigate to: `C:\Z UTD\OneDrive - The University of Texas at Dallas\Documents\Automated Reporting and Workflow System\`
3. Look for `reporting.db` file

### Option 2: VS Code
1. Open the project folder in VS Code
2. The `reporting.db` file will appear in the file tree
3. It will be in the root directory (same level as `app/`, `frontend/`, etc.)

### Option 3: Command Line
```bash
cd "C:\Z UTD\OneDrive - The University of Texas at Dallas\Documents\Automated Reporting and Workflow System"
dir reporting.db
```

## 🔍 Verify Database Creation

After creating a report, verify the file exists:

```bash
python view_db.py
```

This will show you the database contents and confirm it was created.

## 📁 Expected Folder Structure

After creating the database, your folder should look like:

```
Automated Reporting and Workflow System/
├── app/
├── frontend/
├── sql/
├── outputs/
├── reporting.db          ← Database file (created here)
├── requirements.txt
├── README.md
└── ...
```

## ⚡ Quick Test

Run this to check if the file exists:

```bash
python -c "import os; print('EXISTS' if os.path.exists('reporting.db') else 'NOT FOUND')"
```

## 🎯 Summary

- **Location**: Root of your project folder
- **Name**: `reporting.db`
- **When Created**: Automatically when you create your first report (after server restart)
- **How to Find**: Look in the same folder as `app/` and `frontend/`

The file will appear **automatically** - you don't need to create it manually!
