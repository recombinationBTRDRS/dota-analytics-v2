from motor.motor_asyncio import AsyncClient, AsyncIOMotorDatabase, AsyncIOMotorClient
from typing import Optional

_db_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None

async def init_db(connection_string: str, db_name: str) -> None:
    """Initialize MongoDB connection"""
    global _db_client, _db
    _db_client = AsyncIOMotorClient(connection_string)
    _db = _db_client[db_name]


async def close_db() -> None:
    """Close MongoDB connection"""
    global _db_client
    if _db_client:
        _db_client.close()
    

def get_db() -> AsyncIOMotorDatabase:
    """Get database instance"""
    if _db is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _db