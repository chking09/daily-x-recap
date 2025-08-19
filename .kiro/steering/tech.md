---
inclusion: always
---

# Technical Steering for Daily Market Recap

## Technology Stack (Fixed)

### Core Language

- **Python 3.9+**: Minimum version for type hints and dataclasses
- **No alternative languages**: Keep it simple with single language

### API Integration Libraries

- **Google APIs**: `google-api-python-client` (official Google client)
- **Finviz Data**: `finvizfinance` (Python library for Finviz data access)
- **Claude AI**: `anthropic` (official Anthropic client)
- **X API**: `requests` (direct HTTP calls, no third-party wrapper)
- **Environment**: `python-dotenv` (environment variable management)

### Forbidden Technologies

- **Async/await**: Synchronous code only for simplicity
- **Web frameworks**: No Flask, Django, FastAPI
- **Databases**: No SQLite, PostgreSQL, MongoDB
- **Message queues**: No Redis, RabbitMQ, Celery
- **Containerization**: No Docker until core functionality works
- **Cloud services**: No AWS Lambda, Google Cloud Functions initially

## API Integration Patterns

### Authentication Strategy

- **Environment variables**: All API keys in .env file
- **No OAuth flows**: Use pre-generated tokens where possible
- **Simple bearer tokens**: For APIs that support it
- **No token refresh logic**: Use long-lived tokens initially

### Error Handling Pattern

```python
def api_call_with_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

### Rate Limiting Strategy

- **Use finvizfinance library**: Built-in rate limiting and respectful requests
- **Simple delays**: Minimal delays between different data requests
- **Fail gracefully**: If API fails, log and exit
- **No queuing**: Don't build request queues or delays

## Data Processing Guidelines

### Data Validation

- **Input validation**: Check API responses for required fields
- **Type checking**: Use isinstance() for runtime type checking
- **Fail on bad data**: Don't try to fix or guess missing data

### Data Transformation

- **Immutable operations**: Create new objects, don't modify existing
- **Simple transformations**: No complex data manipulation
- **Clear data flow**: Input → Transform → Output

### Memory Management

- **No caching**: Process data and discard
- **Small datasets**: Expect <1MB of data per run
- **No optimization**: Don't worry about memory usage initially

## Configuration Management

### Environment Variables (Already Configured)

The .env file is already created with all required API keys:

- Google Custom Search API key and CSE ID
- Anthropic Claude API key
- X (Twitter) API credentials (Bearer token, API key/secret, Access token/secret)

**No Alpha Vantage needed** - Using free finvizfinance library instead of paid API.

### Configuration Constants

- **Hardcoded values**: Stock market cap threshold, search queries
- **No config files**: Use Python constants in config.py
- **No command line args**: Keep execution simple

## Logging Strategy

### Logging Levels

- **INFO**: Successful operations, pipeline start/end
- **ERROR**: API failures, authentication issues
- **DEBUG**: Not used initially
- **WARNING**: Rate limits, data quality issues

### Log Format

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

## Testing Approach

### Manual Testing Only

- **No test frameworks**: No pytest, unittest initially
- **Manual verification**: Run each component individually
- **Integration testing**: Full pipeline test with real APIs
- **No mocking**: Test against real APIs with test data

### Testing Checklist

- [ ] Google Custom Search returns financial news
- [ ] finvizfinance library returns stock movers and watchlist data
- [ ] Claude generates appropriate content
- [ ] X API posts content successfully
- [ ] Full pipeline completes without errors

## Deployment Strategy

### Local Development

- **Python virtual environment**: `python -m venv venv`
- **Requirements installation**: `pip install -r requirements.txt`
- **Environment ready**: .env file already configured with API keys
- **Manual execution**: `python main.py`

### Production Deployment (Future)

- **Cron job**: Simple scheduled execution
- **No containers initially**: Direct Python execution
- **No CI/CD**: Manual deployment until core works
- **Single server**: No distributed architecture

## Performance Guidelines

### Acceptable Performance

- **Total runtime**: <5 minutes for complete pipeline
- **API response time**: <30 seconds per API call
- **Content generation**: <60 seconds for Claude processing
- **No optimization**: Focus on working code first

### Performance Anti-Patterns

- **Premature optimization**: Don't optimize until it works
- **Complex caching**: No Redis, memcached, or file caching
- **Parallel processing**: No threading or multiprocessing
- **Database optimization**: No databases to optimize

## Security Considerations

### API Key Security

- **Environment variables**: API keys already configured in .env file
- **.env file**: Already added to .gitignore (never commit API keys)
- **No key rotation**: Using long-lived keys for simplicity
- **Ready to use**: All credentials configured and available

### Input Validation

- **API response validation**: Check for required fields
- **No user input**: No external input to validate
- **No SQL injection**: No databases to protect
- **No XSS**: No web interface to secure

## Success Criteria

Technical implementation is successful when:

- All APIs integrate successfully with the configured credentials
- Pipeline completes end-to-end without errors
- Code is maintainable and follows patterns
- Error handling prevents crashes
- Logging provides visibility into operations

**Advantage**: With API keys already configured, you can test each integration immediately as you build it.
