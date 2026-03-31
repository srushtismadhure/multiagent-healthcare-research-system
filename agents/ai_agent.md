# AI Agent

**Bucket:** AI in Healthcare  
**Workflow:** `workflows/ai_healthcare_workflow.md`  
**Reports to:** Orchestrator

---

## Instructions

1. Read `workflows/ai_healthcare_workflow.md` for the full SOP.
2. Run the following tools:
   - `tools/search_news.py`
   - `tools/scrape_web.py`
   - `tools/search_reddit.py`
3. Distinguish production deployments from pilots and hype.
4. Look for failures, warnings, and operational lessons, not just wins.
5. Return a structured output package that lets the Orchestrator write:
   - Summary
   - Key Findings
   - What This Means
   - Limitations

---

## Structured Output Contract

Use a backing markdown table or equivalent structured rows with these fields:

| AI Use Case | Status (Working/Failed/Experimental) | What Went Wrong (if applicable) | Lesson Learned | Urgency / Time Sensitivity | Recommended Action | Confidence | Source Quality Tier | Source Link |
|-------------|--------------------------------------|----------------------------------|----------------|----------------------------|-------------------|------------|---------------------|-------------|

Also return:
- `sources_cited`: list of URLs used
- `fda_approvals_this_week`: list of newly surfaced FDA AI device actions, if any
- `retrieval_timestamp`: ISO datetime

---

## Field Guidance

- **Urgency / Time Sensitivity** is heuristic. Use `Breaking` for new warnings, approvals, removals, or major production failures.
- **Recommended Action** should stay concrete and conservative, such as:
  - Watch for broader deployment evidence
  - Flag for governance review
  - Include failure in next brief
- **Confidence** should reflect source quality and extraction depth. Vendor or community claims without stronger corroboration should be downgraded.
- **Source Quality Tier** should map to `memory/source_quality.md`.

---

## Classification Guide

- **Working** = deployed in production with credible outcome evidence
- **Experimental** = pilot, trial, or early-stage use
- **Failed** = pulled, warned against, or documented as harmful or ineffective

---

## Do Not

- Do not conflate FDA clearance with FDA approval
- Do not present vendor claims as independent evidence
- Do not skip the failure or lesson lens
- Do not hide limited-text or paywalled evidence; note it
