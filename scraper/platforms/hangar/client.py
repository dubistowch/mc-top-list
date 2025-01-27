"""Hangar API client implementation."""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import aiohttp

from scraper.contracts.api_client import APIClientContract, ResourceType
from scraper.utils.http import BaseHTTPClient

class HangarClient(BaseHTTPClient, APIClientContract):
    """Hangar API client."""
    
    BASE_URL = "https://hangar.papermc.io/api/v1"
    DEFAULT_LIMIT = 25
    platform_name = "hangar"
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Hangar client.
        
        Args:
            api_key: Optional API key for authentication
        """
        super().__init__()
        self.api_key = api_key
        self._jwt_token = None
        self._token_expires_at = None
    
    def _setup_headers(self) -> Dict[str, str]:
        """Setup default headers."""
        headers = {
            "User-Agent": "mc-top-list/1.0",
            "Accept": "application/json",
        }
        if self._jwt_token:
            headers["Authorization"] = f"Bearer {self._jwt_token}"
        return headers
    
    def detect_resource_type(self, resource_data: Dict[str, Any]) -> ResourceType:
        """Detect resource type from resource data."""
        # Hangar 主要是插件平台
        return ResourceType.PLUGIN
    
    def supports_resource_type(self, resource_type: ResourceType) -> bool:
        """Check if Hangar supports the resource type."""
        return resource_type == ResourceType.PLUGIN
    
    async def get_resources(self, resource_type: ResourceType, category: str = "all", 
                          page: int = 1, per_page: int = 20) -> Tuple[List[Dict[str, Any]], int]:
        """Get resources from Hangar."""
        if not self.supports_resource_type(resource_type):
            raise ValueError(f"Resource type {resource_type} not supported by Hangar")
        
        # Map categories to sort methods
        sort = "newest" if category == "new" else "downloads" if category == "popular" else "stars"
        
        params = {
            "sort": sort,
            "offset": (page - 1) * per_page,
            "limit": per_page
        }
        
        await self._ensure_authenticated()
        
        try:
            async with self.session.get(
                f"{self.BASE_URL}/projects",
                params=params,
                headers=self._setup_headers()
            ) as response:
                if response.status != 200:
                    response_text = await response.text()
                    raise Exception(f"Failed to fetch resources: {response_text}")
                data = await response.json()
                if not isinstance(data, dict):
                    raise Exception(f"Unexpected response format: {data}")
                result = data.get("result")
                total = data.get("pagination", {}).get("count")
                if result is None or total is None:
                    raise Exception("Missing required fields in response")
                if not isinstance(result, list):
                    raise Exception(f"Unexpected result format: {result}")
                return result, total
        except Exception as e:
            raise Exception(f"Error fetching resources from Hangar: {str(e)}")
    
    async def get_resource_details(self, resource_id: str, resource_type: ResourceType) -> Dict[str, Any]:
        """Get detailed resource information from Hangar."""
        if not self.supports_resource_type(resource_type):
            raise ValueError(f"Resource type {resource_type} not supported by Hangar")
            
        try:
            owner, slug = resource_id.split("/")
            async with self.session.get(
                f"{self.BASE_URL}/projects/{owner}/{slug}",
                headers=self._setup_headers()
            ) as response:
                if response.status != 200:
                    response_text = await response.text()
                    raise Exception(f"Failed to fetch resource details: {response_text}")
                data = await response.json()
                if not isinstance(data, dict):
                    raise Exception(f"Unexpected response format: {data}")
                return data
        except Exception as e:
            raise Exception(f"Error fetching resource details from Hangar: {str(e)}")
    
    async def _ensure_authenticated(self) -> None:
        """Ensure client is authenticated if API key is provided."""
        if not self.api_key:
            return
            
        # Check if token is still valid (with 5 minutes buffer)
        if (self._jwt_token and self._token_expires_at and 
            self._token_expires_at > datetime.now() + timedelta(minutes=5)):
            return
            
        try:
            async with aiohttp.ClientSession() as session:
                params = {"apiKey": self.api_key}
                headers = {
                    "User-Agent": "mc-top-list/1.0",
                    "Accept": "application/json"
                }
                
                async with session.post(
                    f"{self.BASE_URL}/authenticate",
                    params=params,
                    headers=headers
                ) as response:
                    if response.status != 200:
                        response_text = await response.text()
                        raise Exception(f"Failed to authenticate with Hangar API: {response_text}")
                    
                    data = await response.json()
                    token = data.get("token")
                    if not token:
                        raise Exception("No token in authentication response")
                        
                    expiry = data.get("expiresIn", 3600)  # Default to 1 hour if not specified
                    self._jwt_token = token
                    self._token_expires_at = datetime.now() + timedelta(seconds=expiry)
        except Exception as e:
            self._jwt_token = None
            self._token_expires_at = None
            raise Exception(f"Authentication failed: {str(e)}")
    
    async def fetch_resources(self) -> Dict[str, Any]:
        """
        Fetch popular resources from Hangar
        
        Returns:
            Raw API response containing resource data
        """
        await self._ensure_authenticated()
        
        params = {
            "limit": self.DEFAULT_LIMIT,
            "offset": 0,
            "sort": "downloads"  # Sort by downloads for popular resources
        }
        
        async with self.session.get(
            f"{self.BASE_URL}/projects",
            params=params,
            headers=self._setup_headers()
        ) as response:
            response.raise_for_status()
            return await response.json()
    
    async def fetch_resource_details(self, resource_id: str) -> Dict[str, Any]:
        """Fetch details for a specific resource."""
        await self._ensure_authenticated()
        
        # In Hangar, resource_id is in format "author/name"
        author, name = resource_id.split("/")
        
        try:
            async with self.session.get(
                f"{self.BASE_URL}/projects/{author}/{name}",
                headers=self._setup_headers()
            ) as response:
                if response.status != 200:
                    response_text = await response.text()
                    raise Exception(f"Failed to fetch resource details: {response_text}")
                data = await response.json()
                if not isinstance(data, dict):
                    raise Exception(f"Unexpected response format: {data}")
                return data
        except Exception as e:
            raise Exception(f"Error fetching resource details from Hangar: {str(e)}")
    
    async def fetch_resource_versions(self, resource_id: str) -> List[Dict[str, Any]]:
        """Fetch versions for a specific resource."""
        await self._ensure_authenticated()
        
        # In Hangar, resource_id is in format "author/name"
        author, name = resource_id.split("/")
        
        try:
            async with self.session.get(
                f"{self.BASE_URL}/projects/{author}/{name}/versions",
                headers=self._setup_headers()
            ) as response:
                if response.status != 200:
                    response_text = await response.text()
                    raise Exception(f"Failed to fetch resource versions: {response_text}")
                data = await response.json()
                if not isinstance(data, dict):
                    raise Exception(f"Unexpected response format: {data}")
                result = data.get("result")
                if result is None:
                    raise Exception("No 'result' field in response")
                return result
        except Exception as e:
            raise Exception(f"Error fetching resource versions from Hangar: {str(e)}")
    
    async def fetch_resource_dependencies(self, resource_id: str, version: str) -> List[Dict[str, Any]]:
        """Fetch dependencies for a specific resource version."""
        await self._ensure_authenticated()
        
        endpoint = f"{self.BASE_URL}/projects/{resource_id}/versions/{version}/dependencies"
        
        try:
            async with self.session.get(endpoint, headers=self._setup_headers()) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch resource dependencies: {response.status}")
                return await response.json()
        except Exception as e:
            raise Exception(f"Error fetching resource dependencies from Hangar: {str(e)}") 