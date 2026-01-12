# Automated Reporting and Workflow System

An internal reporting automation tool for teams that rely on manual reporting, spreadsheets, and recurring weekly/monthly updates. This system automates SQL report execution, scheduling, and distribution, reducing manual effort by nearly 30% through repeatable workflows and standardized outputs.

## Business Problem

Many teams waste significant time on repetitive reporting tasks:
- Manually pulling data from databases
- Cleaning and formatting data in spreadsheets
- Producing recurring reports on schedule
- Reminding stakeholders to check reports
- Maintaining audit trails of report runs

This manual process is error-prone, time-consuming, and doesn't scale well as reporting needs grow.

## Solution

The Automated Reporting and Workflow System transforms manual reporting into an automated, repeatable workflow:

- **SQL-driven reports**: Define reports using SQL queries
- **Automated scheduling**: Run reports on cron-based schedules
- **Execution tracking**: Monitor run status (queued, running, success, failed)
- **Stakeholder notifications**: Automatic notifications on completion
- **Audit trail**: Complete history of all report runs
- **RESTful API**: Programmatic access to reports and run history
- **CSV export**: Standardized output format for easy consumption

## Tech Stack

- **Backend**: Python 3.11+, FastAPI
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0
- **Scheduler**: APScheduler
- **Containerization**: Docker, Docker Compose
- **API Documentation**: FastAPI auto-generated Swagger/OpenAPI docs

## Architecture

The system follows a clean, service-oriented architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Application                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Reports API │  │   Runs API   │  │  Health API  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌──────▼────────┐  ┌──────▼────────┐
│   Scheduler    │  │     Runner    │  │   Exporter    │
│  (APScheduler) │  │   Service     │  │    Service    │
└───────┬────────┘  └──────┬────────┘  └──────┬────────┘
        │                   │                   │
        │         ┌─────────▼─────────┐         │
        │         │   Notifier        │         │
        │         │   Service         │         │
        │         └─────────┬─────────┘         │
        │                   │                   │
┌───────▼───────────────────▼───────────────────▼────────┐
│              PostgreSQL Database                        │
│  ┌──────────┐  ┌────────────┐  ┌──────────────────┐  │
│  │ Reports  │  │ ReportRuns │  │ NotificationLog  │  │
│  └──────────┘  └────────────┘  └──────────────────┘  │
└────────────────────────────────────────────────────────┘
```

### Execution Flow

1. **Scheduler** loads active reports from the database
2. **Scheduler** triggers report execution based on cron schedules
3. **Runner** creates a run record with QUEUED status
4. **Runner** executes the SQL query via **Exporter**
5. **Exporter** writes results to CSV file in `outputs/` directory
6. **Runner** updates run status (SUCCESS/FAILED) with row count and output path
7. **Notifier** logs notification to database (and can send emails)
8. **API** exposes run history and download endpoints

## How It Works

### Data Model

The system uses three main tables:

- **`reports`**: Stores report definitions (name, SQL query, schedule, format)
- **`report_runs`**: Tracks each execution (status, timestamps, row count, output path, errors)
- **`notification_log`**: Records all notifications sent for report runs

### Key Features

- **Report Definitions**: Store SQL queries with metadata and scheduling
- **Cron Scheduling**: Flexible scheduling using standard cron expressions
- **Status Tracking**: Real-time status updates (QUEUED → RUNNING → SUCCESS/FAILED)
- **Error Handling**: Comprehensive error capture and logging
- **CSV Export**: Standardized output format with timestamped filenames
- **Notification System**: Log-based notifications (extensible to email)
- **REST API**: Full CRUD operations for reports and run management

## Local Setup

### Prerequisites

- Docker and Docker Compose installed
- Git

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Xaaby/Automated-Reporting-and-Workflow-System.git
   cd Automated-Reporting-and-Workflow-System
   ```

2. **Start the services**:
   ```bash
   docker-compose up -d
   ```

   This will:
   - Start PostgreSQL database on port 5432
   - Initialize database schema and sample data
   - Start the FastAPI application on port 8000

3. **Verify the setup**:
   ```bash
   curl http://localhost:8000/health
   ```

   Expected response: `{"status": "healthy"}`

4. **Access API documentation**:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Environment Variables

Create a `.env` file (optional, defaults are set in docker-compose.yml):

