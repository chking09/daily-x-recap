"""
Data Models - Dataclasses for structured data representation
Defines the core data structures used throughout the application
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class NewsArticle:
    """Represents a financial news article from Google Custom Search"""
    title: str
    url: str
    snippet: str
    date: datetime
    
@dataclass
class StockData:
    """Represents stock information from Alpha Vantage API"""
    symbol: str
    name: str
    price: float
    change_percentage: float
    reasoning: str
    market_cap: Optional[float] = None
    
@dataclass
class MarketRecap:
    """Represents the complete market recap data structure"""
    news_summary: str
    stock_movers: list  # List[StockData]
    watchlist_stocks: list  # List[StockData]
    generated_content: str
    timestamp: datetime