from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/ingest", tags=["ingestion"])


@router.post("/opendota")
async def ingest_opendot(match_id: int):
    """
    Ingest a match from OpenDota API

    Args:
        match_id: Dota 2 match ID

    Returns:
        Ingestion status
    """
    # TODO: Implement in Task 2.1
    return {
        "match_id": match_id,
        "status": "pending",
        "message": "Implementation in Task 2.1"
    }


@router.get("/status/{match_id}")
async def get_ingest_status(match_id: int):
    """Get ingestion status for a match"""
    # TODO: Implement in Task 2.1
    return {
        "match_id": match_id,
        "status": "unknown"
    }