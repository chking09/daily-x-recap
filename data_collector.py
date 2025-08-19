"""
Data Collector - API integrations for Google Custom Search and Finviz scraping
Handles external data collection from financial APIs and web scraping
"""

import logging
import time
import re
from typing import List, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests
from bs4 import BeautifulSoup

from models import NewsArticle, StockData
from config import (
    GOOGLE_SEARCH_API_KEY, 
    GOOGLE_SEARCH_CX, 
    GOOGLE_SEARCH_QUERIES,
    SEARCH_DATE_RESTRICT,
    MAX_SEARCH_RESULTS,
    FINVIZ_BASE_URL,
    FINVIZ_SCREENER_URL,
    FINVIZ_QUOTE_URL,
    MIN_MARKET_CAP,
    STOCK_MOVERS_COUNT,
    WATCHLIST_STOCKS_COUNT,
    MAX_RETRIES,
    RETRY_DELAY_BASE
)

def collect_market_news() -> List[NewsArticle]:
    """
    Collect recent financial news using Google Custom Search API
    
    Returns:
        List of NewsArticle objects with recent financial news
    """
    logging.info("Collecting market news from Google Custom Search API")
    
    if not GOOGLE_SEARCH_API_KEY or not GOOGLE_SEARCH_CX:
        logging.error("Google Search API key or Custom Search Engine ID not configured")
        raise ValueError("Google Search API credentials not found in environment variables")
    
    news_articles = []
    
    try:
        # Build the Custom Search service
        service = build("customsearch", "v1", developerKey=GOOGLE_SEARCH_API_KEY)
        
        # Search for financial news using configured queries
        for query in GOOGLE_SEARCH_QUERIES:
            logging.info(f"Searching for: {query}")
            
            # Perform search with retry logic
            search_results = _perform_search_with_retry(
                service, query, GOOGLE_SEARCH_CX, SEARCH_DATE_RESTRICT, MAX_SEARCH_RESULTS
            )
            
            # Process search results
            if search_results and 'items' in search_results:
                for item in search_results['items']:
                    article = NewsArticle(
                        title=item.get('title', ''),
                        url=item.get('link', ''),
                        snippet=item.get('snippet', ''),
                        published_date=item.get('pagemap', {}).get('metatags', [{}])[0].get('article:published_time', '')
                    )
                    news_articles.append(article)
                    
                logging.info(f"Found {len(search_results['items'])} articles for query: {query}")
            else:
                logging.warning(f"No results found for query: {query}")
    
    except HttpError as e:
        logging.error(f"Google Custom Search API error: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error collecting market news: {e}")
        raise
    
    # Remove duplicates based on URL
    unique_articles = []
    seen_urls = set()
    for article in news_articles:
        if article.url not in seen_urls:
            unique_articles.append(article)
            seen_urls.add(article.url)
    
    logging.info(f"Collected {len(unique_articles)} unique news articles")
    return unique_articles


def _perform_search_with_retry(service, query: str, cx: str, date_restrict: str, num_results: int) -> dict:
    """
    Perform Google Custom Search with retry logic for network issues
    
    Args:
        service: Google Custom Search service object
        query: Search query string
        cx: Custom Search Engine ID
        date_restrict: Date restriction parameter
        num_results: Maximum number of results to return
        
    Returns:
        Search results dictionary
    """
    for attempt in range(MAX_RETRIES):
        try:
            result = service.cse().list(
                q=query,
                cx=cx,
                dateRestrict=date_restrict,
                num=num_results
            ).execute()
            return result
            
        except HttpError as e:
            if attempt == MAX_RETRIES - 1:
                logging.error(f"Google Search API failed after {MAX_RETRIES} attempts: {e}")
                raise
            
            # Exponential backoff
            delay = RETRY_DELAY_BASE ** attempt
            logging.warning(f"Google Search API attempt {attempt + 1} failed, retrying in {delay}s: {e}")
            time.sleep(delay)
        
        except Exception as e:
            logging.error(f"Unexpected error in Google Search API call: {e}")
            raise

def get_stock_movers() -> List[StockData]:
    """
    Get top 3 stock movers using Finviz screener
    
    Returns:
        List of StockData objects for stocks with significant price movements
    """
    logging.info("Collecting stock movers from Finviz")
    
    try:
        # Get top gainers and losers from Finviz
        gainers = _scrape_finviz_movers("ta_topgainers")
        losers = _scrape_finviz_movers("ta_toplosers")
        
        # Combine and filter by market cap
        all_movers = gainers + losers
        filtered_movers = []
        
        for stock in all_movers:
            if stock.market_cap >= MIN_MARKET_CAP:
                filtered_movers.append(stock)
        
        # Sort by absolute change percentage and take top 3
        filtered_movers.sort(key=lambda x: abs(x.price_change_percent), reverse=True)
        top_movers = filtered_movers[:STOCK_MOVERS_COUNT]
        
        logging.info(f"Collected {len(top_movers)} stock movers")
        return top_movers
        
    except Exception as e:
        logging.error(f"Error collecting stock movers: {e}")
        raise


