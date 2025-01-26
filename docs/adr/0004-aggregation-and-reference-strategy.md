# ADR 0004: Aggregation and Reference Strategy

## Status
Accepted

## Context
We need to unify or merge records of the same plugin/mod scraped from multiple sites (Spigot, CurseForge, etc.). We also must ensure that items with the same name but actually different plugins do not get incorrectly merged.

## Decision
We will implement:
1. A **canonical ID strategy** for known plugins/mods. (e.g., an internal "slug".)
2. **Merging logic** in the aggregator:
   - Identify duplicates by name, author, or known project ID patterns.
   - Merge data (e.g., version, description, download count) into a single record.
   - Keep references to each source site.
3. **Manual alias mappings** for conflicts:
   - If two items share a name but differ in project ID or author, treat them as separate.
   - If known aliases exist, define them in a `alias_mappings.json` or similar file.

## Consequences
- We maintain a single, consistent record for multi-source plugins (like EssentialsX).
- We need to maintain a mapping or heuristic logic to prevent erroneous merges.
- The aggregator can detect conflicts and place them in a "needs-review" queue if necessary.
- Over time, we may need to refine the logic as new sites or plugins cause collisions.

## Related ADRs
- [ADR 0002](./0002-store-data-as-static-json.md)

## Date
January 26, 2024
