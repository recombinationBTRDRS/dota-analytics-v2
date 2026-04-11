"""Ingestion endpoints with structured logging.

Endpoints for:
- Ingesting matches from OpenDota
- Checking ingestion status
"""

from fastapi import APIRouter, HTTPException, status
from app.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/ingest", tags=["ingestion"])


@router.post("/opendota")
async def ingest_opendota(match_id: int):
    """Ingest a match from OpenDota API.
    
    Args:
        match_id: Dota 2 match ID
        
    Returns:
        Ingestion status
        
    Raises:
        HTTPException: If ingestion fails
    """
    logger.info("ingest_opendota_requested", match_id=match_id)
    
    try:
        # TODO: Implement in Task 2.1
        logger.debug("opendota_fetch_started", match_id=match_id)
        
        return {
            "match_id": match_id,
            "status": "pending",
            "message": "Implementation in Task 2.1"
        }
    
    except Exception as exc:
        logger.error(
            "ingest_opendota_failed",
            match_id=match_id,
            error=str(exc),
            error_type=type(exc).__name__,
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ingestion failed"
        )


@router.get("/status/{match_id}")
async def get_ingest_status(match_id: int):
    """Get ingestion status for a match.
    
    Args:
        match_id: Dota 2 match ID
        
    Returns:
        Ingestion status
    """
    logger.info("ingest_status_requested", match_id=match_id)
    
    # TODO: Implement in Task 2.1
    return {
        "match_id": match_id,
        "status": "unknown"
    }