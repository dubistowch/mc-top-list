"""
Modrinth API client implementation

For API documentation, see: https://docs.modrinth.com/api/
"""

from typing import Dict, Optional, List
import json
import aiohttp
import structlog
from .client_factory import BaseClient, ClientError
from scraper.config import get_config

logger = structlog.get_logger(__name__)

class ModrinthClient(BaseClient):
    """Client for interacting with the Modrinth API"""
    
    platform = "modrinth"
    BASE_URL = "https://api.modrinth.com/v2"
    USER_AGENT = "mc-top-list/1.0.0 (github.com/dubi/mc-top-list)"
    BATCH_SIZE = 100  # Maximum number of resources to fetch per request
    
    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initialize the Modrinth client
        
        Args:
            api_key: Optional API key for authenticated requests
        """
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None
        self.config = get_config()
        
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

    async def _fetch_by_type(self, resource_type: str) -> Dict:
        """
        Fetch resources of a specific type
        
        Args:
            resource_type: Type of resource to fetch
            
        Returns:
            Dict containing fetched resources
        """
        url = f"{self.BASE_URL}/search"
        params = {
            "limit": self.BATCH_SIZE,
            "offset": 0,
            "index": "downloads",  # Sort by downloads
            "facets": json.dumps([["project_type:" + resource_type]]),
            "sort": "downloads"  # Sort by downloads
        }
        
        logger.info("fetching_modrinth_resources", url=url, params=params, type=resource_type)
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error("modrinth_request_failed", 
                           status=response.status, 
                           error=error_text,
                           type=resource_type)
                raise ClientError(f"Modrinth API request failed: {error_text}")
            
            data = await response.json()
            logger.info("modrinth_resources_fetched", 
                      hit_count=len(data.get("hits", [])),
                      total_hits=data.get("total_hits", 0),
                      type=resource_type)
            return data

    async def fetch_resources(self) -> Dict:
        """
        Fetch resources from Modrinth for all configured resource types
        
        Returns:
            Dict containing fetched resources
            
        Raises:
            ClientError: If the request fails
        """
        try:
            await self._ensure_session()
            
            # Get configured resource types
            resource_types = self.config["platforms"]["modrinth"]["resource_types"]
            
            # Fetch resources for each type
            all_resources = {
                "hits": [],
                "total_hits": 0
            }
            
            for resource_type in resource_types:
                try:
                    data = await self._fetch_by_type(resource_type)
                    all_resources["hits"].extend(data.get("hits", []))
                    all_resources["total_hits"] += data.get("total_hits", 0)
                except Exception as e:
                    logger.error("modrinth_type_fetch_failed", 
                               type=resource_type,
                               error=str(e))
                    continue
            
            return all_resources
            
        except aiohttp.ClientError as e:
            logger.error("modrinth_request_error", error=str(e))
            raise ClientError(f"Modrinth API request error: {str(e)}")
        except Exception as e:
            logger.error("modrinth_unexpected_error", error=str(e))
            raise ClientError(f"Unexpected error in Modrinth client: {str(e)}")
        finally:
            await self._close_session() 