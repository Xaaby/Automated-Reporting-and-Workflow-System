from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.db import Base

# Use String for UUID to be compatible with both PostgreSQL and SQLite
# SQLite doesn't have native UUID support, so we store as string


class RunStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class NotificationChannel(str, enum.Enum):
    EMAIL = "EMAIL"
    LOG = "LOG"


class NotificationStatus(str, enum.Enum):
    SENT = "SENT"
    FAILED = "FAILED"


class Report(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    sql_query = Column(Text, nullable=False)
    schedule_cron = Column(String(100), nullable=False)
    output_format = Column(String(50), default="CSV")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    runs = relationship("ReportRun", back_populates="report", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Report(id={self.id}, name={self.name}, is_active={self.is_active})>"


class ReportRun(Base):
    __tablename__ = "report_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = Column(String(36), ForeignKey("reports.id"), nullable=False)
    started_at = Column(DateTime, nullable=False)
    finished_at = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False, default=RunStatus.QUEUED.value)
    row_count = Column(Integer, nullable=True)
    output_path = Column(String(500), nullable=True)
    error_message = Column(Text, nullable=True)

    # Relationships
    report = relationship("Report", back_populates="runs")
    notifications = relationship("NotificationLog", back_populates="report_run", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ReportRun(id={self.id}, report_id={self.report_id}, status={self.status})>"


class NotificationLog(Base):
    __tablename__ = "notification_log"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_run_id = Column(String(36), ForeignKey("report_runs.id"), nullable=False)
    channel = Column(String(20), nullable=False)
    sent_at = Column(DateTime, server_default=func.now())
    status = Column(String(20), nullable=False)
    message = Column(Text, nullable=True)

    # Relationships
    report_run = relationship("ReportRun", back_populates="notifications")

    def __repr__(self):
        return f"<NotificationLog(id={self.id}, report_run_id={self.report_run_id}, status={self.status})>"
