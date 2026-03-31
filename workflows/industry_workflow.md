# Industry Trends and Market Movement — Research Workflow SOP

**Bucket:** Industry Trends and Market Movement  
**Agent:** `agents/industry_agent.md`  
**Run frequency:** Weekly (or on-demand)

---

## Objective

Track where the healthcare industry is heading, with emphasis on AI adoption, digital health funding, M&A, consumer health models, FemTech, and chronic pain innovation.

---

## Search Queries

1. `digital health funding rounds 2025 2026`
2. `healthcare AI adoption rate payer provider`
3. `FemTech women's health market growth`
4. `healthcare M&A acquisition 2025`
5. `ambulatory surgical center growth trend`
6. `value-based care model shift`
7. `Hims Hers Function Health consumer health`
8. `chronic pain digital therapeutics innovation`
9. `Bessemer healthcare AI report`
10. `Rock Health digital health funding`

---

## Sources to Hit

| Source | URL | What to Pull |
|--------|-----|--------------|
| Healthcare Dive | https://www.healthcaredive.com | Breaking industry news |
| Rock Health | https://rockhealth.com | Funding reports |
| Bessemer VP | https://www.bvp.com | Health AI market analysis |
| BCG Health | https://www.bcg.com/industries/health-care | Market trend analysis |
| STAT News | https://www.statnews.com | Investigative industry coverage |
| FemTech World | https://femtechworld.co.uk | Women's health market data |
| Wolters Kluwer | https://www.wolterskluwer.com | Clinical and operational trend commentary |

---

## Structured Output Contract

The workflow should produce structured findings that can support:

- Summary
- Key Findings
- What This Means
- Limitations

Use a backing markdown table or equivalent structured rows with these fields:

| Trend | What's Shifting | Key Data Point | Implication for Women's Health/Chronic Pain | Urgency / Time Sensitivity | Confidence | Source Quality Tier | Recommended Action | Source Link |
|-------|-----------------|----------------|---------------------------------------------|----------------------------|------------|---------------------|-------------------|-------------|

Field notes:
- **Urgency / Time Sensitivity** is heuristic. Reserve `Breaking` for newly announced deals, funding, or abrupt shifts.
- **Confidence** should be lower for projection-heavy or lightly sourced market claims.
- **Source Quality Tier** should map to `memory/source_quality.md`.
- **Recommended Action** may be an orchestrator interpretation when the tooling only returns partial detail.

---

## Focus Areas

Prioritize findings that touch:
1. Women's health and FemTech
2. Chronic pain and pain management
3. AI adoption rates and deployment signals
4. Consumer health models with actual traction

---

## Edge Cases

- If no new funding rounds appear, pull the latest credible quarterly funding summary
- If M&A news is thin, note the lack of major movement rather than forcing weak signals
- Any market-size or CAGR figure must include source and year
