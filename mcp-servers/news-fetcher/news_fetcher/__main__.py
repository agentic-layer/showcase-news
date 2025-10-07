import logging

import requests
from bs4 import BeautifulSoup
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

from .rss_processor import RSSProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server
mcp = FastMCP(name="News Fetcher")

# Initialize processor
rss_processor = RSSProcessor()

# RSS Feeds to monitor
RSS_FEEDS = [
    "https://openai.com/blog/rss.xml",
    "https://www.artificialintelligence-news.com/feed/rss/",
    "https://venturebeat.com/category/ai/feed/",
    "https://ainowinstitute.org/category/news/feed",
]


@mcp.tool()
def fetch_article_titles_and_urls() -> str:
    """
    Fetch recent article titles and URLs from all RSS feeds.

    Returns articles from the last 3 months, limited to 10 articles per feed.

    Returns:
        str: Formatted list of article titles with URLs
    """
    logger.info("MCP TOOL CALLED: fetch_article_titles_and_urls")

    all_articles = []
    total_feeds_processed = 0

    for feed_url in RSS_FEEDS:
        try:
            logger.info(f"Processing RSS feed: {feed_url}")
            # Fetch articles from last 3 months, max 10 per feed
            articles = rss_processor.fetch_feed(feed_url, max_articles=10, months_back=3)

            for article in articles:
                all_articles.append({
                    'title': article['title'],
                    'url': article['url'],
                    'date': article['date_published'],
                    'feed': feed_url
                })

            total_feeds_processed += 1
            logger.info(f"Retrieved {len(articles)} articles from {feed_url}")

        except Exception as e:
            logger.error(f"Error processing feed {feed_url}: {e}")

    if not all_articles:
        result = "No recent articles found"
        logger.info("No articles found from any feed")
        return result

    # Sort articles by date (newest first)
    all_articles.sort(key=lambda x: x['date'], reverse=True)

    # Format response
    result = f"Found {len(all_articles)} recent articles from {total_feeds_processed} feeds:\\n\\n"

    for i, article in enumerate(all_articles[:50], 1):  # Limit to 50 total articles
        result += f"{i}. {article['title']}\\n"
        result += f"   URL: {article['url']}\\n"
        result += f"   Date: {article['date']}\\n"
        result += f"\\n"

    logger.info(f"MCP TOOL RESPONSE: fetch_article_titles_and_urls returned {len(all_articles)} articles")
    return result


@mcp.tool()
def extract_article_content(article_url: str) -> str:
    """
    Extract main content from the given article URL.

    Returns:
        str: Formatted list of article titles with URLs
    """
    logger.info(f"Extracting content from: {article_url}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; Agentic Layer News Fetcher)'
        }
        response = requests.get(article_url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()

        # Extract text from paragraphs
        paragraphs = soup.find_all(['p', 'article', 'div'])
        content_parts = []

        for p in paragraphs:
            text = p.get_text().strip()
            if len(text) > 50:  # Only include substantial paragraphs
                content_parts.append(text)

        content = ' '.join(content_parts)
        return content[:3000]  # Limit content to 3000 chars for summarization

    except Exception as e:
        logger.error(f"Error extracting content from {article_url}: {e}")
        return f"Could not extract content from the article URL: {str(e)}"

@mcp.custom_route("/health", methods=["GET"])
async def health_check(_: Request) -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse({"status": "healthy"})



def main():
    """Run the MCP server."""
    logger.info("Starting simplified News RSS MCP server with streamable-http transport")
    mcp.run(transport="streamable-http", host="0.0.0.0")


if __name__ == "__main__":
    main()
