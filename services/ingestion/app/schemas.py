"""Pydantic schemas for request/response models.

Provides:
- Request DTOs (Data Transfer Objects)
- Response models
- Error responses
- Type validation
"""

from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime


# ============================================================================
# HEALTH CHECK RESPONSES
# ============================================================================

class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str = Field(description="Service status (ok/error)")
    service: str = Field(description="Service name")
    version: str = Field(description="Service version")
    debug: bool = Field(description="Debug mode enabled")
    timestamp: Optional[datetime] = Field(default=None, description="Response timestamp")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "status": "ok",
                "service": "ingestion",
                "version": "1.0.0",
                "debug": True
            }
        }


class ReadyResponse(BaseModel):
    """Readiness check response."""
    
    ready: bool = Field(description="Service ready status")
    service: str = Field(description="Service name")
    port: int = Field(description="Service port")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "ready": True,
                "service": "ingestion",
                "port": 8001
            }
        }


# ============================================================================
# INGESTION REQUESTS/RESPONSES
# ============================================================================

class IngestRequest(BaseModel):
    """Request to ingest a match."""
    
    match_id: int = Field(gt=0, description="Dota 2 match ID")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "match_id": 7123456789
            }
        }


class IngestResponse(BaseModel):
    """Response from match ingestion."""
    
    match_id: int = Field(description="Match ID")
    status: str = Field(description="Ingestion status (pending/ingested/error)")
    message: Optional[str] = Field(default=None, description="Status message")
    request_id: Optional[str] = Field(default=None, description="Request tracking ID")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "match_id": 7123456789,
                "status": "pending",
                "message": "Match queued for ingestion",
                "request_id": "uuid-123"
            }
        }


class IngestStatusResponse(BaseModel):
    """Response for ingestion status check."""
    
    match_id: int = Field(description="Match ID")
    status: str = Field(description="Current ingestion status")
    attempt: int = Field(description="Ingestion attempt number")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "match_id": 7123456789,
                "status": "ingested",
                "attempt": 1,
                "error": None
            }
        }


# ============================================================================
# ERROR RESPONSES
# ============================================================================

class ErrorDetail(BaseModel):
    """Error detail information."""
    
    error: str = Field(description="Error type/title")
    status: int = Field(description="HTTP status code")
    detail: str = Field(description="Detailed error message")
    request_id: Optional[str] = Field(default=None, description="Request tracking ID")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "error": "Invalid match ID",
                "status": 400,
                "detail": "Match ID must be a positive integer",
                "request_id": "uuid-123"
            }
        }


class ValidationErrorResponse(BaseModel):
    """Validation error response."""
    
    error: str = "Validation error"
    status: int = 422
    detail: str = Field(description="Validation error details")
    fields: Dict[str, Any] = Field(description="Field errors")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "error": "Validation error",
                "status": 422,
                "detail": "Input validation failed",
                "fields": {
                    "match_id": ["Value must be greater than 0"]
                }
            }
        }


class NotFoundResponse(BaseModel):
    """Resource not found response."""
    
    error: str = "Not found"
    status: int = 404
    detail: str = Field(description="Resource not found message")
    request_id: Optional[str] = Field(default=None, description="Request tracking ID")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "error": "Not found",
                "status": 404,
                "detail": "Match 123 not found",
                "request_id": "uuid-123"
            }
        }


class ServerErrorResponse(BaseModel):
    """Server error response."""
    
    error: str = "Internal server error"
    status: int = 500
    detail: str = Field(description="Error message")
    request_id: Optional[str] = Field(default=None, description="Request tracking ID")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "error": "Internal server error",
                "status": 500,
                "detail": "An unexpected error occurred",
                "request_id": "uuid-123"
            }
        }


# ============================================================================
# PAGINATED RESPONSES
# ============================================================================

class PaginationMeta(BaseModel):
    """Pagination metadata."""
    
    skip: int = Field(ge=0, description="Number of items skipped")
    limit: int = Field(gt=0, description="Maximum items returned")
    total: int = Field(ge=0, description="Total available items")
    has_more: bool = Field(description="Whether more items are available")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "skip": 0,
                "limit": 50,
                "total": 1000,
                "has_more": True
            }
        }


class PaginatedResponse(BaseModel):
    """Generic paginated response."""
    
    data: list[Dict[str, Any]] = Field(description="Response data")
    meta: PaginationMeta = Field(description="Pagination metadata")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "data": [{"id": 1, "name": "Item 1"}],
                "meta": {
                    "skip": 0,
                    "limit": 50,
                    "total": 100,
                    "has_more": True
                }
            }
        }