"""Repository Pattern implementation for data access.

Provides:
- BaseRepository for common operations
- Specific repositories for collections
- Type-safe data access
- Query abstraction
"""

from typing import Any, Dict, List, Optional, TypeVar, Generic
from abc import ABC
from motor.motor_asyncio import AsyncIOMotorCollection
from app.logging_config import get_logger
from app.db.mongodb import get_db

logger = get_logger(__name__)

T = TypeVar('T', bound=Dict[str, Any])


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository for common CRUD operations.
    
    Provides:
    - Create
    - Read
    - Update
    - Delete
    - List
    """
    
    def __init__(self, collection_name: str):
        """Initialize repository.
        
        Args:
            collection_name: Name of MongoDB collection
        """
        self.collection_name = collection_name
        self._collection: Optional[AsyncIOMotorCollection] = None
    
    @property
    def collection(self) -> AsyncIOMotorCollection:
        """Get MongoDB collection.
        
        Returns:
            AsyncIOMotorCollection: MongoDB collection instance
        """
        if self._collection is not None:
            return self._collection
        
        db = get_db()
        return db[self.collection_name]
    
    @collection.setter
    def collection(self, value: AsyncIOMotorCollection):
        """Allow overriding collection (for tests)."""
        self._collection = value
    
    async def create(self, data: T) -> T:
        """Create new document.
        
        Args:
            data: Document data
            
        Returns:
            Document with inserted ID
        """
        try:
            logger.debug(
                "repository_create_started",
                collection=self.collection_name,
            )
            
            result = await self.collection.insert_one(data)
            data["_id"] = result.inserted_id
            
            logger.info(
                "repository_create_completed",
                collection=self.collection_name,
            )
            
            return data
        
        except Exception as exc:
            logger.error(
                "repository_create_failed",
                collection=self.collection_name,
                error=str(exc),
                exc_info=True,
            )
            raise
    
    async def find_by_id(self, id_value: Any) -> Optional[T]:
        """Find document by ID.
        
        Args:
            id_value: Document ID
            
        Returns:
            Document or None if not found
        """
        try:
            logger.debug(
                "repository_find_by_id_started",
                collection=self.collection_name,
            )
            
            result = await self.collection.find_one({"_id": id_value})
            
            if result:
                logger.debug(
                    "repository_find_by_id_found",
                    collection=self.collection_name,
                )
            
            return result
        
        except Exception as exc:
            logger.error(
                "repository_find_by_id_failed",
                collection=self.collection_name,
                error=str(exc),
                exc_info=True,
            )
            raise
    
    async def find_one(self, query: Dict[str, Any]) -> Optional[T]:
        """Find single document by query.
        
        Args:
            query: MongoDB query
            
        Returns:
            Document or None
        """
        try:
            logger.debug(
                "repository_find_one_started",
                collection=self.collection_name,
            )
            
            result = await self.collection.find_one(query)
            
            if result:
                logger.debug(
                    "repository_find_one_found",
                    collection=self.collection_name,
                )
            
            return result
        
        except Exception as exc:
            logger.error(
                "repository_find_one_failed",
                collection=self.collection_name,
                error=str(exc),
                exc_info=True,
            )
            raise
    
    async def find_many(
        self,
        query: Dict[str, Any],
        limit: int = 100,
        skip: int = 0,
    ) -> List[T]:
        """Find multiple documents.
        
        Args:
            query: MongoDB query
            limit: Maximum documents to return
            skip: Documents to skip
            
        Returns:
            List of documents
        """
        try:
            logger.debug(
                "repository_find_many_started",
                collection=self.collection_name,
            )
            
            cursor = self.collection.find(query).skip(skip).limit(limit)
            results = await cursor.to_list(length=limit)
            
            logger.debug(
                "repository_find_many_completed",
                collection=self.collection_name,
                count=len(results),
            )
            
            return results
        
        except Exception as exc:
            logger.error(
                "repository_find_many_failed",
                collection=self.collection_name,
                error=str(exc),
                exc_info=True,
            )
            raise
    
    async def update(
        self,
        id_value: Any,
        data: Dict[str, Any],
    ) -> Optional[T]:
        """Update document by ID.
        
        Args:
            id_value: Document ID
            data: Update data
            
        Returns:
            Updated document or None
        """
        try:
            logger.debug(
                "repository_update_started",
                collection=self.collection_name,
            )
            
            result = await self.collection.find_one_and_update(
                {"_id": id_value},
                {"$set": data},
                return_document=True,
            )
            
            logger.info(
                "repository_update_completed",
                collection=self.collection_name,
            )
            
            return result
        
        except Exception as exc:
            logger.error(
                "repository_update_failed",
                collection=self.collection_name,
                error=str(exc),
                exc_info=True,
            )
            raise
    
    async def delete(self, id_value: Any) -> bool:
        """Delete document by ID.
        
        Args:
            id_value: Document ID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            logger.debug(
                "repository_delete_started",
                collection=self.collection_name,
            )
            
            result = await self.collection.delete_one({"_id": id_value})
            
            logger.info(
                "repository_delete_completed",
                collection=self.collection_name,
            )
            
            return result.deleted_count > 0
        
        except Exception as exc:
            logger.error(
                "repository_delete_failed",
                collection=self.collection_name,
                error=str(exc),
                exc_info=True,
            )
            raise
    
    async def count(self, query: Optional[Dict[str, Any]] = None) -> int:
        """Count documents matching query.
        
        Args:
            query: MongoDB query (None = all documents)
            
        Returns:
            Count of documents
        """
        try:
            query = query or {}
            
            logger.debug(
                "repository_count_started",
                collection=self.collection_name,
            )
            
            count = await self.collection.count_documents(query)
            
            logger.debug(
                "repository_count_completed",
                collection=self.collection_name,
                count=count,
            )
            
            return count
        
        except Exception as exc:
            logger.error(
                "repository_count_failed",
                collection=self.collection_name,
                error=str(exc),
                exc_info=True,
            )
            raise
    
    async def exists(self, query: Dict[str, Any]) -> bool:
        """Check if document exists.
        
        Args:
            query: MongoDB query
            
        Returns:
            True if document exists
        """
        try:
            result = await self.collection.find_one(query, projection={"_id": 1})
            return result is not None
        
        except Exception as exc:
            logger.error(
                "repository_exists_failed",
                collection=self.collection_name,
                error=str(exc),
                exc_info=True,
            )
            raise


