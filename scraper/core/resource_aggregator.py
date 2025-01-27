"""
Handles aggregation of resources from different platforms.
"""

from typing import Dict, List

from scraper.models.resource import Resource
from scraper.utils.logger import setup_logger


class ResourceAggregator:
    """Handles aggregation of resources from different platforms"""

    def __init__(self):
        """Initialize the resource aggregator"""
        self.logger = setup_logger()

    def aggregate_results(
        self, normalized_results: Dict[str, Dict[str, List[Resource]]]
    ) -> Dict[str, Dict[str, List[Resource]]]:
        """
        Aggregate normalized results
        
        Currently this just combines the results, but could be extended to:
        - Remove duplicates
        - Filter by criteria
        - etc.
        
        Args:
            normalized_results: Normalized results organized by platform and category
            
        Returns:
            Dict mapping platforms to their aggregated resources by category
        """
        aggregated = {}
        
        for platform, categories in normalized_results.items():
            aggregated[platform] = {}
            
            for category, resources in categories.items():
                # 使用 popularity 欄位進行排序
                sorted_resources = sorted(
                    resources,
                    key=lambda x: x.popularity,
                    reverse=True
                )
                
                # 取前 100 個資源
                aggregated[platform][category] = sorted_resources[:100]
                
                self.logger.info(
                    f"Aggregated {len(aggregated[platform][category])} resources "
                    f"for {platform} {category}"
                )
        
        return aggregated 