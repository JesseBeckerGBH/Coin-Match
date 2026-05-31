"""Reddit Scraper for Estate Seller Detection.

This script searches specific subreddits for keywords indicating someone has
inherited a coin collection and is looking to sell.
"""

import httpx
import logging
import asyncio
from typing import List, Dict
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUBREDDITS = ["coins", "coincollecting", "personalfinance", "EstatePlanning"]
KEYWORDS = [
    "inherited", "dad's collection", "grandpa's coins", 
    "mom passed away", "found in attic", "probate", 
    "don't know what it's worth", "how to sell coins"
]

class RedditEstateScraper:
    def __init__(self):
        self.client = httpx.AsyncClient(
            headers={"User-Agent": "CoinMatchEstateScraper/1.0"},
            timeout=10.0
        )

    async def search_reddit(self, subreddit: str, query: str) -> List[Dict]:
        """Search a subreddit for a query using the JSON API."""
        url = f"https://www.reddit.com/r/{subreddit}/search.json"
        params = {
            "q": query,
            "restrict_sr": "on",
            "sort": "new",
            "t": "week"
        }
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            posts = []
            for child in data.get("data", {}).get("children", []):
                post_data = child.get("data", {})
                posts.append({
                    "id": post_data.get("id"),
                    "title": post_data.get("title"),
                    "author": post_data.get("author"),
                    "url": f"https://reddit.com{post_data.get('permalink')}",
                    "content": post_data.get("selftext"),
                    "created_utc": post_data.get("created_utc"),
                    "subreddit": subreddit
                })
            return posts
        except Exception as e:
            logger.error(f"Error searching r/{subreddit} for '{query}': {e}")
            return []

    async def run_scan(self) -> List[Dict]:
        """Run a full scan across all target subreddits and keywords."""
        all_leads = []
        for subreddit in SUBREDDITS:
            for keyword in KEYWORDS:
                logger.info(f"Scanning r/{subreddit} for '{keyword}'...")
                leads = await self.search_reddit(subreddit, keyword)
                all_leads.extend(leads)
                await asyncio.sleep(1)  # Rate limit courtesy
        
        # Deduplicate by ID
        unique_leads = {lead["id"]: lead for lead in all_leads}.values()
        return list(unique_leads)

async def main():
    scraper = RedditEstateScraper()
    leads = await scraper.run_scan()
    logger.info(f"Found {len(leads)} potential estate leads.")
    for lead in leads:
        print(f"- {lead['title']} ({lead['url']})")

if __name__ == "__main__":
    asyncio.run(main())
