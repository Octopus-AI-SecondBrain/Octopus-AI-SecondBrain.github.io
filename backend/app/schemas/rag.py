"""
Octopus AI Second Brain - RAG Schemas
Request and response models for RAG endpoints.
"""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    """Request to ingest a document"""
    source_type: str = Field(..., description="Type of source (file, url, text)")
    title: Optional[str] = Field(None, description="Document title")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class IngestResponse(BaseModel):
    """Response from document ingestion"""
    job_id: int = Field(..., description="Ingestion job ID")
    status: str = Field(..., description="Job status")
    message: str = Field(..., description="Status message")
    total_documents: int = Field(0, description="Number of documents to process")


class SearchRequest(BaseModel):
    """Request to search documents"""
    query: str = Field(..., min_length=1, description="Search query")
    k: int = Field(10, ge=1, le=100, description="Number of results")
    filters: Optional[dict[str, Any]] = Field(None, description="Metadata filters")


class SearchResult(BaseModel):
    """A single search result"""
    content: str = Field(..., description="Document content")
    score: float = Field(..., description="Similarity score")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    chunk_id: Optional[int] = Field(None, description="Chunk ID")
    document_id: Optional[int] = Field(None, description="Document ID")


class SearchResponse(BaseModel):
    """Response from search"""
    results: list[SearchResult] = Field(default_factory=list, description="Search results")
    query: str = Field(..., description="Original query")
    num_results: int = Field(..., description="Number of results returned")
    response_time_ms: float = Field(..., description="Response time in milliseconds")


class AnswerRequest(BaseModel):
    """Request to get an AI-generated answer"""
    query: str = Field(..., min_length=1, description="Question to answer")
    k: int = Field(10, ge=1, le=100, description="Number of context documents")
    filters: Optional[dict[str, Any]] = Field(None, description="Metadata filters")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Generation temperature")
    max_tokens: Optional[int] = Field(None, ge=1, le=4096, description="Max tokens in response")


class AnswerResponse(BaseModel):
    """Response with AI-generated answer"""
    answer: str = Field(..., description="Generated answer")
    query: str = Field(..., description="Original query")
    sources: list[SearchResult] = Field(default_factory=list, description="Source documents")
    num_sources: int = Field(..., description="Number of source documents used")
    response_time_ms: float = Field(..., description="Response time in milliseconds")


class JobStatusResponse(BaseModel):
    """Status of an ingestion job"""
    job_id: int = Field(..., description="Job ID")
    status: str = Field(..., description="Job status (pending, processing, completed, failed)")
    job_type: str = Field(..., description="Type of job")
    total_documents: int = Field(..., description="Total documents to process")
    processed_documents: int = Field(..., description="Documents processed so far")
    result_message: Optional[str] = Field(None, description="Result message")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(..., description="Job creation time")
    started_at: Optional[datetime] = Field(None, description="Job start time")
    completed_at: Optional[datetime] = Field(None, description="Job completion time")


class StatsResponse(BaseModel):
    """RAG system statistics"""
    total_embeddings: int = Field(0, description="Total embeddings in vector store")
    vector_store_backend: str = Field("pgvector", description="Vector store backend (pgvector, faiss)")
    embedding_model: str = Field(..., description="Embedding model name")
    embedding_dimension: int = Field(..., description="Embedding vector dimension")
