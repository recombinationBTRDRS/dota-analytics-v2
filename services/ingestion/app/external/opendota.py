"""OpenDota API client.

Provides:
- Async HTTP client for OpenDota API
- Rate limiting and retry logic
- Connection pooling
- Error handling and logging
"""

from typing import Optional, Dict, Any, List
import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from app.config import get_settings
from app.logging_config import get_logger

logger = get_logger(__name__)

settings = get_settings()


class OpenDotaError(Exception):
    """Base exception for OpenDota API errors."""
    pass


class OpenDotaRateLimitError(OpenDotaError):
    """Rate limit exceeded error."""
    pass


class OpenDotaNotFoundError(OpenDotaError):
    """Resource not found error."""
    pass


class OpenDotaClient:
    """Async client for OpenDota API.
    
    Features:
    - Connection pooling
    - Retry logic with exponential backoff
    - Rate limiting
    - Structured logging
    - Request/response caching (optional)
    """
    
    def __init__(
        self,
        base_url: str = settings.OPENDOTA_BASE_URL,
        timeout: int = settings.OPENDOTA_TIMEOUT,
        retries: int = settings.OPENDOTA_RETRIES,
    ):
        """Initialize OpenDota client.
        
        Args:
            base_url: OpenDota API base URL
            timeout: Request timeout in seconds
            retries: Number of retry attempts
        """
        self.base_url = base_url
        self.timeout = timeout
        self.retries = retries
        self.client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
    
    async def connect(self) -> None:
        """Create HTTP client connection.
        
        Example:
            client = OpenDotaClient()
            await client.connect()
        """
        if self.client is None:
            logger.info("opendota_client_connecting", base_url=self.base_url)
            
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                limits=httpx.Limits(max_keepalive_connections=5),
            )
            
            logger.info("opendota_client_connected")
    
    async def disconnect(self) -> None:
        """Close HTTP client connection.
        
        Example:
            await client.disconnect()
        """
        if self.client:
            try:
                logger.info("opendota_client_disconnecting")
                await self.client.aclose()
                self.client = None
                logger.info("opendota_client_disconnected")
            except Exception as exc:
                logger.error(
                    "opendota_client_disconnect_failed",
                    error=str(exc),
                    exc_info=True,
                )
    
    @retry(
        stop=stop_after_attempt(settings.OPENDOTA_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, OpenDotaRateLimitError)),
    )
    async def _request(
        self,
        method: str,
        url: str,
        **kwargs,
    ) -> httpx.Response:
        """Make HTTP request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc)
            url: Request URL
            **kwargs: Additional request parameters
            
        Returns:
            httpx.Response
            
        Raises:
            OpenDotaError: If request fails after retries
        """
        if self.client is None:
            raise RuntimeError("Client not connected. Call connect() first.")
        
        try:
            logger.debug(
                "opendota_request_starting",
                method=method,
                url=url,
            )
            
            response = await self.client.request(method, url, **kwargs)
            
            # Handle rate limiting
            if response.status_code == 429:
                logger.warning(
                    "opendota_rate_limit_exceeded",
                    retry_after=response.headers.get("Retry-After"),
                )
                raise OpenDotaRateLimitError("Rate limit exceeded")
            
            # Handle not found
            if response.status_code == 404:
                logger.warning("opendota_resource_not_found", url=url)
                raise OpenDotaNotFoundError(f"Resource not found: {url}")
            
            # Handle server errors
            if response.status_code >= 500:
                logger.error(
                    "opendota_server_error",
                    status=response.status_code,
                    url=url,
                )
                response.raise_for_status()
            
            # Handle client errors
            if response.status_code >= 400:
                logger.error(
                    "opendota_client_error",
                    status=response.status_code,
                    url=url,
                )
                response.raise_for_status()
            
            logger.debug(
                "opendota_request_completed",
                method=method,
                url=url,
                status=response.status_code,
            )
            
            return response
        
        except OpenDotaError:
            raise
        except httpx.HTTPError as exc:
            logger.error(
                "opendota_request_failed",
                method=method,
                url=url,
                error=str(exc),
                error_type=type(exc).__name__,
            )
            raise
    
    async def get_match(self, match_id: int) -> Dict[str, Any]:
        """Get match details from OpenDota API.
        
        Args:
            match_id: Dota 2 match ID
            
        Returns:
            Match details dictionary
            
        Raises:
            OpenDotaNotFoundError: If match not found
            OpenDotaError: If request fails
            
        Example:
            async with OpenDotaClient() as client:
                match = await client.get_match(7123456789)
        """
        logger.info("opendota_get_match_requested", match_id=match_id)
        
        try:
            response = await self._request("GET", f"/matches/{match_id}")
            match_data = response.json()
            
            logger.info(
                "opendota_get_match_completed",
                match_id=match_id,
                duration=match_data.get("duration"),
            )
            
            return match_data
        
        except OpenDotaError:
            raise
        except Exception as exc:
            logger.error(
                "opendota_get_match_failed",
                match_id=match_id,
                error=str(exc),
                exc_info=True,
            )
            raise OpenDotaError(f"Failed to fetch match {match_id}: {exc}")
    
    async def get_matches(
        self,
        limit: int = 100,
        less_than_match_id: Optional[int] = None,
        sort: str = "desc",
        min_rank: int = 10,
        game_mode: int = 22,
    ) -> List[Dict[str, Any]]:
        """Get list of matches with optional filters.
        
        Args:
            limit: Maximum matches to return (default 100, max 500)
            less_than_match_id: Get matches before this ID
            sort: Sort order (asc/desc)
            min_rank: Minimum rank tier
            game_mode: Game mode (22 = All Pick Ranked)
            
        Returns:
            List of match summary dictionaries
            
        Example:
            async with OpenDotaClient() as client:
                matches = await client.get_matches(limit=100, min_rank=10)
        """
        logger.info(
            "opendota_get_matches_requested",
            limit=limit,
            min_rank=min_rank,
        )
        
        try:
            params = {
                "limit": min(limit, 500),  # API max is 500
                "sort": sort,
                "min_rank": min_rank,
                "game_mode": game_mode,
            }
            
            if less_than_match_id:
                params["less_than_match_id"] = less_than_match_id
            
            response = await self._request("GET", "/matches", params=params)
            matches = response.json()
            
            logger.info(
                "opendota_get_matches_completed",
                count=len(matches),
                limit=limit,
            )
            
            return matches
        
        except OpenDotaError:
            raise
        except Exception as exc:
            logger.error(
                "opendota_get_matches_failed",
                error=str(exc),
                exc_info=True,
            )
            raise OpenDotaError(f"Failed to fetch matches: {exc}")
    
    async def get_player(self, account_id: int) -> Dict[str, Any]:
        """Get player details from OpenDota API.
        
        Args:
            account_id: Steam account ID
            
        Returns:
            Player details dictionary
            
        Example:
            async with OpenDotaClient() as client:
                player = await client.get_player(123456789)
        """
        logger.info("opendota_get_player_requested", account_id=account_id)
        
        try:
            response = await self._request("GET", f"/players/{account_id}")
            player_data = response.json()
            
            logger.info("opendota_get_player_completed", account_id=account_id)
            
            return player_data
        
        except OpenDotaError:
            raise
        except Exception as exc:
            logger.error(
                "opendota_get_player_failed",
                account_id=account_id,
                error=str(exc),
                exc_info=True,
            )
            raise OpenDotaError(f"Failed to fetch player {account_id}: {exc}")
    
    async def get_hero_stats(self) -> List[Dict[str, Any]]:
        """Get hero statistics from OpenDota API.
        
        Returns:
            List of hero statistics
            
        Example:
            async with OpenDotaClient() as client:
                heroes = await client.get_hero_stats()
        """
        logger.info("opendota_get_hero_stats_requested")
        
        try:
            response = await self._request("GET", "/heroStats")
            heroes = response.json()
            
            logger.info("opendota_get_hero_stats_completed", count=len(heroes))
            
            return heroes
        
        except OpenDotaError:
            raise
        except Exception as exc:
            logger.error(
                "opendota_get_hero_stats_failed",
                error=str(exc),
                exc_info=True,
            )
            raise OpenDotaError(f"Failed to fetch hero stats: {exc}")


# Singleton instance for convenience
_client: Optional[OpenDotaClient] = None


async def get_client() -> OpenDotaClient:
    """Get or create OpenDota client.
    
    Returns:
        OpenDotaClient instance
        
    Example:
        client = await get_client()
        match = await client.get_match(7123456789)
    """
    global _client
    
    if _client is None:
        _client = OpenDotaClient()
        await _client.connect()
    
    return _client


async def close_client() -> None:
    """Close OpenDota client.
    
    Example:
        await close_client()
    """
    global _client
    
    if _client:
        await _client.disconnect()
        _client = None