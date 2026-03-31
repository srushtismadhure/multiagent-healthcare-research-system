"""
scrape_web.py
Scrapes a target URL and returns clean plain text or structured content.
Used by subagents to pull content from cms.gov, kff.org, healthaffairs.org, etc.
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime


def scrape_url(url: str, timeout: int = 15) -> dict:
    """
    Fetches and parses a webpage.

    Returns:
        {
            "url": str,
            "title": str,
            "text": str,        # clean body text
            "fetched_at": str,  # ISO timestamp
            "status": int,
            "error": str | None
        }
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; HealthResearchBot/1.0; "
            "+https://github.com/your-org/health-researcher)"
        )
    }

    result = {
        "url": url,
        "title": "",
        "text": "",
        "fetched_at": datetime.utcnow().isoformat(),
        "status": None,
        "error": None,
    }

    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        result["status"] = resp.status_code
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Title
        title_tag = soup.find("title")
        result["title"] = title_tag.get_text(strip=True) if title_tag else ""

        # Remove nav, footer, scripts, styles
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        raw_text = soup.get_text(separator="\n")
        # Collapse whitespace
        lines = [line.strip() for line in raw_text.splitlines()]
        result["text"] = "\n".join(line for line in lines if line)

    except requests.RequestException as e:
        result["error"] = str(e)

    return result


def scrape_multiple(urls: list[str]) -> list[dict]:
    """Scrape a list of URLs sequentially. Swap for async if volume grows."""
    return [scrape_url(url) for url in urls]


if __name__ == "__main__":
    import sys
    import json

    target = sys.argv[1] if len(sys.argv) > 1 else "https://www.cms.gov/newsroom"
    data = scrape_url(target)
    print(json.dumps(data, indent=2))
