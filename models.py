"""
Data models for the Daily Market Recap system.

This module contains dataclasses that represent the core data structures
used throughout the pipeline for news articles, stock data, and market recaps.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class NewsArticle:
    """Represents a financial news article from Google Custom Search API."""
    title: str
    url: str
    snippet: str
    published_date: str


@dataclass
class StockData:
    """Represents stock information with price and movement data."""
    symbol: str
    company_name: str
    current_price: float
    price_change_percent: float
    market_cap: float
    reason: str  # Why it moved or why it's worth watching


@dataclass
class MarketRecap:
    """Represents the complete market recap with all components."""
    news_summary: str
    stock_movers: List[StockData]
    watchlist_stocks: List[StockData]
    generated_content: str
    timestamp: datetime