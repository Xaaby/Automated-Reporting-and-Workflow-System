# Setup Instructions

## Quick Start (with Docker - Recommended)

If you have Docker installed:

```bash
docker-compose up -d
```

The application will be available at:
- Frontend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Local Development (without Docker)

### Prerequisites

1. **Python 3.11+** (Python 3.14 is supported)
2. **PostgreSQL** - You need PostgreSQL running locally or accessible remotely

### Step 1: Install PostgreSQL

If you don't have PostgreSQL installed:

**Windows:**
- Download from https://www.postgresql.org/download/windows/
- Or use Chocolatey: `choco install postgresql`

**Mac:**
- `brew install postgresql`
- `brew services start postgresql`

**Linux:**
- `sudo apt-get install postgresql postgresql-contrib`
- `sudo systemctl start postgresql`

### Step 2: Create Database

```sql
CREATE DATABASE reporting_db;
CREATE USER reporting_user WITH PASSWORD 'reporting_pass';
GRANT ALL PRIVILEGES ON DATABASE reporting_db TO reporting_user;
```

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or use the run script:

**Windows:**
```bash
run.bat
```

**Linux/Mac:**
```bash
python run_local.py
```

### Step 4: Set Environment Variables (Optional)

Create a `.env` file:

```env
DATABASE_URL=postgresql://reporting_user:reporting_pass@localhost:5432/reporting_db
OUTPUT_DIR=./outputs
```

### Step 5: Run the Server

```bash
python run_local.py
```

Or directly:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Accessing the Application

Once the server is running:

- **Frontend UI**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **API Base URL**: http://localhost:8000/api

## Troubleshooting

### Database Connection Errors

If you see database connection errors:

1. Ensure PostgreSQL is running:
   ```bash
   # Windows
   Get-Service postgresql*
   
   # Linux/Mac
   sudo systemctl status postgresql
   ```

2. Check database credentials in `.env` or `DATABASE_URL` environment variable

3. Verify database exists:
   ```sql
   \l  -- List databases
   ```

### Port Already in Use

If port 8000 is already in use:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

Then update the frontend `API_BASE` in `frontend/index.html` to use port 8001.

### Missing Dependencies

If you get import errors:

```bash
pip install -r requirements.txt --upgrade
```

## Development Notes

- The application will create database tables automatically on startup
- CSV outputs are saved to the `outputs/` directory
- The scheduler runs in the background and executes reports based on their cron schedules
- All API endpoints are documented at `/docs`
