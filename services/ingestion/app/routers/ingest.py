"""Ingestion endpoints with structured logging.

Endpoints for:
- Ingesting matches from OpenDota
- Checking ingestion status
"""

import uuid
from fastapi import APIRouter, HTTPException, status, Query
from app.logging_config import get_logger
from app.schemas import (
    IngestRequest,
    IngestResponse,
    IngestStatusResponse,
    ErrorDetail,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/ingest", tags=["ingestion"])


@router.post(
    "/opendota",
    response_model=IngestResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        400: {"model": ErrorDetail, "description": "Invalid request"},
        500: {"model": ErrorDetail, "description": "Server error"},
    },
)
async def ingest_opendota(request: IngestRequest):
    """Ingest a match from OpenDota API.
    
    Accepts a match ID and queues it for ingestion.
    
    Args:
        request: Match ID to ingest
        
    Returns:
        IngestResponse with status
        
    Raises:
        HTTPException: If request is invalid
    """
    request_id = str(uuid.uuid4())
    
    logger.info(
        "ingest_opendota_requested",
        match_id=request.match_id,
        request_id=request_id,
    )
    
    try:
        # TODO: Implement in Task 2.1
        logger.debug(
            "opendota_fetch_started",
            match_id=request.match_id,
            request_id=request_id,
        )
        
        return IngestResponse(
            match_id=request.match_id,
            status="pending",
            message="Match queued for ingestion",
            request_id=request_id,
        )
    
    except Exception as exc:
        logger.error(
            "ingest_opendota_failed",
            match_id=request.match_id,
            request_id=request_id,
            error=str(exc),
            error_type=type(exc).__name__,
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ingestion failed",
        )


@router.get(
    "/status/{match_id}",
    response_model=IngestStatusResponse,
    responses={
        404: {"model": ErrorDetail, "description": "Match not found"},
        500: {"model": ErrorDetail, "description": "Server error"},
    },
)
async def get_ingest_status(match_id: int):
    """Get ingestion status for a match.
    
    Args:
        match_id: Dota 2 match ID
        
    Returns:
        IngestStatusResponse with current status
        
    Raises:
        HTTPException: If match not found
    """
    logger.info("ingest_status_requested", match_id=match_id)
    
    try:
        # TODO: Implement in Task 2.1
        return IngestStatusResponse(
            match_id=match_id,
            status="unknown",
            attempt=0,
            error=None,
        )
    
    except Exception as exc:
        logger.error(
            "ingest_status_failed",
            match_id=match_id,
            error=str(exc),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Status lookup failed",
        )