class MatchRepository(BaseRepository[Dict[str, Any]]):
    """Repository for Match documents."""
    
    def __init__(self):
        """Initialize match repository."""
        super().__init__("matches")
    
    async def find_by_match_id(self, match_id: int) -> Optional[Dict[str, Any]]:
        """Find match by Dota 2 match ID.
        
        Args:
            match_id: Dota 2 match ID
            
        Returns:
            Match document or None
        """
        return await self.find_one({"match_id": match_id})
    
    async def find_by_patch(self, patch: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Find matches by patch.
        
        Args:
            patch: Patch version (e.g., "7.35d")
            limit: Maximum documents
            
        Returns:
            List of match documents
        """
        return await self.find_many({"patch": patch}, limit=limit)


class IngestionLogRepository(BaseRepository[Dict[str, Any]]):
    """Repository for Ingestion Log documents."""
    
    def __init__(self):
        """Initialize ingestion log repository."""
        super().__init__("ingestion_log")
    
    async def find_by_status(self, status: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Find logs by status.
        
        Args:
            status: Log status (pending, ingested, invalid, duplicate)
            limit: Maximum documents
            
        Returns:
            List of ingestion log documents
        """
        return await self.find_many({"status": status}, limit=limit)
    
    async def count_by_status(self, status: str) -> int:
        """Count logs by status.
        
        Args:
            status: Log status
            
        Returns:
            Count of logs
        """
        return await self.count({"status": status})