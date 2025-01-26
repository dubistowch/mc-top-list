# ADR 0003: Use React for Frontend

## Status
Accepted

## Context
The project needs a frontend solution that can:
- Display and search plugin/mod data efficiently
- Provide a modern user experience
- Be hosted as a static site
- Handle client-side data processing

## Decision
We will build the frontend using React:

### Technical Stack
- React 18+
- Build tool: Vite
- Directory: `/web`
- Deployment: Firebase Hosting

### Key Features
- Client-side search and filtering
- Static file hosting
- Modern component architecture

## Consequences
### Positive
- Large developer ecosystem
- Strong community support
- Easy deployment as static assets
- Modern development experience

### Negative
- Client-side processing limitations
- Initial bundle size considerations
- Need to manage React dependencies

## Related ADRs
- [ADR 0002](./0002-store-data-as-static-json.md)
- [ADR 0005](./0005-github-actions-for-ci-cd.md)

## Date
January 26, 2024
