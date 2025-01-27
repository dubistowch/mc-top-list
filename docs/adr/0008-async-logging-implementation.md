# ADR 0008: Async Logging Implementation

## Status
Accepted

## Context
While implementing an asynchronous data collection system, we found that the standard Python logging module might have performance and thread safety issues in async environments. We need a reliable solution for logging in async contexts, especially when dealing with multiple API clients running concurrently.

## Decision
We will implement an async-aware logging solution:

1. **Core Components**:
   - Custom AsyncLogger class in `utils/logger.py`
   - RotatingFileHandler for log file management
   - Structured logging format with JSON support
   - Correlation IDs for request tracking

2. **Implementation Details**:
   - Singleton pattern for logger initialization
   - Async context tracking with contextvars
   - Rate limiting for log messages
   - Log rotation based on file size and time
   - Different log levels for API clients

3. **Log Format**:
   ```json
   {
     "timestamp": "ISO8601",
     "level": "INFO|WARNING|ERROR",
     "correlation_id": "uuid",
     "source": "api_client_name",
     "message": "log_message",
     "context": {}
   }
   ```

## Consequences
### Positive
- Thread-safe logging in async context
- Better debugging with correlation IDs
- Structured logs for easy parsing
- Efficient log rotation
- Memory-efficient operation

### Negative
- More complex logging setup
- Additional CPU overhead for JSON formatting
- Need for log cleanup automation
- Increased disk usage for detailed logs

## Related ADRs
- [ADR 0007](./0007-api-first-data-collection-strategy.md)
- [ADR 0005](./0005-github-actions-for-ci-cd.md)
- [ADR 0001](./0001-use-python-for-scraper.md)

## Date
01/27/2025 