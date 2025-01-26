# ADR 0005: GitHub Actions for CI/CD

## Status
Accepted

## Context
We want an automated workflow to:
1. Run the scraper daily.
2. Commit/push new data to the repo.
3. Optionally trigger a release or a static site rebuild.

## Decision
Use GitHub Actions with a `scraper.yml` workflow:
- Runs on a schedule (e.g., daily at 3 AM UTC).
- Checks out the repo, sets up Python, runs the scraper, updates JSON files.
- Commits changes if there are any differences.
- Optionally triggers a build/deploy of the React SPA to GitHub Pages.

## Consequences
- Automated data updates without manual intervention.
- Full audit trail of changes to data (via Git commit history).
- Requires configuring GitHub Actions properly (permissions, etc.).
- Future changes to the data format or aggregator logic must be tested to avoid breaking the pipeline.

## Related ADRs
- [ADR 0001](./0001-use-python-for-scraper.md)
- [ADR 0002](./0002-store-data-as-static-json.md)
- [ADR 0003](./0003-use-react-for-frontend.md)

## Date
January 26, 2024
