# Learned Constraints — Memory Store

**Purpose:** Auto-log for rate limit hits, API errors, and tool-level constraints discovered during research runs. Written to by tools automatically (e.g., pubmed_fetcher.py logs rate limit hits here).

---

## NCBI / PubMed Rate Limits

- **Unauthenticated:** 3 requests/second
- **With API key:** 10 requests/second (free — register at https://www.ncbi.nlm.nih.gov/account/)
- **Current key status:** Not configured (add `NCBI_API_KEY` to `.env` to raise limit)

### Rate Limit Events
*(Auto-populated by tools/pubmed_fetcher.py)*

---

## Journal Scraper Constraints

| Journal | Constraint | Discovered |
|---------|-----------|-----------|
| *(populate after first run)* | | |

---

## General API Constraints

| Tool | API/Source | Limit | Notes |
|------|-----------|-------|-------|
| search_news.py | NewsAPI | 100 req/day (free tier) | Upgrade for higher volume |
| search_reddit.py | PRAW/Reddit | 60 req/min | Respect per-subreddit limits |
| pubmed_fetcher.py | NCBI E-utilities | 3 req/sec (no key) | Add NCBI_API_KEY to increase |
| journal_scraper.py | Various HTML | Polite crawl (1 req/sec) | Aggressive scraping may trigger blocks |
| log_to_sheets.py | Google Sheets API | 100 req/100 sec | Batch writes when possible |

---

## Self-Improvement Log

When a tool fails or a constraint is hit, the relevant tool writes a timestamped entry below. Review this before runs to avoid known failure modes.

*(Auto-populated by tools)*
