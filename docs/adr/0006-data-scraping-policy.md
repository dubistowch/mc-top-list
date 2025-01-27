# ADR 0006: Data Scraping Policy

## Status
Superseded by [ADR 0007](./0007-api-first-data-collection-strategy.md)

## Context
As part of the "Minecraft 插件模組爬蟲" project, we aim to collect data from various websites that provide Minecraft plugins and mods. However, some platforms explicitly prohibit data scraping in their Terms of Service (ToS) or End User License Agreement (EULA). To ensure compliance with legal and ethical guidelines, we need to establish a clear policy for data collection.

The following platforms were reviewed for their data access policies:
- **CurseForge**: Provides official API with rate limits
- **Modrinth**: Provides official API with clear documentation
- **SpigotMC**: Prohibits data scraping
- **BuiltByBit (formerly MC-Market)**: Prohibits scraping but provides API
- **Hangar (PaperMC)**: Provides official API
- **Polymart**: No explicit API or scraping policy
- **Planet Minecraft**: No explicit API or scraping policy
- **Bukkit**: Legacy platform, no active development

## Decision
We will:
1. **Prioritize Official APIs**: Use official APIs where available
2. **Respect Rate Limits**: Implement proper rate limiting for all API calls
3. **Exclude Prohibited Sources**: Not scrape websites that explicitly prohibit it
4. **Document Access Methods**: Maintain clear documentation of data sources

**Implementation Status:**
- CurseForge: Implemented using official API
- Modrinth: Implemented using official API
- Other platforms: Pending API availability or policy clarification

## Consequences
### Positive
- Legal and ethical compliance
- Reliable and stable data collection
- Better data quality through official APIs
- Reduced risk of service disruption

### Negative
- Limited data sources
- API rate limits affect collection frequency
- Some platforms may remain inaccessible
- Need to manage multiple API keys

## Related ADRs
- [ADR 0007](./0007-api-first-data-collection-strategy.md)
- [ADR 0005](./0005-github-actions-for-ci-cd.md)

## Date
01/26/2025
