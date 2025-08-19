---
inclusion: always
---

# Structure Steering for Daily Market Recap

## Code Organization Principles

### File Structure (Mandatory)
```
daily-market-recap/
├── main.py                 # Entry point and orchestration
├── data_collector.py       # API integrations (Google + Alpha Vantage)
├── content_generator.py    # Claude AI integration
├── publisher.py           # X API integration
├── models.py              # Data classes only
├── config.py              # Constants and configuration
├── requirements.txt       # Dependencies
├── .env                   # API keys (not in repo)
└── README.md              # Basic usage instructions
```

### Module Responsibilities (Single Responsibility Principle)

#### main.py
- **Only**: Pipeline orchestration and error handling
- **Not**: Business logic, API calls, or data processing

#### data_collector.py
- **Only**: External API integrations and data fetching
- **Not**: Data processing, content generation, or publishing

#### content_generator.py
- **Only**: Claude AI integration and content creation
- **Not**: Data collection, formatting for platforms, or publishing

#### publisher.py
- **Only**: X API integration and posting
- **Not**: Content generation, data collection, or formatting logic

#### models.py
- **Only**: Data classes and type definitions
- **Not**: Business logic, API calls, or processing functions

#### config.py
- **Only**: Constants, configuration values, and environment variable loading
- **Not**: Business logic or API integrations

## Code Style Guidelines

### Function Design
- **Maximum 20 lines per function**
- **Single responsibility**: One function, one job
- **Clear naming**: Function names should describe exactly what they do
- **Type hints**: All functions must have input/output type hints
- **Docstrings**: Brief description of purpose and parameters

### Error Handling
- **Fail fast**: Don't try to recover from API failures
- **Log everything**: All errors, successes, and key operations
- **No silent failures**: Every error must be logged and handled
- **Simple retry**: Maximum 3 attempts for network issues only

### Data Flow
- **Immutable data**: Don't modify data structures in place
- **Clear interfaces**: Each module has well-defined input/output
- **No global state**: Pass data explicitly between functions
- **Structured data**: Use dataclasses, not dictionaries

## Dependencies Management

### Allowed Dependencies
- `googleapiclient-discovery` (Google APIs)
- `alpha-vantage` (Stock data)
- `anthropic` (Claude AI)
- `requests` (HTTP requests)
- `python-dotenv` (Environment variables)
- Standard library only for everything else

### Forbidden Dependencies
- Web frameworks (Flask, Django, FastAPI)
- Database libraries (SQLAlchemy, pymongo)
- Testing frameworks (pytest, unittest beyond basic)
- Async libraries (asyncio, aiohttp)
- Complex configuration libraries
- Logging frameworks beyond standard library

## Import Organization
```python
# Standard library imports
import os
from datetime import datetime
from dataclasses import dataclass

# Third-party imports
import requests
from alpha_vantage.timeseries import TimeSeries

# Local imports
from models import StockData, NewsArticle
from config import ALPHA_VANTAGE_API_KEY
```

## Anti-Patterns to Avoid
- **God objects**: No single class/module doing everything
- **Deep nesting**: Maximum 3 levels of indentation
- **Magic numbers**: Use named constants
- **Premature optimization**: Focus on working code first
- **Over-engineering**: No abstract base classes or complex inheritance
- **Configuration complexity**: Hardcode values initially

## Success Criteria
Code is well-structured when:
- Each file has a single, clear purpose
- Functions are small and focused
- Dependencies are minimal and justified
- Error handling is consistent
- Code is readable without extensive comments