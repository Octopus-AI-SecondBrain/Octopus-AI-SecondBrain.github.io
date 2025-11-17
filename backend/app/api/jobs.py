"""
Job Management API Endpoints
Provides job status tracking, listing, and cancellation.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import Optional

from app.services.job_queue import get_job_queue, JobQueue, JobStatus, JobData
from app.schemas.job import (
    JobResponse,
    JobListResponse,
    JobCancelRequest,
    JobCancelResponse,
)
from app.core.logging import get_logger
from app.db.models.user import User
from app.api.auth import get_current_user

logger = get_logger(__name__)
router = APIRouter(tags=["Jobs"])


def _job_to_response(job: JobData) -> JobResponse:
    """Convert JobData to JobResponse"""
    return JobResponse(
        job_id=job.job_id,
        user_id=job.user_id,
        job_type=job.job_type,
        status=job.status,
        total_items=job.total_items,
        processed_items=job.processed_items,
        failed_items=job.failed_items,
        progress=job.progress,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        duration_seconds=job.duration_seconds,
        error_message=job.error_message,
        retry_count=job.retry_count,
        result=job.result,
        metadata=job.metadata,
    )


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
    job_queue: JobQueue = Depends(get_job_queue),
) -> JobResponse:
    """
    Get status of a specific job.

    Args:
        job_id: Job identifier
        current_user: Authenticated user
        job_queue: Job queue service

    Returns:
        Job status and progress information

    Raises:
        404: Job not found
        403: User doesn't own this job
    """
    job = await job_queue.get_job(job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found",
        )

    # Check authorization
    if job.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this job",
        )

    return _job_to_response(job)


@router.get("/jobs", response_model=JobListResponse)
async def list_user_jobs(
    limit: int = 50,
    status_filter: Optional[JobStatus] = None,
    current_user: User = Depends(get_current_user),
    job_queue: JobQueue = Depends(get_job_queue),
) -> JobListResponse:
    """
    List all jobs for the authenticated user.

    Args:
        limit: Maximum number of jobs to return (default: 50)
        status_filter: Optional filter by job status
        current_user: Authenticated user
        job_queue: Job queue service

    Returns:
        List of user's jobs
    """
    jobs = await job_queue.list_user_jobs(
        user_id=current_user.id,
        limit=min(limit, 100),  # Cap at 100
        status_filter=status_filter,
    )

    return JobListResponse(
        jobs=[_job_to_response(job) for job in jobs],
        total=len(jobs),
    )


@router.post("/jobs/{job_id}/cancel", response_model=JobCancelResponse)
async def cancel_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    job_queue: JobQueue = Depends(get_job_queue),
) -> JobCancelResponse:
    """
    Cancel a pending or processing job.

    Args:
        job_id: Job identifier
        current_user: Authenticated user
        job_queue: Job queue service

    Returns:
        Cancellation status

    Raises:
        404: Job not found
        403: User doesn't own this job
        400: Job cannot be cancelled (already completed/failed/cancelled)
    """
    job = await job_queue.get_job(job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found",
        )

    # Check authorization
    if job.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to cancel this job",
        )

    # Check if job can be cancelled
    if job.is_terminal:
        return JobCancelResponse(
            success=False,
            message=f"Job cannot be cancelled: already {job.status.value}",
            job=_job_to_response(job),
        )

    # Cancel the job
    updated_job = await job_queue.cancel_job(job_id)

    if not updated_job:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel job",
        )

    logger.info(f"Job cancelled by user: {job_id} (user={current_user.id})")

    return JobCancelResponse(
        success=True,
        message="Job cancelled successfully",
        job=_job_to_response(updated_job),
    )


@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    job_queue: JobQueue = Depends(get_job_queue),
) -> None:
    """
    Delete a job record (for completed/failed jobs).

    Args:
        job_id: Job identifier
        current_user: Authenticated user
        job_queue: Job queue service

    Raises:
        404: Job not found
        403: User doesn't own this job
        400: Job is still processing
    """
    job = await job_queue.get_job(job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found",
        )

    # Check authorization
    if job.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this job",
        )

    # Only allow deletion of terminal jobs
    if not job.is_terminal:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete job that is still processing. Cancel it first.",
        )

    # Delete from Redis
    from app.core.redis import get_redis

    redis = await get_redis()
    job_key = f"job:{job_id}"
    await redis.delete(job_key)

    logger.info(f"Job deleted by user: {job_id} (user={current_user.id})")
