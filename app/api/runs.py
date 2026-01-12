from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from pydantic import BaseModel
import os

from app.db import get_db
from app.models import Report, ReportRun, RunStatus
from app.services.runner import execute_report

router = APIRouter(prefix="/api", tags=["runs"])


# Pydantic models for response
class ReportRunResponse(BaseModel):
    id: UUID
    report_id: UUID
    started_at: str
    finished_at: str = None
    status: str
    row_count: int = None
    output_path: str = None
    error_message: str = None

    class Config:
        from_attributes = True


@router.post("/reports/{report_id}/run", response_model=ReportRunResponse, status_code=status.HTTP_201_CREATED)
def trigger_manual_run(report_id: UUID, db: Session = Depends(get_db)):
    """
    Trigger a manual run of a report.
    """
    # Check if report exists
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with id {report_id} not found"
        )
    
    try:
        # Execute the report
        report_run = execute_report(db, report_id)
        return report_run
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing report: {str(e)}"
        )


@router.get("/reports/{report_id}/runs", response_model=List[ReportRunResponse])
def get_report_runs(
    report_id: UUID,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get run history for a specific report.
    """
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
    
    return runs


@router.get("/runs/{run_id}", response_model=ReportRunResponse)
def get_run_details(run_id: UUID, db: Session = Depends(get_db)):
    """
    Get details of a specific run.
    """
    run = db.query(ReportRun).filter(ReportRun.id == run_id).first()
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Run with id {run_id} not found"
        )
    
    return run


@router.get("/runs/{run_id}/download")
def download_run_output(run_id: UUID, db: Session = Depends(get_db)):
    """
    Download the CSV output file for a specific run.
    """
    run = db.query(ReportRun).filter(ReportRun.id == run_id).first()
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Run with id {run_id} not found"
        )
    
    if run.status != RunStatus.SUCCESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Run {run_id} did not complete successfully. Status: {run.status.value}"
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
