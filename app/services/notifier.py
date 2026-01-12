from datetime import datetime
from sqlalchemy.orm import Session

from app.models import ReportRun, NotificationLog, NotificationChannel, NotificationStatus
import os


def send_notification(db: Session, report_run: ReportRun):
    """
    Send notification for a report run.
    Currently implements log-based notifications.
    Future: Can be extended to send emails via SMTP.
    
    Args:
        db: Database session
        report_run: ReportRun object to send notification for
    """
    # Determine notification message based on status
    if report_run.status.value == "SUCCESS":
        message = (
            f"Report '{report_run.report.name}' completed successfully. "
            f"Rows exported: {report_run.row_count}. "
            f"Output: {report_run.output_path}"
        )
        status = NotificationStatus.SENT
    elif report_run.status.value == "FAILED":
        message = (
            f"Report '{report_run.report.name}' failed. "
            f"Error: {report_run.error_message}"
        )
        status = NotificationStatus.SENT  # Still log it as "sent" to notification log
    else:
        message = f"Report '{report_run.report.name}' status: {report_run.status.value}"
        status = NotificationStatus.SENT
    
    # Create notification log entry
    notification = NotificationLog(
        report_run_id=report_run.id,
        channel=NotificationChannel.LOG,
        status=status,
        message=message
    )
    
    db.add(notification)
    db.commit()
    
    # Future: Add SMTP email notification here
    # if os.getenv("SMTP_HOST"):
    #     send_email_notification(report_run, message)
    
    return notification


def send_email_notification(report_run: ReportRun, message: str):
    """
    Send email notification via SMTP.
    Placeholder for future implementation.
    
    Args:
        report_run: ReportRun object
        message: Notification message
    """
    # TODO: Implement SMTP email sending
    # This would use smtplib to send emails to configured recipients
    pass