def get_watchlist_stocks() -> List[StockData]:
    """
    Get 3 stocks to watch using Finviz data
    
    Returns:
        List of StockData objects for stocks worth monitoring
    """
    logging.info("Collecting watchlist stocks from Finviz")
    
    # Stocks with upcoming catalysts or interesting technical setups
    # These are selected based on common watchlist criteria
    watchlist_candidates = [
        ('NFLX', 'Streaming competition and content spending'),
        ('AMD', 'AI chip competition with NVIDIA'),
        ('DIS', 'Streaming wars and park recovery'),
        ('PYPL', 'Digital payments growth'),
        ('SHOP', 'E-commerce platform expansion'),
        ('SQ', 'Fintech and Bitcoin exposure'),
        ('ROKU', 'Connected TV advertising'),
        ('ZM', 'Remote work trends'),
        ('PLTR', 'AI and data analytics'),
        ('COIN', 'Cryptocurrency exchange'),
        ('CRWD', 'Cybersecurity growth'),
        ('SNOW', 'Cloud data platform'),
        ('UBER', 'Mobility and delivery services'),
        ('AIRBNB', 'Travel recovery trends')
    ]
    
    watchlist_stocks = []
    
    try:
        for symbol, watch_reason in watchlist_candidates:
            try:
                # Get stock data from Finviz
                stock_data = _get_finviz_stock_data(symbol)
                
                if stock_data and stock_data.market_cap >= MIN_MARKET_CAP:
                    # Update the reason for watching
                    stock_data.reason = watch_reason
                    watchlist_stocks.append(stock_data)
                    
                    logging.info(f"Added to watchlist: {symbol} - {watch_reason}")
                    
                    # Stop once we have enough stocks
                    if len(watchlist_stocks) >= WATCHLIST_STOCKS_COUNT:
                        break
                
                # Rate limiting to be respectful to Finviz
                time.sleep(1)
                
            except Exception as e:
                logging.warning(f"Failed to get data for {symbol}: {e}")
                continue
    
    except Exception as e:
        logging.error(f"Error collecting watchlist stocks: {e}")
        raise
    
    logging.info(f"Collected {len(watchlist_stocks)} watchlist stocks")
    return watchlist_stocks


def _get_stock_quote_with_retry(symbol: str) -> dict:
    """
    Get stock quote data with retry logic for Alpha Vantage API
    
    Args:
        symbol: Stock symbol to get quote for
        
    Returns:
        Quote data dictionary or None if failed
    """
    for attempt in range(MAX_RETRIES):
        try:
            # Use direct API call for better control
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': ALPHA_VANTAGE_API_KEY
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API errors
            if 'Error Message' in data:
                logging.error(f"Alpha Vantage API error for {symbol}: {data['Error Message']}")
                return None
            
            if 'Note' in data:
                logging.warning(f"Alpha Vantage API rate limit for {symbol}: {data['Note']}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(60)  # Wait 1 minute for rate limit
                    continue
                return None
            
            # Extract quote data
            global_quote = data.get('Global Quote', {})
            if global_quote:
                return global_quote
            else:
                logging.warning(f"No quote data returned for {symbol}")
                return None
                
        except requests.RequestException as e:
            if attempt == MAX_RETRIES - 1:
                logging.error(f"Alpha Vantage API failed after {MAX_RETRIES} attempts for {symbol}: {e}")
                return None
            
            # Exponential backoff
            delay = RETRY_DELAY_BASE ** attempt
            logging.warning(f"Alpha Vantage API attempt {attempt + 1} failed for {symbol}, retrying in {delay}s: {e}")
            time.sleep(delay)
        
        except Exception as e:
            logging.error(f"Unexpected error getting quote for {symbol}: {e}")
            return None
    
    return None


def _generate_movement_reason(symbol: str, change_percent: float) -> str:
    """
    Generate a simple reason for stock movement
    
    Args:
        symbol: Stock symbol
        change_percent: Percentage change
        
    Returns:
        Reason string for the movement
    """
    direction = "surged" if change_percent > 0 else "plunged"
    
    # Simple reasons based on common market drivers
    generic_reasons = {
        "positive": [
            "strong earnings beat",
            "positive analyst upgrade", 
            "bullish market sentiment",
            "sector momentum",
            "raised guidance"
        ],
        "negative": [
            "disappointing earnings",
            "analyst downgrade",
            "market selloff pressure", 
            "profit-taking activity",
            "lowered outlook"
        ]
    }
    
    reason_type = "positive" if change_percent > 0 else "negative"
    # Use first reason for simplicity (in real implementation, could be more sophisticated)
    base_reason = generic_reasons[reason_type][0]
    
    return f"Stock {direction} {abs(change_percent):.1f}% on {base_reason}"