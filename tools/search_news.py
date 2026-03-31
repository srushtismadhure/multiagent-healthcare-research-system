"""
search_news.py
Queries the NewsAPI (newsapi.org) for recent healthcare articles.
Returns structured results ready for subagent consumption.
"""

import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = "https://newsapi.org/v2/everything"


def search_news(
    query: str,
    days_back: int = 7,
    language: str = "en",
    sort_by: str = "publishedAt",
    page_size: int = 20,
) -> list[dict]:
    """
    Search recent news articles for a given query.

    Returns list of:
        {
            "title": str,
            "source": str,
            "published_at": str,
            "url": str,
            "description": str
        }
    """
    if not NEWS_API_KEY:
        raise EnvironmentError("NEWS_API_KEY not set in .env")

    from_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")

    params = {
        "q": query,
        "from": from_date,
        "language": language,
        "sortBy": sort_by,
        "pageSize": page_size,
        "apiKey": NEWS_API_KEY,
    }

    resp = requests.get(BASE_URL, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    articles = []
    for item in data.get("articles", []):
        articles.append(
            {
                "title": item.get("title", ""),
                "source": item.get("source", {}).get("name", ""),
                "published_at": item.get("publishedAt", ""),
                "url": item.get("url", ""),
                "description": item.get("description", ""),
            }
        )

    return articles


if __name__ == "__main__":
    import sys
    import json

    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "CMS healthcare policy"
    results = search_news(q)
    print(json.dumps(results, indent=2))
