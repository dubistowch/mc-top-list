# 19. 新資料結構

## Status
Accepted

## Context
As our project evolves, we need a more flexible and extensible data structure to support:
1. Unified management of multi-platform resources (Modrinth, Hangar, Polymart)
2. Dynamic expansion of resource types
3. Time-series data storage
4. Fast data retrieval and updates

## Decision

### 1. Directory Structure
```
data/
├── raw/                    # Raw data
│   └── {timestamp}/       # Timestamp directory
│       ├── modrinth_mod_raw.json
│       ├── modrinth_plugin_raw.json
│       ├── hangar_raw.json
│       ├── polymart_plugin_raw.json
│       ├── polymart_mod_raw.json
│       ├── polymart_resourcepack_raw.json
│       ├── polymart_datapack_raw.json
│       └── polymart_pluginpack_raw.json
├── processed/             # Processed data
│   └── {timestamp}/      # Timestamp directory
│       ├── modrinth_processed.json
│       ├── hangar_processed.json
│       └── polymart_processed.json
└── aggregated/           # Aggregated data
    └── {timestamp}/     # Timestamp directory
        └── aggregated.json
```

### 2. Data Format

#### 2.1 Raw Data Format
```json
{
    "hits": [...],  // For Modrinth
    "result": [...],  // For Polymart
    "offset": 0,
    "limit": 100,
    "total": 50
}
```

#### 2.2 Processed Data
```json
{
    "timestamp": "2025-02-01T17:02:24",
    "platform": "platform_name",
    "resources": {
        "mod": [...],
        "plugin": [...],
        "modpack": [...],
        "resourcepack": [...],
        "datapack": [...],
        "pluginpack": [...]
    }
}
```

#### 2.3 Aggregated Data
```json
{
    "metadata": {
        "timestamp": "20250201_170224",
        "total_resources": 1234,
        "platforms": ["modrinth", "hangar", "polymart"]
    },
    "resources": {
        "tabs": [
            {"id": "mod", "label": "模組"},
            {"id": "plugin", "label": "插件"},
            {"id": "modpack", "label": "模組包"},
            {"id": "pluginpack", "label": "插件包"},
            {"id": "resourcepack", "label": "資源包"},
            {"id": "datapack", "label": "資料包"},
            {"id": "addon", "label": "附加元件"}
        ],
        "resources": {
            "mod": {
                "popular": [...],
                "new": [...],
                "all": [...]
            }
        }
    }
}
```

### 3. Data Validation
Using Python's type system and dataclasses for validation:
```python
@dataclass
class Resource:
    id: str
    name: str
    description: str
    author: str
    downloads: int
    resource_type: str
    platform: str
    created_at: datetime
    updated_at: datetime
    versions: List[str]
    categories: List[str]
    website_url: str
    source_url: Optional[str]
    license: Optional[str]
```

### 4. Time Management
1. Use ISO 8601 format for timestamps
2. Use YYYYMMDD_HHMMSS format for directories
3. Maintain `latest` symlink pointing to most recent data

## Consequences

### Positive
- Better data organization
- Support for time-series data
- Type-safe data handling
- Easier version control
- Improved data retrieval performance
- 支援多平台資源統一管理（Modrinth、Hangar、Polymart）
- 資源類型分檔儲存提高了資料的可讀性

### Negative
- Requires more storage space
- Increased data management complexity
- Requires periodic data cleanup
- 需要處理不同平台的資料格式差異
- 需要維護多個平台的 API 相容性

## Implementation Notes
1. Use Python's `pathlib` for path handling
2. Implement data cleanup strategy
3. Ensure correct file permissions
4. Implement error recovery mechanisms
5. 確保各平台的資料轉換邏輯正確
6. 定期檢查 API 變更

## Related ADRs
- [ADR 0002](./0002-store-data-as-static-json.md) (Superseded)
- [ADR 0012](./0012-resource-type-expansion.md)
- [ADR 0015](./0015-data-aggregation-and-storage.md)
- [ADR 0018](./0018-resource-type-modification-guide.md)

## Date
02/01/2025