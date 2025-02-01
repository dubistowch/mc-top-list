"""
Polymart API client implementation

For API documentation, see: https://polymart.org/wiki/api
"""

from typing import Dict, Optional, List
import aiohttp
import structlog
from .client_factory import BaseClient, ClientError
from scraper.config import get_config

logger = structlog.get_logger(__name__)

class PolymartClient(BaseClient):
    """Client for interacting with the Polymart API"""
    
    platform = "polymart"
    USER_AGENT = "mc-top-list/1.0 (https://github.com/dqbd/mc-top-list)"
    
    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initialize the Polymart client
        
        Args:
            api_key: Optional API key for authenticated requests
        """
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None
        self.config = get_config()
        self.base_url = self.config["platforms"]["polymart"]["api_url"]
        self.batch_size = self.config["platforms"]["polymart"]["batch_size"]
    
    async def _ensure_session(self) -> None:
        """Ensure aiohttp session exists"""
        if not self.session:
            headers = {
                "User-Agent": self.USER_AGENT,
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.9",
                "content-type": "application/json",
                "origin": "https://polymart.org",
                "referer": "https://polymart.org/",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site"
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
            
        Raises:
            ClientError: If the request fails
        """
        # Polymart API endpoint for resource search
        url = f"{self.base_url}/resources"
        
        # Map our resource types to Polymart's categories
        category_map = {
            "plugin": 1,  # Plugins
            "mod": 2,     # Mods
            "resourcepack": 3,  # Resource Packs
            "datapack": 4,  # Data Packs
            "pluginpack": 5  # Plugin Packs/Setups
        }
        
        params = {
            "page_size": self.batch_size,
            "page": 1,
            "sort": "downloads",  # Sort by downloads
            "category": category_map.get(resource_type, 1),  # Default to plugins if unknown
            "fields": "id,name,tag_line,description,price,currency,downloads,author,created,updated,versions,categories,links"
        }
        
        try:
            logger.info("fetching_polymart_resources", url=url, params=params, type=resource_type)
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error("polymart_request_failed", 
                               status=response.status, 
                               error=error_text,
                               type=resource_type)
                    raise ClientError(f"Polymart API request failed: {error_text}")
                
                data = await response.json()
                if not data.get("success", False):
                    error = data.get("error", {}).get("message", "Unknown error")
                    logger.error("polymart_api_error", error=error, type=resource_type)
                    raise ClientError(f"Polymart API error: {error}")
                
                resources = data.get("response", {}).get("resources", [])
                logger.info("polymart_resources_fetched", 
                          resource_count=len(resources),
                          type=resource_type)
                return {
                    "resources": resources,
                    "total": data.get("response", {}).get("total", 0)
                }
                
        except aiohttp.ClientError as e:
            logger.error("polymart_request_error", error=str(e), type=resource_type)
            raise ClientError(f"Polymart API request error: {str(e)}")
        except Exception as e:
            logger.error("polymart_unexpected_error", error=str(e), type=resource_type)
            raise ClientError(f"Unexpected error in Polymart client: {str(e)}")

    async def fetch_resources(self) -> Dict:
        """
        Fetch resources from Polymart API.
        
        Returns:
            Dict containing the API response grouped by resource type
        """
        try:
            await self._ensure_session()
            
            # Get configured resource types
            resource_types = self.config["platforms"]["polymart"]["resource_types"]
            all_resources = {}
            
            # Map our resource types to Polymart's types
            type_map = {
                "plugin": "Plugins",
                "mod": "Mods",
                "resourcepack": "Resource Packs",
                "datapack": "Data Packs",
                "pluginpack": "Setups"
            }
            
            for resource_type in resource_types:
                start = 0
                resources_for_type = []
                
                while True:
                    payload = {
                        "premium": "-1",
                        "exclusive": "-1",
                        "type": type_map.get(resource_type, "Plugins"),
                        "category": "All",
                        "ver": "",
                        "query": "",
                        "sort": "downloads",
                        "tier": None,
                        "seed": 869199770,
                        "payment_methods": None,
                        "max_price": None,
                        "server_software": None,
                        "start": start,
                        "limit": self.batch_size,
                        "stringify": "0"
                    }
                    
                    url = f"{self.base_url}/search"
                    logger.info("fetching_polymart_resources", 
                               url=url,
                               payload=payload,
                               type=resource_type)
                    
                    async with self.session.post(url, json=payload) as response:
                        data = await response.json()
                        if not data.get("response", {}).get("result"):
                            logger.warning("no_resources_found",
                                         type=resource_type,
                                         response=data)
                            break
                            
                        resources = data.get("response", {}).get("result", [])
                        resources_for_type.extend(resources)
                        
                        # Check if we've reached the last page
                        if len(resources) < self.batch_size:
                            break
                            
                        start += self.batch_size
                
                # Store resources for this type
                all_resources[resource_type] = {
                    "result": resources_for_type,
                    "total": len(resources_for_type)
                }
            
            return all_resources
            
        except Exception as e:
            logger.error("polymart_fetch_failed", error=str(e))
            raise ClientError(f"Failed to fetch Polymart resources: {str(e)}")
        finally:
            await self._close_session()

    async def fetch_resources_by_type(self) -> Dict:
        """
        Fetch resources from Polymart for all configured resource types
        
        Returns:
            Dict containing fetched resources by type
            
        Raises:
            ClientError: If the request fails
        """
        try:
            await self._ensure_session()
            
            # Get configured resource types
            resource_types = self.config["platforms"]["polymart"]["resource_types"]
            
            # Fetch resources for each type
            all_resources = {}
            
            for resource_type in resource_types:
                try:
                    data = await self._fetch_by_type(resource_type)
                    all_resources[resource_type] = data
                    logger.info("polymart_type_fetched",
                               type=resource_type,
                               resource_count=len(data.get("resources", [])))
                except Exception as e:
                    logger.error("polymart_type_fetch_failed", 
                               type=resource_type,
                               error=str(e))
                    continue
            
            return all_resources
            
        except aiohttp.ClientError as e:
            logger.error("polymart_request_error", error=str(e))
            raise ClientError(f"Polymart API request error: {str(e)}")
        except Exception as e:
            logger.error("polymart_unexpected_error", error=str(e))
            raise ClientError(f"Unexpected error in Polymart client: {str(e)}")
        finally:
            await self._close_session() 