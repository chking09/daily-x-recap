"""
Content Generator - Claude AI integration for market recap content creation
Transforms structured data into engaging, educational content
"""

import logging
from typing import List
from anthropic import Anthropic
from models import NewsArticle, StockData
from config import CLAUDE_API_KEY, MAX_TWEET_LENGTH


def generate_recap(news_articles: List[NewsArticle], stock_movers: List[StockData],
                   watchlist_stocks: List[StockData]) -> str:
    """
    Generate witty, educational market recap content using Claude AI

    Args:
        news_articles: List of NewsArticle objects
        stock_movers: List of StockData objects for significant movers
        watchlist_stocks: List of StockData objects for stocks to watch

    Returns:
        Formatted content string ready for X platform posting
    """
    logging.info("Generating market recap content with Claude AI")

    if not CLAUDE_API_KEY:
        raise ValueError("CLAUDE_API_KEY not found in environment variables")

    try:
        # Initialize Anthropic client
        client = Anthropic(api_key=CLAUDE_API_KEY)

        # Prepare structured data for Claude
        news_summary = _format_news_for_prompt(news_articles)
        movers_summary = _format_stocks_for_prompt(stock_movers, "movers")
        watchlist_summary = _format_stocks_for_prompt(watchlist_stocks, "watchlist")

        # Create the prompt for Claude
        prompt = _create_content_prompt(news_summary, movers_summary, watchlist_summary)

        # Generate content using Claude
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            temperature=0.7,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        generated_content = response.content[0].text.strip()

        # Validate content length for X platform
        if len(generated_content) > MAX_TWEET_LENGTH:
            logging.warning("Generated content exceeds X character limit (%d chars), "
                          "attempting regeneration", len(generated_content))
            # Try to regenerate with stricter length requirement
            strict_prompt = _create_strict_length_prompt(news_summary, movers_summary,
                                                       watchlist_summary)
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                temperature=0.5,
                messages=[
                    {
                        "role": "user",
                        "content": strict_prompt
                    }
                ]
            )
            generated_content = response.content[0].text.strip()

            # If still too long, truncate intelligently
            if len(generated_content) > MAX_TWEET_LENGTH:
                logging.warning("Regenerated content still too long, truncating")
                generated_content = _truncate_content(generated_content)

        logging.info("Successfully generated market recap content (%d characters)",
                    len(generated_content))
        return generated_content

    except Exception as e:
        logging.error("Failed to generate content with Claude AI: %s", str(e))
        raise


def _format_news_for_prompt(news_articles: List[NewsArticle]) -> str:
    """Format news articles for inclusion in Claude prompt"""
    if not news_articles:
        return "No significant market news available today."
    
    news_items = []
    for article in news_articles[:3]:  # Limit to top 3 articles
        news_items.append(f"- {article.title}: {article.snippet}")
    
    return "\n".join(news_items)


def _format_stocks_for_prompt(stocks: List[StockData], stock_type: str) -> str:
    """Format stock data for inclusion in Claude prompt"""
    if not stocks:
        return f"No {stock_type} data available."

    stock_items = []
    for stock in stocks:
        if stock_type == "movers":
            stock_items.append(
                f"- {stock.symbol} ({stock.company_name}): "
                f"{stock.price_change_percent:+.1f}% to ${stock.current_price:.2f}. "
                f"Reason: {stock.reason}"
            )
        else:  # watchlist
            stock_items.append(
                f"- {stock.symbol} ({stock.company_name}): ${stock.current_price:.2f}. "
                f"Watch because: {stock.reason}"
            )

    return "\n".join(stock_items)


def _create_strict_length_prompt(news_summary: str, movers_summary: str,
                               watchlist_summary: str) -> str:
    """Create a strict prompt for very short content generation"""
    return f"""Write a market recap in EXACTLY 200 characters or less. Include:
- 1 sentence on market news
- Top stock movers: mention 2-3 symbols with % change
- Watchlist: mention 1-2 symbols to watch

Data:
NEWS: {news_summary[:100]}...
MOVERS: {movers_summary[:150]}...
WATCHLIST: {watchlist_summary[:100]}...

Be witty but extremely concise. Every character counts. No hashtags."""


def _create_content_prompt(news_summary: str, movers_summary: str,
                          watchlist_summary: str) -> str:
    """Create the prompt for Claude AI content generation"""
    return f"""You are a witty, educational financial content creator writing a daily \
market recap for beginner/intermediate investors. Your goal is to make complex market \
information accessible and engaging.

MARKET NEWS TODAY:
{news_summary}

TOP 3 STOCK MOVERS:
{movers_summary}

TOP 3 STOCKS TO WATCH:
{watchlist_summary}

Create a VERY concise, engaging market recap that:
1. Summarizes the key market news in 1-2 sentences
2. Mentions the top stock movers with brief context
3. Mentions watchlist stocks worth monitoring
4. Uses a witty, conversational tone while remaining informative
5. MUST stay under 250 characters total (this is critical)
6. Avoids giving specific financial advice
7. Uses accessible language that beginners can understand

Format as a single cohesive X/Twitter post. Be extremely concise - every word counts. \
Think "market summary in a nutshell" not detailed analysis."""


def _truncate_content(content: str) -> str:
    """Truncate content to fit X character limits while preserving meaning"""
    if len(content) <= MAX_TWEET_LENGTH:
        return content
    
    # Find the last complete sentence that fits
    sentences = content.split('. ')
    truncated = ""
    
    for sentence in sentences:
        test_content = truncated + sentence + ". "
        if len(test_content) <= MAX_TWEET_LENGTH - 3:  # Leave room for "..."
            truncated = test_content
        else:
            break
    
    # If no complete sentences fit, truncate at word boundary
    if not truncated:
        words = content.split()
        truncated = ""
        for word in words:
            test_content = truncated + word + " "
            if len(test_content) <= MAX_TWEET_LENGTH - 3:
                truncated = test_content
            else:
                break
    
    return truncated.strip() + "..."