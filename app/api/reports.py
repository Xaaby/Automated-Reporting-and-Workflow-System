from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from pydantic import BaseModel

from app.db import get_db
from app.models import Report
from app.services.scheduler import schedule_report, reload_scheduler

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
    id: UUID
    name: str
    description: str = None
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
    reports = db.query(Report).offset(skip).limit(limit).all()
    return reports


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(report_id: UUID, db: Session = Depends(get_db)):
    """
    Get a specific report by ID.
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with id {report_id} not found"
        )
    return report


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(report_data: ReportCreate, db: Session = Depends(get_db)):
    """
    Create a new report definition.
    """
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
    if report.is_active:
        schedule_report(report)
    
    return report


@router.put("/{report_id}", response_model=ReportResponse)
def update_report(
    report_id: UUID,
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
    
    return report
