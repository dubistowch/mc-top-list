"""
Modrinth API client implementation

For API documentation, see: https://docs.modrinth.com/api/
"""

from typing import Dict, Optional
import json
import aiohttp
import structlog
from .client_factory import BaseClient, ClientError

logger = structlog.get_logger(__name__)

class ModrinthClient(BaseClient):
    """Client for interacting with the Modrinth API"""
    
    platform = "modrinth"
    BASE_URL = "https://api.modrinth.com/v2"
    USER_AGENT = "mc-top-list/1.0.0 (github.com/dubi/mc-top-list)"
    
    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initialize the Modrinth client
        
        Args:
            api_key: Optional API key for authenticated requests
        """
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _ensure_session(self) -> None:
        """Ensure aiohttp session exists"""
        if not self.session:
            headers = {
                "User-Agent": self.USER_AGENT
            }
            if self.api_key:
                headers["Authorization"] = self.api_key
            self.session = aiohttp.ClientSession(headers=headers)
    
    async def _close_session(self) -> None:
        """Close aiohttp session if it exists"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def fetch_resources(self) -> Dict:
        """
        Fetch resources from Modrinth
        
        Returns:
            Dict containing fetched resources
            
        Raises:
            ClientError: If the request fails
        """
        try:
            await self._ensure_session()
            
            # Fetch popular mods
            url = f"{self.BASE_URL}/search"
            params = {
                "limit": 100,
                "offset": 0,
                "index": "downloads",  # Sort by downloads
                "facets": json.dumps([["project_type:mod"]]),  # Only mods
                "sort": "downloads"  # Sort by downloads
            }
            
            logger.info("fetching_modrinth_resources", url=url, params=params)
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error("modrinth_request_failed", 
                               status=response.status, 
                               error=error_text)
                    raise ClientError(f"Modrinth API request failed: {error_text}")
                
                data = await response.json()
                logger.info("modrinth_resources_fetched", 
                          hit_count=len(data.get("hits", [])),
                          total_hits=data.get("total_hits", 0))
                return data
                
        except aiohttp.ClientError as e:
            logger.error("modrinth_request_error", error=str(e))
            raise ClientError(f"Modrinth API request error: {str(e)}")
        except Exception as e:
            logger.error("modrinth_unexpected_error", error=str(e))
            raise ClientError(f"Unexpected error in Modrinth client: {str(e)}")
        finally:
            await self._close_session() 