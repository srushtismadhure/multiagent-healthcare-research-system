# Women's Health — Research Workflow SOP

**Bucket:** Women's Health  
**Agent:** `agents/women_health_agent.md`  
**Run frequency:** Weekly (or on-demand)

---

## Objective

Track the full women’s health landscape across policy, clinical care, market activity, and care gaps. Focus on evidence-backed developments and avoid reducing women’s health to reproductive health alone.

---

## Search Queries

Use queries designed to surface policy updates, clinical evidence, and market signals:

1. `women's health policy Medicaid reproductive health state law update 2025`
2. `maternal mortality US data CDC report OB desert access statistics`
3. `FemTech funding women's health startup investment rounds data 2025`
4. `menopause care insurance coverage US guidelines ACOG update`
5. `endometriosis diagnosis delay healthcare study outcomes women`
6. `PCOS fibromyalgia underdiagnosis women clinical research outcomes`
7. `fertility IVF coverage mandate state legislation update US`
8. `women's health AI bias clinical study diagnostic disparity women`
9. `maternity care desert rural hospital closure obstetrics access data`
10. `women's health reimbursement gaps US maternal menopause coverage`

---

## Sources to Hit

| Source | URL | What to Pull |
|--------|-----|--------------|
| KFF Women's Health | https://www.kff.org/womens-health-policy | Policy analysis and coverage context |
| CMS / Medicaid | https://www.medicaid.gov | Coverage and reimbursement policy |
| ACOG | https://www.acog.org | Clinical guidance |
| CDC | https://www.cdc.gov | Maternal health and population data |
| Commonwealth Fund | https://www.commonwealthfund.org | Equity and access research |
| Rock Health | https://rockhealth.com | Funding trends and market reports |
| FemTech World | https://femtechworld.co.uk | Startup and product activity |
| STAT News | https://www.statnews.com | Investigative reporting |
| JAMA / NEJM | journals | Clinical evidence and commentary |
| State legislative sites / Ballotpedia | https://ballotpedia.org | State policy tracking |
| Reddit (selected communities) | Reddit | Sentiment only |

---

## Structured Output Contract

The workflow should produce structured findings that can support:

- Summary
- Key Findings
- What This Means
- Limitations

Use a backing markdown table or equivalent structured rows with these fields:

| Topic | Category (Policy/Clinical/Market/Care Gap) | Finding | Who It Affects | Policy/Market/Clinical Implication | Urgency / Time Sensitivity | Confidence | Source Quality Tier | Recommended Action | Source Link |
|-------|--------------------------------------------|---------|----------------|------------------------------------|----------------------------|------------|---------------------|-------------------|-------------|

Field notes:
- **Urgency / Time Sensitivity** is heuristic and should reflect recency, policy stage, or time-sensitive access changes.
- **Confidence** should reflect source quality plus extraction depth.
- **Source Quality Tier** should map to `memory/source_quality.md`.
- **Recommended Action** may be an orchestrator interpretation when the evidence is meaningful but not fully detailed.

---

## Required Extraction

For each finding, extract:
- topic
- category
- finding
- who it affects
- implication

Also capture geography or state specificity when available.

---

## Priority Areas

Always prioritize:
1. Reproductive health policy
2. Maternal health and OB-desert signals
3. FemTech funding and launches
4. Chronic conditions disproportionately affecting women
5. Menopause care
6. AI bias in women’s health

---

## Edge Cases

- If policy status is unclear, flag it for human review
- If sources conflict, say so directly
- If FemTech data varies, cite source and year
- If no major update appears, summarize the most recent material trend rather than inventing novelty

---

## Output Note

This workflow defines where to search and what to extract.  
The final report presentation is narrative-first and owned by the Orchestrator.
