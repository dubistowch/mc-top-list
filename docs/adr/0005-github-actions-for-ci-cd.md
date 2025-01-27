# ADR 0005: GitHub Actions for CI/CD

## Status
Accepted

## Context
We want an automated workflow to:
1. Run the data collection daily
2. Process and aggregate the data
3. Commit/push new data to the repo
4. Deploy the static site with updated data

## Decision
Use GitHub Actions with multiple workflows:

### Data Collection (`collect.yml`)
- Runs on a schedule (daily at 3 AM UTC)
- Checks out the repo, sets up Python environment
- Runs API clients to collect data
- Processes and aggregates the data
- Commits changes if there are differences

### Deployment (`deploy.yml`)
- Triggered by changes to main branch or manually
- Builds and deploys React SPA to GitHub Pages
- Updates site with latest data

### Security
- Uses GitHub Secrets for API keys
- Implements proper error handling for missing credentials
- Rate limiting and API usage monitoring

## Consequences
### Positive
- Fully automated data collection and deployment
- Clear audit trail via Git history
- Separate concerns between collection and deployment
- Easy to monitor and debug issues

### Negative
- Requires careful GitHub Actions configuration
- API rate limits may affect collection reliability
- Need to manage multiple workflow files

## Related ADRs
- [ADR 0007](./0007-api-first-data-collection-strategy.md)
- [ADR 0001](./0001-use-python-for-scraper.md)
- [ADR 0002](./0002-store-data-as-static-json.md)
- [ADR 0003](./0003-use-react-for-frontend.md)

## Date
01/26/2025
