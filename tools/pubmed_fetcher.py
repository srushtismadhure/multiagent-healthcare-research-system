"""
pubmed_fetcher.py
Fetches study metadata from PubMed using the free NCBI E-utilities API.

Rate limit: 3 requests per second (NCBI guideline for unauthenticated requests).
With an API key (free from NCBI), the limit rises to 10 req/sec.

NCBI E-utilities docs: https://www.ncbi.nlm.nih.gov/books/NBK25497/
"""

import os
import time
import logging
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

NCBI_API_KEY = os.getenv("NCBI_API_KEY", "")  # Optional — raises rate limit to 10/sec
BASE_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
BASE_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
BASE_SUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

RATE_LIMIT_DELAY = 0.34  # seconds between requests (~3/sec)
MEMORY_LOG = Path(__file__).parent.parent / "memory" / "learned_constraints.md"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def _log_rate_limit_hit(query: str) -> None:
    """Appends a rate-limit event to memory/learned_constraints.md."""
    timestamp = datetime.utcnow().isoformat()
    entry = f"\n- [{timestamp}] NCBI rate limit hit on query: `{query}`\n"
    try:
        with open(MEMORY_LOG, "a") as f:
            f.write(entry)
    except Exception as e:
        logger.warning(f"Could not write to learned_constraints.md: {e}")


def _build_params(extra: dict) -> dict:
    params = {"retmode": "json", "db": "pubmed"}
    if NCBI_API_KEY:
        params["api_key"] = NCBI_API_KEY
    params.update(extra)
    return params


def search_pubmed(query: str, max_results: int = 10) -> list[str]:
    """
    Search PubMed for a query and return a list of PMIDs.

    Args:
        query: Search string (e.g., "AI clinical validation")
        max_results: Maximum number of PMIDs to return

    Returns:
        List of PMID strings
    """
    params = _build_params({
        "term": query,
        "retmax": max_results,
        "sort": "date",
    })

    try:
        time.sleep(RATE_LIMIT_DELAY)
        resp = requests.get(BASE_SEARCH_URL, params=params, timeout=15)

        if resp.status_code == 429:
            logger.warning(f"Rate limit hit for query: {query}")
            _log_rate_limit_hit(query)
            time.sleep(2)
            resp = requests.get(BASE_SEARCH_URL, params=params, timeout=15)

        resp.raise_for_status()
        data = resp.json()
        return data.get("esearchresult", {}).get("idlist", [])

    except requests.RequestException as e:
        logger.error(f"PubMed search failed for '{query}': {e}")
        return []


def fetch_summaries(pmids: list[str]) -> list[dict]:
    """
    Fetch metadata summaries for a list of PMIDs.

    Args:
        pmids: List of PubMed IDs

    Returns:
        List of dicts: {pmid, title, authors, pub_date, abstract_summary, journal, url}
    """
    if not pmids:
        return []

    params = _build_params({
        "id": ",".join(pmids),
        "retmax": len(pmids),
    })

    try:
        time.sleep(RATE_LIMIT_DELAY)
        resp = requests.get(BASE_SUMMARY_URL, params=params, timeout=15)

        if resp.status_code == 429:
            logger.warning("Rate limit hit during summary fetch")
            _log_rate_limit_hit(f"summary fetch for {len(pmids)} PMIDs")
            time.sleep(2)
            resp = requests.get(BASE_SUMMARY_URL, params=params, timeout=15)

        resp.raise_for_status()
        data = resp.json()

        results = []
        uids = data.get("result", {}).get("uids", [])

        for uid in uids:
            item = data["result"].get(uid, {})
            authors = [a.get("name", "") for a in item.get("authors", [])]
            author_str = authors[0] + " et al." if len(authors) > 1 else (authors[0] if authors else "")

            results.append({
                "pmid": uid,
                "title": item.get("title", ""),
                "authors": author_str,
                "pub_date": item.get("pubdate", ""),
                "abstract_summary": item.get("source", ""),  # summary endpoint gives source, not abstract
                "journal": item.get("fulljournalname", item.get("source", "")),
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{uid}/",
            })

        return results

    except requests.RequestException as e:
        logger.error(f"PubMed summary fetch failed: {e}")
        return []


def fetch_studies(query: str, max_results: int = 10) -> list[dict]:
    """
    Full pipeline: search PubMed and return structured study metadata.

    Args:
        query: Search string
        max_results: Maximum number of studies to return

    Returns:
        List of dicts with {pmid, title, authors, pub_date, abstract_summary, journal, url}
    """
    logger.info(f"Searching PubMed: '{query}' (max {max_results})")
    pmids = search_pubmed(query, max_results)
    logger.info(f"Found {len(pmids)} PMIDs")

    if not pmids:
        return []

    return fetch_summaries(pmids)


def fetch_multiple_queries(queries: list[str], max_per_query: int = 5) -> list[dict]:
    """
    Run multiple search queries and return deduplicated results.

    Args:
        queries: List of search strings
        max_per_query: Max results per query

    Returns:
        Deduplicated list of study dicts
    """
    seen_pmids = set()
    all_results = []

    for query in queries:
        results = fetch_studies(query, max_per_query)
        for result in results:
            if result["pmid"] not in seen_pmids:
                seen_pmids.add(result["pmid"])
                all_results.append(result)

    logger.info(f"Total unique studies across {len(queries)} queries: {len(all_results)}")
    return all_results


if __name__ == "__main__":
    import sys
    import json

    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "women's health outcomes study"
    results = fetch_studies(query, max_results=5)
    print(json.dumps(results, indent=2))
