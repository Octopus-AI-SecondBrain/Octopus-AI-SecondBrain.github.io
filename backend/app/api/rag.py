"""
Octopus AI Second Brain - RAG Endpoints
"""
from typing import Annotated
from pathlib import Path
import tempfile
import shutil

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db
from ..db.models.user import User
from ..schemas.rag import (
    IngestResponse,
    SearchRequest,
    SearchResponse,
    SearchResult,
    AnswerRequest,
    AnswerResponse,
    StatsResponse,
)
from ..services.rag_service import RAGService
from ..services.job_queue import get_job_queue, JobQueue, JobType
from ..api.auth import get_current_user
from ..core.logging import get_logger
from ..core.settings import get_settings

logger = get_logger(__name__)
router = APIRouter(prefix="/rag", tags=["RAG"])
settings = get_settings()


def get_rag_service(db: AsyncSession = Depends(get_db)) -> RAGService:
    """Get RAG service instance"""
    return RAGService(db)


@router.post("/ingest/file", response_model=IngestResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_file(
    file: UploadFile = File(..., description="File to ingest"),
    metadata: str = Form("{}", description="Optional metadata as JSON string"),
    current_user: Annotated[User, Depends(get_current_user)] = None,  # type: ignore[assignment]
    job_queue: JobQueue = Depends(get_job_queue),
) -> IngestResponse:
    """
    Ingest a file into the RAG system (async).

    Creates a background job to process the file. Use GET /api/jobs/{job_id}
    to check the status and progress of the ingestion.

    Args:
        file: Uploaded file (PDF, TXT, MD, etc.)
        metadata: Optional metadata as JSON string
        current_user: Authenticated user
        job_queue: Job queue service

    Returns:
        Job information (202 Accepted status)

    Raises:
        HTTPException: If file type not supported or job creation fails
    """
    import json
    import os

    # Parse metadata
    try:
        metadata_dict = json.loads(metadata)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid metadata JSON",
        )

    # Validate file type
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )

    file_suffix = Path(file.filename).suffix.lower()
    allowed_extensions = {".txt", ".md", ".pdf", ".json", ".csv", ".xml", ".yaml", ".yml", ".log", ".rst"}

    if file_suffix not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_suffix} not supported. Allowed: {', '.join(allowed_extensions)}",
        )

    try:
        # Save file to permanent upload directory
        upload_dir = settings.upload_dir
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique filename
        import uuid
        unique_filename = f"{uuid.uuid4()}{file_suffix}"
        file_path = upload_dir / unique_filename

        # Save uploaded file
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Create background job
        job = await job_queue.create_job(
            user_id=current_user.id,
            job_type=JobType.INGEST_FILE,
            total_items=1,
            metadata={
                "file_path": str(file_path),
                "original_filename": file.filename,
                "content_type": file.content_type,
                "file_size": os.path.getsize(file_path),
                **metadata_dict,
            },
        )

        logger.info(
            f"Created file ingestion job: {job.job_id} "
            f"(file={file.filename}, user={current_user.username})"
        )

        return IngestResponse(
            job_id=job.job_id,
            status="pending",
            message=f"File upload successful. Processing in background. Check job status at /api/jobs/{job.job_id}",
            total_documents=1,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create ingestion job: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create ingestion job",
        )


