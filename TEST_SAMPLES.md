# Sample Values for Testing "Create New Report"

## Quick Test Values (Works with PostgreSQL System Tables)

### Sample 1: System Information Report
```
Report Name: Daily Database Stats
Description: Shows current database connection and version information
SQL Query: 
SELECT 
    current_database() as database_name,
    version() as postgres_version,
    current_timestamp as report_time,
    (SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public') as table_count

Cron Schedule: 0 9 * * *
Active: Yes
```

### Sample 2: Simple Test Report
```
Report Name: Test Report
Description: A simple test report to verify the system works
SQL Query: 
SELECT 
    'Test' as report_type,
    CURRENT_DATE as report_date,
    CURRENT_TIME as report_time,
    42 as test_number

Cron Schedule: */5 * * * *
Active: Yes
```

### Sample 3: Table List Report
```
Report Name: Available Tables
Description: Lists all tables in the public schema
SQL Query: 
SELECT 
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name

Cron Schedule: 0 8 * * 1
Active: Yes
```

## If You Have Sample Data Tables

### Sample 4: User Count Report (if you have a users table)
```
Report Name: Daily Active Users
Description: Count of active users for today
SQL Query: 
SELECT 
    CURRENT_DATE as report_date,
    COUNT(*) as total_users
FROM users
WHERE created_at >= CURRENT_DATE

Cron Schedule: 0 9 * * *
Active: Yes
```

### Sample 5: Sales Summary (if you have an orders table)
```
Report Name: Weekly Sales Summary
Description: Weekly sales aggregation
SQL Query: 
SELECT 
    DATE_TRUNC('week', order_date) as week,
    COUNT(*) as order_count,
    SUM(amount) as total_revenue
FROM orders
WHERE order_date >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY DATE_TRUNC('week', order_date)
ORDER BY week DESC

Cron Schedule: 0 8 * * 1
Active: Yes
```

## Recommended First Test

**Start with Sample 2 (Simple Test Report)** - it will always work because it doesn't query any tables:

```
Report Name: System Test Report
Description: Basic functionality test
SQL Query: 
SELECT 
    'Automated Reporting System' as system_name,
    CURRENT_DATE as report_date,
    CURRENT_TIME as report_time,
    'Test successful' as status

Cron Schedule: 0 9 * * *
Active: Yes
```

This will:
- ✅ Always execute successfully (no table dependencies)
- ✅ Generate a CSV with 1 row
- ✅ Verify the system is working
- ✅ Show you the complete workflow

## Cron Schedule Examples

- `0 9 * * *` - Every day at 9:00 AM
- `0 8 * * 1` - Every Monday at 8:00 AM  
- `*/15 * * * *` - Every 15 minutes (good for testing)
- `0 7 1 * *` - First day of every month at 7:00 AM
- `0 0 * * 0` - Every Sunday at midnight

## Testing Workflow

1. **Create the report** using Sample 2 above
2. **Click "Run Now"** to trigger immediate execution
3. **Check "View History"** to see the run status
4. **Download CSV** if the run was successful
5. **Verify the CSV** contains the expected data

## Troubleshooting

If you get SQL errors:
- Make sure the SQL query is valid PostgreSQL syntax
- Check that referenced tables exist
- Use Sample 2 first to verify the system works
- Check the run history for specific error messages
