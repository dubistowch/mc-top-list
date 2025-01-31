# ADR 0013: Codebase Restructuring

## Status
Proposed

## Context
The current codebase exhibits signs of over-engineering, manifesting in:
1. Excessive architectural complexity with multiple layers of abstraction
2. Overly dispersed file structure
3. Complex transformation logic
4. Test structure requiring optimization

These issues impact maintainability, development velocity, and code comprehension.

## Decision
We will undertake a comprehensive codebase restructuring with the following approach:

### Phase 1: Foundation Restructuring

Reorganize directory structure to:
```
scraper/
├── clients/          # Unified API clients
├── services/         # Core business logic
└── models/           # Simplified data models
```

### Phase 2: File Migration and Refactoring Plan

#### 1. Core Files (Priority: High)
- Migrate `scraper.py` to `services/scraper_service.py`
  - Simplify main logic
  - Remove duplicate error handling
  - Standardize logging

#### 2. Platform Files (Priority: High)
- Migrate `platforms/modrinth/client.py` to `clients/modrinth.py`
- Migrate `platforms/hangar/client.py` to `clients/hangar.py`
- Consolidate `platforms/*/transformers/*` into `services/transformers/`
  - Merge duplicate transformation logic
  - Simplify resource type handling

#### 3. Model Files (Priority: Medium)
- Simplify `models/resource.py`
- Add `models/platform.py` for platform configuration

#### 4. Utility Files (Priority: Low)
- Reorganize `utils/`
- Merge `validators/` into relevant services
- Simplify `persistence/` and move to `services/storage/`

#### 5. Configuration Files (Priority: Medium)
- Simplify `config/` to single configuration file
- Integrate `api_config.yml` into `config.yml`

#### 6. Test Files (Priority: High)
- Restructure `tests/`
- Simplify `run_tests.py`

### Code Standards

1. Type Hints:
```python
from typing import Dict, List, Optional

def process_resource(resource_id: str) -> Optional[Dict]:
    pass
```

2. Error Handling:
```python
class ScraperError(Exception):
    pass

class ResourceNotFoundError(ScraperError):
    pass
```

3. Logging Format:
```python
logger.info("Processing resource: %s", resource_id)
logger.error("Failed to fetch resource: %s, error: %s", resource_id, str(error))
```

### Design Patterns

1. Factory Pattern:
```python
class ClientFactory:
    @staticmethod
    def create(platform: str) -> BaseClient:
        if platform == "modrinth":
            return ModrinthClient()
        return HangarClient()
```

2. Strategy Pattern:
```python
class TransformerStrategy:
    def transform(self, data: Dict) -> Dict:
        pass
```

### Configuration Management

Unified configuration format:
```yaml
# config.yml
platforms:
  modrinth:
    api_url: "https://api.modrinth.com/v2"
    batch_size: 100
  hangar:
    api_url: "https://hangar.papermc.io/api/v1"
    batch_size: 50
```

### Testing Strategy

1. Integration Tests:
```python
class TestScraperIntegration:
    def test_fetch_and_transform(self):
        service = ScraperService()
        result = service.fetch_and_transform("modrinth")
        assert result is not None
```

2. Unit Tests:
```python
class TestTransformer:
    def test_resource_transformation(self):
        transformer = ResourceTransformer()
        result = transformer.transform(sample_data)
        assert result["id"] is not None
```

## Consequences

### Positive
1. Reduced code complexity
2. Improved maintainability
3. Simplified development workflow
4. Enhanced code readability
5. Easier testing

### Negative
1. Time investment required for refactoring
2. Temporary impact on new feature development
3. Documentation updates needed

### Risk Management
1. Create branch before each refactoring phase
2. Maintain test coverage above 80%
3. Follow Python PEP 8 guidelines
4. Maintain backward compatibility
5. Regular documentation updates

## Related ADRs
- [ADR 0010](./0010-code-refactoring-principles.md)
- [ADR 0011](./0011-scraper-code-organization.md)

## Progress Tracking

```markdown
### Completed
- [ ] Foundation restructuring
- [ ] Core file migration
- [ ] Platform file refactoring
- [ ] Model simplification
- [ ] Utility reorganization
- [ ] Configuration unification
- [ ] Test restructuring

### Pending
- [ ] Documentation updates
- [ ] Performance optimization
- [ ] Code coverage improvement
```

## Date
01/31/2025