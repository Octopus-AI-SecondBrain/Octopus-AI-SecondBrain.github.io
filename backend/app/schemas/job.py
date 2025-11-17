"""
Job-related API schemas
"""
from typing import Optional, Any
from datetime import datetime

from pydantic import BaseModel, Field

from app.services.job_queue import JobStatus, JobType


class JobResponse(BaseModel):
    """Job status response"""

    job_id: str = Field(..., description="Unique job identifier")
    user_id: int = Field(..., description="User who created the job")
    job_type: JobType = Field(..., description="Type of job")
    status: JobStatus = Field(..., description="Current job status")

    # Progress
    total_items: int = Field(..., description="Total items to process")
    processed_items: int = Field(..., description="Items processed so far")
    failed_items: int = Field(..., description="Items that failed")
    progress: float = Field(..., ge=0.0, le=1.0, description="Progress (0.0 to 1.0)")

    # Timing
    created_at: datetime = Field(..., description="Job creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Job start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Job completion timestamp")
    duration_seconds: Optional[float] = Field(None, description="Job duration in seconds")

    # Error info
    error_message: Optional[str] = Field(None, description="Error message if failed")
    retry_count: int = Field(..., description="Number of retry attempts")

    # Result
    result: Optional[dict[str, Any]] = Field(None, description="Job result data")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Job metadata")


class JobListResponse(BaseModel):
    """List of jobs response"""

    jobs: list[JobResponse] = Field(..., description="List of jobs")
    total: int = Field(..., description="Total number of jobs")


class JobCancelRequest(BaseModel):
    """Request to cancel a job"""

    job_id: str = Field(..., description="Job ID to cancel")


class JobCancelResponse(BaseModel):
    """Job cancellation response"""

    success: bool = Field(..., description="Whether cancellation succeeded")
    message: str = Field(..., description="Status message")
    job: Optional[JobResponse] = Field(None, description="Updated job data")
