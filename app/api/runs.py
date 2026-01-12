from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import os

from app.db import get_db
from app.models import Report, ReportRun, RunStatus
from app.services.runner import execute_report

router = APIRouter(prefix="/api", tags=["runs"])


# Pydantic models for response
class ReportRunResponse(BaseModel):
    id: str  # Changed from UUID to str for SQLite compatibility
    report_id: str  # Changed from UUID to str for SQLite compatibility
    started_at: str
    finished_at: Optional[str] = None
    status: str
    row_count: Optional[int] = None
    output_path: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


@router.post("/reports/{report_id}/run", response_model=ReportRunResponse, status_code=status.HTTP_201_CREATED)
def trigger_manual_run(report_id: str, db: Session = Depends(get_db)):  # Changed from UUID to str
    """
    Trigger a manual run of a report.
    """
    try:
        # Check if report exists
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report with id {report_id} not found"
            )
        
        # Execute the report
        report_run = execute_report(db, report_id)
        # Convert to response format manually to ensure proper serialization
        return ReportRunResponse(
            id=str(report_run.id),
            report_id=str(report_run.report_id),
            started_at=report_run.started_at.isoformat() if report_run.started_at else "",
            finished_at=report_run.finished_at.isoformat() if report_run.finished_at else None,
            status=report_run.status if isinstance(report_run.status, str) else report_run.status.value,
            row_count=report_run.row_count,
            output_path=report_run.output_path,
            error_message=report_run.error_message
        )
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        if "connection" in error_msg.lower() or "database" in error_msg.lower():
            error_msg = f"Database connection error: {error_msg}. Please check your database configuration."
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )


@router.get("/reports/{report_id}/runs", response_model=List[ReportRunResponse])
def get_report_runs(
    report_id: str,  # Changed from UUID to str
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get run history for a specific report.
    """
    try:
        # Check if report exists
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report with id {report_id} not found"
            )
        
        runs = (
            db.query(ReportRun)
            .filter(ReportRun.report_id == report_id)
            .order_by(ReportRun.started_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        # Convert to response format manually to ensure proper serialization
        return [
            ReportRunResponse(
                id=str(r.id),
                report_id=str(r.report_id),
                started_at=r.started_at.isoformat() if r.started_at else "",
                finished_at=r.finished_at.isoformat() if r.finished_at else None,
                status=r.status if isinstance(r.status, str) else r.status.value,
                row_count=r.row_count,
                output_path=r.output_path,
                error_message=r.error_message
            )
            for r in runs
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}. Please check your database configuration."
        )


@router.get("/runs/{run_id}", response_model=ReportRunResponse)
def get_run_details(run_id: str, db: Session = Depends(get_db)):  # Changed from UUID to str
    """
    Get details of a specific run.
    """
    run = db.query(ReportRun).filter(ReportRun.id == run_id).first()
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Run with id {run_id} not found"
        )
    
    # Convert to response format manually to ensure proper serialization
    return ReportRunResponse(
        id=str(run.id),
        report_id=str(run.report_id),
        started_at=run.started_at.isoformat() if run.started_at else "",
        finished_at=run.finished_at.isoformat() if run.finished_at else None,
        status=run.status if isinstance(run.status, str) else run.status.value,
        row_count=run.row_count,
        output_path=run.output_path,
        error_message=run.error_message
    )


@router.get("/runs/{run_id}/download")
def download_run_output(run_id: str, db: Session = Depends(get_db)):  # Changed from UUID to str
    """
    Download the CSV output file for a specific run.
    """
    run = db.query(ReportRun).filter(ReportRun.id == run_id).first()
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Run with id {run_id} not found"
        )
    
    # Handle both enum and string status values
    run_status = run.status if isinstance(run.status, str) else run.status.value
    if run_status != RunStatus.SUCCESS.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Run {run_id} did not complete successfully. Status: {run_status}"
        )
    
    if not run.output_path or not os.path.exists(run.output_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Output file not found for run {run_id}"
        )
    
    # Extract filename from path
    filename = os.path.basename(run.output_path)
    
    return FileResponse(
        path=run.output_path,
        filename=filename,
        media_type="text/csv"
    )
