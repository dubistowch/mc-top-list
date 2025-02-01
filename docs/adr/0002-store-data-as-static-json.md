# ADR 0002: Store Data as Static JSON

## Status
Superseded by [ADR 0018](./0018-new-data-structure.md)

## Context
Our project requires a data storage solution that balances:
- Easy access from React SPA
- Simple maintenance and version control
- Cost-effective hosting
- Efficient data updates

## Decision
We will implement a static JSON-based storage solution:

### Data Structure
- Raw data location: `data/raw/<site_name>.json`
- Aggregated data: `data/aggregated/resources.json`
- Schema definitions: `data/schema/`

### Implementation Details
1. Each API client outputs to its own raw JSON file
2. Aggregator script combines and normalizes data based on resource model
3. Final JSON serves as the data source for the SPA
4. Daily updates via GitHub Actions

## Consequences
### Positive
- Zero database hosting costs
- Simple version control via Git
- Easy to backup and restore
- Transparent data changes through commits
- Consistent data format through resource model

### Negative
- Limited to client-side filtering and search
- Potential performance issues with large datasets
- No real-time updates
- Must manage file size for optimal loading

## Related ADRs
- [ADR 0009](./0009-simplified-resource-model.md)
- [ADR 0007](./0007-api-first-data-collection-strategy.md)
- [ADR 0005](./0005-github-actions-for-ci-cd.md)

## Date
01/26/2025
