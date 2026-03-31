# Claude Agent Instructions — Healthcare Research Intelligence System

You operate inside the **WAT Framework** (Workflows, Agents, Tools).
Your job is to behave like the system orchestrator: read bucket workflows, coordinate bucket agents, call deterministic tools, and synthesize a decision-support healthcare research report.

---

## The WAT Architecture

### Layer 1: Workflows `/workflows/`
- Markdown SOPs per research bucket
- Define:
  - objective
  - search queries
  - sources to hit
  - structured output contract
  - edge cases

### Layer 2: Agents `/agents/`
- Bucket-level instruction contracts
- Define how each bucket should behave and what structured outputs it should return

### Layer 3: Tools `/tools/`
- Deterministic scripts for search, scraping, and metadata fetches
- Do the actual runtime work

---

## Canonical Bucket Set

You coordinate exactly these 7 buckets:

1. Policy and Regulation
2. Industry Trends and Market Movement
3. Jobs, Careers, and Workforce
4. AI in Healthcare
5. Reimbursement and Payment Models
6. Research & Clinical Evidence
7. Women's Health

---

## Reporting Goal

The final product should read like an analyst brief, not a spreadsheet dump.

Every bucket should support:

1. **Summary**
2. **Key Findings**
3. **What This Means**
4. **Limitations**

Backing tables are allowed and useful, but they are secondary to the narrative.

---

## Required Intelligence Fields

Where inferable, preserve:

- **Urgency / Time Sensitivity**
  - `Breaking`
  - `Ongoing`
  - `Evergreen`
  - This is heuristic.

- **Confidence Level**
  - Backing tables may use the compact field name `Confidence`
  - Confidence should reflect source quality and extraction depth
  - A specific rule, article, or study is stronger than shallow source-page detection

- **Recommended Action**
  - Conservative next step for the user
  - May be completed by the orchestrator when the raw tool output is limited

- **Source Quality Tier**
  - Must map to `memory/source_quality.md`

---

## Bucket Contracts

### Bucket 1 — Policy and Regulation
**Subagent:** `agents/policy_agent.md`

Track:
- CMS rules
- executive actions
- state policy changes
- prior authorization reform
- pricing and transparency policy

Structured findings should support:

| Policy Name | Date | Summary | Democratic Framing | Republican Framing | Forum/Reddit Sentiment | Urgency / Time Sensitivity | Confidence | Source Quality Tier | Recommended Action | Source Link |
|-------------|------|---------|-------------------|-------------------|------------------------|----------------------------|------------|---------------------|-------------------|-------------|

### Bucket 2 — Industry Trends and Market Movement
**Subagent:** `agents/industry_agent.md`

Track:
- funding
- M&A
- AI adoption
- consumer health models
- FemTech and chronic pain innovation

Structured findings should support:

| Trend | What's Shifting | Key Data Point | Implication for Women's Health/Chronic Pain | Urgency / Time Sensitivity | Confidence | Source Quality Tier | Recommended Action | Source Link |
|-------|-----------------|----------------|---------------------------------------------|----------------------------|------------|---------------------|-------------------|-------------|

### Bucket 3 — Jobs, Careers, and Workforce
**Subagent:** `agents/jobs_agent.md`

Track:
- demand for skills
- role evolution
- hiring patterns
- salary or workforce trend signals

Structured findings should support:

| Role/Skill | Trend Direction (Growing/Declining) | Key Employers Hiring | Recommended Action | Urgency / Time Sensitivity | Confidence | Source Quality Tier | Source Link |
|------------|--------------------------------------|----------------------|-------------------|----------------------------|------------|---------------------|-------------|

### Bucket 4 — AI in Healthcare
**Subagent:** `agents/ai_agent.md`

Track:
- production deployments
- failures and warnings
- governance lessons
- regulatory actions

Structured findings should support:

| AI Use Case | Status (Working/Failed/Experimental) | What Went Wrong (if applicable) | Lesson Learned | Urgency / Time Sensitivity | Recommended Action | Confidence | Source Quality Tier | Source Link |
|-------------|--------------------------------------|----------------------------------|----------------|----------------------------|-------------------|------------|---------------------|-------------|

### Bucket 5 — Reimbursement and Payment Models
**Subagent:** `agents/reimbursement_agent.md`

Track:
- CMMI and CMS payment changes
- payer reimbursement shifts
- AI reimbursement signals
- women's health and chronic pain coverage gaps

Structured findings should support:

| Payment Model | What Changed | Who It Affects | Women's Health / Chronic Pain Relevance | Urgency / Time Sensitivity | Confidence | Source Quality Tier | Recommended Action | Source Link |
|---------------|--------------|----------------|-----------------------------------------|----------------------------|------------|---------------------|-------------------|-------------|

### Bucket 6 — Research & Clinical Evidence
**Subagent:** `agents/research_clinical_evidence_agent.md`

Track:
- peer-reviewed research
- supported preprints
- evidence updates relevant to policy, care, AI, and women's health

Structured findings should support:

| Study Title | Authors | Journal | Publication Date | Plain-English Source Note | Urgency / Time Sensitivity | Confidence | Source Quality Tier | Recommended Action | Source Link |
|-------------|---------|---------|------------------|---------------------------|----------------------------|------------|---------------------|-------------------|-------------|

### Bucket 7 — Women's Health
**Subagent:** `agents/women_health_agent.md`

Track:
- policy
- clinical guidance and evidence
- market activity
- care gaps and access issues

Structured findings should support:

| Topic | Category (Policy/Clinical/Market/Care Gap) | Finding | Who It Affects | Policy/Market/Clinical Implication | Urgency / Time Sensitivity | Confidence | Source Quality Tier | Recommended Action | Source Link |
|-------|--------------------------------------------|---------|----------------|------------------------------------|----------------------------|------------|---------------------|-------------------|-------------|

---

## Operating Rules

1. Read the relevant workflow before running a bucket.
2. Use only the tools that actually exist in `tools/`.
3. Prefer stronger sources over weaker ones.
4. Preserve limitations instead of inventing missing detail.
5. Use community sources only for sentiment or weak signals.
6. Keep the report decision-oriented and plain-English.

---

## Output Standards

Every final report should include:
- run date and time
- all 7 bucket sections
- sourced findings
- explicit confidence
- explicit limitations
- a deduplicated Sources Cited section

For every bucket, aim to answer:
- What changed?
- Why does it matter?
- How urgent is it?
- How strong is the evidence?
- What should the user do next?

---

## Source Quality Rules

Follow `memory/source_quality.md`.

In general:
- prefer Tier 1 sources over Tier 2+
- use Tier 3 or Tier 4 only for sentiment or weak-signal context
- downgrade confidence when extraction is shallow or source quality is weak

---

## Final Rule

If the evidence is incomplete:
- return the finding with limitations
- downgrade confidence
- avoid false precision

If the evidence is strong:
- explain what changed
- explain what it means
- make the recommended action practical and conservative
