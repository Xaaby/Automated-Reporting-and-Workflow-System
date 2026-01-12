# File Storage and Database Configuration

## 📁 Where CSV Files Are Saved

### Current Configuration
**CSV Output Location**: `./outputs/` directory (relative to project root)

**Full Path**: 
```
C:\Z UTD\OneDrive - The University of Texas at Dallas\Documents\Automated Reporting and Workflow System\outputs\
```

### How Files Are Named
Files are saved with this format:
```
{ReportName}_{YYYYMMDD}_{HHMMSS}.csv
```

**Example:**
- Report Name: "Daily User Count"
- Timestamp: 2024-01-15 10:30:05
- Filename: `Daily_User_Count_20240115_103005.csv`

### Configuration Details

**From `app/services/runner.py`:**
```python
output_dir = os.getenv("OUTPUT_DIR", "./outputs")
```

**From `app/services/exporter.py`:**
- Creates the `outputs/` directory if it doesn't exist
- Saves CSV files with timestamped filenames
- Returns the full path to the saved file

**From `docker-compose.yml` (if using Docker):**
```yaml
OUTPUT_DIR: /app/outputs
volumes:
  - ./outputs:/app/outputs  # Maps to local ./outputs directory
```

## 🗄️ Database Configuration

### Current Database Settings

**Database Type**: PostgreSQL 15

**Default Connection String:**
```
postgresql://reporting_user:reporting_pass@localhost:5432/reporting_db
```

**From `app/db.py`:**
```python
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://reporting_user:reporting_pass@localhost:5432/reporting_db"
)
```

### Database Details

**Host**: `localhost` (or `db` if using Docker)
**Port**: `5432`
**Database Name**: `reporting_db`
**Username**: `reporting_user`
**Password**: `reporting_pass`

### What's Stored in the Database

The PostgreSQL database stores:

1. **`reports` table** - Report definitions
   - Report name, description
   - SQL query
   - Schedule (cron expression)
   - Active status

2. **`report_runs` table** - Execution history
   - Run status (QUEUED, RUNNING, SUCCESS, FAILED)
   - Start/finish timestamps
   - Row count
   - Output file path (reference to CSV file)
   - Error messages (if failed)

3. **`notification_log` table** - Notification records
   - Notification status
   - Messages
   - Timestamps

### Important Note

**CSV files are NOT stored in the database** - they are saved as files in the `outputs/` directory.

The database only stores:
- The **path** to the CSV file (in `report_runs.output_path`)
- **Metadata** about the run (status, timestamps, row count)

## 📊 Data Flow

```
1. Report Definition Created
   ↓
   Stored in PostgreSQL (reports table)

2. Report Executed (scheduled or manual)
   ↓
   SQL Query Executed → Results Retrieved
   ↓
   CSV File Created → Saved to ./outputs/ directory
   ↓
   Run Record Created → Stored in PostgreSQL (report_runs table)
   ↓
   Output Path Stored → Points to CSV file location
```

## 🔍 Current Status

**CSV Files Location**: ✅ `outputs/` directory exists
**Database**: ⚠️ PostgreSQL not currently connected

**To see your files:**
- Check: `C:\Z UTD\OneDrive - The University of Texas at Dallas\Documents\Automated Reporting and Workflow System\outputs\`
- Files will appear here after successful report runs

**To check database:**
- Currently trying to connect to: `localhost:5432/reporting_db`
- Status: Not connected (PostgreSQL not running)

## 🛠️ Changing File Location

To change where CSV files are saved:

1. **Set environment variable:**
   ```bash
   $env:OUTPUT_DIR = "C:\MyReports\outputs"
   ```

2. **Or create `.env` file:**
   ```
   OUTPUT_DIR=C:\MyReports\outputs
   ```

3. **Or modify `docker-compose.yml`** (if using Docker):
   ```yaml
   environment:
     OUTPUT_DIR: /custom/path/outputs
   volumes:
     - ./custom-outputs:/custom/path/outputs
   ```

## 🗄️ Changing Database

To use a different database:

1. **Set environment variable:**
   ```bash
   $env:DATABASE_URL = "postgresql://user:pass@host:5432/dbname"
   ```

2. **Or create `.env` file:**
   ```
   DATABASE_URL=postgresql://user:pass@host:5432/dbname
   ```

3. **Or modify `docker-compose.yml`** (if using Docker):
   ```yaml
   environment:
     DATABASE_URL: postgresql://user:pass@host:5432/dbname
   ```

## 📝 Summary

- **CSV Files**: Saved to `./outputs/` directory (local filesystem)
- **Database**: PostgreSQL at `localhost:5432/reporting_db` (metadata storage)
- **File Paths**: Stored in database, actual files on disk
- **Current Status**: Outputs directory exists, database needs connection
