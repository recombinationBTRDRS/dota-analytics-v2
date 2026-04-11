"""Dependency injection for database access.

Provides:
- Database instance injection for endpoints
- Repository injection
- Connection management
"""

from typing import AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import Depends

from app.db.mongodb import get_db
from app.db.repositories import MatchRepository, IngestionLogRepository


async def get_database() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Dependency: Get database instance.
    
    Yields:
        AsyncIOMotorDatabase instance
        
    Example:
        @app.get("/matches")
        async def get_matches(db: AsyncIOMotorDatabase = Depends(get_database)):
            matches = await db.matches.find().to_list(50)
            return matches
    """
    db = get_db()
    yield db


def get_match_repository() -> MatchRepository:
    """Dependency: Get match repository.
    
    Returns:
        MatchRepository instance
        
    Example:
        @app.get("/matches/{match_id}")
        async def get_match(
            match_id: int,
            repo: MatchRepository = Depends(get_match_repository)
        ):
            match = await repo.find_by_match_id(match_id)
            return match
    """
    return MatchRepository()


def get_ingestion_log_repository() -> IngestionLogRepository:
    """Dependency: Get ingestion log repository.
    
    Returns:
        IngestionLogRepository instance
        
    Example:
        @app.get("/logs/status/{status}")
        async def get_logs(
            status: str,
            repo: IngestionLogRepository = Depends(get_ingestion_log_repository)
        ):
            logs = await repo.find_by_status(status)
            return logs
    """
    return IngestionLogRepository()