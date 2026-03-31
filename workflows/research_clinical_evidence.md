# Research & Clinical Evidence — Research Workflow SOP

**Bucket:** Research & Clinical Evidence  
**Agent:** `agents/research_clinical_evidence_agent.md`  
**Run frequency:** Weekly (or on-demand)

---

## Objective

Find high-signal clinical studies and evidence updates relevant to healthcare policy, care delivery, women's health, chronic pain, AI in clinical settings, and digital health effectiveness. Use only the sources and fields the current tool layer supports, and be explicit when only limited metadata is available.

---

## Search Queries

1. `healthcare AI clinical trial`
2. `women's health outcomes study`
3. `chronic pain management evidence`
4. `digital health effectiveness randomized controlled trial`
5. `AI clinical validation`
6. `FemTech clinical outcomes`
7. `payment model patient outcomes`
8. `ambient clinical documentation accuracy`
9. `maternal health intervention systematic review`
10. `prior authorization patient outcomes`

---

## Supported Sources to Hit

| Source | URL | Tool | What the Current Tooling Supports |
|--------|-----|------|-----------------------------------|
| PubMed | https://pubmed.ncbi.nlm.nih.gov | `pubmed_fetcher.py` | PMID, title, authors, publication date, journal, source URL |
| PLOS Medicine | https://journals.plos.org/plosmedicine | `journal_scraper.py` | Title, authors, publication date, abstract snippet, source URL |
| JAMA Network Open | https://jamanetwork.com/journals/jamanetworkopen | `journal_scraper.py` | Title, authors, publication date, source URL |
| medRxiv | https://www.medrxiv.org | `journal_scraper.py` | Title, authors, publication date, source URL, preprint flag |

---

## Future / Unsupported Sources

These sources may be useful later, but they are not active automated inputs in the current tool layer:

- bioRxiv
- Nature open-access sections
- The Lancet open-access sections
- NEJM
- Health Affairs
- ClinicalTrials.gov
- Cochrane Library

---

## Structured Output Contract

The workflow should produce structured findings that can support:

- Summary
- Key Findings
- What This Means
- Limitations

Use a backing markdown table or equivalent structured rows with these fields:

| Study Title | Authors | Journal | Publication Date | Plain-English Source Note | Urgency / Time Sensitivity | Confidence | Source Quality Tier | Recommended Action | Source Link |
|-------------|---------|---------|------------------|---------------------------|----------------------------|------------|---------------------|-------------------|-------------|

Field notes:
- **Plain-English Source Note** should rely only on metadata, abstract text, or snippet text actually returned by the tools.
- **Urgency / Time Sensitivity** is heuristic. Most research signals are `Ongoing` or `Evergreen`.
- **Confidence** should be downgraded for preprints, metadata-only records, or shallow extraction.
- **Source Quality Tier** should map to `memory/source_quality.md`.
- **Recommended Action** is often an orchestrator interpretation field, such as `Watch for peer review` or `Include in evidence brief`.

---

## Edge Case Handling

| Situation | Action |
|-----------|--------|
| Preprint (medRxiv) | Include, label clearly as `PREPRINT`, and keep confidence low |
| Metadata-only record | Include only if still useful; note the limitation |
| Missing title or source URL | Drop the record |
| Duplicate result across sources | Keep the cleaner or richer record |
| Unsupported source mentioned in notes | Mark as future/unsupported, not active automated coverage |

---

## Validation Requirements

- Every row must have a usable title and source URL
- Preserve PMID when available, but do not require DOI
- Do not invent study type, DOI, or retraction metadata unless a tool provides it

---

## Memory Check

Before running, check `memory/research_sources.md` for:
- high-performing queries
- supported-source limitations
- known rate-limit constraints
