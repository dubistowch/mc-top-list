"""
Tests for scraper service
"""

import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, AsyncMock

from ..services.scraper_service import ScraperService
from ..models.platform import Platform
from ..models.resource import Resource

@pytest.fixture
def mock_client():
    """Create a mock API client"""
    client = AsyncMock()
    client.fetch_resources.return_value = {
        "hits": [
            {
                "project_id": "test-mod",
                "title": "Test Mod",
                "description": "A test mod",
                "author": "Tester",
                "downloads": 1000,
                "project_type": "mod",
                "date_created": "2024-01-01T00:00:00Z",
                "date_modified": "2024-01-02T00:00:00Z",
                "versions": ["1.19", "1.20"],
                "categories": ["technology"],
                "slug": "test-mod"
            }
        ]
    }
    return client

@pytest.fixture
def mock_storage():
    """Create a mock storage service"""
    storage = AsyncMock()
    return storage

@pytest.fixture
def service(tmp_path, mock_client, mock_storage):
    """Create a scraper service with mocked dependencies"""
    service = ScraperService(storage_dir=tmp_path)
    
    # Replace client factory
    service.client_factory.create = Mock(return_value=mock_client)
    
    # Replace storage services
    service.raw_storage = mock_storage
    service.processed_storage = mock_storage
    
    return service

@pytest.mark.asyncio
async def test_fetch_resources(service, mock_client):
    """Test fetching resources from a platform"""
    result = await service.fetch_resources("modrinth")
    
    assert result == mock_client.fetch_resources.return_value
    mock_client.fetch_resources.assert_called_once()

@pytest.mark.asyncio
async def test_process_platform(service):
    """Test processing a platform's resources"""
    platform = Platform(name="modrinth", batch_size=100)
    resources = await service.process_platform(platform)
    
    assert len(resources) == 1
    assert isinstance(resources[0], Resource)
    assert resources[0].name == "Test Mod"
    assert resources[0].platform == "modrinth"

@pytest.mark.asyncio
async def test_run(service, mock_storage):
    """Test complete scraping process"""
    results = await service.run()
    
    assert "modrinth" in results
    assert len(results["modrinth"]) == 1
    
    # Verify storage calls
    assert mock_storage.save_raw_data.called
    assert mock_storage.save_processed_data.called 