# ADR 0018: Resource Type Modification Guide

## Status
Accepted

## Context
When adding or modifying resource types in the system, multiple related code components need to be updated simultaneously. To ensure consistency and completeness of modifications, we need a clear guide that outlines all the necessary changes.

## Decision
We will establish a standardized process that lists all code locations that need to be updated when adding or modifying resource types:

### 1. Configuration Updates
- Location: `scraper/config.yml`
- Required Changes:
  - Add new type to the `resource_types` list for corresponding platforms

### 2. API Client Modifications
- Location: `scraper/clients/{platform}.py`
- Required Changes:
  - Add mappings in type conversion (e.g., `category_map`, `type_map`)
  - Ensure `fetch_resources` method supports new types
  - Implement resource type grouping data structures

### 3. Data Storage Format
- Raw Data:
  - Location: `data/raw/{timestamp}/{platform}_{type}_raw.json`
  - Format: Separate file for each resource type
  - Structure:
    ```json
    {
      "hits": [...],
      "offset": 0,
      "limit": 100,
      "total": 50
    }
    ```
- Processed Data:
  - Location: `data/processed/{timestamp}/{platform}_processed.json`
  - Format: All types merged in single file
  - Structure:
    ```json
    {
      "timestamp": "2024-02-01T00:00:00Z",
      "platform": "platform_name",
      "resources": {
        "mod": [...],
        "plugin": [...],
        "pluginpack": [...]
      }
    }
    ```

### 4. Data Transformer Updates
- Location: `scraper/services/transformers/{platform}.py`
- Required Changes:
  - Ensure `transform` method supports new resource type
  - Update related logging
  - Handle type-specific field conversions

### 5. Data Aggregator Modifications
- Location: `scraper/services/aggregator.py`
- Required Changes:
  - Add type labels in `_group_resources` method
  - Ensure correct classification of new type resources
  - Update statistics calculation logic

### 6. Test Case Updates
- Location: `scraper/tests/test_scraper.py`
- Required Changes:
  - Add test data for new resource type
  - Add test cases for transformation logic
  - Add test cases for aggregation results
  - Update related mock data

### 7. Documentation Updates
- Required Changes:
  - Update supported resource types list in README.md
  - Update resource type descriptions in API documentation
  - Update aggregation result format documentation
  - Update related ADR documents

## Consequences

### Positive
1. Standardized modification process reduces oversights
2. Clear modification guide improves development efficiency
3. Complete documentation updates ensure system documentation accuracy
4. Ensures consistency in data aggregation results
5. Resource type file separation improves data readability and maintainability
6. Independent file storage facilitates version control and diff comparison

### Negative
1. Multiple files need modification for each new resource type
2. Additional testing work required to ensure modification correctness
3. Need to ensure aggregation logic compatibility with new resource types
4. Resource type file separation results in increased file count
5. Increased complexity in maintaining cross-type relationships
6. Potential performance impact from handling multiple file types

## Related ADRs
- [ADR 0015](./0015-data-aggregation-and-storage.md)
- [ADR 0019](./0019-new-data-structure.md)

## References
- [Polymart API Documentation](https://polymart.org/wiki/api)
- [Modrinth API Documentation](https://docs.modrinth.com/api-spec/)
- System Architecture Documentation
- [ADR 0000](./0000-adr-writing-convention.md)

## Date
02/01/2025