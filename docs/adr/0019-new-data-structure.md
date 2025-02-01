# ADR 0019: New Data Structure Design

## Status
Accepted

## Context
As our project evolves, we need a more flexible and extensible data structure to support:
1. Unified management of multi-platform resources (Modrinth, Hangar, Polymart)
2. Dynamic expansion of resource types
3. Time-series data storage
4. Fast data retrieval and updates
5. Consistent data validation and type safety

## Decision
We will implement a new data structure with the following components:

### 1. Directory Structure
```
data/
├── raw/                    # Raw data from platforms
│   └── {timestamp}/       # Timestamp directory
│       ├── modrinth_mod_raw.json
│       ├── modrinth_plugin_raw.json
│       ├── hangar_raw.json
│       ├── polymart_plugin_raw.json
│       ├── polymart_mod_raw.json
│       ├── polymart_resourcepack_raw.json
│       ├── polymart_datapack_raw.json
│       └── polymart_pluginpack_raw.json
├── processed/             # Normalized platform data
│   └── {timestamp}/      # Timestamp directory
│       ├── modrinth_processed.json
│       ├── hangar_processed.json
│       └── polymart_processed.json
└── aggregated/           # Combined platform data
    └── {timestamp}/     # Timestamp directory
        └── aggregated.json
```

### 2. Data Format Specifications

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

#### 2.2 Processed Data Format
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

#### 2.3 Aggregated Data Format
```json
{
    "metadata": {
        "timestamp": "20250201_170224",
        "total_resources": 1234,
        "platforms": ["modrinth", "hangar", "polymart"]
    },
    "resources": {
        "tabs": [
            {"id": "mod", "label": "Mods"},
            {"id": "plugin", "label": "Plugins"},
            {"id": "modpack", "label": "Modpacks"},
            {"id": "pluginpack", "label": "Plugin Packs"},
            {"id": "resourcepack", "label": "Resource Packs"},
            {"id": "datapack", "label": "Data Packs"},
            {"id": "addon", "label": "Add-ons"}
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
We will use Python's type system and dataclasses for validation:
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

### 4. Time Management Strategy
1. Use ISO 8601 format for timestamps in data
2. Use YYYYMMDD_HHMMSS format for directory names
3. Maintain `latest` symlink pointing to most recent data directory
4. Implement data retention policies for historical data

## Consequences

### Positive
1. Improved data organization and structure
2. Robust support for time-series data analysis
3. Type-safe data handling with validation
4. Better version control and data tracking
5. Enhanced data retrieval performance
6. Unified management of multi-platform resources
7. Improved data readability through type separation

### Negative
1. Increased storage space requirements
2. Higher complexity in data management
3. Need for periodic data cleanup
4. Additional overhead in handling platform-specific data formats
5. Ongoing maintenance of API compatibility
6. More complex data migration processes

## Implementation Guidelines
1. Use Python's `pathlib` for consistent path handling
2. Implement automated data cleanup strategies
3. Ensure proper file permissions and security
4. Develop robust error recovery mechanisms
5. Maintain platform-specific data transformation logic
6. Regular API compatibility checks
7. Implement data integrity validation

## Related ADRs
- [ADR 0002](./0002-store-data-as-static-json.md) (Superseded)
- [ADR 0012](./0012-resource-type-expansion.md)
- [ADR 0015](./0015-data-aggregation-and-storage.md)
- [ADR 0018](./0018-resource-type-modification-guide.md)

## References
- [Python Type Hints Documentation](https://docs.python.org/3/library/typing.html)
- [ISO 8601 Time Format](https://www.iso.org/iso-8601-date-and-time-format.html)
- [JSON Schema Specification](https://json-schema.org/)

## Date
02/01/2025