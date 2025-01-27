"""Tests for Modrinth transformers."""

import pytest
from datetime import datetime

from scraper.platforms.modrinth.transformers import (
    ModrinthModTransformer,
    ModrinthModpackTransformer,
    ModrinthResourcePackTransformer
)
from scraper.contracts.api_client import ResourceType

@pytest.fixture
def base_resource_data():
    """Base resource data fixture."""
    return {
        "id": "test-id",
        "title": "Test Resource",
        "description": "Test description",
        "author": "TestAuthor",
        "downloads": 1000,
        "published": "2024-01-01T00:00:00Z",
        "updated": "2024-01-02T00:00:00Z"
    }

def test_mod_transformer(base_resource_data):
    """Test mod transformer."""
    # Arrange
    transformer = ModrinthModTransformer()
    mod_data = {
        **base_resource_data,
        "loaders": ["fabric", "forge", "unknown"],
        "client_side": "required",
        "server_side": "optional"
    }

    # Act
    result = transformer.transform(mod_data)

    # Assert
    assert result["resource_type"] == ResourceType.MOD.value
    assert result["id"] == "test-id"
    assert result["name"] == "Test Resource"
    assert result["mod_loader"] == ["fabric", "forge", "other"]
    assert result["side"] == "client"

def test_modpack_transformer(base_resource_data):
    """Test modpack transformer."""
    # Arrange
    transformer = ModrinthModpackTransformer()
    modpack_data = {
        **base_resource_data,
        "loaders": ["fabric"],
        "latest_version": {
            "dependencies": [
                {"project_id": "mod1", "name": "Mod One", "version_number": "1.0.0"},
                {"project_id": "mod2", "name": "Mod Two", "version_number": "2.0.0"}
            ]
        }
    }

    # Act
    result = transformer.transform(modpack_data)

    # Assert
    assert result["resource_type"] == ResourceType.MODPACK.value
    assert result["mod_loader"] == ["fabric"]
    assert result["mods_count"] == 2
    assert len(result["included_mods"]) == 2
    assert result["included_mods"][0]["name"] == "Mod One"

def test_resource_pack_transformer(base_resource_data):
    """Test resource pack transformer."""
    # Arrange
    transformer = ModrinthResourcePackTransformer()
    resource_pack_data = {
        **base_resource_data,
        "description": "A beautiful 32x32 texture pack with custom sounds",
        "game_versions": ["1.20.1", "1.20.2"]
    }

    # Act
    result = transformer.transform(resource_pack_data)

    # Assert
    assert result["resource_type"] == ResourceType.RESOURCE_PACK.value
    assert result["resolution"] == "32x32"
    assert "textures" in result["features"]
    assert "sounds" in result["features"]
    assert result["game_versions"] == ["1.20.1", "1.20.2"] 