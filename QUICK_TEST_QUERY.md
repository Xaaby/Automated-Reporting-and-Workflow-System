# Quick Test Query for SQLite

## Simple Test Query (No Tables Required)

This query works immediately with SQLite and doesn't require any existing tables:

```sql
SELECT 
    'System Test' as test_name,
    datetime('now') as current_time,
    'SQLite Database' as database_type,
    1 + 1 as calculation,
    'Query executed successfully!' as status
```

**What it does:**
- Returns a single row with test data
- Uses SQLite's built-in `datetime()` function
- No tables needed - works immediately
- Perfect for testing the report execution

## Database Information Query

Get information about your SQLite database:

```sql
SELECT 
    name as table_name,
    type as object_type,
    sql as definition
FROM sqlite_master
WHERE type IN ('table', 'view')
ORDER BY name
```

**What it does:**
- Lists all tables and views in the database
- Shows their SQL definitions
- Helps you see what's available

## Report System Tables Query

See all the reports and runs in the system:

```sql
SELECT 
    r.id,
    r.name,
    r.is_active,
    r.schedule_cron,
    COUNT(rr.id) as total_runs,
    MAX(rr.started_at) as last_run
FROM reports r
LEFT JOIN report_runs rr ON r.id = rr.report_id
GROUP BY r.id, r.name, r.is_active, r.schedule_cron
ORDER BY r.name
```

**What it does:**
- Shows all reports in the system
- Counts how many times each report has run
- Shows when each report last ran
- Uses the actual tables from your reporting system

## Simple Aggregation Test

Test aggregation functions:

```sql
SELECT 
    'Total Reports' as metric,
    COUNT(*) as value
FROM reports
UNION ALL
SELECT 
    'Active Reports',
    COUNT(*)
FROM reports
WHERE is_active = 1
UNION ALL
SELECT 
    'Total Runs',
    COUNT(*)
FROM report_runs
```

**What it does:**
- Counts total reports
- Counts active reports
- Counts total runs
- Returns multiple rows with statistics

## Recommended: Start with the Simple Test Query

Use this for your first test:

**Report Name:** `System Test Report`
**Description:** `Quick test to verify the system works`
**SQL Query:**
```sql
SELECT 
    'System Test' as test_name,
    datetime('now') as current_time,
    'SQLite Database' as database_type,
    1 + 1 as calculation,
    'Query executed successfully!' as status
```
**Cron Schedule:** `0 9 * * *` (Daily at 9 AM)
**Active:** Yes

This will:
1. Create a report successfully
2. Execute immediately when you click "Run Now"
3. Generate a CSV file with the results
4. Show up in the run history

## How to Use

1. Click "+ Create New Report"
2. Fill in the form with the values above
3. Click "Create Report"
4. Click "Run Now" on the newly created report
5. Check the "Run History" to see the results
6. Download the CSV to see the output
