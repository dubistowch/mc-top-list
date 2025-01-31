"""
Modrinth data transformer
"""

from typing import Dict, List
from datetime import datetime
import structlog

from .base import BaseTransformer
from ...models.resource import Resource

logger = structlog.get_logger(__name__)

class ModrinthTransformer(BaseTransformer):
    """Transformer for Modrinth API data"""
    
    def transform(self, raw_data: Dict) -> List[Resource]:
        """
        Transform Modrinth API data into normalized resources
        
        Args:
            raw_data: Raw data from Modrinth API
            
        Returns:
            List of normalized Resource objects
        """
        resources = []
        
        try:
            hits = raw_data.get("hits", [])
            for hit in hits:
                try:
                    # Get license info safely
                    license_id = "unknown"
                    license_data = hit.get("license", {})
                    if isinstance(license_data, dict):
                        license_id = license_data.get("id", "unknown")
                    elif isinstance(license_data, str):
                        license_id = license_data
                    
                    # Create resource object
                    resource = Resource(
                        id=hit["project_id"],
                        name=hit["title"],
                        description=hit.get("description", ""),
                        author=hit.get("author", "Unknown"),
                        downloads=hit.get("downloads", 0),
                        resource_type="mod",  # Always mod for Modrinth
                        platform="modrinth",
                        created_at=datetime.fromisoformat(hit.get("date_created", "2025-01-01T00:00:00Z")),
                        updated_at=datetime.fromisoformat(hit.get("date_modified", "2025-01-01T00:00:00Z")),
                        versions=hit.get("versions", []),
                        categories=hit.get("categories", []),
                        website_url=f"https://modrinth.com/mod/{hit.get('slug', hit['project_id'])}",
                        source_url=hit.get("source_url"),
                        license=license_id
                    )
                    resources.append(resource)
                except KeyError as e:
                    logger.warning("missing_required_field", 
                                 error=str(e), 
                                 resource_id=hit.get("project_id", "unknown"))
                    continue
                except ValueError as e:
                    logger.warning("invalid_data", 
                                 error=str(e), 
                                 resource_id=hit.get("project_id", "unknown"))
                    continue
                
            logger.info("modrinth_resources_transformed", 
                       resource_count=len(resources),
                       total_hits=raw_data.get("total_hits", 0))
            return resources
            
        except Exception as e:
            logger.error("modrinth_transform_failed", error=str(e))
            raise ValueError(f"Failed to transform Modrinth data: {str(e)}") 