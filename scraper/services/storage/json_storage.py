"""
JSON file storage implementation
"""

import json
import logging
from typing import Dict, List, Any, Union
from datetime import datetime
from pathlib import Path

from .base import BaseStorage
from ...models.resource import Resource

logger = logging.getLogger(__name__)

class JsonStorage(BaseStorage):
    """Storage implementation using JSON files"""
    
    async def save_raw_data(self, data: Dict[str, Any], timestamp: datetime) -> None:
        """
        Save raw API response data as JSON
        
        Args:
            data: Raw data from API
            timestamp: Data collection timestamp
        """
        try:
            # Create timestamp directory
            timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
            timestamp_dir = self.base_dir / "data" / "raw" / timestamp_str
            timestamp_dir.mkdir(parents=True, exist_ok=True)
            
            for platform, platform_data in data.items():
                file_path = timestamp_dir / f"{platform}_raw.json"
                
                logger.info("Saving raw data for %s to %s", platform, file_path)
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(platform_data, f, indent=2, ensure_ascii=False)
                    
        except Exception as e:
            logger.error("Failed to save raw data: %s", str(e))
            raise
    
    async def save_processed_data(self, resources: Dict[str, List[Resource]], timestamp: datetime) -> None:
        """
        Save processed resource data as JSON
        
        Args:
            resources: Processed resources by platform
            timestamp: Data collection timestamp
        """
        try:
            # Create timestamp directory
            timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
            timestamp_dir = self.base_dir / "data" / "processed" / timestamp_str
            timestamp_dir.mkdir(parents=True, exist_ok=True)
            
            for platform, platform_resources in resources.items():
                file_path = timestamp_dir / f"{platform}_processed.json"
                
                # Convert resources to dictionaries
                resource_dicts = [resource.to_dict() for resource in platform_resources]
                
                logger.info("Saving processed data for %s to %s", platform, file_path)
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump({
                        "timestamp": timestamp.isoformat(),
                        "platform": platform,
                        "resources": resource_dicts
                    }, f, indent=2, ensure_ascii=False)
                    
        except Exception as e:
            logger.error("Failed to save processed data: %s", str(e))
            raise
    
    def _parse_resource(self, data: Dict) -> Resource:
        """
        Parse resource data from JSON.
        
        Args:
            data: Raw resource data
            
        Returns:
            Resource object
        """
        # Convert datetime strings to datetime objects
        if "created_at" in data:
            data["created_at"] = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
        if "updated_at" in data:
            data["updated_at"] = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
            
        return Resource(**data)
    
    def load_processed_data(self, timestamp: str, platform: str) -> List[Resource]:
        """
        Load processed data for a platform.
        
        Args:
            timestamp: Data timestamp
            platform: Platform name
            
        Returns:
            List of Resource objects
        """
        file_path = self.base_dir / "data" / "processed" / timestamp / f"{platform}_processed.json"
        if not file_path.exists():
            return []
            
        with open(file_path) as f:
            data = json.load(f)
            return [self._parse_resource(resource) for resource in data.get("resources", [])]
    
    def save_aggregated_data(self, timestamp: str, data: Dict) -> None:
        """
        Save aggregated data.
        
        Args:
            timestamp: Data timestamp
            data: Aggregated data to save
        """
        # Create directory if not exists
        output_dir = self.base_dir / "data" / "aggregated" / timestamp
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save aggregated data
        output_file = output_dir / "aggregated.json"
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2, default=str) 