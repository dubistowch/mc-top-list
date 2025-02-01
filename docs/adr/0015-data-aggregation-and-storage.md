# ADR 0015: Data Aggregation and Storage Implementation

## Status
Accepted

## Context
As part of our ongoing efforts to improve the Minecraft plugin/mod data collection system, we need to implement a robust and efficient data aggregation and storage mechanism. The system needs to handle data from multiple sources (Modrinth, Hangar) and store it in a format that is both easily accessible and maintainable.

## Decision
We will implement the following data aggregation and storage strategy:

1. **Data Aggregation Service**
   - Create a dedicated aggregator service that combines data from multiple sources
   - Implement transformation logic for each platform's specific data format
   - Use a unified resource model for consistent data representation

2. **Storage Implementation**
   - Store aggregated data in JSON format
   - Organize data in timestamped directories
   - Implement versioning through directory structure

3. **File Organization**
   - Store raw data separately from aggregated data
   - Use ISO format timestamps in directory names
   - Maintain a consistent file structure across all data types

## Consequences
### Positive
- Improved data organization and accessibility
- Clear separation of concerns between scraping and aggregation
- Better maintainability through structured storage
- Easy data version tracking

### Negative
- Additional complexity in data transformation logic
- Increased storage requirements due to keeping historical data
- Need for data cleanup/archival strategy

## Related ADRs
- [ADR 0012](./0012-resource-type-expansion.md)
- [ADR 0013](./0013-codebase-restructuring.md)
- [ADR 0014](./0014-testing-and-quality-assurance.md)


## Date
02/01/2025