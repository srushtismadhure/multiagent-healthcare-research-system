# AI in Healthcare — Research Workflow SOP

**Bucket:** AI in Healthcare  
**Agent:** `agents/ai_agent.md`  
**Run frequency:** Weekly (or on-demand)

---

## Objective

Track what healthcare AI implementations are working in production, what is failing, what regulators are doing, and what lessons are emerging from deployments, pilots, and public setbacks.

---

## Search Queries

1. `FDA AI medical device approval 2025`
2. `ambient AI clinical documentation production`
3. `radiology AI detection accuracy real world`
4. `AI prior authorization automation healthcare`
5. `LLM clinical notes hallucination failure`
6. `AI bias healthcare FDA warning`
7. `FHIR interoperability AI integration`
8. `OpenAI Google Anthropic healthcare product`
9. `AI governance health system framework`
10. `NEJM AI clinical study 2025`

---

## Sources to Hit

| Source | URL | What to Pull |
|--------|-----|--------------|
| FDA AI/ML Device List | https://www.fda.gov/medical-devices/software-medical-device-samd/artificial-intelligence-and-machine-learning-aiml-enabled-medical-devices | New approvals, clearances, or other device actions |
| STAT News | https://www.statnews.com | AI criticism and failure reporting |
| NEJM | https://www.nejm.org | Clinical AI study results |
| Health Tech Magazine | https://healthtechmagazine.net | Enterprise deployment stories |
| Chief Healthcare Executive | https://www.chiefhealthcareexecutive.com | Leadership implementation views |
| NVIDIA Blog | https://blogs.nvidia.com/blog/category/healthcare | Infrastructure and vendor positioning |
| IEEE Spectrum | https://spectrum.ieee.org | Technical AI health reporting |
| Reddit r/MachineLearning | Reddit | Researcher reaction |
| Reddit r/medicine | Reddit | Clinician reaction |

---

## Structured Output Contract

The workflow should produce structured findings that can support:

- Summary
- Key Findings
- What This Means
- Limitations

Use a backing markdown table or equivalent structured rows with these fields:

| AI Use Case | Status (Working/Failed/Experimental) | What Went Wrong (if applicable) | Lesson Learned | Urgency / Time Sensitivity | Recommended Action | Confidence | Source Quality Tier | Source Link |
|-------------|--------------------------------------|----------------------------------|----------------|----------------------------|-------------------|------------|---------------------|-------------|

Field notes:
- **Urgency / Time Sensitivity** is heuristic. New warnings, approvals, removals, or serious failures may be `Breaking`.
- **Recommended Action** may be an orchestrator interpretation when current tooling only exposes shallow evidence.
- **Confidence** should reflect source quality plus extraction depth.
- **Source Quality Tier** should map to `memory/source_quality.md`.

---

## Focus Areas

Prioritize:
1. Production deployments over hype
2. Failures and corrective actions
3. Ambient AI and documentation tools
4. Prior authorization automation
5. AI bias affecting women or underrepresented patients

---

## Edge Cases

- FDA actions may be irregular; if nothing is new, note the most recent material action
- If only a headline or shallow snippet is accessible, say so clearly
- Distinguish FDA clearance from FDA approval
