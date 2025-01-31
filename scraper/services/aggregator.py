"""Resource aggregation service."""

from typing import Dict, List
from collections import defaultdict
import structlog
from datetime import datetime
from pathlib import Path

from ..models.resource import Resource, ResourceCategory
from ..services.storage.json_storage import JsonStorage

logger = structlog.get_logger(__name__)

class ResourceAggregator:
    """Service for aggregating resources from different platforms."""
    
    def __init__(self, storage: JsonStorage):
        """
        Initialize aggregator with storage service.
        
        Args:
            storage: Storage service instance
        """
        self.storage = storage
    
    def _group_resources(self, resources: List[Resource]) -> Dict:
        """
        Group resources by type and category.
        
        Args:
            resources: List of resources to group
            
        Returns:
            Dict with grouped resources by type
        """
        # 按資源類型分組
        grouped = defaultdict(lambda: defaultdict(list))
        
        for resource in resources:
            # 轉換為字典格式
            resource_dict = resource.to_dict()
            
            # 加入到對應的分類
            if resource.downloads > 1000:  # 可配置的閾值
                grouped[resource.resource_type][ResourceCategory.POPULAR.value].append(resource_dict)
            
            thirty_days_ago = datetime.now().timestamp() - (30 * 24 * 60 * 60)
            if resource.created_at.timestamp() > thirty_days_ago:
                grouped[resource.resource_type][ResourceCategory.NEW.value].append(resource_dict)
            
            grouped[resource.resource_type][ResourceCategory.ALL.value].append(resource_dict)
        
        return grouped
    
    def aggregate(self, timestamp: str) -> Dict:
        """
        Aggregate resources from all platforms.
        
        Args:
            timestamp: Timestamp of data to aggregate
            
        Returns:
            Dict containing aggregated resources
        """
        try:
            # Load processed data
            all_resources = []
            platforms = []
            for platform in ["modrinth", "hangar"]:
                try:
                    resources = self.storage.load_processed_data(timestamp, platform)
                    if resources:
                        all_resources.extend(resources)
                        platforms.append(platform)
                except Exception as e:
                    logger.error("failed_to_load_platform_data",
                               platform=platform,
                               error=str(e))
            
            # Group resources
            grouped = self._group_resources(all_resources)
            
            # Add metadata
            result = {
                "metadata": {
                    "timestamp": timestamp,
                    "total_resources": len(all_resources),
                    "platforms": platforms
                },
                "resources": grouped
            }
            
            # Save aggregated data
            self.storage.save_aggregated_data(timestamp, result)
            
            logger.info("resources_aggregated",
                       timestamp=timestamp,
                       total_count=len(all_resources))
            
            return result
            
        except Exception as e:
            logger.error("aggregation_failed", error=str(e))
            raise ValueError(f"Failed to aggregate resources: {str(e)}") 