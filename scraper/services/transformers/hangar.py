"""
Hangar data transformer
"""

from typing import Dict, List
from datetime import datetime
import structlog

from .base import BaseTransformer
from ...models.resource import Resource

logger = structlog.get_logger(__name__)

class HangarTransformer(BaseTransformer):
    """Transformer for Hangar API data"""
    
    def transform(self, raw_data: Dict) -> List[Resource]:
        """
        Transform Hangar API data into normalized resources
        
        Args:
            raw_data: Raw data from Hangar API
            
        Returns:
            List of normalized Resource objects
        """
        resources = []
        
        try:
            results = raw_data.get("result", [])
            for result in results:
                try:
                    # Get stats safely
                    stats = result.get("stats", {})
                    if not isinstance(stats, dict):
                        stats = {}
                    
                    # Get dates safely
                    created_at = result.get("createdAt", "2025-01-01T00:00:00Z")
                    updated_at = result.get("lastUpdated", created_at)
                    
                    # Create resource object
                    resource = Resource(
                        id=str(result["id"]),
                        name=result["name"],
                        description=result.get("description", ""),
                        author=result.get("owner", "Unknown"),
                        downloads=stats.get("downloads", 0),
                        resource_type="plugin",  # Hangar only hosts plugins
                        platform="hangar",
                        created_at=datetime.fromisoformat(created_at.replace("Z", "+00:00")),
                        updated_at=datetime.fromisoformat(updated_at.replace("Z", "+00:00")),
                        versions=result.get("gameVersions", []),
                        categories=result.get("categories", []),
                        website_url=f"https://hangar.papermc.io/{result.get('owner', 'unknown')}/{result['name']}",
                        source_url=None,  # Not available in API response
                        license=result.get("licenseName", "unknown")
                    )
                    resources.append(resource)
                except KeyError as e:
                    logger.warning("missing_required_field", 
                                 error=str(e), 
                                 resource_id=result.get("id", "unknown"))
                    continue
                except ValueError as e:
                    logger.warning("invalid_data", 
                                 error=str(e), 
                                 resource_id=result.get("id", "unknown"))
                    continue
                
            logger.info("hangar_resources_transformed", 
                       resource_count=len(resources),
                       total_results=len(results))
            return resources
            
        except Exception as e:
            logger.error("hangar_transform_failed", error=str(e))
            raise ValueError(f"Failed to transform Hangar data: {str(e)}") 