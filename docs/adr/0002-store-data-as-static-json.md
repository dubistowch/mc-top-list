# ADR 0002: Store Data as Static JSON

## Status
Accepted

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
- Aggregated data: `data/aggregated/plugins_mods.json`
- Schema definitions: `data/schema/`

### Implementation Details
1. Each scraper outputs to its own raw JSON file
2. Aggregator script combines and normalizes data
3. Final JSON serves as the data source for the SPA

## Consequences
### Positive
- Zero database hosting costs
- Simple version control via Git
- Easy to backup and restore
- Transparent data changes through commits

### Negative
- Limited to client-side filtering and search
- Potential performance issues with large datasets
- No real-time updates
- Must manage file size for optimal loading
