"""Modrinth modpack transformer implementation."""

from typing import Any, Dict, List, Optional
from datetime import datetime

from ....contracts.transformer import TransformerContract
from ....contracts.api_client import ResourceType

class ModrinthModpackTransformer(TransformerContract):
    """Transformer for Modrinth modpack resources."""

    def get_resource_type(self) -> ResourceType:
        return ResourceType.MODPACK

    def transform(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform modpack-specific data."""
        base_data = self.transform_base_fields(raw_data)
        modpack_data = {
            "mod_count": self._extract_mod_count(raw_data),
            "minecraft_versions": self._extract_minecraft_versions(raw_data)
        }
        return {**base_data, **modpack_data}

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

    def _extract_mod_count(self, raw_data: Dict[str, Any]) -> int:
        return len(raw_data.get("dependencies", []))

    def _extract_minecraft_versions(self, raw_data: Dict[str, Any]) -> List[str]:
        return raw_data.get("game_versions", []) 