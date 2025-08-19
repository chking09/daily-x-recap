"""
Configuration - Constants and environment variable loading
Centralizes all configuration values and API credentials
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys (loaded from .env file)
GOOGLE_SEARCH_API_KEY = os.getenv('GOOGLE_SEARCH_API_KEY')
GOOGLE_SEARCH_CX = os.getenv('GOOGLE_SEARCH_CX')
ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY')
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
X_API_KEY = os.getenv('X_API_KEY')
X_API_SECRET = os.getenv('X_API_SECRET')
X_ACCESS_TOKEN = os.getenv('X_ACCESS_TOKEN')
X_ACCESS_SECRET = os.getenv('X_ACCESS_SECRET')

# Stock filtering criteria
MIN_MARKET_CAP = 2_000_000_000  # $2 billion minimum market cap

# Google Custom Search configuration
FINANCIAL_NEWS_QUERIES = [
    "stock market news today",
    "financial markets today",
    "market movers today"
]

# API endpoints
GOOGLE_SEARCH_URL = "https://www.googleapis.com/customsearch/v1"
X_API_BASE_URL = "https://api.twitter.com/2"

# Content constraints
MAX_TWEET_LENGTH = 280
RETRY_ATTEMPTS = 3
RETRY_DELAY = 2  # seconds