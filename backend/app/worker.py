"""
Background Worker for Processing Jobs
Processes ingestion jobs from the queue asynchronously.
"""
import asyncio
import logging
import signal
import sys
from typing import Optional
from contextlib import asynccontextmanager

from app.core.logging import setup_logging, get_logger
from app.core.settings import get_settings
from app.core.redis import get_redis, close_redis
from app.services.job_queue import get_job_queue, JobQueue, JobData, JobStatus, JobType
from app.services.rag_service import RAGService
from app.db.session import async_session_maker

setup_logging()
logger = get_logger(__name__)


class JobWorker:
    """
    Background worker that processes jobs from Redis queue.
    """

    def __init__(self):
        self._running = False
        self._settings = get_settings()
        self._poll_interval = 2  # seconds
        self._max_concurrent_jobs = 5

    async def process_ingest_file_job(self, job: JobData) -> dict:
        """
        Process file ingestion job.

        Args:
            job: Job data containing file path and metadata

        Returns:
            Processing result

        Raises:
            Exception: If processing fails
        """
        file_path = job.metadata.get("file_path")
        user_id = job.user_id

        if not file_path:
            raise ValueError("Missing file_path in job metadata")

        logger.info(f"Processing file ingestion: {file_path} (job={job.job_id})")

        # Get database session
        async with async_session_maker() as db:
            # Initialize RAG service
            rag_service = RAGService(db)

            # Process the file
            result = await rag_service.ingest_file(
                file_path=file_path,
                user_id=user_id,
            )

            # Update progress to 100%
            job_queue = await get_job_queue()
            await job_queue.update_progress(job.job_id, processed_items=1)

            return {
                "documents_created": result.get("documents_created", 0),
                "chunks_created": result.get("chunks_created", 0),
                "embeddings_created": result.get("embeddings_created", 0),
                "file_path": file_path,
            }

    async def process_ingest_text_job(self, job: JobData) -> dict:
        """
        Process text ingestion job.

        Args:
            job: Job data containing text content and metadata

        Returns:
            Processing result

        Raises:
            Exception: If processing fails
        """
        title = job.metadata.get("title", "Untitled")
        content = job.metadata.get("content")
        user_id = job.user_id

        if not content:
            raise ValueError("Missing content in job metadata")

        logger.info(f"Processing text ingestion: {title} (job={job.job_id})")

        # Get database session
        async with async_session_maker() as db:
            # Initialize RAG service
            rag_service = RAGService(db)

            # Process the text
            result = await rag_service.ingest_text(
                title=title,
                content=content,
                user_id=user_id,
                metadata=job.metadata.get("doc_metadata", {}),
            )

            # Update progress to 100%
            job_queue = await get_job_queue()
            await job_queue.update_progress(job.job_id, processed_items=1)

            return {
                "documents_created": result.get("documents_created", 0),
                "chunks_created": result.get("chunks_created", 0),
                "embeddings_created": result.get("embeddings_created", 0),
                "title": title,
            }

    async def process_batch_ingest_job(self, job: JobData) -> dict:
        """
        Process batch file ingestion job.

        Args:
            job: Job data containing list of file paths

        Returns:
            Processing result

        Raises:
            Exception: If processing fails
        """
        file_paths = job.metadata.get("file_paths", [])
        user_id = job.user_id

        if not file_paths:
            raise ValueError("Missing file_paths in job metadata")

        logger.info(f"Processing batch ingestion: {len(file_paths)} files (job={job.job_id})")

        total_documents = 0
        total_chunks = 0
        total_embeddings = 0
        failed_files = []

        job_queue = await get_job_queue()

        for idx, file_path in enumerate(file_paths):
            try:
                # Get database session
                async with async_session_maker() as db:
                    rag_service = RAGService(db)

                    # Process the file
                    result = await rag_service.ingest_file(
                        file_path=file_path,
                        user_id=user_id,
                    )

                    total_documents += result.get("documents_created", 0)
                    total_chunks += result.get("chunks_created", 0)
                    total_embeddings += result.get("embeddings_created", 0)

                    # Update progress
                    await job_queue.update_progress(
                        job.job_id,
                        processed_items=idx + 1,
                    )

                    logger.debug(f"Processed file {idx + 1}/{len(file_paths)}: {file_path}")

            except Exception as e:
                logger.error(f"Failed to process file {file_path}: {e}")
                failed_files.append({"path": file_path, "error": str(e)})
                await job_queue.update_progress(
                    job.job_id,
                    processed_items=idx + 1,
                    failed_items=1,
                    increment=True,
                )

        return {
            "total_files": len(file_paths),
            "successful_files": len(file_paths) - len(failed_files),
            "failed_files": len(failed_files),
            "documents_created": total_documents,
            "chunks_created": total_chunks,
            "embeddings_created": total_embeddings,
            "failures": failed_files[:10],  # Limit error details
        }

    async def process_job(self, job: JobData) -> None:
        """
        Process a single job based on its type.

        Args:
            job: Job to process

        Raises:
            Exception: If processing fails
        """
        logger.info(f"Processing job: {job.job_id} (type={job.job_type}, user={job.user_id})")

        job_queue = await get_job_queue()

        try:
            # Mark job as started
            await job_queue.start_job(job.job_id)

            # Process based on job type
            if job.job_type == JobType.INGEST_FILE:
                result = await self.process_ingest_file_job(job)
            elif job.job_type == JobType.INGEST_TEXT:
                result = await self.process_ingest_text_job(job)
            elif job.job_type == JobType.BATCH_INGEST:
                result = await self.process_batch_ingest_job(job)
            else:
                raise ValueError(f"Unknown job type: {job.job_type}")

            # Mark job as completed
            await job_queue.complete_job(job.job_id, result=result)
            logger.info(f"Job completed successfully: {job.job_id}")

        except Exception as e:
            logger.error(f"Job failed: {job.job_id}: {e}", exc_info=True)

            # Mark job as failed (will retry if applicable)
            await job_queue.fail_job(
                job.job_id,
                error_message=str(e),
                should_retry=True,
            )

    async def poll_queue(self, job_type: JobType) -> Optional[str]:
        """
        Poll queue for pending jobs.

        Args:
            job_type: Type of jobs to poll for

        Returns:
            Job ID if found, None otherwise
        """
        redis = await get_redis()
        queue_key = f"queue:{job_type.value}"

        # Pop job ID from queue (left pop for FIFO)
        job_id = await redis.lpop(queue_key)

        if job_id:
            logger.debug(f"Popped job from queue: {job_id} (type={job_type})")

        return job_id

    async def run(self) -> None:
        """
        Run the worker loop.
        Continuously polls queues and processes jobs.
        """
        logger.info("Worker starting...")
        self._running = True

        # Initialize Redis
        await get_redis()

        # Active tasks
        active_tasks: set[asyncio.Task] = set()

        try:
            while self._running:
                # Clean up completed tasks
                done_tasks = {task for task in active_tasks if task.done()}
                for task in done_tasks:
                    try:
                        await task  # Raise any exceptions
                    except Exception as e:
                        logger.error(f"Task failed: {e}", exc_info=True)
                    active_tasks.discard(task)

                # Check if we can process more jobs
                if len(active_tasks) < self._max_concurrent_jobs:
                    job_queue = await get_job_queue()

                    # Poll queues for each job type
                    for job_type in [JobType.INGEST_FILE, JobType.INGEST_TEXT, JobType.BATCH_INGEST]:
                        # Check if we have capacity
                        if len(active_tasks) >= self._max_concurrent_jobs:
                            break

                        # Poll queue for job
                        job_id = await self.poll_queue(job_type)

                        if job_id:
                            # Get job data
                            job = await job_queue.get_job(job_id)

                            if job and job.status == JobStatus.PENDING:
                                # Create task to process job
                                task = asyncio.create_task(self.process_job(job))
                                active_tasks.add(task)
                                logger.info(
                                    f"Started processing job: {job_id} "
                                    f"(active={len(active_tasks)}/{self._max_concurrent_jobs})"
                                )
                            elif job:
                                logger.warning(
                                    f"Skipping job {job_id}: status={job.status} (expected PENDING)"
                                )
                            else:
                                logger.warning(f"Job not found: {job_id}")

                # Sleep before next poll
                await asyncio.sleep(self._poll_interval)

        except Exception as e:
            logger.error(f"Worker error: {e}", exc_info=True)
            raise
        finally:
            # Wait for active tasks to complete
            if active_tasks:
                logger.info(f"Waiting for {len(active_tasks)} active tasks to complete...")
                await asyncio.gather(*active_tasks, return_exceptions=True)

            # Cleanup
            await close_redis()
            logger.info("Worker stopped")

    def stop(self) -> None:
        """Stop the worker gracefully"""
        logger.info("Stopping worker...")
        self._running = False


async def main():
    """Main entry point for the worker"""
    worker = JobWorker()

    # Setup signal handlers
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        worker.stop()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        await worker.run()
    except KeyboardInterrupt:
        logger.info("Worker interrupted by user")
    except Exception as e:
        logger.error(f"Worker failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
