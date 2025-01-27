# ADR 0009: Simplified Resource Model

## Status
Accepted

## Context
The original resource model contained redundant fields and complex nested structures, which increased maintenance difficulty and could lead to data inconsistency. We need a simpler, more maintainable model that still captures all essential information.

## Decision
We will implement a simplified resource model:

1. **Core Resource Model**:
   ```python
   @dataclass
   class Resource:
       id: str
       source: str
       name: str
       description: str
       author: str
       downloads: int
       created_at: datetime
       updated_at: datetime
       versions: List[str]
       metadata: Dict[str, Any]
   ```

2. **Implementation Details**:
   - Use dataclasses for all models
   - Strict type hints throughout
   - Metadata field for platform-specific data
   - JSON serialization support
   - Validation methods

3. **Standardization**:
   - Consistent field naming across platforms
   - ISO8601 for all timestamps
   - Unified version format
   - Standard metadata structure

## Consequences
### Positive
- Easier to maintain and test
- Reduced data redundancy
- Better code readability
- Simplified data processing
- Clear data structure

### Negative
- Need to update existing processors
- Some platform-specific data in metadata
- Potential data migration needed
- Less detailed default structure

## Related ADRs
- [ADR 0007](./0007-api-first-data-collection-strategy.md)
- [ADR 0004](./0004-aggregation-and-reference-strategy.md)
- [ADR 0001](./0001-use-python-for-scraper.md)

## Date
01/27/2025 