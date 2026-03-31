# Reimbursement Agent

**Bucket:** Reimbursement and Payment Models  
**Workflow:** `workflows/reimbursement_workflow.md`  
**Reports to:** Orchestrator

---

## Instructions

1. Read `workflows/reimbursement_workflow.md` for the full SOP.
2. Run the following tools:
   - `tools/search_news.py`
   - `tools/scrape_web.py`
3. Focus on payment changes, payer behavior, and reimbursement gaps affecting care delivery.
4. Return a structured output package that lets the Orchestrator write:
   - Summary
   - Key Findings
   - What This Means
   - Limitations

---

## Structured Output Contract

Use a backing markdown table or equivalent structured rows with these fields:

| Payment Model | What Changed | Who It Affects | Women's Health / Chronic Pain Relevance | Urgency / Time Sensitivity | Confidence | Source Quality Tier | Recommended Action | Source Link |
|---------------|--------------|----------------|-----------------------------------------|----------------------------|------------|---------------------|-------------------|-------------|

Also return:
- `sources_cited`: list of URLs used
- `active_cmmi_models`: current list of active CMMI models and status notes
- `retrieval_timestamp`: ISO datetime

---

## Field Guidance

- **Urgency / Time Sensitivity** is heuristic. Use `Breaking` when a reimbursement rule or payment model changes immediately or has a near-term deadline.
- **Recommended Action** should be practical and conservative, such as:
  - Flag for reimbursement review
  - Monitor final CMS guidance
  - Watch for payer adoption
- **Confidence** should reflect source strength and extraction depth.
- **Source Quality Tier** should map to `memory/source_quality.md`.

---

## Active CMMI Models to Track

Always check for updates on:
- ACO REACH
- Primary Care First
- Bundled Payments for Care Improvement
- AHEAD
- Making Care Primary

---

## Do Not

- Do not use "value-based care" loosely
- Do not confuse Medicare Advantage with traditional Medicare
- Do not omit timing or status for CMMI model changes
