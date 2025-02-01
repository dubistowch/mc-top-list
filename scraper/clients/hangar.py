"""
Hangar API client implementation
"""

from typing import Dict, Optional
import aiohttp
import structlog
from .client_factory import BaseClient, ClientError

logger = structlog.get_logger(__name__)

class HangarClient(BaseClient):
    """Client for interacting with the Hangar API"""
    
    platform = "hangar"
    BASE_URL = "https://hangar.papermc.io/api/v1"
    
    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initialize the Hangar client
        
        Args:
            api_key: Optional API key for authenticated requests
        """
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _ensure_session(self) -> None:
        """Ensure aiohttp session exists"""
        if not self.session:
            headers = {}
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
        Fetch resources from Hangar
        
        Returns:
            Dict containing fetched resources
            
        Raises:
            ClientError: If the request fails
        """
        try:
            await self._ensure_session()
            
            # Fetch popular plugins
            url = f"{self.BASE_URL}/projects"
            params = {
                "limit": 100,
                "offset": 0,
                "sort": "-downloads"
            }
            
            logger.info("fetching_hangar_resources", url=url)
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error("hangar_request_failed", 
                               status=response.status, 
                               error=error_text)
                    raise ClientError(f"Hangar API request failed: {error_text}")
                
                data = await response.json()
                result = data.get("result", [])
                logger.info("hangar_resources_fetched", 
                          result_count=len(result))
                
                # 只回傳資源列表部分，並加上 plugin 類型
                return {"plugin": {"result": result}}
                
        except aiohttp.ClientError as e:
            logger.error("hangar_request_error", error=str(e))
            raise ClientError(f"Hangar API request error: {str(e)}")
        except Exception as e:
            logger.error("hangar_unexpected_error", error=str(e))
            raise ClientError(f"Unexpected error in Hangar client: {str(e)}")
        finally:
            await self._close_session() 