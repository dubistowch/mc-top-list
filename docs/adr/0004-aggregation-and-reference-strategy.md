# ADR 0004: Aggregation and Reference Strategy

## Status
Superseded by [ADR 0009](./0009-simplified-resource-model.md)

## Context
We need to unify or merge records of the same plugin/mod collected from multiple sites (Modrinth, CurseForge, etc.). We also must ensure that items with the same name but actually different plugins do not get incorrectly merged.

## Decision
We will implement:
1. A **canonical ID strategy** for known resources based on their source site ID.
2. **Merging logic** in the aggregator:
   - Use source site's unique project ID as primary identifier
   - Merge data (e.g., version, description, download count) into a single record
   - Keep references to each source site
3. **Resource model** for standardization:
   - Each resource has a unique source site and ID combination
   - Common fields are mapped to standard format
   - Site-specific data is preserved in metadata

## Consequences
### Positive
- Each resource has a guaranteed unique identifier
- No need for complex alias mapping
- Clear data lineage and source tracking
- Simplified aggregation logic

### Negative
- Cannot merge identical resources across platforms
- Duplicate entries for cross-platform resources
- Increased storage requirements

## Related ADRs
- [ADR 0009](./0009-simplified-resource-model.md)
- [ADR 0007](./0007-api-first-data-collection-strategy.md)
- [ADR 0002](./0002-store-data-as-static-json.md)

## Date
01/26/2025
