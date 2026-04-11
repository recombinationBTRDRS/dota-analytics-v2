"""Tests for repository pattern.

Test suite for:
- BaseRepository CRUD operations
- MatchRepository
- IngestionLogRepository
- Error handling
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.db.repositories import (
    BaseRepository,
    MatchRepository,
    IngestionLogRepository,
)


class TestBaseRepository:
    """Test BaseRepository functionality."""
    
    @pytest.mark.asyncio
    async def test_repository_initialization(self):
        """Test repository initialization."""
        repo = MatchRepository()
        assert repo.collection_name == "matches"
    
    @pytest.mark.asyncio
    async def test_repository_create(self):
        """Test create operation."""
        repo = MatchRepository()
        
        # Mock the collection
        repo.collection = AsyncMock()
        repo.collection.insert_one = AsyncMock()
        repo.collection.insert_one.return_value = MagicMock(inserted_id=123)
        
        data = {"match_id": 7123456789, "duration": 2345}
        result = await repo.create(data)
        
        assert result["_id"] == 123
        repo.collection.insert_one.assert_called_once_with(data)
    
    @pytest.mark.asyncio
    async def test_repository_find_by_id(self):
        """Test find_by_id operation."""
        repo = MatchRepository()
        
        repo.collection = AsyncMock()
        repo.collection.find_one = AsyncMock()
        repo.collection.find_one.return_value = {"_id": 123, "match_id": 456}
        
        result = await repo.find_by_id(123)
        
        assert result["_id"] == 123
        repo.collection.find_one.assert_called_once_with({"_id": 123})
    
    @pytest.mark.asyncio
    async def test_repository_find_one(self):
        """Test find_one operation."""
        repo = MatchRepository()
        
        repo.collection = AsyncMock()
        repo.collection.find_one = AsyncMock()
        repo.collection.find_one.return_value = {"match_id": 7123456789}
        
        result = await repo.find_one({"match_id": 7123456789})
        
        assert result["match_id"] == 7123456789
    
    @pytest.mark.asyncio
    async def test_repository_count(self):
        """Test count operation."""
        repo = MatchRepository()
        
        repo.collection = AsyncMock()
        repo.collection.count_documents = AsyncMock(return_value=42)
        
        count = await repo.count({"patch": "7.35"})
        
        assert count == 42


class TestMatchRepository:
    """Test MatchRepository specific operations."""
    
    @pytest.mark.asyncio
    async def test_find_by_match_id(self):
        """Test find_by_match_id operation."""
        repo = MatchRepository()
        
        repo.collection = AsyncMock()
        repo.collection.find_one = AsyncMock()
        repo.collection.find_one.return_value = {
            "match_id": 7123456789,
            "duration": 2345
        }
        
        result = await repo.find_by_match_id(7123456789)
        
        assert result["match_id"] == 7123456789
    
    @pytest.mark.asyncio
    async def test_find_by_patch(self):
        """Test find_by_patch operation."""
        repo = MatchRepository()
        
        repo.collection = AsyncMock()
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=[
            {"match_id": 1, "patch": "7.35"},
            {"match_id": 2, "patch": "7.35"},
        ])
        repo.collection.find = MagicMock(return_value=mock_cursor)
        mock_cursor.skip = MagicMock(return_value=mock_cursor)
        mock_cursor.limit = MagicMock(return_value=mock_cursor)
        
        result = await repo.find_by_patch("7.35", limit=50)
        
        assert len(result) == 2


class TestIngestionLogRepository:
    """Test IngestionLogRepository specific operations."""
    
    @pytest.mark.asyncio
    async def test_find_by_status(self):
        """Test find_by_status operation."""
        repo = IngestionLogRepository()
        
        repo.collection = AsyncMock()
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=[
            {"match_id": 1, "status": "ingested"},
        ])
        repo.collection.find = MagicMock(return_value=mock_cursor)
        mock_cursor.skip = MagicMock(return_value=mock_cursor)
        mock_cursor.limit = MagicMock(return_value=mock_cursor)
        
        result = await repo.find_by_status("ingested")
        
        assert len(result) == 1
    
    @pytest.mark.asyncio
    async def test_count_by_status(self):
        """Test count_by_status operation."""
        repo = IngestionLogRepository()
        
        repo.collection = AsyncMock()
        repo.collection.count_documents = AsyncMock(return_value=10)
        
        count = await repo.count_by_status("ingested")
        
        assert count == 10