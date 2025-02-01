"""
Polymart data transformer
"""

from typing import Dict, List
from datetime import datetime
import structlog

from .base import BaseTransformer
from ...models.resource import Resource

logger = structlog.get_logger(__name__)

class PolymartTransformer(BaseTransformer):
    """Transformer for Polymart API data"""
    
    def transform(self, raw_data: Dict) -> List[Resource]:
        """
        Transform Polymart API data into normalized resources
        
        Args:
            raw_data: Raw data from Polymart API, grouped by resource type
            
        Returns:
            List of normalized Resource objects
        """
        resources = []
        
        try:
            # Process each resource type
            for resource_type, type_data in raw_data.items():
                # Get resources from response structure
                resources_data = type_data.get("result", [])
                if not resources_data:
                    logger.warning("no_resources_found", type=resource_type)
                    continue

                for resource in resources_data:
                    try:
                        # Get version info
                        version = resource.get("version", "")
                        versions = [version] if version else []
                        
                        # Get author info
                        author = "Unknown"
                        author_data = resource.get("owner", {})
                        if isinstance(author_data, dict):
                            author = author_data.get("name", "Unknown")
                        
                        # Create website URL
                        website_url = resource.get("url", "")
                        if not website_url:
                            website_url = f"https://polymart.org/resource/{resource.get('id', '')}"
                        
                        # Parse timestamps
                        try:
                            created_at = datetime.fromtimestamp(resource.get("creationTime", 0))
                            updated_at = datetime.fromtimestamp(resource.get("lastUpdateTime", 0))
                        except (ValueError, TypeError):
                            created_at = datetime.now()
                            updated_at = datetime.now()
                            
                        # Get categories
                        categories = []
                        if resource.get("supportedServerSoftware"):
                            categories.extend(
                                [s.strip().lower() for s in resource["supportedServerSoftware"].split(",")]
                            )
                        
                        # Create resource object
                        resource_obj = Resource(
                            id=str(resource.get("id", "")),
                            name=resource.get("title", "Unknown"),
                            description=resource.get("subtitle", "") or "",
                            author=author,
                            downloads=resource.get("downloads", 0),
                            resource_type=resource_type,
                            platform="polymart",
                            created_at=created_at,
                            updated_at=updated_at,
                            versions=versions,
                            categories=categories,
                            website_url=website_url,
                            source_url=resource.get("sourceCodeLink"),
                            license="unknown"
                        )
                        resources.append(resource_obj)
                    except KeyError as e:
                        logger.warning("missing_required_field", 
                                     error=str(e), 
                                     resource_id=resource.get("id", "unknown"))
                        continue
                    except ValueError as e:
                        logger.warning("invalid_data", 
                                     error=str(e), 
                                     resource_id=resource.get("id", "unknown"))
                        continue
                
                logger.info("polymart_type_transformed", 
                           type=resource_type,
                           resource_count=len([r for r in resources if r.resource_type == resource_type]))
            
            logger.info("polymart_resources_transformed", 
                       resource_count=len(resources))
            return resources
            
        except Exception as e:
            logger.error("polymart_transform_failed", error=str(e))
            raise ValueError(f"Failed to transform Polymart data: {str(e)}")