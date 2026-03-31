# Research Sources — Memory Store

**Purpose:** Track which PubMed search terms return high-quality results, which research sources are currently automated vs future/unsupported, rate-limit history, and source-specific notes for the Research & Clinical Evidence bucket.

---

## PubMed Search Query Performance

Track which queries return high signal-to-noise results. Update after each run.

| Query | Quality | Notes | Last Run |
|-------|---------|-------|---------|
| `AI clinical validation` | TBD | Returns mix of hype and real studies — filter by journal tier | — |
| `women's health outcomes study` | TBD | Broad; add MeSH terms to narrow | — |
| `chronic pain management evidence` | TBD | — | — |
| `digital health effectiveness randomized controlled trial` | TBD | Adding "randomized controlled trial" significantly improves signal | — |
| `healthcare AI clinical trial` | TBD | — | — |

**Quality scale:** High (mostly relevant, Tier 1 journals) | Medium (mixed) | Low (noisy, mostly irrelevant)

---

## Research Source Automation Status

| Source | Current Automation Status | Access | Notes |
|--------|---------------------------|--------|-------|
| PubMed | Supported | Open | Primary automated research source via `pubmed_fetcher.py` |
| PLOS Medicine | Supported | Open Access | Available via `journal_scraper.py` |
| JAMA Network Open | Supported | Open Access | Available via `journal_scraper.py` |
| medRxiv | Supported | Open Access (Preprints) | Available via `journal_scraper.py`; flag all results as PREPRINT |
| bioRxiv | Future / Unsupported | Open Access (Preprints) | Not currently automated by the tool layer |
| NEJM | Future / Unsupported | Paywalled | Not currently automated by the tool layer |
| Health Affairs | Future / Unsupported | Paywalled | Not currently automated by the tool layer |
| The Lancet | Future / Unsupported | Mixed | Not currently automated by the tool layer |
| Nature | Future / Unsupported | Mixed | Not currently automated by the tool layer |
| ClinicalTrials.gov | Future / Unsupported | Open | No current tool exists in this repo |

---

## NCBI / PubMed Rate Limit Log

NCBI allows **3 requests/second** without an API key, **10/second** with one (free to register).
Register at: https://www.ncbi.nlm.nih.gov/account/

| Timestamp | Query | Action Taken |
|-----------|-------|-------------|
| *(populate after first run)* | | |

**To get an NCBI API key:** Register at https://www.ncbi.nlm.nih.gov/account/ → API Key Management.
Add to `.env` as `NCBI_API_KEY`.

---

## Common Retraction and Correction Patterns

| Pattern | How to Detect | Action |
|---------|--------------|--------|
| PubMed retraction notice | Check `PublicationTypeList` for "Retracted Publication" | Flag [RETRACTED], do not cite as evidence |
| Expression of concern | Check `PublicationTypeList` for "Published Erratum" | Flag [UNDER CONCERN] |
| Preprint superseded by peer-reviewed version | Same title appears in both medRxiv and a journal | Use peer-reviewed version; drop preprint |
| Fraudulent authorship | Often flagged in PubMed comments/notes field | Flag and exclude |

---

## Search Term Learnings

*(Populate after first few runs)*

### Terms That Improve Signal
- Adding "randomized controlled trial" to any query significantly improves study quality
- Adding "systematic review" or "meta-analysis" filters for higher-evidence studies
- MeSH terms outperform free-text for clinical topics (e.g., `"Women's Health"[MeSH]`)

### Terms That Return Noise
*(Populate after first runs)*

### Source-Specific Tips
- PLOS Medicine API returns the richest metadata among the currently supported journal tools
- medRxiv HTML structure changes periodically — update scraper if results drop to 0
- JAMA Network Open search page requires specific URL params — verify after each run
- Treat future/unsupported sources as manual follow-up targets, not active automated coverage
