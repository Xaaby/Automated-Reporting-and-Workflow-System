from datetime import datetime
from sqlalchemy.orm import Session
from uuid import UUID

from app.models import Report, ReportRun, RunStatus
from app.services.exporter import export_to_csv
from app.services.notifier import send_notification
import os


def execute_report(db: Session, report_id: UUID, output_dir: str = None) -> ReportRun:
    """
    Execute a report: run SQL query, export to CSV, and track the run.
    
    Args:
        db: Database session
        report_id: UUID of the report to execute
        output_dir: Directory for output files (defaults to ./outputs)
    
    Returns:
        ReportRun object with execution results
    """
    if output_dir is None:
        output_dir = os.getenv("OUTPUT_DIR", "./outputs")
    
    # Get report
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise ValueError(f"Report with id {report_id} not found")
    
    # Create run record with QUEUED status
    report_run = ReportRun(
        report_id=str(report_id),
        started_at=datetime.now(),
        status=RunStatus.QUEUED.value
    )
    db.add(report_run)
    db.commit()
    db.refresh(report_run)
    
    try:
        # Update status to RUNNING
        report_run.status = RunStatus.RUNNING.value
        db.commit()
        
        # Execute query and export to CSV
        output_path, row_count = export_to_csv(
            db=db,
            sql_query=report.sql_query,
            output_dir=output_dir,
            report_name=report.name
        )
        
        # Update run with success details
        report_run.status = RunStatus.SUCCESS.value
        report_run.finished_at = datetime.now()
        report_run.row_count = row_count
        report_run.output_path = output_path
        db.commit()
        db.refresh(report_run)
        
        # Ensure report relationship is loaded
        _ = report_run.report
        
        # Send notification
        send_notification(db, report_run)
        
    except Exception as e:
        # Update run with failure details
        report_run.status = RunStatus.FAILED.value
        report_run.finished_at = datetime.now()
        report_run.error_message = str(e)
        db.commit()
        db.refresh(report_run)
        
        # Ensure report relationship is loaded
        _ = report_run.report
        
        # Send failure notification
        send_notification(db, report_run)
        
        # Re-raise to allow caller to handle
        raise
    
    return report_run
