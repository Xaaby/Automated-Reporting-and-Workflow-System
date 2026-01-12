#!/usr/bin/env python3
"""
Local development server runner.
This script helps run the application locally without Docker.
"""
import os
import sys
import subprocess
import time

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import psycopg2
        import apscheduler
        print("✓ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e.name}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def check_database():
    """Check if database is accessible."""
    import os
    from app.db import engine
    
    try:
        with engine.connect() as conn:
            print("✓ Database connection successful")
            return True
    except Exception as e:
        print(f"✗ Database connection failed: {str(e)}")
        print("\nPlease ensure PostgreSQL is running and DATABASE_URL is set correctly.")
        print("Default: postgresql://reporting_user:reporting_pass@localhost:5432/reporting_db")
        return False

def main():
    """Main function to run the local server."""
    print("=" * 60)
    print("Automated Reporting System - Local Development Server")
    print("=" * 60)
    print()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print()
    
    # Check database (optional, will show error but continue)
    print("Checking database connection...")
    check_database()
    print()
    
    # Set environment variables if not set
    if not os.getenv("DATABASE_URL"):
        os.environ["DATABASE_URL"] = "postgresql://reporting_user:reporting_pass@localhost:5432/reporting_db"
        print("Using default DATABASE_URL")
    
    if not os.getenv("OUTPUT_DIR"):
        os.environ["OUTPUT_DIR"] = "./outputs"
        print("Using default OUTPUT_DIR: ./outputs")
    
    # Create outputs directory
    os.makedirs("outputs", exist_ok=True)
    
    print()
    print("=" * 60)
    print("Starting server...")
    print("API will be available at: http://localhost:8000")
    print("Frontend will be available at: http://localhost:8000/ui")
    print("API docs will be available at: http://localhost:8000/docs")
    print("=" * 60)
    print()
    
    # Run uvicorn
    try:
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    except Exception as e:
        print(f"\n\nError starting server: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
