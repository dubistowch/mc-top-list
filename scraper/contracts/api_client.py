"""API client contracts module."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum

class ResourceType(Enum):
    """Resource type enumeration."""
    PLUGIN = "plugin"
    MOD = "mod"
    MODPACK = "modpack"
    RESOURCE_PACK = "resource_pack"

class APIClientContract(ABC):
    """Base contract for platform API clients."""
    
    @abstractmethod
    def _setup_headers(self) -> None:
        """Setup API headers including authentication if needed."""
        pass

    @abstractmethod
    async def get_resources(self, resource_type: ResourceType, category: str = "all", 
                          page: int = 1, per_page: int = 20) -> Tuple[List[Dict[str, Any]], int]:
        """Get resources of specified type from the platform.
        
        Args:
            resource_type: Type of resources to fetch
            category: Resource category (new/popular/all)
            page: Page number
            per_page: Number of items per page
            
        Returns:
            Tuple containing:
            - List of resources
            - Total count of resources
        """
        pass

    @abstractmethod
    async def get_resource_details(self, resource_id: str, resource_type: ResourceType) -> Dict[str, Any]:
        """Get detailed information about a specific resource.
        
        Args:
            resource_id: Resource identifier
            resource_type: Type of the resource
            
        Returns:
            Resource details
        """
        pass

    @abstractmethod
    def detect_resource_type(self, resource_data: Dict[str, Any]) -> ResourceType:
        """Detect the type of resource from its data.
        
        Args:
            resource_data: Raw resource data
            
        Returns:
            Detected resource type
        """
        pass

    @abstractmethod
    def supports_resource_type(self, resource_type: ResourceType) -> bool:
        """Check if the platform supports the resource type.
        
        Args:
            resource_type: Resource type to check
            
        Returns:
            True if supported, False otherwise
        """
        pass

    @abstractmethod
    async def fetch_resources(self) -> Dict[str, Any]:
        """Fetch popular resources from the platform.
        
        Returns:
            Raw API response containing resource data
        """
        pass 