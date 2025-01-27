# ADR 0001: Use Python for Scraper

## Status
Accepted

## Context
We need a scripting language to build and maintain our Minecraft mod/plugin scraper. The solution needs to address:
- Data scraping requirements from multiple sources
- Ease of maintenance and contribution
- Integration with CI/CD pipeline
- Performance considerations for regular scraping tasks

## Decision
We will use Python 3.x as the primary language for the scraper implementation:
- Python version: 3.9 or higher
- Key libraries:
  - `aiohttp` for async HTTP requests
  - `pyyaml` for configuration management
  - `typing-extensions` for type hints
  - `pytest` for testing
- Code organization:
  - Main scraper code in `/scraper` directory
  - Site-specific scrapers in `/scraper/api_clients`
  - Shared utilities in `/scraper/utils`
  - Models in `/scraper/models`

## Consequences
### Positive
- Rich ecosystem of libraries for web scraping and API integration
- Excellent documentation and community support
- Easy to read and maintain code
- Strong integration with GitHub Actions
- Async support for efficient API calls

### Negative
- Need to manage Python dependencies
- Must ensure consistent Python environment across different platforms
- May need to handle rate limiting and other API challenges

## Related ADRs
- [ADR 0007](./0007-api-first-data-collection-strategy.md)
- [ADR 0005](./0005-github-actions-for-ci-cd.md)
- [ADR 0002](./0002-store-data-as-static-json.md)

## Date
01/26/2025
