"""Transformer contracts module."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

from .api_client import ResourceType
from scraper.models.resource import Resource

class TransformerContract(ABC):
    """Base contract for resource transformers."""
    
    @abstractmethod
    def get_resource_type(self) -> ResourceType:
        """Return the resource type this transformer handles."""
        pass
    
    @abstractmethod
    def transform(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform platform-specific data to standardized format."""
        pass
    
    @abstractmethod
    def transform_base_fields(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform common base fields that all resources share."""
        pass
    
    @abstractmethod
    def _extract_id(self, raw_data: Dict[str, Any]) -> str:
        """Extract resource ID."""
        pass
    
    @abstractmethod
    def _extract_name(self, raw_data: Dict[str, Any]) -> str:
        """Extract resource name."""
        pass
    
    @abstractmethod
    def _extract_description(self, raw_data: Dict[str, Any]) -> Optional[str]:
        """Extract resource description."""
        pass
    
    @abstractmethod
    def _extract_author(self, raw_data: Dict[str, Any]) -> str:
        """Extract resource author."""
        pass
    
    @abstractmethod
    def _extract_downloads(self, raw_data: Dict[str, Any]) -> int:
        """Extract download count."""
        pass
    
    @abstractmethod
    def _extract_created_at(self, raw_data: Dict[str, Any]) -> str:
        """Extract creation timestamp."""
        pass
    
    @abstractmethod
    def _extract_updated_at(self, raw_data: Dict[str, Any]) -> str:
        """Extract last update timestamp."""
        pass

class ResourceTransformerContract:
    """Resource transformer interface"""

    def extract_downloads(self, resource_data: Dict) -> int:
        """
        Extract download count from resource data
        
        Args:
            resource_data: Raw resource data
            
        Returns:
            Download count
        """
        raise NotImplementedError

    def extract_dates(self, resource_data: Dict) -> Tuple[str, str]:
        """
        Extract creation and update dates from resource data
        
        Args:
            resource_data: Raw resource data
            
        Returns:
            Tuple of (created_at, updated_at) dates in ISO format
        """
        raise NotImplementedError

    def map_resource_type(self, resource_type: str) -> str:
        """
        Map platform-specific resource type to standard type
        
        Args:
            resource_type: Platform-specific resource type
            
        Returns:
            Standardized resource type
        """
        raise NotImplementedError

    def get_resource_url(self, resource_id: str, author: str) -> str:
        """
        Generate resource URL
        
        Args:
            resource_id: Resource ID
            author: Resource author
            
        Returns:
            Resource URL
        """
        raise NotImplementedError

    def calculate_popularity(self, resource_data: Dict) -> float:
        """
        Calculate resource popularity score
        
        Args:
            resource_data: Raw resource data
            
        Returns:
            Popularity score (higher is more popular)
        """
        raise NotImplementedError

    def transform_resource(self, resource_data: Dict) -> Dict:
        """
        Transform platform-specific resource data to standard format
        
        Args:
            resource_data: Raw resource data
            
        Returns:
            Transformed resource data in standard format
        """
        raise NotImplementedError 