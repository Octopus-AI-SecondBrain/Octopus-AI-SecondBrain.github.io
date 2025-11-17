"""
Octopus AI Second Brain - Common Schemas
Common request and response models.
"""
from typing import Any, Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[Any] = Field(None, description="Additional error details")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Overall status (healthy, degraded, unhealthy)")
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Environment (development, staging, production)")
    database: str = Field(..., description="Database status")
    redis: str = Field(..., description="Redis cache/queue status")
    vector_store: str = Field(..., description="Vector store status")
    openai: str = Field(..., description="OpenAI API status")
    message: str = Field(..., description="Status message")
    
    
class MessageResponse(BaseModel):
    """Simple message response"""
    message: str = Field(..., description="Message")
    success: bool = Field(True, description="Operation success status")
