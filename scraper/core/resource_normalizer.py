"""
Handles normalization of resource data from different platforms.
"""

from typing import Dict, List
from datetime import datetime

from scraper.models.resource import Resource, ResourceCategory, VersionInfo, Statistics, Source
from scraper.utils.logger import setup_logger
from scraper.validators.schema_validator import SchemaValidator
from scraper.platforms.modrinth.transformers.resource import ModrinthResourceTransformer
from scraper.platforms.hangar.transformers.resource import HangarResourceTransformer


class ResourceNormalizer:
    """Handles normalization of resource data"""

    def __init__(self):
        """Initialize the resource normalizer"""
        self.logger = setup_logger()
        self.validator = SchemaValidator()
        self.transformers = {
            "modrinth": ModrinthResourceTransformer(),
            "hangar": HangarResourceTransformer()
        }

    def normalize_results(
        self, raw_results: Dict[str, List[Dict]]
    ) -> Dict[str, Dict[str, List[Resource]]]:
        """
        Normalize raw results into Resource objects
        
        Args:
            raw_results: Raw results organized by platform, containing lists of resources
            
        Returns:
            Dict mapping platforms to their normalized resources by category
        """
        normalized: Dict[str, Dict[str, List[Resource]]] = {}
        
        for platform, resources in raw_results.items():
            normalized[platform] = {"popular": []}  # Initialize with popular category
            transformer = self.transformers.get(platform)
            
            if not transformer:
                self.logger.error(f"No transformer found for platform: {platform}")
                continue
            
            for resource_data in resources:
                try:
                    # Transform platform-specific data to standard format
                    transformed_data = transformer.transform_resource(resource_data)
                    
                    # Validate against schema
                    self.validator.validate(transformed_data, "resource")
                    
                    # Create version info
                    version_info = VersionInfo(
                        version=transformed_data["version"],
                        game_version=transformed_data["game_version"],
                        download_url=transformed_data["download_url"],
                        dependencies=[]  # 使用預設值
                    )
                    
                    # Create statistics
                    stats = Statistics(
                        downloads=transformed_data["downloads"],
                        rating=transformed_data["rating"],
                        votes=transformed_data["votes"]
                    )
                    
                    # Create source
                    source = Source(
                        platform=platform,
                        url=transformed_data["url"],
                        external_id=transformed_data["id"]
                    )
                    
                    # Create Resource object
                    resource = Resource(
                        id=transformed_data["id"],
                        name=transformed_data["name"],
                        type=transformed_data["resource_type"],
                        description=transformed_data["description"],
                        authors=[transformed_data["author"]],
                        version=version_info,
                        sources=[source],
                        stats=stats,
                        created_at=datetime.fromisoformat(transformed_data["created_at"].replace("Z", "+00:00")),
                        updated_at=datetime.fromisoformat(transformed_data["updated_at"].replace("Z", "+00:00")),
                        category=ResourceCategory(transformed_data["category"]),
                        popularity=transformed_data["popularity"]  # 使用轉換器提供的熱門度分數
                    )
                    
                    normalized[platform]["popular"].append(resource)
                    
                except Exception as e:
                    self.logger.error(f"Failed to normalize resource {resource_data.get('id', 'unknown')}: {e}")
                    continue
        
        return normalized 