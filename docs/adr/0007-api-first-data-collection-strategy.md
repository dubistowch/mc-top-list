# ADR 0007: API-First Data Collection Strategy

## Status
Accepted

## Context
After evaluating various Minecraft plugin/mod platforms, we found that several major platforms provide official APIs. Using official APIs not only ensures compliance with terms of service but also provides more reliable and stable data access methods.

Currently confirmed platforms with API support:
- Hangar: Official API for PaperMC resources
- Modrinth: Well-documented REST API
- Polymart: Limited API access
- Builtbybit: Requires authorization

## Decision
We will adopt an "API-First" data collection strategy:

1. **API Integration Priority**:
   - Hangar API (Primary)
   - Modrinth API (Primary)
   - Polymart API (Primary)
   - Builtbybit API (Primary)
   - Other APIs (Secondary, based on availability)

2. **Implementation Architecture**:
   - Abstract API client interface in `/scraper/interfaces/api_client.py`
   - Platform-specific clients in `/scraper/api_clients/`
   - Unified resource model for data standardization
   - API key management system with environment variables

3. **Collection Strategy**:
   - Daily updates via GitHub Actions
   - Rate limit compliance through configuration
   - Error handling and retry mechanisms
   - Async operations for better performance

## Consequences
### Positive
- Fully compliant data collection
- Reliable and stable data sources
- Better error handling and monitoring
- Standardized data format
- Efficient async operations

### Negative
- Limited to platforms with APIs
- API rate limits affect collection speed
- Multiple API keys to manage
- Some APIs may require payment

## Related ADRs
- [ADR 0009](./0009-simplified-resource-model.md)
- [ADR 0008](./0008-async-logging-implementation.md)
- [ADR 0006](./0006-data-scraping-policy.md)
- [ADR 0005](./0005-github-actions-for-ci-cd.md)
- [ADR 0001](./0001-use-python-for-scraper.md)

## Date
01/26/2025
