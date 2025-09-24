"""Simple RSS processing and article extraction."""

import logging
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict

# Configure logging
logger = logging.getLogger(__name__)


class RSSProcessor:
    """Simple RSS feed processor."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; Agentic Layer News Fetcher)'
        })

    def fetch_feed(self, feed_url: str, max_articles: int = 10, months_back: int = 3) -> List[Dict[str, str]]:
        """Fetch RSS feed and return list of articles from the last N months, limited to max_articles."""
        logger.info(f"EXTERNAL CALL: Fetching RSS feed from {feed_url} (max_articles={max_articles}, months_back={months_back})")
        try:
            feed = feedparser.parse(feed_url)
            logger.info(f"RSS FEED RESPONSE: Retrieved {len(feed.entries)} entries from {feed_url}")
            articles = []

            # Calculate cutoff date (2 months back)
            cutoff_date = datetime.now() - timedelta(days=months_back * 30)
            logger.info(f"Filtering articles newer than {cutoff_date.isoformat()}")

            filtered_count = 0
            for entry in feed.entries:
                # Convert time_struct to datetime (using first 6 elements: year, month, day, hour, minute, second)
                time_struct = entry.published_parsed
                article_date = datetime(*time_struct[:6])

                # Only include articles from the last 2 months
                if article_date >= cutoff_date:
                    articles.append({
                        'url': entry.link,
                        'title': entry.title,
                        'date_published': article_date.isoformat()
                    })
                else:
                    filtered_count += 1

                # Limit to max_articles per feed
                if len(articles) >= max_articles:
                    break

            logger.info(f"RSS PROCESSING COMPLETE: {feed_url} - {len(articles)} articles accepted, {filtered_count} filtered out by date")
            return articles
        except Exception as e:
            logger.error(f"ERROR fetching feed {feed_url}: {e}")
            return []

    def extract_article_content(self, article_url: str) -> str:
        """Extract article content by concatenating all <p> tags."""
        logger.info(f"EXTERNAL CALL: Extracting article content from {article_url}")
        try:
            response = self.session.get(article_url, timeout=10)
            response.raise_for_status()
            logger.info(f"HTTP RESPONSE: {response.status_code} from {article_url} (content-length: {len(response.content)} bytes)")

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract all paragraph text
            paragraphs = soup.find_all('p')
            content = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])

            logger.info(f"CONTENT EXTRACTION COMPLETE: {article_url} - extracted {len(content)} characters from {len(paragraphs)} paragraphs")
            return content
        except Exception as e:
            logger.error(f"ERROR extracting content from {article_url}: {e}")
            return ""

