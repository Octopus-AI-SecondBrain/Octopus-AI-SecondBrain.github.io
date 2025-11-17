"""
Octopus AI Second Brain - Ingestion Job Model
Tracks document ingestion jobs for async processing.
"""
from datetime import datetime
from typing import Optional
import enum

from sqlalchemy import String, Text, DateTime, Integer, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ..session import Base


class JobStatus(str, enum.Enum):
    """Job status enumeration"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class IngestionJob(Base):
    """Ingestion job model for async document processing"""

    __tablename__ = "ingestion_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("sources.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Job info
    status: Mapped[JobStatus] = mapped_column(
        SQLEnum(JobStatus, native_enum=False), default=JobStatus.PENDING, nullable=False, index=True
    )
    job_type: Mapped[str] = mapped_column(String(50), nullable=False)  # file_upload, url_scrape, etc.
    
    # Progress tracking
    total_documents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    processed_documents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Results and errors
    result_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Job metadata
    job_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="ingestion_jobs")
    source = relationship("Source", back_populates="ingestion_jobs")

    def __repr__(self) -> str:
        return (
            f"<IngestionJob(id={self.id}, status={self.status}, "
            f"progress={self.processed_documents}/{self.total_documents})>"
        )
