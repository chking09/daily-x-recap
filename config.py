"""
Configuration constants and API key management for Daily Market Recap.

This module loads API keys from environment variables and defines constants
for API endpoints, search queries, and filtering criteria.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys (loaded from .env file)
GOOGLE_SEARCH_API_KEY = os.getenv('GOOGLE_SEARCH_API_KEY')
GOOGLE_SEARCH_CX = os.getenv('GOOGLE_SEARCH_CX')
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
X_API_KEY = os.getenv('X_API_KEY')
X_API_SECRET = os.getenv('X_API_SECRET')
X_ACCESS_TOKEN = os.getenv('X_ACCESS_TOKEN')
X_ACCESS_SECRET = os.getenv('X_ACCESS_SECRET')

# Stock filtering criteria
MIN_MARKET_CAP = 2_000_000_000  # $2 billion minimum market cap

# Google Custom Search API configuration
GOOGLE_SEARCH_QUERIES = [
    "stock market news today",
    "financial markets today",
    "stock market movers today",
    "market news earnings"
]

# Search parameters
SEARCH_DATE_RESTRICT = "d1"  # Last 1 day
MAX_SEARCH_RESULTS = 10

# Finviz scraping configuration
FINVIZ_BASE_URL = "https://finviz.com"
FINVIZ_SCREENER_URL = "https://finviz.com/screener.ashx"
FINVIZ_QUOTE_URL = "https://finviz.com/quote.ashx"

# Content generation parameters
MAX_TWEET_LENGTH = 280
STOCK_MOVERS_COUNT = 3
WATCHLIST_STOCKS_COUNT = 3

# X API v2 endpoints
X_API_BASE_URL = "https://api.twitter.com"
X_TWEETS_ENDPOINT = "/2/tweets"

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY_BASE = 2  # Base delay in seconds for exponential backoff