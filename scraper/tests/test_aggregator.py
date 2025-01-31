"""Tests for resource aggregator."""

import pytest
from pathlib import Path
from datetime import datetime

from scraper.services.aggregator import ResourceAggregator
from scraper.services.storage.json_storage import JsonStorage
from scraper.models.resource import Resource, ResourceCategory

@pytest.fixture
def storage(tmp_path):
    """Create a temporary storage instance."""
    return JsonStorage(base_dir=tmp_path)

@pytest.fixture
def aggregator(storage):
    """Create an aggregator instance."""
    return ResourceAggregator(storage)

@pytest.mark.asyncio
async def test_aggregator_with_real_data():
    """Test aggregator with real data from processed directory."""
    # 初始化服務
    base_dir = Path(__file__).parent.parent.parent  # mc-top-list directory
    storage = JsonStorage(base_dir=base_dir)
    aggregator = ResourceAggregator(storage)
    
    # 使用最新的資料目錄
    processed_dir = base_dir / "data" / "processed"
    timestamps = sorted([d.name for d in processed_dir.iterdir() if d.is_dir()])
    assert timestamps, "No processed data found"
    
    latest_timestamp = timestamps[-1]
    print(f"\n使用最新的資料時間戳: {latest_timestamp}")
    
    # 執行聚合
    result = aggregator.aggregate(latest_timestamp)
    
    # 驗證結果
    assert "metadata" in result
    assert "resources" in result
    assert result["metadata"]["total_resources"] > 0
    assert len(result["metadata"]["platforms"]) > 0
    
    # 輸出結果
    print("\n=== 聚合結果 ===")
    print(f"總資源數: {result['metadata']['total_resources']}")
    print(f"平台: {result['metadata']['platforms']}")
    print("\n各平台資源統計:")
    
    for platform, types in result['resources'].items():
        print(f"\n{platform}:")
        for res_type, categories in types.items():
            print(f"  {res_type}:")
            for category, resources in categories.items():
                print(f"    {category}: {len(resources)} 個資源")
    
    # 驗證聚合資料已儲存
    aggregated_file = base_dir / "data" / "aggregated" / latest_timestamp / "aggregated.json"
    assert aggregated_file.exists(), "Aggregated file not created" 