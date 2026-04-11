"""Tests for OpenDota API client.

Test suite for:
- HTTP requests
- Retry logic
- Error handling
- Rate limiting
- Connection pooling
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.external.opendota import (
    OpenDotaClient,
    OpenDotaError,
    OpenDotaRateLimitError,
    OpenDotaNotFoundError,
)


class TestOpenDotaClient:
    """Test OpenDota client functionality."""
    
    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test client initialization."""
        client = OpenDotaClient()
        assert client.base_url == "https://api.opendota.com/api"
        assert client.timeout == 30
        assert client.client is None
    
    @pytest.mark.asyncio
    async def test_client_connect(self):
        """Test client connection."""
        client = OpenDotaClient()
        await client.connect()
        assert client.client is not None
        await client.disconnect()
    
    @pytest.mark.asyncio
    async def test_client_disconnect(self):
        """Test client disconnection."""
        client = OpenDotaClient()
        await client.connect()
        await client.disconnect()
        assert client.client is None
    
    @pytest.mark.asyncio
    async def test_client_context_manager(self):
        """Test client as context manager."""
        async with OpenDotaClient() as client:
            assert client.client is not None


class TestOpenDotaGetMatch:
    """Test get_match method."""
    
    @pytest.mark.asyncio
    async def test_get_match_success(self):
        """Test successful match fetch."""
        client = OpenDotaClient()
        await client.connect()
        
        # Mock response object (не coroutine!)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "match_id": 7123456789,
            "duration": 2345,
            "radiant_win": True,
        }
        
        # Mock _request to return sync object (not async)
        client._request = AsyncMock(return_value=mock_response)
        
        match = await client.get_match(7123456789)
        
        assert match["match_id"] == 7123456789
        assert match["duration"] == 2345
        assert match["radiant_win"] is True
        
        await client.disconnect()
    
    @pytest.mark.asyncio
    async def test_get_match_not_found(self):
        """Test match not found error."""
        client = OpenDotaClient()
        await client.connect()
        
        # Mock to raise NotFoundError
        client._request = AsyncMock(
            side_effect=OpenDotaNotFoundError("Not found")
        )
        
        with pytest.raises(OpenDotaError):
            await client.get_match(999999999)
        
        await client.disconnect()
    
    @pytest.mark.asyncio
    async def test_get_match_connection_required(self):
        """Test that get_match requires connection."""
        client = OpenDotaClient()
        # Don't connect
        
        # RuntimeError gets wrapped in OpenDotaError by exception handler
        with pytest.raises(OpenDotaError):
            await client.get_match(7123456789)


class TestOpenDotaGetMatches:
    """Test get_matches method."""
    
    @pytest.mark.asyncio
    async def test_get_matches_success(self):
        """Test successful matches fetch."""
        client = OpenDotaClient()
        await client.connect()
        
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"match_id": 1, "duration": 2000},
            {"match_id": 2, "duration": 2100},
        ]
        
        client._request = AsyncMock(return_value=mock_response)
        
        matches = await client.get_matches(limit=100, min_rank=10)
        
        assert len(matches) == 2
        assert matches[0]["match_id"] == 1
        assert matches[1]["match_id"] == 2
        
        await client.disconnect()
    
    @pytest.mark.asyncio
    async def test_get_matches_with_filters(self):
        """Test get_matches with custom filters."""
        client = OpenDotaClient()
        await client.connect()
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"match_id": 100, "duration": 2500},
        ]
        
        client._request = AsyncMock(return_value=mock_response)
        
        matches = await client.get_matches(
            limit=50,
            min_rank=20,
            sort="asc",
        )
        
        assert len(matches) == 1
        assert matches[0]["match_id"] == 100
        
        # Verify _request was called with correct params
        call_args = client._request.call_args
        assert call_args[0][0] == "GET"  # method
        assert call_args[0][1] == "/matches"  # url
        
        await client.disconnect()
    
    @pytest.mark.asyncio
    async def test_get_matches_limit_cap(self):
        """Test that limit is capped at 500."""
        client = OpenDotaClient()
        await client.connect()
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        
        client._request = AsyncMock(return_value=mock_response)
        
        # Request with limit > 500
        await client.get_matches(limit=1000)
        
        # Check that API was called with limit=500 (capped)
        call_args = client._request.call_args
        params = call_args[1]["params"]
        assert params["limit"] == 500
        
        await client.disconnect()


class TestOpenDotaGetPlayer:
    """Test get_player method."""
    
    @pytest.mark.asyncio
    async def test_get_player_success(self):
        """Test successful player fetch."""
        client = OpenDotaClient()
        await client.connect()
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "account_id": 123456789,
            "personaname": "TestPlayer",
            "mmr_estimate": {"estimate": 5000},
        }
        
        client._request = AsyncMock(return_value=mock_response)
        
        player = await client.get_player(123456789)
        
        assert player["account_id"] == 123456789
        assert player["personaname"] == "TestPlayer"
        
        await client.disconnect()
    
    @pytest.mark.asyncio
    async def test_get_player_not_found(self):
        """Test player not found error."""
        client = OpenDotaClient()
        await client.connect()
        
        client._request = AsyncMock(
            side_effect=OpenDotaNotFoundError("Not found")
        )
        
        with pytest.raises(OpenDotaError):
            await client.get_player(999999999)
        
        await client.disconnect()


class TestOpenDotaGetHeroStats:
    """Test get_hero_stats method."""
    
    @pytest.mark.asyncio
    async def test_get_hero_stats_success(self):
        """Test successful hero stats fetch."""
        client = OpenDotaClient()
        await client.connect()
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": 1, "name": "Anti-Mage", "pick_rate": 0.15},
            {"id": 2, "name": "Axe", "pick_rate": 0.12},
        ]
        
        client._request = AsyncMock(return_value=mock_response)
        
        heroes = await client.get_hero_stats()
        
        assert len(heroes) == 2
        assert heroes[0]["name"] == "Anti-Mage"
        
        await client.disconnect()


class TestOpenDotaErrors:
    """Test OpenDota error handling."""
    
    def test_opendota_error_base(self):
        """Test base OpenDota error."""
        error = OpenDotaError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)
    
    def test_rate_limit_error(self):
        """Test rate limit error."""
        error = OpenDotaRateLimitError("Rate limited")
        assert isinstance(error, OpenDotaError)
        assert str(error) == "Rate limited"
    
    def test_not_found_error(self):
        """Test not found error."""
        error = OpenDotaNotFoundError("Not found")
        assert isinstance(error, OpenDotaError)
        assert str(error) == "Not found"


class TestOpenDotaErrorHandling:
    """Test error scenarios."""
    
    @pytest.mark.asyncio
    async def test_rate_limit_error_handling(self):
        """Test rate limit error is raised."""
        client = OpenDotaClient()
        await client.connect()
        
        client._request = AsyncMock(
            side_effect=OpenDotaRateLimitError("Rate limited")
        )
        
        with pytest.raises(OpenDotaRateLimitError):
            await client.get_match(7123456789)
        
        await client.disconnect()
    
    @pytest.mark.asyncio
    async def test_generic_exception_wrapped(self):
        """Test generic exceptions are wrapped in OpenDotaError."""
        client = OpenDotaClient()
        await client.connect()
        
        client._request = AsyncMock(
            side_effect=ValueError("Some error")
        )
        
        with pytest.raises(OpenDotaError):
            await client.get_match(7123456789)
        
        await client.disconnect()