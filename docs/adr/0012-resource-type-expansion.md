# ADR 0012: Resource Type Expansion

## Status
Accepted

## Context
Initially, our system was designed to collect general resource data from various Minecraft platforms. As the project evolves, we need to explicitly support and differentiate between different types of resources: plugins, mods, modpacks, and resource packs. Each type has its unique characteristics and metadata that need to be properly captured and organized.

## Decision
We will expand our resource model and collection strategy to explicitly support different resource types:

1. **Resource Type Classification**:
   - Plugin: Server-side modifications (from Hangar)
   - Mod: Client/Server modifications (from Modrinth)
   - Modpack: Collection of mods and configurations (from Modrinth)
   - Resource Pack: Visual and audio assets (from Modrinth)
   - Datapack: Custom data and functionality using vanilla mechanics (from Modrinth)
   - Addon: Server-side extensions with specific platform support (from Hangar)

2. **Schema Updates**:
   - Added `resource_type` field to the resource model with enum values
   - Extended schema to include type-specific metadata
   - Maintained backward compatibility with existing data
   - Implemented JSON Schema validation for each type

3. **Implementation Changes**:
   ```
   scraper/
   ├── platforms/           # Platform-specific implementations
   │   ├── modrinth/       # Mods, modpacks, resource packs, datapacks
   │   └── hangar/         # Plugins, addons
   ├── core/               # Core scraping logic
   ├── contracts/          # Interface definitions
   ├── models/             # Type-specific model implementations
   ├── transformers/       # Data transformation logic
   └── persistence/        # Data storage handling
   ```

4. **Data Organization**:
   - Raw data stored by timestamp and platform
   - Normalized data categorized by resource type
   - Aggregated data combines resources across platforms
   - Schema validation at each transformation step

5. **API Integration Updates**:
   - Implemented platform-specific API clients
   - Added type-specific data transformers
   - Enhanced error handling and logging
   - Asynchronous data fetching with connection pooling

## Consequences

### Positive
- Better organization of different resource types
- More accurate metadata collection
- Improved search and filtering capabilities
- Clear distinction between resource types
- Better support for type-specific features
- Robust error handling and validation
- Efficient asynchronous data collection

### Negative
- Increased complexity in data models
- More storage space required
- Additional processing overhead
- More complex validation rules
- Need to maintain multiple schema versions

## Implementation Notes
- Successfully implemented resource type detection and validation
- Added support for Modrinth and Hangar platforms
- Implemented asynchronous data fetching with proper resource cleanup
- Added comprehensive logging for better monitoring
- Current implementation shows different resource counts between platforms:
  - Modrinth: Currently showing 0 popular resources (needs investigation)
  - Hangar: Successfully fetching 25 popular resources

## Related ADRs
- [ADR 0011](./0011-scraper-code-organization.md)
- [ADR 0007](./0007-api-first-data-collection-strategy.md)
- [ADR 0009](./0009-simplified-resource-model.md)

## Date
01/28/2025