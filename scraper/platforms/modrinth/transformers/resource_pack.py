"""Modrinth resource pack transformer implementation."""

from typing import Any, Dict, List, Optional
from datetime import datetime

from ....contracts.transformer import TransformerContract
from ....contracts.api_client import ResourceType

class ModrinthResourcePackTransformer(TransformerContract):
    """Transformer for Modrinth resource pack resources."""

    def get_resource_type(self) -> ResourceType:
        return ResourceType.RESOURCE_PACK

    def transform(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform resource pack-specific data."""
        base_data = self.transform_base_fields(raw_data)
        pack_data = {
            "resolution": self._extract_resolution(raw_data),
            "minecraft_versions": self._extract_minecraft_versions(raw_data)
        }
        return {**base_data, **pack_data}

    def transform_base_fields(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform common base fields."""
        return {
            "id": self._extract_id(raw_data),
            "name": self._extract_name(raw_data),
            "description": self._extract_description(raw_data),
            "author": self._extract_author(raw_data),
            "downloads": self._extract_downloads(raw_data),
            "created_at": self._extract_created_at(raw_data),
            "updated_at": self._extract_updated_at(raw_data),
            "resource_type": self.get_resource_type().value,
            "category": "popular"  # Default to popular since we're sorting by downloads
        }

    def _extract_id(self, raw_data: Dict[str, Any]) -> str:
        return raw_data["project_id"]

    def _extract_name(self, raw_data: Dict[str, Any]) -> str:
        return raw_data["title"]

    def _extract_description(self, raw_data: Dict[str, Any]) -> Optional[str]:
        return raw_data.get("description", "")

    def _extract_author(self, raw_data: Dict[str, Any]) -> str:
        return raw_data.get("author", "Unknown")

    def _extract_downloads(self, raw_data: Dict[str, Any]) -> int:
        return raw_data.get("downloads", 0)

    def _extract_created_at(self, raw_data: Dict[str, Any]) -> str:
        return raw_data.get("date_created", datetime.now().isoformat())

    def _extract_updated_at(self, raw_data: Dict[str, Any]) -> str:
        return raw_data.get("date_modified", datetime.now().isoformat())

    def _extract_resolution(self, raw_data: Dict[str, Any]) -> str:
        # Try to extract resolution from description or tags
        description = raw_data.get("description", "").lower()
        tags = raw_data.get("categories", [])
        
        # Check common resolutions
        resolutions = ["16x", "32x", "64x", "128x", "256x", "512x", "1024x"]
        
        for res in resolutions:
            if res in description or res in tags:
                return res
        
        return "unknown"

    def _extract_minecraft_versions(self, raw_data: Dict[str, Any]) -> List[str]:
        return raw_data.get("game_versions", []) 