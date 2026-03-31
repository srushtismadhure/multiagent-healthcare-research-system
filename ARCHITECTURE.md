# Healthcare Research Intelligence System — Architecture

> **For humans only.** This file is a reference guide for anyone working on or with this system.

---

## 1. Overview

This system is a healthcare intelligence platform organized around the **WAT Framework**:

- **Workflows** define what to research and what fields to extract
- **Agents** define how each bucket should behave and what structured output it should return
- **Tools** do deterministic work such as search, scraping, and metadata retrieval

The reporting model is now **narrative-first and decision-support oriented**.  
The primary output is not a spreadsheet dump. It is an analyst-style brief built from structured findings.

---

## 2. WAT Framework

| Layer | What It Does | Where Files Live |
|-------|--------------|-----------------|
| **W — Workflows** | Markdown SOPs that define each bucket's objective, search queries, source targets, structured output contract, and edge cases | `workflows/` |
| **A — Agents** | Markdown instruction files that define bucket-level behavior, validation rules, and structured return contracts | `agents/` |
| **T — Tools** | Python scripts that perform deterministic execution such as search, scraping, and metadata fetches | `tools/` |

The **Orchestrator** coordinates the run, normalizes results, and assembles the final report.

---

## 3. Canonical Bucket Set

Use exactly these 7 buckets:

| # | Bucket Name | Agent File | Workflow File |
|---|-------------|------------|---------------|
| 1 | Policy and Regulation | `agents/policy_agent.md` | `workflows/policy_workflow.md` |
| 2 | Industry Trends and Market Movement | `agents/industry_agent.md` | `workflows/industry_workflow.md` |
| 3 | Jobs, Careers, and Workforce | `agents/jobs_agent.md` | `workflows/jobs_workflow.md` |
| 4 | AI in Healthcare | `agents/ai_agent.md` | `workflows/ai_healthcare_workflow.md` |
| 5 | Reimbursement and Payment Models | `agents/reimbursement_agent.md` | `workflows/reimbursement_workflow.md` |
| 6 | Research & Clinical Evidence | `agents/research_clinical_evidence_agent.md` | `workflows/research_clinical_evidence.md` |
| 7 | Women's Health | `agents/women_health_agent.md` | `workflows/women_health_workflow.md` |

---

## 4. Reporting Model

Every bucket should support these four report sections:

1. **Summary**
2. **Key Findings**
3. **What This Means**
4. **Limitations**

Structured tables still matter, but they are now a **backing format**, not the primary report experience.

---

## 5. Required Intelligence Fields

Where inferable, findings should preserve:

- **Urgency / Time Sensitivity**
  - `Breaking`
  - `Ongoing`
  - `Evergreen`
  - This is heuristic, not perfect truth.

- **Confidence Level**
  - Backing-table field name remains `Confidence`
  - Should reflect both source strength and extraction depth
  - A shallow source-page detection should not be labeled the same way as a clearly sourced article, rule, or study

- **Recommended Action**
  - Conservative next step for the user
  - Often an orchestrator interpretation rather than a raw tool output

- **Source Quality Tier**
  - Should map to `memory/source_quality.md`
  - Tier reflects source category, not whether the finding is favorable

---

## 6. Execution Flow

```text
1. TRIGGER
   -> user starts a run

2. ORCHESTRATOR LOADS CONTEXT
   -> workflows/
   -> agents/
   -> relevant memory/ files

3. RUN 7 BUCKETS
   -> each bucket uses its assigned tools
   -> each bucket returns structured findings + source links + limitations

4. NORMALIZE
   -> preserve canonical fields from memory/output_schemas.md
   -> keep placeholders where tools cannot provide deeper detail

5. ASSEMBLE REPORT
   -> Summary
   -> Key Findings
   -> What This Means
   -> Limitations
   -> Sources Cited

6. WRITE OUTPUT
   -> local markdown report in outputs/

7. OPTIONAL LATER INTEGRATIONS
   -> downstream sharing/logging layers such as Google Docs or Google Sheets
```

---

## 7. Output Contract vs Presentation

`memory/output_schemas.md` defines the **canonical structured fields** the system should preserve.

The final report may transform those fields into:
- narrative summaries
- decision-support paragraphs
- concise bullet findings
- optional backing tables

This separation is intentional:
- schemas keep the data stable
- the orchestrator owns presentation

---

## 8. Source Quality and Confidence

Source quality comes from `memory/source_quality.md`.

General rule:
- prefer official, primary, and peer-reviewed sources first
- use secondary reporting for context
- use community/forum sources only for sentiment or weak-signal monitoring

Confidence should combine:
- source quality
- corroboration
- extraction depth

Examples:
- Official rule text or specific peer-reviewed study with clear metadata -> higher confidence
- Single trade-press story with shallow extraction -> medium or lower confidence
- Forum discussion or anecdote -> low confidence

---

## 9. Design Principles

- Keep the system deterministic-friendly
- Do not assume LLM reasoning in v1
- Preserve structured fields even when the final report is narrative
- Be explicit about shallow extraction, paywalls, unsupported sources, and contradictions
- Prefer a usable partial brief over false precision

---

## 10. Key Files

| Area | Purpose |
|------|---------|
| `agents/orchestrator.md` | Defines the top-level reporting contract |
| `memory/output_schemas.md` | Defines canonical structured fields per bucket |
| `agents/*.md` | Define bucket-specific behavior and return contracts |
| `workflows/*.md` | Define search plans, source targets, extraction fields, and edge cases |
| `memory/source_quality.md` | Defines the source tier hierarchy |
| `orchestrator.py` | Deterministic execution layer that assembles the final report |

---

## 11. Bottom Line

This repo is designed to produce a **decision-support analyst brief** backed by structured findings.

The tables are still useful, but they are no longer the product.  
The product is a clearer answer to:

- What changed?
- Why does it matter?
- How urgent is it?
- How strong is the evidence?
- What should the user do next?