@router.post("/ingest/text", response_model=IngestResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_text(
    source_type: str = Form(..., description="Source type (text)"),
    title: str = Form(..., description="Document title"),
    content: str = Form(..., description="Text content"),
    metadata: str = Form("{}", description="Optional metadata as JSON string"),
    current_user: Annotated[User, Depends(get_current_user)] = None,  # type: ignore[assignment]
    job_queue: JobQueue = Depends(get_job_queue),
) -> IngestResponse:
    """
    Ingest text content into the RAG system (async).

    Creates a background job to process the text. Use GET /api/jobs/{job_id}
    to check the status and progress of the ingestion.

    Args:
        source_type: Source type identifier
        title: Document title
        content: Text content
        metadata: Optional metadata as JSON string
        current_user: Authenticated user
        job_queue: Job queue service

    Returns:
        Job information (202 Accepted status)
    """
    import json

    # Parse metadata
    try:
        metadata_dict = json.loads(metadata)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid metadata JSON",
        )

    # Validate content
    if not content or not content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content cannot be empty",
        )

    try:
        # Create background job
        job = await job_queue.create_job(
            user_id=current_user.id,
            job_type=JobType.INGEST_TEXT,
            total_items=1,
            metadata={
                "title": title,
                "content": content,
                "source_type": source_type,
                "content_length": len(content),
                "doc_metadata": metadata_dict,
            },
        )

        logger.info(
            f"Created text ingestion job: {job.job_id} "
            f"(title='{title}', user={current_user.username})"
        )

        return IngestResponse(
            job_id=job.job_id,
            status="pending",
            message=f"Text ingestion queued. Processing in background. Check job status at /api/jobs/{job.job_id}",
            total_documents=1,
        )

    except Exception as e:
        logger.error(f"Failed to create ingestion job: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create ingestion job",
        )


@router.post("/search", response_model=SearchResponse)
async def search(
    data: SearchRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    rag_service: RAGService = Depends(get_rag_service),
) -> SearchResponse:
    """
    Search for relevant documents using semantic similarity.
    
    Args:
        data: Search request with query and filters
        current_user: Authenticated user
        rag_service: RAG service
        
    Returns:
        Search results with similarity scores
    """
    # Add user_id filter to ensure users only see their own documents
    filters = data.filters or {}
    filters["user_id"] = current_user.id
    
    try:
        results, response_time = await rag_service.search(
            query=data.query,
            k=data.k,
            filters=filters,
        )
        
        logger.info(f"Search returned {len(results)} results for user {current_user.username}")
        
        # Convert to SearchResult objects
        search_results = [
            SearchResult(
                content=r["content"],
                score=r["score"],
                metadata=r["metadata"],
                chunk_id=r.get("chunk_id"),
                document_id=r.get("document_id"),
            )
            for r in results
        ]
        
        return SearchResponse(
            query=data.query,
            results=search_results,
            num_results=len(results),
            response_time_ms=response_time,
        )
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed",
        )


@router.post("/answer", response_model=AnswerResponse)
async def answer(
    data: AnswerRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    rag_service: RAGService = Depends(get_rag_service),
) -> AnswerResponse:
    """
    Generate an answer to a question using RAG.
    
    Args:
        data: Answer request with question and parameters
        current_user: Authenticated user
        rag_service: RAG service
        
    Returns:
        Generated answer with source citations
    """
    # Add user_id filter to ensure users only see their own documents
    filters = data.filters or {}
    filters["user_id"] = current_user.id
    
    try:
        answer_text, sources, response_time = await rag_service.answer(
            query=data.query,
            k=data.k,
            filters=filters,
            temperature=data.temperature,
            max_tokens=data.max_tokens,
        )
        
        logger.info(f"Generated answer for user {current_user.username}")
        
        # Convert to SearchResult objects
        search_results = [
            SearchResult(
                content=s["content"],
                score=s["score"],
                metadata=s["metadata"],
                chunk_id=s.get("chunk_id"),
                document_id=s.get("document_id"),
            )
            for s in sources
        ]
        
        return AnswerResponse(
            query=data.query,
            answer=answer_text,
            sources=search_results,
            num_sources=len(sources),
            response_time_ms=response_time,
        )
        
    except Exception as e:
        logger.error(f"Answer generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Answer generation failed",
        )


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    current_user: Annotated[User, Depends(get_current_user)],
    rag_service: RAGService = Depends(get_rag_service),
) -> StatsResponse:
    """
    Get RAG system statistics.
    
    Args:
        current_user: Authenticated user
        rag_service: RAG service
        
    Returns:
        System statistics
    """
    try:
        stats = await rag_service.get_stats()
        
        return StatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get statistics",
        )
