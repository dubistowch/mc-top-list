"""Tests for Hangar transformers."""

import pytest
from datetime import datetime

from scraper.platforms.hangar.transformers import HangarPluginTransformer
from scraper.contracts.api_client import ResourceType

@pytest.fixture
def base_resource_data():
    """Base resource data fixture."""
    return {
        "owner": "TestAuthor",
        "slug": "test-plugin",
        "name": "Test Plugin",
        "description": "Test description",
        "stats": {
            "downloads": 1000
        },
        "created_at": "2024-01-01T00:00:00Z",
        "last_updated": "2024-01-02T00:00:00Z"
    }

def test_plugin_transformer(base_resource_data):
    """Test plugin transformer."""
    # Arrange
    transformer = HangarPluginTransformer()
    plugin_data = {
        **base_resource_data,
        "platform_dependencies": [
            {
                "platform": "paper",
                "version": "1.20.1"
            },
            {
                "platform": "spigot",
                "version": "1.20.1"
            },
            {
                "platform": "unknown",
                "version": "1.20.1"
            }
        ]
    }

    # Act
    result = transformer.transform(plugin_data)

    # Assert
    assert result["resource_type"] == ResourceType.PLUGIN.value
    assert result["id"] == "TestAuthor/test-plugin"
    assert result["name"] == "Test Plugin"
    assert result["server_type"] == ["paper", "spigot", "other"]
    assert result["api_version"] == "1.20.1"

def test_plugin_transformer_no_dependencies(base_resource_data):
    """Test plugin transformer with no dependencies."""
    # Arrange
    transformer = HangarPluginTransformer()
    plugin_data = {
        **base_resource_data
    }

    # Act
    result = transformer.transform(plugin_data)

    # Assert
    assert result["resource_type"] == ResourceType.PLUGIN.value
    assert result["server_type"] == ["paper"]  # Default value
    assert result["api_version"] == "unknown"

def test_plugin_transformer_missing_optional_fields(base_resource_data):
    """Test plugin transformer with missing optional fields."""
    # Arrange
    transformer = HangarPluginTransformer()
    plugin_data = {
        **base_resource_data
    }
    del plugin_data["last_updated"]
    del plugin_data["description"]

    # Act
    result = transformer.transform(plugin_data)

    # Assert
    assert result["resource_type"] == ResourceType.PLUGIN.value
    assert result["updated_at"] == plugin_data["created_at"]  # Fallback to created_at
    assert result["description"] is None 