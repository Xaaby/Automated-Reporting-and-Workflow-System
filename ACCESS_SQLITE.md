# How to Access SQLite Database

## 📁 Database File Location

**File**: `reporting.db`  
**Full Path**: `C:\Z UTD\OneDrive - The University of Texas at Dallas\Documents\Automated Reporting and Workflow System\reporting.db`

**Note**: The file is created automatically when you create your first report.

## 🔧 Methods to Access SQLite

### Method 1: Command Line (sqlite3)

If you have SQLite installed:

```bash
# Navigate to project directory
cd "C:\Z UTD\OneDrive - The University of Texas at Dallas\Documents\Automated Reporting and Workflow System"

# Open database
sqlite3 reporting.db

# Then run SQL commands:
.tables                    # List all tables
.schema reports            # Show table structure
SELECT * FROM reports;     # View all reports
SELECT * FROM report_runs; # View all runs
.quit                      # Exit
```

**Install sqlite3** (if not installed):
- Download from: https://www.sqlite.org/download.html
- Or use Chocolatey: `choco install sqlite`

### Method 2: DB Browser for SQLite (Recommended - GUI)

**Best option for visual browsing!**

1. **Download**: https://sqlitebrowser.org/
2. **Install** DB Browser for SQLite
3. **Open** the application
4. **Click** "Open Database"
5. **Navigate** to: `C:\Z UTD\OneDrive - The University of Texas at Dallas\Documents\Automated Reporting and Workflow System\reporting.db`
6. **Browse** tables, run queries, view data visually

**Features**:
- ✅ Visual table browser
- ✅ SQL query editor
- ✅ Data editing
- ✅ Export to CSV/JSON
- ✅ Free and open source

### Method 3: VS Code Extension

If you use VS Code:

1. **Install Extension**: "SQLite" by alexcvzz
2. **Open** `reporting.db` file in VS Code
3. **Right-click** → "Open Database"
4. **Browse** tables and run queries in VS Code

### Method 4: Python Script

Create a simple Python script to query the database:

```python
# query_db.py
import sqlite3

conn = sqlite3.connect('reporting.db')
cursor = conn.cursor()

# List all reports
print("=== Reports ===")
cursor.execute("SELECT id, name, is_active, created_at FROM reports")
for row in cursor.fetchall():
    print(row)

# List all runs
print("\n=== Report Runs ===")
cursor.execute("SELECT id, report_id, status, row_count, started_at FROM report_runs")
for row in cursor.fetchall():
    print(row)

conn.close()
```

Run: `python query_db.py`

### Method 5: Online SQLite Viewer

1. Go to: https://sqliteviewer.app/ or https://inloop.github.io/sqlite-viewer/
2. Upload your `reporting.db` file
3. Browse tables online

## 📊 Useful SQL Queries

Once you have access, try these queries:

### View All Reports
```sql
SELECT * FROM reports;
```

### View Reports with Run Count
```sql
SELECT 
    r.id,
    r.name,
    r.is_active,
    COUNT(rr.id) as total_runs,
    MAX(rr.started_at) as last_run
FROM reports r
LEFT JOIN report_runs rr ON r.id = rr.report_id
GROUP BY r.id, r.name, r.is_active;
```

### View Recent Runs
```sql
SELECT 
    rr.id,
    r.name as report_name,
    rr.status,
    rr.row_count,
    rr.started_at,
    rr.finished_at
FROM report_runs rr
JOIN reports r ON rr.report_id = r.id
ORDER BY rr.started_at DESC
LIMIT 10;
```

### View Failed Runs
```sql
SELECT 
    r.name as report_name,
    rr.status,
    rr.error_message,
    rr.started_at
FROM report_runs rr
JOIN reports r ON rr.report_id = r.id
WHERE rr.status = 'FAILED'
ORDER BY rr.started_at DESC;
```

### View Notifications
```sql
SELECT * FROM notification_log
ORDER BY sent_at DESC
LIMIT 20;
```

## 🗂️ Database Schema

### Tables

1. **reports**
   - `id` (String/UUID)
   - `name` (String)
   - `description` (Text)
   - `sql_query` (Text)
   - `schedule_cron` (String)
   - `output_format` (String)
   - `is_active` (Boolean)
   - `created_at` (DateTime)

2. **report_runs**
   - `id` (String/UUID)
   - `report_id` (String/UUID, FK)
   - `started_at` (DateTime)
   - `finished_at` (DateTime)
   - `status` (String: QUEUED, RUNNING, SUCCESS, FAILED)
   - `row_count` (Integer)
   - `output_path` (String)
   - `error_message` (Text)

3. **notification_log**
   - `id` (String/UUID)
   - `report_run_id` (String/UUID, FK)
   - `channel` (String: EMAIL, LOG)
   - `sent_at` (DateTime)
   - `status` (String: SENT, FAILED)
   - `message` (Text)

## 🔍 Quick Access Script

I can create a simple Python script for you to quickly view the database. Would you like me to create it?

## 💡 Recommended Approach

**For beginners**: Use **DB Browser for SQLite** (Method 2) - it's the easiest and most visual.

**For developers**: Use **VS Code Extension** (Method 3) or **command line** (Method 1).

**For quick checks**: Use the **Python script** (Method 4).