```env
DATABASE_URL=postgresql://reporting_user:reporting_pass@localhost:5432/reporting_db
OUTPUT_DIR=./outputs
```

## API Examples

### List All Reports

```bash
curl http://localhost:8000/api/reports
```

**Response**:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Daily User Count",
    "description": "Report showing daily active user count",
    "sql_query": "SELECT CURRENT_DATE as report_date, COUNT(DISTINCT user_id) as active_users FROM users WHERE last_active >= CURRENT_DATE",
    "schedule_cron": "0 9 * * *",
    "output_format": "CSV",
    "is_active": true,
    "created_at": "2024-01-15T10:00:00Z"
  }
]
```

### Create a New Report

```bash
curl -X POST http://localhost:8000/api/reports \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Weekly Sales Summary",
    "description": "Weekly sales aggregation",
    "sql_query": "SELECT DATE_TRUNC('\''week'\'', order_date) as week, SUM(amount) as total FROM orders GROUP BY DATE_TRUNC('\''week'\'', order_date)",
    "schedule_cron": "0 8 * * 1",
    "output_format": "CSV",
    "is_active": true
  }'
```

### Trigger Manual Run

```bash
curl -X POST http://localhost:8000/api/reports/{report_id}/run
```

**Response**:
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "report_id": "550e8400-e29b-41d4-a716-446655440000",
  "started_at": "2024-01-15T10:30:00Z",
  "finished_at": "2024-01-15T10:30:05Z",
  "status": "SUCCESS",
  "row_count": 150,
  "output_path": "./outputs/Daily_User_Count_20240115_103005.csv",
  "error_message": null
}
```

### Get Run History

```bash
curl http://localhost:8000/api/reports/{report_id}/runs
```

### Download Report Output

```bash
curl http://localhost:8000/api/runs/{run_id}/download -o report.csv
```

### Update Report (Enable/Disable)

```bash
curl -X PUT http://localhost:8000/api/reports/{report_id} \
  -H "Content-Type: application/json" \
  -d '{
    "is_active": false
  }'
```

## Docker Commands

### Start Services
```bash
docker-compose up -d
```

### View Logs
```bash
docker-compose logs -f app
```

### Stop Services
```bash
docker-compose down
```

### Stop and Remove Volumes
```bash
docker-compose down -v
```

### Rebuild After Code Changes
```bash
docker-compose up -d --build
```

## Project Structure

```
automated-reporting-workflow/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── db.py                # Database connection and session management
│   ├── models.py            # SQLAlchemy models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── runner.py        # Report execution service
│   │   ├── scheduler.py     # APScheduler integration
│   │   ├── exporter.py      # CSV export service
│   │   └── notifier.py      # Notification service
│   ├── api/
│   │   ├── __init__.py
│   │   ├── reports.py       # Reports API endpoints
│   │   └── runs.py          # Runs API endpoints
│   └── utils/
│       ├── __init__.py
│       └── validators.py    # Validation utilities
├── sql/
│   ├── init.sql             # Database schema and sample data
│   └── sample_queries.sql   # Sample SQL queries
├── outputs/                 # Generated CSV files
├── docker-compose.yml       # Docker Compose configuration
├── Dockerfile              # Application Docker image
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Cron Expression Format

Reports use standard cron expressions with 5 fields:

```
minute hour day month day_of_week
```

**Examples**:
- `0 9 * * *` - Every day at 9:00 AM
- `0 8 * * 1` - Every Monday at 8:00 AM
- `0 7 1 * *` - First day of every month at 7:00 AM
- `*/15 * * * *` - Every 15 minutes
- `0 0 * * 0` - Every Sunday at midnight

## Use Cases

This system is ideal for:

- **Financial Services**: Regulatory reporting, daily P&L summaries
- **Telecom**: Network performance reports, customer metrics
- **Consulting Delivery Teams**: Project status reports, resource utilization
- **Operations & Support**: Incident summaries, SLA tracking
- **Healthcare IT**: Patient metrics, compliance reports

## Future Enhancements

- Email notifications via SMTP
- JSON export format support
- Web UI for report management
- Data quality checks (row count thresholds)
- Retry mechanism for failed runs
- Report templates and parameterized queries

## License

This project is for internal use and portfolio demonstration.

## Contributing

This is a portfolio project. For questions or suggestions, please open an issue.
