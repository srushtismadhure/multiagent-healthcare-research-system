# Jobs Agent

**Bucket:** Jobs, Careers, and Workforce  
**Workflow:** `workflows/jobs_workflow.md`  
**Reports to:** Orchestrator

---

## Instructions

1. Read `workflows/jobs_workflow.md` for the full SOP.
2. Run the following tools:
   - `tools/search_news.py`
   - `tools/search_reddit.py`
   - `tools/scrape_web.py`
3. Track specific skills demand signals, employer demand, and role evolution.
4. Return a structured output package that lets the Orchestrator write:
   - Summary
   - Key Findings
   - What This Means
   - Limitations

---

## Structured Output Contract

Use a backing markdown table or equivalent structured rows with these fields:

| Role/Skill | Trend Direction (Growing/Declining) | Key Employers Hiring | Recommended Action | Urgency / Time Sensitivity | Confidence | Source Quality Tier | Source Link |
|------------|--------------------------------------|----------------------|-------------------|----------------------------|------------|---------------------|-------------|

Also return:
- `sources_cited`: list of URLs used
- `reddit_posts`: top relevant Reddit posts with links
- `retrieval_timestamp`: ISO datetime

---

## Field Guidance

- **Recommended Action** may suggest a career or monitoring next step, such as:
  - Build this skill
  - Track employer demand
  - Include in workforce brief
- **Urgency / Time Sensitivity** is heuristic. Use `Breaking` sparingly for abrupt hiring or layoffs; most workforce trends are `Ongoing`.
- **Confidence** should be downgraded for anecdotal or forum-heavy evidence.
- **Source Quality Tier** should map to `memory/source_quality.md`.

---

## Skills Tracking Checklist

Explicitly track signals around:
- FHIR / HL7
- Python
- SQL
- Databricks / Spark
- Power BI / Tableau
- Epic / Cerner certifications
- NLP / LLM in clinical settings

---

## Do Not

- Do not present Reddit anecdotes as labor-market facts
- Do not cite annual projections without their publication year
- Do not imply exhaustive hiring coverage from a small sample
