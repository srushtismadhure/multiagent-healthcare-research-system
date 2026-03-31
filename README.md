# multiagent-healthcare-research-system

> A multi-agent research automation system that monitors, retrieves, and synthesizes information across seven healthcare domains — built on a custom WAT framework with LLM-powered summarization and structured Google Workspace outputs.

![Multi-Agent System](https://img.shields.io/badge/Multi--Agent%20System-blue)
![Healthcare AI](https://img.shields.io/badge/Healthcare%20AI-teal)
![LLM-Powered](https://img.shields.io/badge/LLM--Powered-orange)
![Clinical Data](https://img.shields.io/badge/Clinical%20Data-red)
![Google Workspace](https://img.shields.io/badge/Google%20Workspace-lightgrey)
![Autonomous Execution](https://img.shields.io/badge/Autonomous%20Execution-green)

---

## Project Overview

This is a functional prototype of an autonomous multi-agent research pipeline designed to track and synthesize developments across seven healthcare domains. The system is built on a custom **WAT (Workflows, Agents, Tools)** framework and uses an **Orchestrator + parallel subagents** model, where each domain agent runs its own retrieval, evaluation, and summarization workflow concurrently.

Outputs are written as structured summaries to per-domain Google Docs, with metadata and run history logged to a master Google Sheet — giving analysts and product teams a continuously updated, organized intelligence feed without manual research overhead.

Built by a healthcare data analyst with a background in clinical informatics, health data engineering, and applied AI — this project reflects how modern LLM tooling can be applied to real workflows in healthcare research and decision support.

---

## What I Built

This project represents end-to-end design and engineering work, not configuration of an existing framework:

- **Designed the multi-agent architecture** — defined the Orchestrator + parallel subagent pattern and scoped each agent's responsibility boundaries within the WAT framework
- **Built the orchestration logic** — workflow sequencing, domain task dispatch, retry handling, and cross-agent output aggregation
- **Defined agent scopes, prompts, and output schemas** — each of the seven domain agents has a distinct system prompt, source tier configuration, and structured output format
- **Integrated LLM-based synthesis** — wired Claude (Anthropic) into the retrieval-summarization pipeline for each domain agent
- **Connected structured outputs to Google Workspace** — automated writing to per-domain Google Docs and a master tracking Google Sheet via the Google Docs and Sheets APIs
- **Authored `ARCHITECTURE.md`** — full system design documentation with ASCII diagrams, agent specs, and source tier rationale

---

## Key Features

- **Orchestrated multi-agent execution** — an Orchestrator agent dispatches tasks to seven domain-specific subagents, each running its own retrieval and synthesis cycle
- **Parallel agent runs** — domain agents execute concurrently, reducing total pipeline runtime across all seven research areas
- **Source quality tiering** — agents apply a defined credibility and recency framework to evaluate and prioritize sources before synthesis
- **Policy context annotation** — regulatory and policy domain outputs include structured framing of stakeholder positions and legislative context, not just raw headlines
- **Structured LLM summarization** — Claude synthesizes retrieved content into analyst-ready summaries following a consistent per-domain output schema
- **Google Workspace reporting** — summaries are written automatically to per-domain Google Docs; run metadata, timestamps, and source counts are tracked in a master Google Sheet
- **Modular WAT design** — workflows, agents, and tools are independently scoped, making it straightforward to add new domains or swap retrieval sources
- **Healthcare-grounded output design** — output schemas are mapped to real analytical use cases including value-based care, FemTech, SDOH, and reimbursement

---

## Architecture

The architecture is intentionally separated into three layers — orchestration, domain execution, and output — so that each concern is independently testable and extensible. The parallel subagent model was chosen because each healthcare domain has different source types, retrieval logic, and synthesis requirements; a single monolithic agent would conflate these and make the system harder to tune or debug.

### Components

**1. Orchestrator Agent**
Central coordinator built on the WAT framework. Dispatches research tasks to domain subagents, manages workflow sequencing and retries, and aggregates run metadata into the master Google Sheet. The Orchestrator does not perform synthesis — it coordinates execution and handles failures gracefully.

**2. Parallel Domain Subagents (×7)**
Each subagent is scoped to one research domain and owns its source list, quality-tier evaluation logic, synthesis prompt chain, and Google Doc target. All seven agents execute concurrently per run cycle. Agent separation ensures that prompt tuning, source changes, or schema updates in one domain do not affect others.

**3. WAT Framework Layer**
Custom-built Workflows, Agents, Tools layer that governs task routing, agent memory scoping, retry and fallback logic, and tool invocations — including web retrieval, Google Doc writes, and Sheets updates.

**4. Output Layer — Google Workspace**
Structured summaries are written to per-domain Google Docs on each run. Cross-domain metadata — including timestamps, source counts, and quality tier distribution — is logged to a master Google Sheet for run tracking and review.

### System Diagram

```
Orchestrator
├── Policy & Regulation Agent          ──► Google Doc (Policy)
├── Industry Trends Agent              ──► Google Doc (Trends)
├── Jobs & Careers Agent               ──► Google Doc (Jobs)
├── AI in Healthcare Agent             ──► Google Doc (AI/ML)
├── Women's Health & FemTech Agent     ──► Google Doc (FemTech)
├── Reimbursement & Payment Agent      ──► Google Doc (Reimbursement)
└── Research & Clinical Evidence Agent ──► Google Doc (Clinical)
                                              └──────────► Master Google Sheet
```

---

## Research Domains

Each domain has a dedicated agent with its own source tier list, system prompt, and output schema.

| Domain | Coverage |
|--------|----------|
| **Policy & Regulation** | CMS, ONC, FDA rulemaking, and federal health legislation — with structured stakeholder position framing |
| **Industry Trends** | Healthcare market shifts, M&A activity, digital health investment, and payer-provider dynamics |
| **Jobs & Careers in Health Data** | Labor market signals for clinical analysts, health informatics professionals, and health AI roles |
| **AI in Healthcare** | LLM and ML deployment trends, clinical decision support, AI governance, and FDA digital health approvals |
| **Women's Health & FemTech** | PCOS, maternal outcomes, reproductive health policy, FemTech product activity, and equity gaps |
| **Reimbursement & Payment Models** | HEDIS, value-based care contracts, capitation, shared savings, and Medicaid/Medicare policy changes |
| **Research & Clinical Evidence** | Peer-reviewed trials, SDOH studies, EHR-based research, and outcomes analytics |

---

## Tech Stack

### Tools & Frameworks

| Layer | Stack |
|-------|-------|
| **AI / LLM** | Claude (Anthropic) via Claude Code |
| **Agent Framework** | Custom WAT (Workflows, Agents, Tools) |
| **IDE** | Cursor + Claude Code CLI |
| **Output Integrations** | Google Docs API, Google Sheets API |
| **Languages** | Python, SQL |
| **Architecture Pattern** | Orchestrator + parallel subagents |
| **Documentation** | `ARCHITECTURE.md` with ASCII system diagrams |

### Healthcare & Compliance Context

| Area | Approach |
|------|----------|
| **Data Standards** | FHIR-aware output design where applicable |
| **Privacy** | HIPAA-aware architecture; no PHI is processed or stored |
| **Domain Grounding** | Output schemas tied to real healthcare use cases (VBC, SDOH, FemTech, reimbursement) |

---

## Use Cases

- **Healthcare product and strategy teams** — track regulatory and reimbursement changes relevant to product positioning without manual monitoring
- **Clinical data analysts** — access synthesized, structured evidence summaries tied to outcomes analytics and payment models
- **Health AI practitioners** — follow AI/ML governance developments, FDA approval trends, and deployment benchmarks across the industry
- **FemTech teams and researchers** — monitor women's health policy, market activity, and equity-focused research in a single feed
- **Health informatics professionals** — automate domain intelligence gathering into shareable, organized Google Workspace documents

---

## Getting Started

### Prerequisites

- Python 3.10+
- Claude API key (Anthropic)
- Google Cloud project with Docs and Sheets APIs enabled
- Service account credentials (JSON)
- Claude Code CLI installed

### Installation

```bash
git clone https://github.com/your-username/multiagent-healthcare-research-system
cd multiagent-healthcare-research-system
pip install -r requirements.txt
cp .env.example .env                     # Add your API keys
python setup/init_google_docs.py         # Initialize output documents
```

### Run

```bash
python orchestrator.py --run-all          # Full research cycle across all domains
python orchestrator.py --domain femtech   # Single domain run
python orchestrator.py --dry-run          # Preview outputs without writing to Docs
```

See `ARCHITECTURE.md` for full system design, source tier configuration, and per-agent prompt schema.

---

## Future Improvements

Planned enhancements as the system matures beyond prototype:

- **Statement-level citations** — link each synthesized claim back to a specific source URL and retrieval timestamp
- **Confidence scoring** — surface a per-summary confidence indicator based on source tier distribution and coverage breadth
- **Human-in-the-loop review** — add an optional review gate before outputs are written to Google Docs, supporting analyst oversight
- **Monitoring dashboard** — lightweight run dashboard showing agent status, source counts, and output freshness across all domains
- **Scheduled automation** — cron or cloud-trigger-based scheduling so the pipeline runs on a defined cadence without manual invocation
- **Cloud / container deployment** — containerize the pipeline (Docker) and deploy to a cloud environment for persistent, scalable execution

---

## Disclaimer

This system is designed for **research synthesis and workflow automation only**. It does not provide clinical, medical, legal, or regulatory advice. Outputs are AI-generated summaries intended to support human research and analysis — not to replace professional judgment. All outputs should be reviewed and validated before informing any clinical, policy, or business decision.

---

*Built by a healthcare data analyst with expertise in clinical informatics, health data engineering, and applied AI. Focused on making healthcare intelligence more structured, accessible, and actionable.*
