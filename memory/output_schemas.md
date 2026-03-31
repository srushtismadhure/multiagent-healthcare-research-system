# Output Schemas — Memory Store

**Purpose:** Canonical structured fields for each research bucket.  
These schemas define the fields the system should preserve, but the final report may transform them into narrative sections such as **Summary**, **Key Findings**, **What This Means**, and **Limitations**.

---

## Shared Reporting Contract

Every bucket should support:

1. **Summary** — plain-English overview of the bucket's top signals
2. **Key Findings** — the structured findings that back the section
3. **What This Means** — decision-support interpretation
4. **Limitations** — what was missing, shallow, unsupported, or uncertain

Tables remain a useful transport and review format, but they are not the only valid final presentation.

---

## Shared Field Notes

- **`Confidence`** is the compact backing-table field name for the report's **Confidence Level**.  
  It should reflect both source strength and extraction depth. If the system only detected a source page or shallow snippet, confidence should be downgraded accordingly.

- **`Source Quality Tier`** maps to `memory/source_quality.md`.  
  Use the repo's source hierarchy rather than inventing a new one.

- **`Urgency / Time Sensitivity`** is heuristic.  
  Default labels:
  - `Breaking` = newly announced, newly effective, or materially changed now
  - `Ongoing` = active issue, contested policy, ongoing rollout, or continuing trend
  - `Evergreen` = important context, baseline evidence, or durable background signal

- **`Recommended Action`** is usually an orchestrator interpretation field.  
  Keep it conservative and tied to the evidence actually available.

- **Limitations** are usually bucket-level notes rather than mandatory per-row fields.

---

## Bucket 1: Policy and Regulation

```markdown
| Policy Name | Date | Summary | Democratic Framing | Republican Framing | Forum/Reddit Sentiment | Urgency / Time Sensitivity | Confidence | Source Quality Tier | Recommended Action | Source Link |
|-------------|------|---------|-------------------|-------------------|------------------------|----------------------------|------------|---------------------|-------------------|-------------|
```

**Confidence values:** High | Medium | Low  
**Date format:** YYYY-MM-DD

---

## Bucket 2: Industry Trends and Market Movement

```markdown
| Trend | What's Shifting | Key Data Point | Implication for Women's Health/Chronic Pain | Urgency / Time Sensitivity | Confidence | Source Quality Tier | Recommended Action | Source Link |
|-------|-----------------|----------------|---------------------------------------------|----------------------------|------------|---------------------|-------------------|-------------|
```

---

## Bucket 3: Jobs, Careers, and Workforce

```markdown
| Role/Skill | Trend Direction (Growing/Declining) | Key Employers Hiring | Recommended Action | Urgency / Time Sensitivity | Confidence | Source Quality Tier | Source Link |
|------------|--------------------------------------|----------------------|-------------------|----------------------------|------------|---------------------|-------------|
```

**Trend Direction values:** Growing | Stable | Declining

---

## Bucket 4: AI in Healthcare

```markdown
| AI Use Case | Status (Working/Failed/Experimental) | What Went Wrong (if applicable) | Lesson Learned | Urgency / Time Sensitivity | Recommended Action | Confidence | Source Quality Tier | Source Link |
|-------------|--------------------------------------|----------------------------------|----------------|----------------------------|-------------------|------------|---------------------|-------------|
```

**Status values:** Working | Failed | Experimental

---

## Bucket 5: Reimbursement and Payment Models

```markdown
| Payment Model | What Changed | Who It Affects | Women's Health / Chronic Pain Relevance | Urgency / Time Sensitivity | Confidence | Source Quality Tier | Recommended Action | Source Link |
|---------------|--------------|----------------|-----------------------------------------|----------------------------|------------|---------------------|-------------------|-------------|
```

---

## Bucket 6: Research & Clinical Evidence

```markdown
| Study Title | Authors | Journal | Publication Date | Plain-English Source Note | Urgency / Time Sensitivity | Confidence | Source Quality Tier | Recommended Action | Source Link |
|-------------|---------|---------|------------------|---------------------------|----------------------------|------------|---------------------|-------------------|-------------|
```

---

## Bucket 7: Women's Health

```markdown
| Topic | Category (Policy/Clinical/Market/Care Gap) | Finding | Who It Affects | Policy/Market/Clinical Implication | Urgency / Time Sensitivity | Confidence | Source Quality Tier | Recommended Action | Source Link |
|-------|--------------------------------------------|---------|----------------|------------------------------------|----------------------------|------------|---------------------|-------------------|-------------|
```

---

## Master Research Document Header

Every output document should begin with:

```markdown
# Healthcare Research Intelligence Report
**Run Date:** YYYY-MM-DD
**Run Time:** HH:MM UTC
**Run ID:** YYYYMMDD_HHMMSS
```

The final report may then transform the structured data into narrative bucket sections.

---

## Research Log Row Format

If a run log is maintained, the row may include:

| Column | Type | Description |
|--------|------|-------------|
| Run Date | Date (YYYY-MM-DD) | Date of research run |
| Run Time | Time (HH:MM UTC) | Time run completed |
| Document Title | String | Title of output doc |
| Buckets Covered | String | Canonical bucket names included in the run |
| Key Findings Summary | String | Short narrative summary of the run |
| Source Count | Integer | Number of unique sources cited |
| Doc Link | URL or Path | Markdown file path or later downstream link |
