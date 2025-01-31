"""
JSON file storage implementation
"""

import json
import logging
from typing import Dict, List, Any
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
            timestamp_dir = self._get_timestamp_dir(timestamp)
            
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
            timestamp_dir = self._get_timestamp_dir(timestamp)
            
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