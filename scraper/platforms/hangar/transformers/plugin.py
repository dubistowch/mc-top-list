"""Hangar plugin transformer implementation."""

from typing import Any, Dict, List, Optional
from datetime import datetime

from ....contracts.transformer import TransformerContract
from ....contracts.api_client import ResourceType

class HangarPluginTransformer(TransformerContract):
    """Transformer for Hangar plugin resources."""

    def get_resource_type(self) -> ResourceType:
        return ResourceType.PLUGIN

    def transform(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform plugin-specific data."""
        base_data = self.transform_base_fields(raw_data)
        plugin_data = {
            "platforms": self._extract_platforms(raw_data),
            "minecraft_versions": self._extract_minecraft_versions(raw_data)
        }
        return {**base_data, **plugin_data}

    def transform_base_fields(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform common base fields."""
        namespace = raw_data.get("namespace", {})
        owner = namespace.get("owner", "Unknown")
        
        return {
            "id": str(raw_data.get("id", "unknown")),
            "name": raw_data.get("name", "Unknown"),
            "description": raw_data.get("description", ""),
            "author": owner,  # 使用 namespace.owner 作為作者
            "downloads": raw_data.get("stats", {}).get("downloads", 0),
            "created_at": raw_data.get("createdAt", ""),
            "updated_at": raw_data.get("lastUpdated", ""),
            "resource_type": "plugin",  # Hangar 只支援插件
            "category": "popular"  # 預設為熱門
        }

    def _extract_id(self, raw_data: Dict[str, Any]) -> str:
        return str(raw_data.get("id", "unknown"))

    def _extract_name(self, raw_data: Dict[str, Any]) -> str:
        return raw_data.get("name", "Unknown")

    def _extract_description(self, raw_data: Dict[str, Any]) -> Optional[str]:
        return raw_data.get("description", "")

    def _extract_author(self, raw_data: Dict[str, Any]) -> str:
        namespace = raw_data.get("namespace", {})
        owner = namespace.get("owner")
        if not owner:
            # 如果找不到作者，使用 Unknown 作為預設值
            self.logger.warning(f"No author found for resource {raw_data.get('id', 'unknown')}")
            return "Unknown"
        return owner

    def _extract_downloads(self, raw_data: Dict[str, Any]) -> int:
        stats = raw_data.get("stats", {})
        return stats.get("downloads", 0)

    def _extract_created_at(self, raw_data: Dict[str, Any]) -> str:
        return raw_data.get("createdAt", datetime.now().isoformat())

    def _extract_updated_at(self, raw_data: Dict[str, Any]) -> str:
        return raw_data.get("lastUpdated", datetime.now().isoformat())

    def _extract_platforms(self, raw_data: Dict[str, Any]) -> List[str]:
        settings = raw_data.get("settings", {})
        tags = settings.get("tags", [])
        return tags

    def _extract_minecraft_versions(self, raw_data: Dict[str, Any]) -> List[str]:
        return []  # Version information is not directly available in the API response 