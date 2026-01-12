from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
import logging
import traceback

from app.db import get_db
from app.models import Report
from app.services.scheduler import schedule_report, reload_scheduler

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reports", tags=["reports"])


# Pydantic models for request/response
class ReportCreate(BaseModel):
    name: str
    description: str = None
    sql_query: str
    schedule_cron: str
    output_format: str = "CSV"
    is_active: bool = True


class ReportUpdate(BaseModel):
    name: str = None
    description: str = None
    sql_query: str = None
    schedule_cron: str = None
    output_format: str = None
    is_active: bool = None


class ReportResponse(BaseModel):
    id: str  # Changed from UUID to str for SQLite compatibility
    name: str
    description: Optional[str] = None  # Allow None for optional description
    sql_query: str
    schedule_cron: str
    output_format: str
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True


@router.get("", response_model=List[ReportResponse])
def list_reports(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    List all reports.
    """
    try:
        reports = db.query(Report).offset(skip).limit(limit).all()
        # Convert to response format manually to ensure proper serialization
        result = []
        for r in reports:
            # Handle None description explicitly
            desc = r.description if r.description is not None else None
            result.append(ReportResponse(
                id=str(r.id),
                name=r.name,
                description=desc,
                sql_query=r.sql_query,
                schedule_cron=r.schedule_cron,
                output_format=r.output_format,
                is_active=r.is_active,
                created_at=r.created_at.isoformat() if r.created_at else ""
            ))
        return result
    except Exception as e:
        error_msg = str(e)
        if "connection" in error_msg.lower() or "database" in error_msg.lower() or "operational" in error_msg.lower():
            error_msg = f"Database connection error: {error_msg}. Please check your database configuration."
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(report_id: str, db: Session = Depends(get_db)):  # Changed from UUID to str
    """
    Get a specific report by ID.
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with id {report_id} not found"
        )
    # Convert to response format manually to ensure proper serialization
    return ReportResponse(
        id=str(report.id),
        name=report.name,
        description=report.description if report.description else None,
        sql_query=report.sql_query,
        schedule_cron=report.schedule_cron,
        output_format=report.output_format,
        is_active=report.is_active,
        created_at=report.created_at.isoformat() if report.created_at else ""
    )


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(report_data: ReportCreate, db: Session = Depends(get_db)):
    """
    Create a new report definition.
    """
    try:
        # Create new report
        report = Report(
            name=report_data.name,
            description=report_data.description,
            sql_query=report_data.sql_query,
            schedule_cron=report_data.schedule_cron,
            output_format=report_data.output_format,
            is_active=report_data.is_active
        )
        
        db.add(report)
        db.commit()
        db.refresh(report)
        
        # Schedule the report if it's active
        # Wrap in try-except to prevent scheduling errors from breaking report creation
        if report.is_active:
            try:
                schedule_report(report)
            except Exception as e:
                logger.warning(f"Could not schedule report {report.id}: {str(e)}")
                # Don't fail the entire request if scheduling fails
        
        # Convert to response format manually to ensure proper serialization
        return ReportResponse(
            id=str(report.id),
            name=report.name,
            description=report.description if report.description else None,  # Handle None properly
            sql_query=report.sql_query,
            schedule_cron=report.schedule_cron,
            output_format=report.output_format,
            is_active=report.is_active,
            created_at=report.created_at.isoformat() if report.created_at else ""
        )
    except Exception as e:
        error_msg = str(e)
        if "connection" in error_msg.lower() or "database" in error_msg.lower() or "operational" in error_msg.lower():
            error_msg = f"Database connection error: {error_msg}. Please check your database configuration."
        logger.error(f"Error creating report: {error_msg}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )


@router.put("/{report_id}", response_model=ReportResponse)
def update_report(
    report_id: str,  # Changed from UUID to str
    report_data: ReportUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a report definition. Can be used to enable/disable reports.
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with id {report_id} not found"
        )
    
    # Update fields if provided
    if report_data.name is not None:
        report.name = report_data.name
    if report_data.description is not None:
        report.description = report_data.description
    if report_data.sql_query is not None:
        report.sql_query = report_data.sql_query
    if report_data.schedule_cron is not None:
        report.schedule_cron = report_data.schedule_cron
    if report_data.output_format is not None:
        report.output_format = report_data.output_format
    if report_data.is_active is not None:
        report.is_active = report_data.is_active
    
    db.commit()
    db.refresh(report)
    
    # Reload scheduler to pick up changes
    reload_scheduler()
    
    # Convert to response format manually to ensure proper serialization
    return ReportResponse(
        id=str(report.id),
        name=report.name,
        description=report.description if report.description else None,
        sql_query=report.sql_query,
        schedule_cron=report.schedule_cron,
        output_format=report.output_format,
        is_active=report.is_active,
        created_at=report.created_at.isoformat() if report.created_at else ""
    )
