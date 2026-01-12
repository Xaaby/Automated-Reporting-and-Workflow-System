from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from uuid import UUID
import logging

from app.db import SessionLocal
from app.models import Report
from app.services.runner import execute_report

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = BackgroundScheduler()


def trigger_report(report_id):
    """
    Trigger a report execution (called by scheduler).
    
    Args:
        report_id: UUID string of the report to execute
    """
    db = SessionLocal()
    try:
        logger.info(f"Triggering report execution for report_id: {report_id}")
        # Convert string to UUID if needed, or use string directly
        from uuid import UUID as UUIDType
        if isinstance(report_id, str):
            report_id_uuid = report_id
        else:
            report_id_uuid = str(report_id)
        execute_report(db, report_id_uuid)
    except Exception as e:
        logger.error(f"Error executing report {report_id}: {str(e)}")
    finally:
        db.close()


def schedule_report(report: Report):
    """
    Schedule a single report based on its cron expression.
    
    Args:
        report: Report model instance
    """
    try:
        # Ensure scheduler is running
        if not scheduler.running:
            logger.warning("Scheduler is not running. Starting scheduler...")
            scheduler.start()
        
        # Parse cron expression (format: "minute hour day month day_of_week")
        cron_parts = report.schedule_cron.split()
        if len(cron_parts) != 5:
            logger.error(f"Invalid cron expression for report {report.id}: {report.schedule_cron}")
            return
        
        minute, hour, day, month, day_of_week = cron_parts
        
        # Create cron trigger
        trigger = CronTrigger(
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            day_of_week=day_of_week
        )
        
        # Add job to scheduler
        scheduler.add_job(
            func=trigger_report,
            trigger=trigger,
            args=[report.id],
            id=str(report.id),
            name=report.name,
            replace_existing=True
        )
        
        logger.info(f"Scheduled report '{report.name}' (ID: {report.id}) with cron: {report.schedule_cron}")
        
    except Exception as e:
        logger.error(f"Error scheduling report {report.id}: {str(e)}")
        # Don't re-raise - let report creation succeed even if scheduling fails


def load_and_schedule_reports():
    """
    Load all active reports from database and schedule them.
    """
    db = SessionLocal()
    try:
        active_reports = db.query(Report).filter(Report.is_active == True).all()
        
        logger.info(f"Loading {len(active_reports)} active reports")
        
        for report in active_reports:
            schedule_report(report)
            
    except Exception as e:
        logger.error(f"Error loading reports: {str(e)}")
    finally:
        db.close()


def start_scheduler():
    """
    Start the scheduler and load all active reports.
    """
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")
        load_and_schedule_reports()
    else:
        logger.warning("Scheduler is already running")


def stop_scheduler():
    """
    Stop the scheduler gracefully.
    """
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
    else:
        logger.warning("Scheduler is not running")


def reload_scheduler():
    """
    Reload all reports from database and reschedule them.
    Useful when reports are added, updated, or deleted.
    """
    # Remove all existing jobs
    scheduler.remove_all_jobs()
    
    # Reload and schedule
    load_and_schedule_reports()
