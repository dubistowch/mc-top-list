"""
Global pytest configuration and fixtures
"""

from pathlib import Path
from typing import AsyncGenerator, Dict
import pytest
import pytest_asyncio
from aioresponses import aioresponses
import structlog

# Configure structured logging for tests
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer(),
    ]
)

@pytest.fixture
def test_data_dir() -> Path:
    """Return the path to test data directory"""
    return Path(__file__).parent / "fixtures"

@pytest.fixture
def config_dir(test_data_dir: Path) -> Path:
    """Return the path to test config directory"""
    return test_data_dir / "configs"

@pytest.fixture
def responses_dir(test_data_dir: Path) -> Path:
    """Return the path to test responses directory"""
    return test_data_dir / "responses"

@pytest_asyncio.fixture
async def mock_aiohttp() -> AsyncGenerator[aioresponses, None]:
    """Fixture for mocking aiohttp requests"""
    with aioresponses() as m:
        yield m

@pytest.fixture
def sample_modrinth_response() -> Dict:
    """Return a sample Modrinth API response"""
    return {
        "hits": [
            {
                "project_id": "test-mod-1",
                "title": "Test Mod 1",
                "description": "A test mod",
                "author": "test_author",
                "downloads": 1000,
                "created": "2025-01-01T00:00:00Z",
                "updated": "2025-01-31T00:00:00Z",
                "versions": ["1.0.0", "1.1.0"]
            }
        ]
    }

@pytest.fixture
def sample_hangar_response() -> Dict:
    """Return a sample Hangar API response"""
    return {
        "result": [
            {
                "id": "test-plugin-1",
                "name": "Test Plugin 1",
                "description": "A test plugin",
                "owner": "test_author",
                "stats": {
                    "downloads": 500
                },
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-31T00:00:00Z",
                "versions": ["1.0.0"]
            }
        ]
    } 