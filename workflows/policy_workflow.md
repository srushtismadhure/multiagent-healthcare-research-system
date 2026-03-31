# Policy and Regulation — Research Workflow SOP

**Bucket:** Policy and Regulation  
**Agent:** `agents/policy_agent.md`  
**Run frequency:** Weekly (or on-demand)

---

## Objective

Surface the most important healthcare policy and regulatory changes from the last 7 days, especially CMS rules, executive orders, state-level coverage activity, prior authorization reform, and pricing or transparency policy.

---

## Search Queries

1. `CMS final rule 2025 2026`
2. `Medicare Advantage payment policy update`
3. `Medicaid waiver state expansion`
4. `prior authorization reform CMS`
5. `340B drug pricing ruling`
6. `HIPAA update enforcement`
7. `Physician Fee Schedule proposed rule`
8. `White House executive order healthcare`
9. `ACA marketplace enrollment rule`
10. `price transparency hospital enforcement`

---

## Sources to Hit (in order)

| Source | URL | What to Pull |
|--------|-----|--------------|
| CMS Newsroom | https://www.cms.gov/newsroom | Latest press releases and rule announcements |
| White House Actions | https://www.whitehouse.gov/presidential-actions | Executive orders touching healthcare |
| KFF | https://kff.org | Policy analysis and summaries |
| Health Affairs | https://healthaffairs.org | Policy commentary and analysis |
| McDermott+ EO Tracker | https://www.mcdermottplus.com | Executive-order tracking |
| Ballotpedia EO Tracker | https://ballotpedia.org | Public status tracking |
| AHA News | https://www.aha.org/news | Provider-side reaction |
| Modern Healthcare | https://www.modernhealthcare.com | Industry framing |

---

## Structured Output Contract

The workflow should produce structured findings that can support the final bucket sections:

- Summary
- Key Findings
- What This Means
- Limitations

Use a backing markdown table or equivalent structured rows with these fields:

| Policy Name | Date | Summary | Democratic Framing | Republican Framing | Forum/Reddit Sentiment | Urgency / Time Sensitivity | Confidence | Source Quality Tier | Recommended Action | Source Link |
|-------------|------|---------|-------------------|-------------------|------------------------|----------------------------|------------|---------------------|-------------------|-------------|

Field notes:
- **Urgency / Time Sensitivity** is heuristic and should be based on recency, effective date, and policy stage.
- **Confidence** should reflect both source quality and extraction depth.
- **Source Quality Tier** should map to `memory/source_quality.md`.
- **Recommended Action** is decision-support oriented and may be completed by the Orchestrator when only limited evidence is available.

---

## Sentiment Pull Instructions

For major policy findings, collect framing only when it is credibly observable:
- 2-3 relevant headlines or coverage angles if available
- stakeholder or political framing when clearly evidenced
- forum or community sentiment only as context, never as validation

If framing is thin or noisy, say so in limitations rather than forcing symmetry.

---

## Edge Cases

- If CMS newsroom has no new items this week, check the Federal Register for proposed or final rules
- If White House has no new healthcare executive actions, note that explicitly and move on
- If a rule is still proposed, label it clearly as `PROPOSED`
- If a source is paywalled, use only the accessible headline, abstract, or snippet and note the limitation

---

## Memory Check

Before running, check `memory/cms_known_rules.md` to avoid re-documenting unchanged rules.  
Return candidate new rules so the Orchestrator can decide whether to update curated memory later.
