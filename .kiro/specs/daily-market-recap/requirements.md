# Requirements Document

## Introduction

The Daily Market Recap is a simple data pipeline that:
1. **Collects** financial news (Google Custom Search API) and stock data (finvizfinance library)
2. **Processes** the data using Claude AI to generate a witty, informative market summary
3. **Publishes** the content automatically to X (Twitter) via X API v2

The system focuses on three core elements: 3 stocks that moved significantly, 3 stocks to watch, and relevant market news - all presented in an accessible, engaging format for beginner/intermediate investors.

## Requirements

### Requirement 1

**User Story:** As a beginner/intermediate investor, I want to receive a daily market recap that explains major market events in an accessible way, so that I can stay informed about market trends without being overwhelmed by complex financial terminology.

#### Acceptance Criteria

1. WHEN the daily recap is generated THEN the system SHALL include a summary of major relevant market news in plain English
2. WHEN presenting market news THEN the system SHALL explain the potential impact on retail investors
3. WHEN technical terms are used THEN the system SHALL provide brief, clear explanations
4. WHEN the recap is generated THEN the system SHALL maintain a witty, engaging tone while remaining informative

### Requirement 2

**User Story:** As an investor tracking market performance, I want to see which mid-large cap stocks made significant moves today, so that I can understand what drove major market activity and learn from these movements.

#### Acceptance Criteria

1. WHEN the daily recap is generated THEN the system SHALL identify exactly 3 mid-large cap stocks that made large moves (positive or negative)
2. WHEN a stock is featured THEN the system SHALL include the stock symbol, company name, and percentage change
3. WHEN a stock is featured THEN the system SHALL provide context for why the stock moved significantly
4. WHEN selecting stocks THEN the system SHALL focus on mid-large cap companies (market cap > $2 billion)
5. WHEN explaining stock movements THEN the system SHALL relate the information to broader market trends or company-specific events

### Requirement 3

**User Story:** As an investor planning future trades, I want to know which mid-large cap stocks to watch in the coming days, so that I can identify potential investment opportunities and stay ahead of market trends.

#### Acceptance Criteria

1. WHEN the daily recap is generated THEN the system SHALL recommend exactly 3 mid-large cap stocks to watch in the coming days
2. WHEN a stock is recommended THEN the system SHALL include the stock symbol, company name, and current price
3. WHEN a stock is recommended THEN the system SHALL explain why it's worth watching (upcoming earnings, product launches, market catalysts, etc.)
4. WHEN selecting watchlist stocks THEN the system SHALL focus on mid-large cap companies (market cap > $2 billion)
5. WHEN making recommendations THEN the system SHALL provide educational context about what factors make a stock worth monitoring

### Requirement 4

**User Story:** As a user, I want the system to run automatically and post to X, so that I get a daily market recap without manual work.

#### Acceptance Criteria

1. WHEN triggered THEN the system SHALL complete the full pipeline: collect data → generate content → post to X
2. WHEN posting to X THEN the system SHALL respect character limits and format appropriately
3. IF any step fails THEN the system SHALL log the error and stop (no partial posts)
4. WHEN complete THEN the system SHALL log success with timestamp

### Requirement 5

**User Story:** As a beginner investor, I want the content to be educational and accessible, so that I can learn while staying informed.

#### Acceptance Criteria

1. WHEN generating content THEN Claude SHALL explain market movements in plain English
2. WHEN discussing stocks THEN Claude SHALL provide brief context for why they moved or are worth watching
3. WHEN the content is generated THEN it SHALL maintain a witty, engaging tone while being informative

### Requirement 6

**User Story:** As a system administrator, I want the program to use reliable data sources for gathering information, so that the market recap has accurate, up-to-date information from trusted sources.

#### Acceptance Criteria

1. WHEN gathering market news THEN the system SHALL use Google Custom Search API with:
   - customsearch.cse().list() method for performing searches
   - Required parameters: cx (Custom Search Engine ID), q (query terms)
   - Optional parameters: dateRestrict for recent news, siteSearch for specific financial sites
   - Support for up to 100 results per query with pagination
2. WHEN retrieving stock data THEN the system SHALL use finvizfinance library including:
   - Using screener.overview.Overview() for filtering stocks by performance
   - Using quote.finvizfinance() for individual stock data
   - Extracting market cap, price, and percentage change data from library methods
   - Built-in rate limiting and respectful API usage
3. WHEN posting content THEN the system SHALL use X API v2 POST /2/tweets endpoint with OAuth 2.0 Authorization Code with PKCE authentication
4. WHEN finvizfinance library calls fail THEN the system SHALL implement retry logic with exponential backoff
5. WHEN rate limiting web requests THEN the system SHALL respect limits:
   - X API v2: 200 requests per 15 minutes for tweet creation
   - finvizfinance library: Built-in rate limiting and respectful usage
   - Google Custom Search API: 100 queries per day (free tier), 10,000 queries per day (paid)
6. WHEN finvizfinance responses are received THEN the system SHALL validate data structure and handle library errors appropriately