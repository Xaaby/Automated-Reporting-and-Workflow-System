#!/usr/bin/env python3
"""
Simple script to view SQLite database contents
"""
import sqlite3
import os
from datetime import datetime

DB_FILE = "reporting.db"

def format_datetime(dt_str):
    """Format datetime string for display"""
    if dt_str:
        try:
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return dt_str
    return "N/A"

def view_database():
    """View database contents"""
    if not os.path.exists(DB_FILE):
        print(f"Database file '{DB_FILE}' not found.")
        print("   Create a report first to generate the database.")
        return
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    print("=" * 70)
    print("SQLite Database Viewer - Automated Reporting System")
    print("=" * 70)
    print()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    if not tables:
        print("WARNING: No tables found in database.")
        conn.close()
        return
    
    print(f"Found {len(tables)} table(s): {', '.join(tables)}")
    print()
    
    # View Reports
    if 'reports' in tables:
        print("=" * 70)
        print("REPORTS")
        print("=" * 70)
        cursor.execute("SELECT id, name, description, is_active, created_at FROM reports")
        reports = cursor.fetchall()
        
        if reports:
            print(f"Found {len(reports)} report(s):\n")
            for i, (id, name, desc, active, created) in enumerate(reports, 1):
                status = "[ACTIVE]" if active else "[INACTIVE]"
                print(f"{i}. {name} ({id[:8]}...)")
                print(f"   Status: {status}")
                if desc:
                    print(f"   Description: {desc[:50]}...")
                print(f"   Created: {format_datetime(created)}")
                print()
        else:
            print("No reports found.\n")
    
    # View Report Runs
    if 'report_runs' in tables:
        print("=" * 70)
        print("REPORT RUNS")
        print("=" * 70)
        cursor.execute("""
            SELECT 
                rr.id, 
                r.name,
                rr.status, 
                rr.row_count, 
                rr.started_at,
                rr.finished_at,
                rr.error_message
            FROM report_runs rr
            LEFT JOIN reports r ON rr.report_id = r.id
            ORDER BY rr.started_at DESC
            LIMIT 10
        """)
        runs = cursor.fetchall()
        
        if runs:
            print(f"Last {len(runs)} run(s):\n")
            for i, (run_id, report_name, status, row_count, started, finished, error) in enumerate(runs, 1):
                print(f"{i}. Run {run_id[:8]}...")
                if report_name:
                    print(f"   Report: {report_name}")
                print(f"   Status: {status}")
                if row_count is not None:
                    print(f"   Rows: {row_count}")
                print(f"   Started: {format_datetime(started)}")
                if finished:
                    print(f"   Finished: {format_datetime(finished)}")
                if error:
                    print(f"   Error: {error[:50]}...")
                print()
        else:
            print("No runs found.\n")
    
    # View Notifications
    if 'notification_log' in tables:
        print("=" * 70)
        print("NOTIFICATIONS")
        print("=" * 70)
        cursor.execute("""
            SELECT channel, status, message, sent_at
            FROM notification_log
            ORDER BY sent_at DESC
            LIMIT 5
        """)
        notifications = cursor.fetchall()
        
        if notifications:
            print(f"Last {len(notifications)} notification(s):\n")
            for i, (channel, status, message, sent_at) in enumerate(notifications, 1):
                print(f"{i}. [{channel}] {status}")
                print(f"   {message[:60]}...")
                print(f"   {format_datetime(sent_at)}")
                print()
        else:
            print("No notifications found.\n")
    
    # Database Stats
    print("=" * 70)
    print("DATABASE STATISTICS")
    print("=" * 70)
    
    if 'reports' in tables:
        cursor.execute("SELECT COUNT(*) FROM reports")
        report_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM reports WHERE is_active = 1")
        active_count = cursor.fetchone()[0]
        print(f"Total Reports: {report_count} ({active_count} active)")
    
    if 'report_runs' in tables:
        cursor.execute("SELECT COUNT(*) FROM report_runs")
        run_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM report_runs WHERE status = 'SUCCESS'")
        success_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM report_runs WHERE status = 'FAILED'")
        failed_count = cursor.fetchone()[0]
        print(f"Total Runs: {run_count} ({success_count} successful, {failed_count} failed)")
    
    if 'notification_log' in tables:
        cursor.execute("SELECT COUNT(*) FROM notification_log")
        notif_count = cursor.fetchone()[0]
        print(f"Total Notifications: {notif_count}")
    
    # File size
    file_size = os.path.getsize(DB_FILE)
    print(f"Database File Size: {file_size / 1024:.2f} KB")
    
    print()
    print("=" * 70)
    
    conn.close()

if __name__ == "__main__":
    view_database()
