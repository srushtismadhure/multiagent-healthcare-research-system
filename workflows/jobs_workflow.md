# Jobs, Careers, and Workforce — Research Workflow SOP

**Bucket:** Jobs, Careers, and Workforce  
**Agent:** `agents/jobs_agent.md`  
**Run frequency:** Weekly (or on-demand)

---

## Objective

Track the healthcare data and informatics job market: skill demand, role evolution, hiring signals, salary benchmarks, and how AI is changing analyst and informatics work.

---

## Search Queries

1. `healthcare data analyst jobs 2025`
2. `health informatics FHIR jobs hiring`
3. `clinical analyst AI automation impact`
4. `Epic Cerner data engineer job postings`
5. `HIMSS workforce survey 2025`
6. `health IT salary benchmark 2025`
7. `Databricks Spark healthcare analytics jobs`
8. `SmarterDx Mass General Brigham hiring data`
9. `r/healthinformatics job market`
10. `BLS healthcare occupations outlook`

---

## Sources to Hit

| Source | URL | What to Pull |
|--------|-----|--------------|
| BLS Occupational Outlook | https://www.bls.gov/ooh | Job growth projections |
| HIMSS | https://www.himss.org | Workforce and informatics reports |
| Healthcare IT Today | https://www.healthcareittoday.com | HIT hiring news |
| LinkedIn (thought leaders) | LinkedIn search | Representative hiring-manager and practitioner signals |
| Reddit r/healthIT | https://www.reddit.com/r/healthIT | Practitioner sentiment |
| Reddit r/healthinformatics | https://www.reddit.com/r/healthinformatics | Career discussion |
| Indeed / Glassdoor | Trend data | Salary and demand signals |

---

## Structured Output Contract

The workflow should produce structured findings that can support:

- Summary
- Key Findings
- What This Means
- Limitations

Use a backing markdown table or equivalent structured rows with these fields:

| Role/Skill | Trend Direction (Growing/Declining) | Key Employers Hiring | Recommended Action | Urgency / Time Sensitivity | Confidence | Source Quality Tier | Source Link |
|------------|--------------------------------------|----------------------|-------------------|----------------------------|------------|---------------------|-------------|

Field notes:
- **Recommended Action** may suggest a practical next step such as building a skill, tracking a hiring pattern, or including the signal in a workforce brief.
- **Urgency / Time Sensitivity** is heuristic. Most workforce trends are `Ongoing`.
- **Confidence** should be downgraded for anecdotal or forum-heavy evidence.
- **Source Quality Tier** should map to `memory/source_quality.md`.

---

## Skills to Track

Always check for signals around:
- FHIR / HL7
- Python / SQL
- Databricks / Spark
- Power BI / Tableau
- Epic / Cerner certifications
- NLP / LLM in clinical settings
- ICD-10 / CPT coding knowledge

---

## Edge Cases

- LinkedIn job posts are rate-limited; use representative signals, not exhaustive lists
- BLS data updates annually; always note the vintage year
- Reddit sentiment is anecdotal and should be labeled accordingly
