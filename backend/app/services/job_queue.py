"""
Job Queue Service for async task processing.
Handles document ingestion, embedding generation, and other long-running tasks.
"""
import uuid
import json
import logging
from enum import Enum
from typing import Optional, Any
from datetime import datetime, timedelta

from pydantic import BaseModel, Field

from app.core.redis import get_redis
from app.core.settings import get_settings

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    """Job execution status"""

    PENDING = "pending"  # Job created, not started
    PROCESSING = "processing"  # Job is being processed
    COMPLETED = "completed"  # Job finished successfully
    FAILED = "failed"  # Job failed with error
    CANCELLED = "cancelled"  # Job was cancelled by user


class JobType(str, Enum):
    """Types of jobs supported"""

    INGEST_FILE = "ingest_file"  # File ingestion job
    INGEST_TEXT = "ingest_text"  # Text ingestion job
    BATCH_INGEST = "batch_ingest"  # Batch file ingestion
    REINDEX = "reindex"  # Re-index all documents
    DELETE_DOCUMENTS = "delete_documents"  # Bulk document deletion


class JobData(BaseModel):
    """Job metadata and state"""

    job_id: str = Field(..., description="Unique job identifier")
    user_id: int = Field(..., description="User who created the job")
    job_type: JobType = Field(..., description="Type of job")
    status: JobStatus = Field(default=JobStatus.PENDING, description="Current status")

    # Progress tracking
    total_items: int = Field(default=1, ge=0, description="Total items to process")
    processed_items: int = Field(default=0, ge=0, description="Items processed so far")
    failed_items: int = Field(default=0, ge=0, description="Items that failed")

    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Error handling
    error_message: Optional[str] = None
    retry_count: int = Field(default=0, ge=0, description="Number of retry attempts")
    max_retries: int = Field(default=3, ge=0, description="Max retry attempts allowed")

    # Result data
    result: Optional[dict[str, Any]] = None
    metadata: dict[str, Any] = Field(default_factory=dict, description="Job metadata")

    @property
    def progress(self) -> float:
        """Calculate progress percentage (0.0 to 1.0)"""
        if self.total_items == 0:
            return 0.0
        return min(self.processed_items / self.total_items, 1.0)

    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate job duration in seconds"""
        if not self.started_at:
            return None
        end_time = self.completed_at or datetime.utcnow()
        return (end_time - self.started_at).total_seconds()

    @property
    def is_terminal(self) -> bool:
        """Check if job is in terminal state (completed, failed, cancelled)"""
        return self.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED)


class JobQueue:
    """
    Job queue manager with Redis backend.
    Handles job lifecycle: creation, status updates, completion, and cleanup.
    """

    def __init__(self):
        self._settings = get_settings()
        self._redis_settings = self._settings.redis

    @staticmethod
    def _job_key(job_id: str) -> str:
        """Generate Redis key for job"""
        return f"job:{job_id}"

    @staticmethod
    def _user_jobs_key(user_id: int) -> str:
        """Generate Redis key for user's job list"""
        return f"user:{user_id}:jobs"

    @staticmethod
    def _queue_key(job_type: JobType) -> str:
        """Generate Redis key for job type queue"""
        return f"queue:{job_type.value}"

    async def create_job(
        self,
        user_id: int,
        job_type: JobType,
        total_items: int = 1,
        metadata: Optional[dict[str, Any]] = None,
    ) -> JobData:
        """
        Create a new job and add to queue.

        Args:
            user_id: User creating the job
            job_type: Type of job
            total_items: Total number of items to process
            metadata: Additional job metadata

        Returns:
            Created job data
        """
        job_id = str(uuid.uuid4())

        job = JobData(
            job_id=job_id,
            user_id=user_id,
            job_type=job_type,
            total_items=total_items,
            max_retries=self._redis_settings.max_retries,
            metadata=metadata or {},
        )

        # Store job in Redis
        redis = await get_redis()
        job_key = self._job_key(job_id)
        await redis.set_json(job_key, job.model_dump(mode="json"), ttl=self._redis_settings.job_ttl)

        # Add to user's job list
        user_jobs_key = self._user_jobs_key(user_id)
        await redis.lpush(user_jobs_key, job_id)

        # Add to processing queue
        queue_key = self._queue_key(job_type)
        await redis.rpush(queue_key, job_id)

        logger.info(f"Job created: {job_id} (type={job_type}, user={user_id})")
        return job

    async def get_job(self, job_id: str) -> Optional[JobData]:
        """
        Get job by ID.

        Args:
            job_id: Job identifier

        Returns:
            Job data or None if not found
        """
        redis = await get_redis()
        job_key = self._job_key(job_id)
        job_dict = await redis.get_json(job_key)

        if not job_dict:
            return None

        # Convert datetime strings to datetime objects
        for date_field in ("created_at", "started_at", "completed_at"):
            if job_dict.get(date_field):
                job_dict[date_field] = datetime.fromisoformat(job_dict[date_field].replace("Z", "+00:00"))

        return JobData(**job_dict)

    async def update_job(self, job: JobData) -> bool:
        """
        Update job data in Redis.

        Args:
            job: Job data to update

        Returns:
            True if update successful
        """
        redis = await get_redis()
        job_key = self._job_key(job.job_id)

        # Update job data
        success = await redis.set_json(
            job_key, job.model_dump(mode="json"), ttl=self._redis_settings.job_ttl
        )

        if success:
            logger.debug(f"Job updated: {job.job_id} (status={job.status}, progress={job.progress:.1%})")

        return success

    async def start_job(self, job_id: str) -> Optional[JobData]:
        """
        Mark job as started.

        Args:
            job_id: Job identifier

        Returns:
            Updated job data or None if not found
        """
        job = await self.get_job(job_id)
        if not job:
            logger.warning(f"Cannot start job {job_id}: not found")
            return None

        job.status = JobStatus.PROCESSING
        job.started_at = datetime.utcnow()

        await self.update_job(job)
        logger.info(f"Job started: {job_id}")
        return job

    async def update_progress(
        self,
        job_id: str,
        processed_items: Optional[int] = None,
        failed_items: Optional[int] = None,
        increment: bool = False,
    ) -> Optional[JobData]:
        """
        Update job progress.

        Args:
            job_id: Job identifier
            processed_items: Number of items processed (or increment if increment=True)
            failed_items: Number of failed items (or increment if increment=True)
            increment: If True, add to existing counts; if False, set absolute values

        Returns:
            Updated job data or None if not found
        """
        job = await self.get_job(job_id)
        if not job:
            logger.warning(f"Cannot update progress for job {job_id}: not found")
            return None

        if processed_items is not None:
            if increment:
                job.processed_items += processed_items
            else:
                job.processed_items = processed_items

        if failed_items is not None:
            if increment:
                job.failed_items += failed_items
            else:
                job.failed_items = failed_items

        await self.update_job(job)
        return job

    async def complete_job(
        self,
        job_id: str,
        result: Optional[dict[str, Any]] = None,
    ) -> Optional[JobData]:
        """
        Mark job as completed successfully.

        Args:
            job_id: Job identifier
            result: Job result data

        Returns:
            Updated job data or None if not found
        """
        job = await self.get_job(job_id)
        if not job:
            logger.warning(f"Cannot complete job {job_id}: not found")
            return None

        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        job.result = result or {}
        job.processed_items = job.total_items  # Ensure progress is 100%

        # Store with shorter TTL for completed jobs
        redis = await get_redis()
        job_key = self._job_key(job_id)
        await redis.set_json(
            job_key, job.model_dump(mode="json"), ttl=self._redis_settings.job_result_ttl
        )

        logger.info(
            f"Job completed: {job_id} (duration={job.duration_seconds:.1f}s, "
            f"items={job.processed_items}, failed={job.failed_items})"
        )
        return job

    async def fail_job(
        self,
        job_id: str,
        error_message: str,
        should_retry: bool = True,
    ) -> Optional[JobData]:
        """
        Mark job as failed.

        Args:
            job_id: Job identifier
            error_message: Error description
            should_retry: Whether job should be retried

        Returns:
            Updated job data or None if not found
        """
        job = await self.get_job(job_id)
        if not job:
            logger.warning(f"Cannot fail job {job_id}: not found")
            return None

        job.error_message = error_message
        job.retry_count += 1

        # Check if job should be retried
        if should_retry and job.retry_count <= job.max_retries:
            job.status = JobStatus.PENDING
            logger.warning(
                f"Job failed, will retry: {job_id} "
                f"(attempt {job.retry_count}/{job.max_retries}): {error_message}"
            )

            # Re-queue with exponential backoff delay
            queue_key = self._queue_key(job.job_type)
            redis = await get_redis()

            # Simple delay simulation: just re-add to queue
            # (In production, use Redis Sorted Sets with timestamp for delayed execution)
            await redis.rpush(queue_key, job_id)

        else:
            job.status = JobStatus.FAILED
            job.completed_at = datetime.utcnow()
            logger.error(
                f"Job failed permanently: {job_id} "
                f"(attempts={job.retry_count}): {error_message}"
            )

        await self.update_job(job)
        return job

    async def cancel_job(self, job_id: str) -> Optional[JobData]:
        """
        Cancel a pending or processing job.

        Args:
            job_id: Job identifier

        Returns:
            Updated job data or None if not found
        """
        job = await self.get_job(job_id)
        if not job:
            logger.warning(f"Cannot cancel job {job_id}: not found")
            return None

        if job.is_terminal:
            logger.warning(f"Cannot cancel job {job_id}: already in terminal state {job.status}")
            return job

        job.status = JobStatus.CANCELLED
        job.completed_at = datetime.utcnow()

        await self.update_job(job)
        logger.info(f"Job cancelled: {job_id}")
        return job

    async def list_user_jobs(
        self,
        user_id: int,
        limit: int = 50,
        status_filter: Optional[JobStatus] = None,
    ) -> list[JobData]:
        """
        List jobs for a user.

        Args:
            user_id: User ID
            limit: Maximum number of jobs to return
            status_filter: Optional status filter

        Returns:
            List of job data
        """
        redis = await get_redis()
        user_jobs_key = self._user_jobs_key(user_id)

        # Get job IDs for user
        job_ids = await redis.lrange(user_jobs_key, 0, limit - 1)

        jobs = []
        for job_id in job_ids:
            job = await self.get_job(job_id)
            if job and (status_filter is None or job.status == status_filter):
                jobs.append(job)

        return jobs

    async def cleanup_old_jobs(self, max_age_hours: int = 24) -> int:
        """
        Clean up old completed/failed jobs.

        Args:
            max_age_hours: Maximum age in hours for jobs to keep

        Returns:
            Number of jobs cleaned up
        """
        # Redis TTL handles automatic cleanup
        # This method is for manual cleanup if needed
        logger.info(f"Job cleanup triggered (max_age={max_age_hours}h)")

        redis = await get_redis()
        cleaned = 0

        # Scan all job keys
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        job_keys = await redis.scan("job:*")

        for job_key in job_keys:
            job_dict = await redis.get_json(job_key)
            if not job_dict:
                continue

            # Parse completed_at timestamp
            completed_at_str = job_dict.get("completed_at")
            if not completed_at_str:
                continue

            completed_at = datetime.fromisoformat(completed_at_str.replace("Z", "+00:00"))

            # Delete if old enough and in terminal state
            status = job_dict.get("status")
            if (
                status in ("completed", "failed", "cancelled")
                and completed_at < cutoff_time
            ):
                await redis.delete(job_key)
                cleaned += 1

        logger.info(f"Job cleanup completed: {cleaned} jobs removed")
        return cleaned


# Global job queue instance
_job_queue: Optional[JobQueue] = None


async def get_job_queue() -> JobQueue:
    """Get job queue instance (singleton)"""
    global _job_queue
    if _job_queue is None:
        _job_queue = JobQueue()
    return _job_queue
