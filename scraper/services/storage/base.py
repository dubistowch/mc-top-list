"""
Base storage interface
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path

from ...models.resource import Resource

class BaseStorage(ABC):
    """Base interface for data storage operations"""
    
    def __init__(self, base_dir: Path):
        """
        Initialize storage
        
        Args:
            base_dir: Base directory for data storage
        """
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_timestamp_dir(self, timestamp: datetime) -> Path:
        """
        Get directory path for specific timestamp
        
        Args:
            timestamp: Timestamp for the data
            
        Returns:
            Path object for the timestamp directory
        """
        dir_name = timestamp.strftime("%Y%m%d_%H%M%S")
        path = self.base_dir / dir_name
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @abstractmethod
    async def save_raw_data(self, data: Dict[str, Any], timestamp: datetime) -> None:
        """
        Save raw API response data
        
        Args:
            data: Raw data from API
            timestamp: Data collection timestamp
        """
        pass
    
    @abstractmethod
    async def save_processed_data(self, resources: Dict[str, List[Resource]], timestamp: datetime) -> None:
        """
        Save processed resource data
        
        Args:
            resources: Processed resources by platform
            timestamp: Data collection timestamp
        """
        pass 