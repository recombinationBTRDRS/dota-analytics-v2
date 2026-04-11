"""MongoDB connection and utilities.

Provides:
- Async MongoDB client management
- Connection pooling
- Database initialization
- Context managers for connections
"""

from typing import Optional, AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import get_settings
from app.logging_config import get_logger
from urllib.parse import urlparse

logger = get_logger(__name__)

# Global database instance
_db_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


async def init_db() -> AsyncIOMotorDatabase:
    """Initialize MongoDB connection.
    
    Creates async client and returns database instance.
    
    Returns:
        AsyncIOMotorDatabase: MongoDB database instance
        
    Raises:
        ConnectionError: If connection fails
        
    Example:
        db = await init_db()
        matches = await db.matches.find_one({"_id": 123})
    """
    global _db_client, _db
    
    settings = get_settings()
    
    def sanitize_url(url: str) -> str:
        """Remove credentials from URL for logging."""
        parsed = urlparse(url)
        if parsed.password:
            safe_netloc = f"{parsed.hostname}:{parsed.port}" if parsed.port else parsed.hostname
        else:
            safe_netloc = parsed.netloc
        safe_url = f"{parsed.scheme}://{safe_netloc}/{parsed.path.lstrip('/')}"
        return safe_url

    try:
        logger.info("mongodb_connection_starting", url=sanitize_url(settings.MONGODB_URL))
        
        # Create async client
        _db_client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
        )
        
        # Test connection
        await _db_client.admin.command('ping')
        logger.info("mongodb_connection_successful")
        
        # Get database
        _db = _db_client[settings.MONGODB_DB_NAME]
        logger.info("mongodb_database_selected", db_name=settings.MONGODB_DB_NAME)
        
        return _db
    
    except Exception as exc:
        logger.error(
            "mongodb_connection_failed",
            error=str(exc),
            error_type=type(exc).__name__,
            exc_info=True,
        )
        raise ConnectionError(f"Failed to connect to MongoDB: {exc}") from exc


async def close_db() -> None:
    """Close MongoDB connection.
    
    Gracefully closes the async client.
    
    Example:
        await close_db()
    """
    global _db_client, _db
    
    if _db_client:
        try:
            logger.info("mongodb_connection_closing")
            _db_client.close()
            _db_client = None  # ← Очисти
            _db = None         # ← Очисти
            logger.info("mongodb_connection_closed")
        except Exception as exc:
            logger.error("mongodb_close_failed", error=str(exc))
            _db_client = None  # ← Очисти й у error case
            _db = None



def get_db() -> AsyncIOMotorDatabase:
    """Get database instance (must be initialized first).
    
    Returns:
        AsyncIOMotorDatabase: MongoDB database instance
        
    Raises:
        RuntimeError: If database not initialized
        
    Example:
        db = get_db()
    """
    if _db is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _db


async def get_db_context() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Get database as async context manager.
    
    Yields:
        AsyncIOMotorDatabase: MongoDB database instance
        
    Example:
        async with get_db_context() as db:
            await db.matches.insert_one({...})
    """
    if _db is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    yield _db


async def ensure_indexes() -> None:
    """Ensure all database indexes are created.
    
    Creates indexes for optimal query performance.
    
    Example:
        await ensure_indexes()
    """
    db = get_db()
    
    try:
        logger.info("mongodb_indexes_creation_starting")
        
        # Matches collection indexes
        await db.matches.create_index("match_id", unique=True)
        await db.matches.create_index("start_time")
        await db.matches.create_index("patch")
        await db.matches.create_index("ingested_at")
        
        # Ingestion log indexes
        await db.ingestion_log.create_index("match_id", unique=True)
        await db.ingestion_log.create_index("status")
        await db.ingestion_log.create_index("last_attempt")
        
        logger.info("mongodb_indexes_creation_completed")
    
    except Exception as exc:
        logger.error(
            "mongodb_indexes_creation_failed",
            error=str(exc),
            exc_info=True,
        )
        raise


async def validate_collection_schemas() -> None:
    """Validate collection schemas.
    
    Ensures collections have proper validators.
    
    Example:
        await validate_collection_schemas()
    """
    db = get_db()
    
    try:
        logger.info("mongodb_schema_validation_starting")
        
        # Matches collection validator
        matches_validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["match_id", "duration"],
                "properties": {
                    "match_id": {"bsonType": "int"},
                    "duration": {"bsonType": "int"},
                    "radiant_win": {"bsonType": "bool"},
                    "start_time": {"bsonType": "int"},
                    "patch": {"bsonType": "string"},
                }
            }
        }
        
        # Create validator
        try:
            await db.command(
                "collMod",
                "matches",
                validator=matches_validator
            )
            logger.info("matches_schema_validated")
        except Exception as exc:
            # Collection might not exist yet
            logger.debug("matches_collection_not_exists_yet", error=str(exc))
        
        logger.info("mongodb_schema_validation_completed")
    
    except Exception as exc:
        logger.error(
            "mongodb_schema_validation_failed",
            error=str(exc),
            exc_info=True,
        )