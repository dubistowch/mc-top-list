"""Modrinth mod transformer implementation."""

from typing import Any, Dict, List, Optional
from datetime import datetime

from ....contracts.transformer import TransformerContract
from ....contracts.api_client import ResourceType

class ModrinthModTransformer(TransformerContract):
    """Transformer for Modrinth mod resources."""

    def get_resource_type(self) -> ResourceType:
        return ResourceType.MOD

    def transform(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform mod-specific data."""
        base_data = self.transform_base_fields(raw_data)
        mod_data = {
            "mod_loader": self._extract_mod_loaders(raw_data),
            "side": self._extract_side(raw_data)
        }
        return {**base_data, **mod_data}

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
        return raw_data.get("slug", "unknown")

    def _extract_name(self, raw_data: Dict[str, Any]) -> str:
        return raw_data.get("title", "Unknown")

    def _extract_description(self, raw_data: Dict[str, Any]) -> Optional[str]:
        return raw_data.get("description", "")

    def _extract_author(self, raw_data: Dict[str, Any]) -> str:
        team = raw_data.get("team", "Unknown")
        if isinstance(team, list) and len(team) > 0:
            return team[0].get("user", {}).get("username", "Unknown")
        return "Unknown"

    def _extract_downloads(self, raw_data: Dict[str, Any]) -> int:
        return raw_data.get("downloads", 0)

    def _extract_created_at(self, raw_data: Dict[str, Any]) -> str:
        return raw_data.get("published", datetime.now().isoformat())

    def _extract_updated_at(self, raw_data: Dict[str, Any]) -> str:
        return raw_data.get("updated", datetime.now().isoformat())

    def _extract_mod_loaders(self, raw_data: Dict[str, Any]) -> List[str]:
        loaders = []
        for loader in raw_data.get("loaders", []):
            if loader in ["forge", "fabric", "quilt", "neoforge"]:
                loaders.append(loader)
            else:
                loaders.append("other")
        return loaders

    def _extract_side(self, raw_data: Dict[str, Any]) -> str:
        client_side = raw_data.get("client_side", "required")
        server_side = raw_data.get("server_side", "required")

        if client_side == "required" and server_side == "required":
            return "both"
        elif client_side == "required":
            return "client"
        elif server_side == "required":
            return "server"
        else:
            return "both"  # Default to both if unclear 