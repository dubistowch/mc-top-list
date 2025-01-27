# ADR 0011: Scraper Code Organization and Testing Strategy

## Status
Accepted

## Context
After implementing the initial version of the scraper, we identified several areas that needed improvement:
1. The code structure was not following the Single Responsibility Principle
2. Data transformation logic was mixed with API client code
3. Testing strategy was not well-defined
4. Terminology was inconsistent across the codebase
5. Data storage structure needed better organization

## Decision
We will reorganize the scraper code with the following principles:

1. **Code Structure**:
   ```
   scraper/
   ├── api_clients/          # API clients for different platforms
   │   ├── base.py          # Base API client
   │   ├── hangar.py        # Hangar API client
   │   └── modrinth.py      # Modrinth API client
   ├── transformers/         # Data transformers
   │   ├── base.py          # Base transformer
   │   ├── hangar.py        # Hangar transformer
   │   └── modrinth.py      # Modrinth transformer
   ├── models/              # Data models
   │   └── resource.py      # Resource model
   ├── data/                # Data storage
   │   ├── raw/             # Raw data from APIs
   │   ├── normalized/      # Normalized data
   │   ├── aggregated/      # Aggregated data from all platforms
   │   └── schema/          # JSON schema definitions
   └── tests/               # Test suite
       ├── __init__.py
       └── test_scraper.py  # Scraper tests
   ```

2. **Separation of Concerns**:
   - API clients handle only HTTP requests and responses
   - Transformers handle data normalization and conversion
   - Models define data structures and validation

3. **Data Organization Strategy**:
   - Raw Data:
     - Store original API responses without modification
     - Maintain platform-specific data structures
     - Keep historical data for debugging and analysis
   - Normalized Data:
     - Convert to standardized format using transformers
     - Follow schema definitions strictly
     - Maintain data integrity and consistency
   - Aggregated Data:
     - Combine normalized data from all platforms
     - Provide unified view of resources
     - Enable cross-platform analysis

4. **Testing Strategy**:
   - Unit tests for each component
   - Mock objects for external dependencies
   - Async test support
   - Test data fixtures
   - Schema validation tests

5. **Standardized Terminology**:
   - platform: Minecraft resource platforms (e.g., Hangar, Modrinth)
   - resource: Minecraft resources (mods, plugins)
   - category: Resource categories (new, popular, all)
   - created_at: Resource creation timestamp
   - updated_at: Resource last update timestamp

## Consequences

### Positive
- Better code maintainability through clear separation of concerns
- Improved testability with dedicated test suite
- Consistent terminology across the codebase
- Easier to add new platforms
- Better error handling and data validation
- Clear data lineage from raw to normalized format
- Ability to reprocess data if needed
- Better debugging capabilities with raw data preservation

### Negative
- More complex project structure
- Additional abstraction layers
- More files to maintain
- Learning curve for new developers
- Increased storage requirements for multiple data formats
- Additional processing overhead for data transformation

## Related ADRs
- [ADR 0007](./0007-api-first-data-collection-strategy.md)
- [ADR 0009](./0009-simplified-resource-model.md)
- [ADR 0010](./0010-code-refactoring-principles.md)

## Date
01/27/2024 