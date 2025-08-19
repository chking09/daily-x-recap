# Implementation Plan

- [x] 1. Set up project structure and dependencies

  - Create directory structure with main.py, data_collector.py, content_generator.py, publisher.py, models.py, config.py
  - Create requirements.txt with essential dependencies: google-api-python-client, finvizfinance, anthropic, requests, python-dotenv
  - API keys are already configured in .env file (GOOGLE_SEARCH_API_KEY, GOOGLE_SEARCH_CX, CLAUDE_API_KEY, X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET)
  - _Requirements: 6.1, 6.2, 6.3_

- [x] 2. Implement data models and configuration

  - Create NewsArticle, StockData, and MarketRecap dataclasses in models.py
  - Implement config.py with constants for API endpoints, stock filtering criteria (>$2B market cap), and search queries
  - Load API keys from .env file using python-dotenv
  - _Requirements: 2.1, 2.2, 3.1, 3.2_

- [x] 3. Build Google Custom Search API integration

  - Implement collect_market_news() function in data_collector.py
  - Use googleapiclient to create customsearch service with API key
  - Configure search queries for financial news with dateRestrict parameter for recent news
  - Return list of NewsArticle objects with title, URL, snippet, and date
  - _Requirements: 1.1, 6.1_

- [x] 4. Build finvizfinance library integration

  - Implement get_stock_movers() and get_watchlist_stocks() functions in data_collector.py
  - Use finvizfinance.screener.overview.Overview() to filter stocks by performance and market cap
  - Use finvizfinance.quote.finvizfinance() to get individual stock fundamental data
  - Filter stocks by market cap > $2 billion criteria using screener filters
  - Return StockData objects with symbol, name, price, change percentage, and reasoning
  - Leverage built-in rate limiting and respectful API usage
  - _Requirements: 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 6.2_

- [ ] 5. Implement Claude AI content generation

  - Create generate_recap() function in content_generator.py
  - Use Anthropic client to process structured data into engaging content
  - Ensure output respects X character limits and maintains witty, educational tone
  - Include context for stock movements and educational insights for beginners
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 5.1, 5.2, 5.3_

- [ ] 6. Build X API publishing integration

  - Implement post_to_x() function in publisher.py
  - Use requests library to call POST /2/tweets endpoint with OAuth 1.0a authentication
  - Handle character limits and format content appropriately for X platform
  - Return success/failure status for logging
  - _Requirements: 4.1, 4.2, 6.3_

- [ ] 7. Create main controller and pipeline orchestration

  - Implement run_daily_recap() function in main.py
  - Orchestrate sequential execution: collect data → generate content → publish to X
  - Add error handling with fail-fast approach and logging
  - Include success logging with timestamps
  - _Requirements: 4.1, 4.3, 4.4_

- [ ] 8. Add comprehensive error handling and logging

  - Implement try-catch blocks for each API integration
  - Add logging for errors, API failures, and successful completions
  - Implement simple retry logic (3 attempts) for network issues with exponential backoff
  - Ensure pipeline stops on any failure without partial posts
  - _Requirements: 4.3, 4.4, 6.4, 6.5_

- [ ] 9. Test individual API integrations

  - Write simple test script to verify Google Custom Search API returns financial news
  - Test finvizfinance library returns valid stock data with market cap filtering
  - Verify Claude AI generates appropriate content within character limits
  - Test X API successfully posts content with proper OAuth 1.0a authentication
  - _Requirements: 6.6_

- [ ] 10. Perform end-to-end integration testing
  - Run complete pipeline from data collection through publishing
  - Verify all components work together without errors
  - Test error handling by simulating API failures
  - Validate final output meets all content requirements (3 movers, 3 watchlist, news summary)
  - _Requirements: 1.1, 2.1, 3.1, 4.1, 5.1_
