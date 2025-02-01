# ADR 0017: Platform Adapter Pattern Implementation

## Status
Accepted

## Context
As our project expands to support more Minecraft resource platforms, we need a standardized approach for adding and maintaining platform adapters. Each platform has its unique API structure and data format, requiring a unified transformation method.

## Decision

### 1. Platform Adapter Structure
```python
platform/
├── clients/              # API client implementations
│   ├── base.py          # Base client interface
│   └── {platform}.py    # Platform-specific client
└── transformers/        # Data transformers
    ├── base.py         # Base transformer interface
    └── {platform}.py   # Platform-specific transformer
```

### 2. Client Implementation Guidelines
1. Must inherit from `BaseClient` class
2. Implement the following methods:
   ```python
   class PlatformClient(BaseClient):
       platform = "platform_name"  # Platform identifier
       
       async def fetch_resources(self) -> Dict:
           """Fetch resource list"""
           pass
           
       async def _ensure_session(self) -> None:
           """Ensure HTTP session exists"""
           pass
           
       async def _close_session(self) -> None:
           """Close HTTP session"""
           pass
   ```

### 3. Transformer Implementation Guidelines
1. Must inherit from `BaseTransformer` class
2. Implement the following methods:
   ```python
   class PlatformTransformer(BaseTransformer):
       def transform(self, raw_data: Dict) -> List[Resource]:
           """Transform raw data to standard resource format"""
           pass
   ```

### 4. Resource Model Guidelines
All platform data must be transformed into the standard `Resource` model:
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

### 5. Configuration Guidelines
Define platform-specific settings in `config.yml`:
```yaml
platforms:
  platform_name:
    api_url: "https://api.example.com/v1"
    resource_types:
      - type1
      - type2
```

### 6. Error Handling Guidelines
1. Use custom exception classes
2. Implement appropriate error logging
3. Ensure proper resource cleanup

### 7. Service Registration Guidelines
1. Register client in `ScraperService._register_clients()`:
   ```python
   def _register_clients(self) -> None:
       self.client_factory.register("platform_name", PlatformClient)
   ```

2. Register transformer in `ScraperService._init_transformers()`:
   ```python
   def _init_transformers(self) -> None:
       self.transformers = {
           "platform_name": PlatformTransformer()
       }
   ```

3. Add platform to the platforms list in `ScraperService.run()`:
   ```python
   platforms = [
       Platform(name="platform_name", batch_size=100)
   ]
   ```

## Consequences

### Positive
- Standardized platform integration process
- Consistent error handling
- Clear code organization
- Easy platform extension
- Type-safe data handling

### Negative
- Requires more initial development time
- May need additional transformation logic
- Need to maintain more interface code

## Implementation Notes
1. Reference `modrinth.py` and `hangar.py` as implementation examples
2. Use asynchronous HTTP client (aiohttp)
3. Implement comprehensive unit tests
4. Ensure compliance with code quality standards

## Related ADRs
- [ADR 0001](./0001-use-python-for-scraper.md)
- [ADR 0007](./0007-api-first-data-collection-strategy.md)
- [ADR 0011](./0011-scraper-code-organization.md)
- [ADR 0012](./0012-resource-type-expansion.md)

## Date
02/01/2025