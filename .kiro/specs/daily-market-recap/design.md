# Design Document

## Overview

The Daily Market Recap is a simple data pipeline that collects financial data from Google Custom Search API and finvizfinance library, processes it with Claude AI, and publishes the result to X (Twitter). The system follows a linear workflow: **Collect → Process → Publish**.

## Architecture

### High-Level Flow

```
[Google Custom Search API] → [Data Collection] → [Claude Processing] → [X API v2 Publishing]
[finvizfinance Library]    ↗
```

### Core Components

1. **Data Collector**: Interfaces with Google Custom Search API and finvizfinance library
2. **Content Generator**: Uses Claude AI to process raw data into engaging content
3. **Publisher**: Posts formatted content to X using X API v2
4. **Main Controller**: Orchestrates the pipeline execution

## Components and Interfaces

### 1. Data Collector Module

**Purpose**: Gather financial news and stock data from external APIs and finvizfinance library

**Interfaces**:

- `collect_market_news()` → Returns list of relevant financial news articles
- `get_stock_movers()` → Returns 3 mid-large cap stocks with significant moves
- `get_watchlist_stocks()` → Returns 3 mid-large cap stocks to watch

**Dependencies**:

- Google Custom Search API client (`google-api-python-client`)
- finvizfinance library (`finvizfinance`)

**Key Implementation Details**:

- Google Custom Search: Use `customsearch.cse().list()` with financial news queries
- finvizfinance: Use `screener.overview.Overview()` for filtering stocks by performance
- Use `quote.finvizfinance()` for individual stock fundamental data
- Extract stock data including market cap, price, and percentage changes from library methods
- Filter stocks by market cap > $2 billion using screener filters
- Built-in rate limiting and respectful API usage
- Return structured data objects for downstream processing

### 2. Content Generator Module

**Purpose**: Transform raw financial data into engaging, educational content

**Interfaces**:

- `generate_recap(news_data, movers_data, watchlist_data)` → Returns formatted market recap text

**Dependencies**:

- Claude AI API client (Anthropic)

**Key Implementation Details**:

- Accept structured data from Data Collector
- Use Claude to synthesize information into witty, accessible content
- Ensure output respects X character limits (280 characters or thread format)
- Include educational context for beginner/intermediate investors

### 3. Publisher Module

**Purpose**: Post generated content to X (Twitter)

**Interfaces**:

- `post_to_x(content)` → Returns success/failure status

**Dependencies**:

- X API v2 client
- OAuth 2.0 authentication

**Key Implementation Details**:

- Use `POST /2/tweets` endpoint
- Handle character limits (split into threads if necessary)
- Include appropriate hashtags and formatting
- Return posting status for logging

### 4. Main Controller

**Purpose**: Orchestrate the complete pipeline execution

**Interfaces**:

- `run_daily_recap()` → Executes full pipeline

**Key Implementation Details**:

- Sequential execution: collect → process → publish
- Error handling: stop on any failure, log errors
- Success logging with timestamps
- Simple retry logic for API failures

## Data Models

### NewsArticle

```python
@dataclass
class NewsArticle:
    title: str
    url: str
    snippet: str
    published_date: str
```

### StockData

```python
@dataclass
class StockData:
    symbol: str
    company_name: str
    current_price: float
    price_change_percent: float
    market_cap: float
    reason: str  # Why it moved or why it's worth watching
```

### MarketRecap

```python
@dataclass
class MarketRecap:
    news_summary: str
    stock_movers: List[StockData]
    watchlist_stocks: List[StockData]
    generated_content: str
    timestamp: datetime
```

## Error Handling

### Strategy: Fail Fast

- Any API failure stops the entire pipeline
- Log all errors with timestamps
- No partial content generation or posting
- Simple retry mechanism (3 attempts) for network issues

### Error Types

1. **API Authentication Errors**: Log and exit
2. **Rate Limit Errors**: Log and exit (retry on next scheduled run)
3. **Data Quality Issues**: Log and exit
4. **Content Generation Failures**: Log and exit

## Testing Strategy

### Manual Testing Approach

1. **Unit Testing**: One test per API integration to verify connectivity
2. **Integration Testing**: Single end-to-end test of complete pipeline
3. **Data Validation**: Verify each API returns expected data structure
4. **Content Quality**: Manual review of Claude-generated content

### Test Cases

- Google Custom Search returns financial news articles
- finvizfinance library returns valid stock data with market cap filtering
- Claude generates content within character limits
- X API successfully posts content
- Complete pipeline executes without errors

## Implementation Notes

### Configuration

- Store API keys in environment variables
- Hardcode search queries and stock filtering criteria initially
- Use simple configuration file only if needed for deployment

### Scheduling

- External scheduler (cron, Task Scheduler, or cloud scheduler)
- Single entry point: `python main.py`
- No built-in scheduling logic

### Dependencies

```
- google-api-python-client
- finvizfinance
- anthropic
- requests (for X API v2)
- python-dotenv (for environment variables)
```

### File Structure

```
daily-market-recap/
├── main.py                 # Entry point and controller
├── data_collector.py       # Google Search + finvizfinance
├── content_generator.py    # Claude AI integration
├── publisher.py           # X API v2 integration
├── models.py              # Data classes
├── config.py              # Configuration and constants
└── requirements.txt       # Dependencies
```

This design prioritizes simplicity and maintainability while ensuring all core requirements are met. The linear pipeline approach makes debugging straightforward and prevents complex state management issues.
