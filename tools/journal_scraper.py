"""
journal_scraper.py
Fetches recent publications from open-access journal homepages and APIs.

Targets open-access content only:
  - PLOS Medicine (fully open access, has API)
  - JAMA Network Open (fully open access)
  - Nature open-access articles
  - The Lancet open-access section
  - medRxiv preprints (health sciences)
  - bioRxiv preprints (life sciences)

Note: Results from medRxiv/bioRxiv are preprints — always flagged as NOT peer-reviewed.
"""

import time
import logging
import requests
from datetime import datetime
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

REQUEST_DELAY = 1.0  # seconds between requests — be polite

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; HealthResearchBot/1.0; "
        "+https://github.com/your-org/health-researcher)"
    )
}


def _get(url: str, params: dict = None) -> requests.Response | None:
    """GET with delay and error handling."""
    time.sleep(REQUEST_DELAY)
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=20)
        resp.raise_for_status()
        return resp
    except requests.RequestException as e:
        logger.error(f"Request failed for {url}: {e}")
        return None


# ---------------------------------------------------------------------------
# PLOS Medicine — has a public API (search.plos.org)
# ---------------------------------------------------------------------------

def fetch_plos_medicine(search_term: str, max_results: int = 10) -> list[dict]:
    """
    Fetch articles from PLOS Medicine via the PLOS search API.
    All PLOS content is open access.
    """
    url = "https://api.plos.org/search"
    params = {
        "q": f"everything:{search_term} AND journal_key:PLoSMedicine",
        "fl": "id,title,author,publication_date,abstract,journal",
        "rows": max_results,
        "wt": "json",
    }

    resp = _get(url, params=params)
    if not resp:
        return []

    docs = resp.json().get("response", {}).get("docs", [])
    results = []
    for doc in docs:
        doi = doc.get("id", "")
        results.append({
            "title": doc.get("title", [""])[0] if isinstance(doc.get("title"), list) else doc.get("title", ""),
            "authors": ", ".join(doc.get("author", [])[:3]) + (" et al." if len(doc.get("author", [])) > 3 else ""),
            "pub_date": doc.get("publication_date", "")[:10],
            "abstract": (doc.get("abstract", [""])[0] if isinstance(doc.get("abstract"), list) else doc.get("abstract", ""))[:500],
            "url": f"https://doi.org/{doi}" if doi else "",
            "journal": "PLOS Medicine",
            "is_preprint": False,
        })
    return results


# ---------------------------------------------------------------------------
# medRxiv — preprint server, has an API
# ---------------------------------------------------------------------------

def fetch_medrxiv(search_term: str, max_results: int = 10) -> list[dict]:
    """
    Fetch preprints from medRxiv via their API.
    All results are PREPRINTS — not peer-reviewed.
    """
    # medRxiv search API: https://api.biorxiv.org/details/medrxiv/
    # For search, we use their full-text search endpoint
    url = "https://api.biorxiv.org/pubs/medrxiv/0/100"
    resp = _get(url)
    if not resp:
        return []

    # medRxiv doesn't have a keyword search API — use their search page scrape instead
    search_url = f"https://www.medrxiv.org/search/{requests.utils.quote(search_term)}"
    resp = _get(search_url)
    if not resp:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    articles = soup.select("article.highwire-article")[:max_results]

    results = []
    for article in articles:
        title_el = article.select_one(".highwire-cite-title")
        authors_el = article.select_one(".highwire-citation-authors")
        date_el = article.select_one(".highwire-cite-metadata-date")
        link_el = article.select_one("a.highwire-cite-linked-title")

        title = title_el.get_text(strip=True) if title_el else ""
        authors = authors_el.get_text(strip=True)[:100] if authors_el else ""
        pub_date = date_el.get_text(strip=True) if date_el else ""
        href = link_el.get("href", "") if link_el else ""
        url = f"https://www.medrxiv.org{href}" if href.startswith("/") else href

        if title:
            results.append({
                "title": title,
                "authors": authors,
                "pub_date": pub_date,
                "abstract": "",
                "url": url,
                "journal": "medRxiv",
                "is_preprint": True,
            })

    return results


# ---------------------------------------------------------------------------
# JAMA Network Open — open access, HTML scrape
# ---------------------------------------------------------------------------

def fetch_jama_network_open(search_term: str, max_results: int = 10) -> list[dict]:
    """
    Fetch articles from JAMA Network Open via their search page.
    JAMA Network Open is fully open access.
    """
    search_url = "https://jamanetwork.com/searchresults"
    params = {
        "q": search_term,
        "allJournals": "0",
        "journalFilter": "jamanetworkopen",
        "restrictedResults": "openAccess",
    }

    resp = _get(search_url, params=params)
    if not resp:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    items = soup.select(".search-result-item")[:max_results]

    results = []
    for item in items:
        title_el = item.select_one(".search-result-title a")
        authors_el = item.select_one(".search-result-authors")
        date_el = item.select_one(".search-result-date")

        title = title_el.get_text(strip=True) if title_el else ""
        href = title_el.get("href", "") if title_el else ""
        url = f"https://jamanetwork.com{href}" if href.startswith("/") else href
        authors = authors_el.get_text(strip=True)[:100] if authors_el else ""
        pub_date = date_el.get_text(strip=True) if date_el else ""

        if title:
            results.append({
                "title": title,
                "authors": authors,
                "pub_date": pub_date,
                "abstract": "",
                "url": url,
                "journal": "JAMA Network Open",
                "is_preprint": False,
            })

    return results


# ---------------------------------------------------------------------------
# Dispatcher — fetch from any supported journal
# ---------------------------------------------------------------------------

SUPPORTED_JOURNALS = {
    "plos_medicine": fetch_plos_medicine,
    "medrxiv": fetch_medrxiv,
    "jama_network_open": fetch_jama_network_open,
}


def fetch_from_journal(journal_name: str, search_term: str, max_results: int = 10) -> list[dict]:
    """
    Fetch recent publications from a named journal source.

    Args:
        journal_name: One of: 'plos_medicine', 'medrxiv', 'jama_network_open'
        search_term: Keyword(s) to search for
        max_results: Max articles to return

    Returns:
        List of dicts: {title, authors, pub_date, abstract, url, journal, is_preprint}
    """
    fetcher = SUPPORTED_JOURNALS.get(journal_name.lower())
    if not fetcher:
        logger.warning(f"Unsupported journal: {journal_name}. Supported: {list(SUPPORTED_JOURNALS.keys())}")
        return []

    logger.info(f"Fetching from {journal_name}: '{search_term}'")
    return fetcher(search_term, max_results)


def fetch_all_journals(search_term: str, max_per_journal: int = 5) -> list[dict]:
    """
    Fetch from all supported open-access journals and return combined results.

    Args:
        search_term: Keyword(s) to search across all journals
        max_per_journal: Max articles per journal

    Returns:
        Combined list of article dicts, with is_preprint flag set correctly
    """
    all_results = []
    for journal_name in SUPPORTED_JOURNALS:
        results = fetch_from_journal(journal_name, search_term, max_per_journal)
        all_results.extend(results)
        logger.info(f"{journal_name}: {len(results)} results")

    return all_results


if __name__ == "__main__":
    import sys
    import json

    term = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "women's health outcomes"
    results = fetch_all_journals(term, max_per_journal=3)
    print(json.dumps(results, indent=2))
