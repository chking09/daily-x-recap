"""
Data Collector - API integrations for Google Custom Search and Finviz scraping
Handles external data collection from financial APIs and web scraping
"""

import logging
import time
from typing import List
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from finvizfinance.screener.overview import Overview
from finvizfinance.quote import finvizfinance

from models import NewsArticle, StockData
from config import (
    GOOGLE_SEARCH_API_KEY, 
    GOOGLE_SEARCH_CX, 
    GOOGLE_SEARCH_QUERIES,
    SEARCH_DATE_RESTRICT,
    MAX_SEARCH_RESULTS,
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
            logging.info("Searching for: %s", query)
            
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
                    
                logging.info("Found %d articles for query: %s", len(search_results['items']), query)
            else:
                logging.warning("No results found for query: %s", query)
    
    except HttpError as e:
        logging.error("Google Custom Search API error: %s", e)
        raise
    except Exception as e:
        logging.error("Unexpected error collecting market news: %s", e)
        raise
    
    # Remove duplicates based on URL
    unique_articles = []
    seen_urls = set()
    for article in news_articles:
        if article.url not in seen_urls:
            unique_articles.append(article)
            seen_urls.add(article.url)
    
    logging.info("Collected %d unique news articles", len(unique_articles))
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
                logging.error("Google Search API failed after %d attempts: %s", MAX_RETRIES, e)
                raise
            
            # Exponential backoff
            delay = RETRY_DELAY_BASE ** attempt
            logging.warning("Google Search API attempt %d failed, retrying in %ds: %s", attempt + 1, delay, e)
            time.sleep(delay)
        
        except Exception as e:
            logging.error("Unexpected error in Google Search API call: %s", e)
            raise

def get_stock_movers() -> List[StockData]:
    """
    Get top 3 stock movers using Finviz screener
    
    Returns:
        List of StockData objects for stocks with significant price movements
    """
    logging.info("Collecting stock movers from Finviz")
    
    try:
        # Get top gainers using finvizfinance screener
        foverview = Overview()
        filters_dict = {'Market Cap.': '+Mid (over $2bln)'}  # Filter by market cap > $2B
        foverview.set_filter(filters_dict=filters_dict)
        
        # Get screener data
        gainers_df = foverview.screener_view(order='Change')
        
        stock_movers = []
        
        # Process top gainers and losers
        if not gainers_df.empty:
            # Sort by absolute change percentage and take top movers
            gainers_df['Change_Abs'] = gainers_df['Change'].abs()
            top_movers_df = gainers_df.nlargest(STOCK_MOVERS_COUNT, 'Change_Abs')
            
            for _, row in top_movers_df.iterrows():
                try:
                    # Parse market cap
                    market_cap_str = row.get('Market Cap', '0')
                    market_cap = _parse_market_cap(market_cap_str)
                    
                    # Parse price change
                    change_percent = float(row['Change'])
                    
                    # Create StockData object
                    stock_data = StockData(
                        symbol=row['Ticker'],
                        company_name=row['Company'],
                        current_price=float(row['Price']),
                        price_change_percent=change_percent,
                        market_cap=market_cap,
                        reason=_generate_movement_reason(row['Ticker'], change_percent)
                    )
                    
                    stock_movers.append(stock_data)
                    logging.info("Added stock mover: %s (%.1f%%)", row['Ticker'], change_percent)
                    
                except (ValueError, KeyError) as e:
                    logging.warning("Failed to process stock %s: %s", row.get('Ticker', 'Unknown'), e)
                    continue
        
        logging.info("Collected %d stock movers", len(stock_movers))
        return stock_movers
        
    except Exception as e:
        logging.error("Error collecting stock movers: %s", e)
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
                # Get stock data from Finviz using quote
                stock = finvizfinance(symbol)
                stock_data = _get_finviz_stock_data(stock)
                
                if stock_data and stock_data.market_cap >= MIN_MARKET_CAP:
                    # Update the reason for watching
                    stock_data.reason = watch_reason
                    watchlist_stocks.append(stock_data)
                    
                    logging.info("Added to watchlist: %s - %s", symbol, watch_reason)
                    
                    # Stop once we have enough stocks
                    if len(watchlist_stocks) >= WATCHLIST_STOCKS_COUNT:
                        break
                
                # Rate limiting to be respectful to Finviz
                time.sleep(1)
                
            except Exception as e:
                logging.warning("Failed to get data for %s: %s", symbol, e)
                continue
    
    except Exception as e:
        logging.error("Error collecting watchlist stocks: %s", e)
        raise
    
    logging.info("Collected %d watchlist stocks", len(watchlist_stocks))
    return watchlist_stocks



def _get_finviz_stock_data(stock_quote) -> StockData:
    """
    Extract stock data from finvizfinance quote object
    
    Args:
        stock_quote: finvizfinance quote object
        
    Returns:
        StockData object with extracted information
    """
    try:
        # Get fundamental data
        fundamentals = stock_quote.ticker_fundament()
        
        # Extract required fields
        symbol = fundamentals.get('Ticker', '')
        company_name = fundamentals.get('Company', '')
        price_str = fundamentals.get('Price', '0')
        change_str = fundamentals.get('Change', '0%')
        market_cap_str = fundamentals.get('Market Cap', '0')
        
        # Parse numeric values
        current_price = float(price_str) if price_str != '-' else 0.0
        price_change_percent = float(change_str.rstrip('%')) if change_str != '-' else 0.0
        market_cap = _parse_market_cap(market_cap_str)
        
        return StockData(
            symbol=symbol,
            company_name=company_name,
            current_price=current_price,
            price_change_percent=price_change_percent,
            market_cap=market_cap,
            reason=""  # Will be set by calling function
        )
        
    except (ValueError, KeyError) as e:
        logging.error("Failed to parse stock data: %s", e)
        return None


def _parse_market_cap(market_cap_input) -> float:
    """
    Parse market cap string or float to numeric value in dollars
    
    Args:
        market_cap_input: Market cap string like "2.5B" or "500M", or float value
        
    Returns:
        Market cap as float in dollars
    """
    if not market_cap_input or market_cap_input == '-':
        return 0.0
    
    # If already a float, return as is (assuming it's already in correct units)
    if isinstance(market_cap_input, (int, float)):
        return float(market_cap_input)
    
    try:
        # Remove any non-numeric characters except B, M, K
        clean_str = str(market_cap_input).replace('$', '').replace(',', '').strip()
        
        if clean_str.endswith('B'):
            return float(clean_str[:-1]) * 1_000_000_000
        elif clean_str.endswith('M'):
            return float(clean_str[:-1]) * 1_000_000
        elif clean_str.endswith('K'):
            return float(clean_str[:-1]) * 1_000
        else:
            return float(clean_str)
            
    except (ValueError, IndexError):
        logging.warning("Could not parse market cap: %s", market_cap_input)
        return 0.0


def _generate_movement_reason(symbol: str, change_percent: float) -> str:
    """
    Generate a simple reason for stock movement
    
    Args:
        symbol: Stock symbol (for future use in more sophisticated reasoning)
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
    # Use first reason for simplicity (could use symbol for more sophisticated reasoning later)
    base_reason = generic_reasons[reason_type][0]
    
    return "Stock %s %.1f%% on %s" % (direction, abs(change_percent), base_reason)