"""Modrinth API client implementation."""

from typing import Any, Dict, List, Optional, Tuple
import aiohttp
import re

from scraper.contracts.api_client import APIClientContract, ResourceType
from scraper.utils.http import BaseHTTPClient

class ModrinthClient(BaseHTTPClient, APIClientContract):
    """Modrinth platform client implementation."""
    
    BASE_URL = "https://api.modrinth.com/v2"
    DEFAULT_LIMIT = 50
    platform_name = "modrinth"
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Modrinth client.
        
        Args:
            api_key: Optional API key for authentication
        """
        super().__init__()
        self.api_key = api_key
    
    def _setup_headers(self) -> Dict[str, str]:
        """Setup default headers."""
        headers = {
            "User-Agent": "mc-top-list/1.0",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = self.api_key  # Modrinth uses direct token authentication
        return headers
    
    def detect_resource_type(self, resource_data: Dict[str, Any]) -> ResourceType:
        """Detect resource type from resource data."""
        project_type = resource_data.get("project_type", "").lower()
        
        if project_type == "mod":
            return ResourceType.MOD
        elif project_type == "modpack":
            return ResourceType.MODPACK
        elif project_type == "resourcepack":
            return ResourceType.RESOURCE_PACK
        
        # Fallback detection based on other attributes
        if "loaders" in resource_data:
            return ResourceType.MOD
        elif "included_mods" in resource_data:
            return ResourceType.MODPACK
        elif any(kw in resource_data.get("description", "").lower() 
                for kw in ["texture", "resource pack", "resourcepack"]):
            return ResourceType.RESOURCE_PACK
            
        return ResourceType.MOD  # Default to mod if unclear
    
    def supports_resource_type(self, resource_type: ResourceType) -> bool:
        """Check if Modrinth supports the resource type."""
        return resource_type in [ResourceType.MOD, ResourceType.MODPACK, ResourceType.RESOURCE_PACK]
    
    async def get_resources(self, resource_type: ResourceType, category: str = "all", 
                          page: int = 1, per_page: int = 20) -> Tuple[List[Dict[str, Any]], int]:
        """Get resources from Modrinth."""
        if not self.supports_resource_type(resource_type):
            raise ValueError(f"Resource type {resource_type} not supported by Modrinth")

        # Map resource types to Modrinth facets
        facets = [["project_type:", resource_type.value]]
        
        # Map categories to sort methods
        sort = "updated" if category == "new" else "downloads" if category == "popular" else "relevance"
        
        params = {
            "facets": str(facets),  # Modrinth expects facets as string
            "index": sort,
            "limit": per_page,
            "offset": (page - 1) * per_page
        }
        
        url = f"{self.BASE_URL}/search"
        async with self.session.get(url, params=params, headers=self._setup_headers()) as response:
            response.raise_for_status()
            data = await response.json()
            return data["hits"], data["total_hits"]
    
    async def get_resource_details(self, resource_id: str, resource_type: ResourceType) -> Dict[str, Any]:
        """Get detailed resource information from Modrinth."""
        if not self.supports_resource_type(resource_type):
            raise ValueError(f"Resource type {resource_type} not supported by Modrinth")
            
        try:
            async with self.session.get(
                f"{self.BASE_URL}/project/{resource_id}",
                headers=self._setup_headers()
            ) as response:
                if response.status != 200:
                    response_text = await response.text()
                    raise Exception(f"Failed to fetch resource details: {response_text}")
                data = await response.json()
                if not isinstance(data, dict):
                    raise Exception(f"Unexpected response format: {data}")
                
                # Validate that the returned resource matches the expected type
                detected_type = self.detect_resource_type(data)
                if detected_type != resource_type:
                    raise ValueError(f"Resource {resource_id} is of type {detected_type}, not {resource_type}")
                    
                return data
        except Exception as e:
            raise Exception(f"Error fetching resource details from Modrinth: {str(e)}")
    
    async def fetch_resources(self) -> Dict[str, Any]:
        """
        Fetch popular resources from Modrinth
        
        Returns:
            Raw API response containing resource data
        """
        url = f"{self.BASE_URL}/search"
        params = {
            "limit": self.DEFAULT_LIMIT,
            "offset": 0,
            "index": "downloads",  # Sort by downloads for popular resources
            "facets": "[[\"project_type:mod\"]]",  # Only search for mods
            "query": ""  # Empty query to get all resources
        }
        
        headers = {
            "User-Agent": "mc-top-list/1.0.0 (github.com/dubistdu/mc-top-list)",
            "Accept": "application/json"
        }
        
        if self.api_key:
            headers["Authorization"] = self.api_key
        
        async with self.session.get(url, params=params, headers=headers) as response:
            response.raise_for_status()
            return await response.json()
    
    async def fetch_resource_details(self, resource_id: str) -> Dict[str, Any]:
        """Fetch details for a specific resource."""
        try:
            async with self.session.get(
                f"{self.BASE_URL}/project/{resource_id}",
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
            raise Exception(f"Error fetching resource details from Modrinth: {str(e)}")
    
    async def fetch_resource_versions(self, resource_id: str) -> List[Dict[str, Any]]:
        """Fetch versions for a specific resource."""
        try:
            async with self.session.get(
                f"{self.BASE_URL}/project/{resource_id}/version",
                headers=self._setup_headers()
            ) as response:
                if response.status != 200:
                    response_text = await response.text()
                    raise Exception(f"Failed to fetch resource versions: {response_text}")
                data = await response.json()
                if not isinstance(data, list):
                    raise Exception(f"Unexpected response format: {data}")
                return data
        except Exception as e:
            raise Exception(f"Error fetching resource versions from Modrinth: {str(e)}")
    
    async def fetch_resource_dependencies(self, resource_id: str, version: str) -> List[Dict[str, Any]]:
        """Fetch dependencies for a specific resource version."""
        try:
            async with self.session.get(
                f"{self.BASE_URL}/version/{version}",
                headers=self._setup_headers()
            ) as response:
                if response.status != 200:
                    response_text = await response.text()
                    raise Exception(f"Failed to fetch resource dependencies: {response_text}")
                data = await response.json()
                if not isinstance(data, dict):
                    raise Exception(f"Unexpected response format: {data}")
                dependencies = data.get("dependencies")
                if dependencies is None:
                    raise Exception("No 'dependencies' field in response")
                if not isinstance(dependencies, list):
                    raise Exception(f"Unexpected dependencies format: {dependencies}")
                return dependencies
        except Exception as e:
            raise Exception(f"Error fetching resource dependencies from Modrinth: {str(e)}") 