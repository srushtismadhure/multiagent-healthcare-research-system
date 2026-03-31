from __future__ import annotations

from collections import Counter, OrderedDict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Any
from urllib.parse import urlparse


PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
OUTPUT_SCHEMAS_PATH = PROJECT_ROOT / "memory" / "output_schemas.md"

PLACEHOLDER = "Not available from current tool output"
NO_RESULTS_MESSAGE = "No results returned from current tool output"

NEWS_PAGE_SIZE = 5
REDDIT_QUERY_LIMIT = 3
REDDIT_POST_LIMIT = 3
PUBMED_MAX_PER_QUERY = 3
JOURNAL_MAX_PER_QUERY = 2
MAX_KEY_FINDINGS = 4
MAX_IMPLICATIONS = 3
MAX_BACKING_ROWS = 5
SUMMARY_TOPIC_COUNT = 3


@dataclass(frozen=True)
class BucketSpec:
    bucket_id: str
    name: str
    agent_path: Path
    workflow_path: Path
    tools: tuple[str, ...]
    columns: tuple[str, ...]


@dataclass
class BucketResult:
    spec: BucketSpec
    section_markdown: str
    sources: list[str]
    status: str


@dataclass
class NormalizedBucketData:
    rows: list[dict[str, str]]
    sources: list[str]
    warnings: list[str]


def main() -> int:
    run_started_at = datetime.now(timezone.utc)
    run_id = run_started_at.strftime("%Y%m%d_%H%M%S")
    run_metadata = {
        "run_date": run_started_at.strftime("%Y-%m-%d"),
        "run_time": run_started_at.strftime("%H:%M:%S UTC"),
        "run_id": run_id,
        "run_started_at": run_started_at,
    }

    schema_map = load_output_schema_map()
    bucket_registry = build_bucket_registry(schema_map)

    bucket_sections: list[str] = []
    all_sources: list[str] = []

    for bucket_spec in bucket_registry:
        bucket_result = run_bucket(bucket_spec)
        bucket_sections.append(bucket_result.section_markdown)
        all_sources.extend(bucket_result.sources)

    master_report = build_master_report(run_metadata, bucket_sections, all_sources)
    output_path = write_output_file(master_report, run_metadata)
    print(output_path)
    return 0


def build_bucket_registry(schema_map: dict[str, tuple[str, ...]]) -> list[BucketSpec]:
    return [
        BucketSpec(
            bucket_id="policy",
            name="Policy and Regulation",
            agent_path=PROJECT_ROOT / "agents" / "policy_agent.md",
            workflow_path=PROJECT_ROOT / "workflows" / "policy_workflow.md",
            tools=("search_news", "scrape_web"),
            columns=schema_map["Policy and Regulation"],
        ),
        BucketSpec(
            bucket_id="industry",
            name="Industry Trends and Market Movement",
            agent_path=PROJECT_ROOT / "agents" / "industry_agent.md",
            workflow_path=PROJECT_ROOT / "workflows" / "industry_workflow.md",
            tools=("search_news", "scrape_web"),
            columns=schema_map["Industry Trends and Market Movement"],
        ),
        BucketSpec(
            bucket_id="jobs",
            name="Jobs, Careers, and Workforce",
            agent_path=PROJECT_ROOT / "agents" / "jobs_agent.md",
            workflow_path=PROJECT_ROOT / "workflows" / "jobs_workflow.md",
            tools=("search_news", "search_reddit", "scrape_web"),
            columns=schema_map["Jobs, Careers, and Workforce"],
        ),
        BucketSpec(
            bucket_id="ai",
            name="AI in Healthcare",
            agent_path=PROJECT_ROOT / "agents" / "ai_agent.md",
            workflow_path=PROJECT_ROOT / "workflows" / "ai_healthcare_workflow.md",
            tools=("search_news", "search_reddit", "scrape_web"),
            columns=schema_map["AI in Healthcare"],
        ),
        BucketSpec(
            bucket_id="reimbursement",
            name="Reimbursement and Payment Models",
            agent_path=PROJECT_ROOT / "agents" / "reimbursement_agent.md",
            workflow_path=PROJECT_ROOT / "workflows" / "reimbursement_workflow.md",
            tools=("search_news", "scrape_web"),
            columns=schema_map["Reimbursement and Payment Models"],
        ),
        BucketSpec(
            bucket_id="research",
            name="Research & Clinical Evidence",
            agent_path=PROJECT_ROOT / "agents" / "research_clinical_evidence_agent.md",
            workflow_path=PROJECT_ROOT / "workflows" / "research_clinical_evidence.md",
            tools=("pubmed_fetcher", "journal_scraper"),
            columns=schema_map["Research & Clinical Evidence"],
        ),
        BucketSpec(
            bucket_id="women_health",
            name="Women's Health",
            agent_path=PROJECT_ROOT / "agents" / "women_health_agent.md",
            workflow_path=PROJECT_ROOT / "workflows" / "women_health_workflow.md",
            tools=("search_news", "search_reddit", "scrape_web"),
            columns=schema_map["Women's Health"],
        ),
    ]


def load_output_schema_map() -> dict[str, tuple[str, ...]]:
    schema_text = load_text_file(OUTPUT_SCHEMAS_PATH)
    pattern = re.compile(
        r"^## Bucket \d+: (?P<bucket>.+?)\n\n```markdown\n(?P<table>.+?)\n```",
        re.MULTILINE | re.DOTALL,
    )

    schema_map: dict[str, tuple[str, ...]] = {}
    for match in pattern.finditer(schema_text):
        bucket_name = match.group("bucket").strip()
        table_header = match.group("table").strip().splitlines()[0]
        columns = tuple(column.strip() for column in table_header.strip("|").split("|"))
        schema_map[bucket_name] = columns

    return schema_map


def load_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def run_bucket(bucket_spec: BucketSpec) -> BucketResult:
    try:
        agent_text = load_text_file(bucket_spec.agent_path)
        workflow_text = load_text_file(bucket_spec.workflow_path)

        queries = extract_queries_from_workflow(workflow_text)
        source_urls = extract_source_urls_from_workflow(workflow_text)
        subreddits = extract_subreddits(agent_text, workflow_text)

        raw_outputs: dict[str, list[dict[str, Any]]] = {
            "news": [],
            "scrapes": [],
            "reddit": [],
            "pubmed": [],
            "journals": [],
        }
        tool_errors: list[str] = []

        for tool_name in bucket_spec.tools:
            try:
                if tool_name == "search_news":
                    raw_outputs["news"] = run_news_tool(queries)
                elif tool_name == "scrape_web":
                    raw_outputs["scrapes"] = run_scrape_tool(source_urls)
                elif tool_name == "search_reddit":
                    raw_outputs["reddit"] = run_reddit_tool(subreddits, queries)
                elif tool_name == "pubmed_fetcher":
                    raw_outputs["pubmed"] = run_pubmed_tool(queries)
                elif tool_name == "journal_scraper":
                    raw_outputs["journals"] = run_journal_tool(queries)
            except Exception as exc:  # noqa: BLE001
                tool_errors.append(f"{tool_name}: {exc}")

        normalized_data = normalize_tool_outputs(bucket_spec.bucket_id, bucket_spec, raw_outputs)
        combined_warnings = unique_list(normalized_data.warnings + tool_errors)

        if not normalized_data.rows and combined_warnings:
            reason = "; ".join(combined_warnings)
            section_markdown = generate_incomplete_section(bucket_spec.name, reason)
            return BucketResult(
                spec=bucket_spec,
                section_markdown=section_markdown,
                sources=[],
                status="incomplete",
            )

        section_markdown = generate_bucket_section(bucket_spec, normalized_data, combined_warnings)
        return BucketResult(
            spec=bucket_spec,
            section_markdown=section_markdown,
            sources=normalized_data.sources,
            status="complete",
        )
    except Exception as exc:  # noqa: BLE001
        return BucketResult(
            spec=bucket_spec,
            section_markdown=generate_incomplete_section(bucket_spec.name, str(exc)),
            sources=[],
            status="incomplete",
        )


def run_news_tool(queries: list[str]) -> list[dict[str, Any]]:
    from tools.search_news import search_news

    results: list[dict[str, Any]] = []
    for query in queries:
        articles = search_news(query, page_size=NEWS_PAGE_SIZE)
        for article in articles:
            article_copy = dict(article)
            article_copy["_query"] = query
            results.append(article_copy)
    return results


def run_scrape_tool(source_urls: list[str]) -> list[dict[str, Any]]:
    from tools.scrape_web import scrape_multiple

    if not source_urls:
        return []
    return scrape_multiple(source_urls)


def run_reddit_tool(subreddits: list[str], queries: list[str]) -> list[dict[str, Any]]:
    from tools.search_reddit import search_subreddit

    results: list[dict[str, Any]] = []
    bounded_queries = queries[:REDDIT_QUERY_LIMIT]

    for subreddit in subreddits:
        for query in bounded_queries:
            posts = search_subreddit(subreddit, query, limit=REDDIT_POST_LIMIT)
            for post in posts:
                post_copy = dict(post)
                post_copy["_query"] = query
                results.append(post_copy)
    return results


def run_pubmed_tool(queries: list[str]) -> list[dict[str, Any]]:
    from tools.pubmed_fetcher import fetch_multiple_queries

    return fetch_multiple_queries(queries, max_per_query=PUBMED_MAX_PER_QUERY)


def run_journal_tool(queries: list[str]) -> list[dict[str, Any]]:
    from tools.journal_scraper import fetch_all_journals

    results: list[dict[str, Any]] = []
    for query in queries:
        matches = fetch_all_journals(query, max_per_journal=JOURNAL_MAX_PER_QUERY)
        for match in matches:
            match_copy = dict(match)
            match_copy["_query"] = query
            results.append(match_copy)
    return results


def normalize_tool_outputs(
    bucket_id: str,
    bucket_spec: BucketSpec,
    raw_outputs: dict[str, list[dict[str, Any]]],
) -> NormalizedBucketData:
    if bucket_id == "policy":
        return normalize_policy_bucket(bucket_spec, raw_outputs)
    if bucket_id == "industry":
        return normalize_industry_bucket(bucket_spec, raw_outputs)
    if bucket_id == "jobs":
        return normalize_jobs_bucket(bucket_spec, raw_outputs)
    if bucket_id == "ai":
        return normalize_ai_bucket(bucket_spec, raw_outputs)
    if bucket_id == "reimbursement":
        return normalize_reimbursement_bucket(bucket_spec, raw_outputs)
    if bucket_id == "research":
        return normalize_research_bucket(bucket_spec, raw_outputs)
    if bucket_id == "women_health":
        return normalize_women_health_bucket(bucket_spec, raw_outputs)

    raise ValueError(f"Unsupported bucket id: {bucket_id}")


def normalize_policy_bucket(
    bucket_spec: BucketSpec,
    raw_outputs: dict[str, list[dict[str, Any]]],
) -> NormalizedBucketData:
    rows: list[dict[str, str]] = []
    warnings = collect_scrape_warnings(raw_outputs["scrapes"])

    for article in raw_outputs["news"]:
        rows.append(
            {
                "Policy Name": required_value(article.get("title")),
                "Date": normalize_date(article.get("published_at")),
                "Summary": summarize_text(article.get("description")) or PLACEHOLDER,
                "Democratic Framing": PLACEHOLDER,
                "Republican Framing": PLACEHOLDER,
                "Forum/Reddit Sentiment": PLACEHOLDER,
                "Confidence": infer_confidence(url=article.get("url"), source_name=article.get("source")),
                "Source Link": required_value(article.get("url")),
                "__origin": "news",
                "__source_name": required_value(article.get("source")),
                "__query": required_value(article.get("_query")),
            }
        )

    for scrape in valid_scrape_rows(raw_outputs["scrapes"]):
        rows.append(
            {
                "Policy Name": required_value(scrape.get("title")),
                "Date": PLACEHOLDER,
                "Summary": summarize_text(scrape.get("text")) or PLACEHOLDER,
                "Democratic Framing": PLACEHOLDER,
                "Republican Framing": PLACEHOLDER,
                "Forum/Reddit Sentiment": PLACEHOLDER,
                "Confidence": infer_confidence(url=scrape.get("url")),
                "Source Link": required_value(scrape.get("url")),
                "__origin": "scrape",
            }
        )

    return finalize_normalized_bucket(bucket_spec, rows, warnings)


def normalize_industry_bucket(
    bucket_spec: BucketSpec,
    raw_outputs: dict[str, list[dict[str, Any]]],
) -> NormalizedBucketData:
    rows: list[dict[str, str]] = []
    warnings = collect_scrape_warnings(raw_outputs["scrapes"])

    for article in raw_outputs["news"]:
        rows.append(
            {
                "Trend": required_value(article.get("title")),
                "What's Shifting": summarize_text(article.get("description")) or PLACEHOLDER,
                "Key Data Point": PLACEHOLDER,
                "Implication for Women's Health/Chronic Pain": PLACEHOLDER,
                "Confidence": infer_confidence(url=article.get("url"), source_name=article.get("source")),
                "Source Link": required_value(article.get("url")),
                "__origin": "news",
                "__source_name": required_value(article.get("source")),
                "__query": required_value(article.get("_query")),
            }
        )

    for scrape in valid_scrape_rows(raw_outputs["scrapes"]):
        rows.append(
            {
                "Trend": required_value(scrape.get("title")),
                "What's Shifting": summarize_text(scrape.get("text")) or PLACEHOLDER,
                "Key Data Point": PLACEHOLDER,
                "Implication for Women's Health/Chronic Pain": PLACEHOLDER,
                "Confidence": infer_confidence(url=scrape.get("url")),
                "Source Link": required_value(scrape.get("url")),
                "__origin": "scrape",
            }
        )

    return finalize_normalized_bucket(bucket_spec, rows, warnings)


def normalize_jobs_bucket(
    bucket_spec: BucketSpec,
    raw_outputs: dict[str, list[dict[str, Any]]],
) -> NormalizedBucketData:
    rows: list[dict[str, str]] = []
    warnings = collect_scrape_warnings(raw_outputs["scrapes"])

    for article in raw_outputs["news"]:
        rows.append(
            {
                "Role/Skill": required_value(article.get("title")),
                "Trend Direction (Growing/Declining)": PLACEHOLDER,
                "Key Employers Hiring": PLACEHOLDER,
                "Recommended Action": PLACEHOLDER,
                "Confidence": infer_confidence(url=article.get("url"), source_name=article.get("source")),
                "Source Link": required_value(article.get("url")),
                "__origin": "news",
                "__source_name": required_value(article.get("source")),
                "__query": required_value(article.get("_query")),
            }
        )

    for scrape in valid_scrape_rows(raw_outputs["scrapes"]):
        rows.append(
            {
                "Role/Skill": required_value(scrape.get("title")),
                "Trend Direction (Growing/Declining)": PLACEHOLDER,
                "Key Employers Hiring": PLACEHOLDER,
                "Recommended Action": PLACEHOLDER,
                "Confidence": infer_confidence(url=scrape.get("url")),
                "Source Link": required_value(scrape.get("url")),
                "__origin": "scrape",
            }
        )

    for post in raw_outputs["reddit"]:
        rows.append(
            {
                "Role/Skill": required_value(post.get("title")),
                "Trend Direction (Growing/Declining)": PLACEHOLDER,
                "Key Employers Hiring": PLACEHOLDER,
                "Recommended Action": PLACEHOLDER,
                "Confidence": "Low",
                "Source Link": required_value(post.get("permalink")),
                "__origin": "reddit",
                "__query": required_value(post.get("_query")),
            }
        )

    return finalize_normalized_bucket(bucket_spec, rows, warnings)


def normalize_ai_bucket(
    bucket_spec: BucketSpec,
    raw_outputs: dict[str, list[dict[str, Any]]],
) -> NormalizedBucketData:
    rows: list[dict[str, str]] = []
    warnings = collect_scrape_warnings(raw_outputs["scrapes"])

    for article in raw_outputs["news"]:
        summary_text = " ".join(filter(None, [article.get("title"), article.get("description")]))
        status = infer_ai_status(summary_text)
        rows.append(
            {
                "AI Use Case": required_value(article.get("title")),
                "Status (Working/Failed/Experimental)": status,
                "What Went Wrong (if applicable)": summarize_failure_reason(summary_text, status),
                "Lesson Learned": PLACEHOLDER,
                "Confidence": infer_confidence(url=article.get("url"), source_name=article.get("source")),
                "Source Link": required_value(article.get("url")),
                "__origin": "news",
                "__source_name": required_value(article.get("source")),
                "__query": required_value(article.get("_query")),
            }
        )

    for scrape in valid_scrape_rows(raw_outputs["scrapes"]):
        summary_text = " ".join(filter(None, [scrape.get("title"), summarize_text(scrape.get("text"))]))
        status = infer_ai_status(summary_text)
        rows.append(
            {
                "AI Use Case": required_value(scrape.get("title")),
                "Status (Working/Failed/Experimental)": status,
                "What Went Wrong (if applicable)": summarize_failure_reason(summary_text, status),
                "Lesson Learned": PLACEHOLDER,
                "Confidence": infer_confidence(url=scrape.get("url")),
                "Source Link": required_value(scrape.get("url")),
                "__origin": "scrape",
            }
        )

    for post in raw_outputs["reddit"]:
        summary_text = " ".join(filter(None, [post.get("title"), post.get("selftext_preview")]))
        status = infer_ai_status(summary_text)
        rows.append(
            {
                "AI Use Case": required_value(post.get("title")),
                "Status (Working/Failed/Experimental)": status,
                "What Went Wrong (if applicable)": summarize_failure_reason(summary_text, status),
                "Lesson Learned": PLACEHOLDER,
                "Confidence": "Low",
                "Source Link": required_value(post.get("permalink")),
                "__origin": "reddit",
                "__query": required_value(post.get("_query")),
            }
        )

    return finalize_normalized_bucket(bucket_spec, rows, warnings)


def normalize_reimbursement_bucket(
    bucket_spec: BucketSpec,
    raw_outputs: dict[str, list[dict[str, Any]]],
) -> NormalizedBucketData:
    rows: list[dict[str, str]] = []
    warnings = collect_scrape_warnings(raw_outputs["scrapes"])

    for article in raw_outputs["news"]:
        rows.append(
            {
                "Payment Model": required_value(article.get("title")),
                "What Changed": summarize_text(article.get("description")) or PLACEHOLDER,
                "Who It Affects": PLACEHOLDER,
                "Women's Health / Chronic Pain Relevance": PLACEHOLDER,
                "Confidence": infer_confidence(url=article.get("url"), source_name=article.get("source")),
                "Source Link": required_value(article.get("url")),
                "__origin": "news",
                "__source_name": required_value(article.get("source")),
                "__query": required_value(article.get("_query")),
            }
        )

    for scrape in valid_scrape_rows(raw_outputs["scrapes"]):
        rows.append(
            {
                "Payment Model": required_value(scrape.get("title")),
                "What Changed": summarize_text(scrape.get("text")) or PLACEHOLDER,
                "Who It Affects": PLACEHOLDER,
                "Women's Health / Chronic Pain Relevance": PLACEHOLDER,
                "Confidence": infer_confidence(url=scrape.get("url")),
                "Source Link": required_value(scrape.get("url")),
                "__origin": "scrape",
            }
        )

    return finalize_normalized_bucket(bucket_spec, rows, warnings)


def normalize_research_bucket(
    bucket_spec: BucketSpec,
    raw_outputs: dict[str, list[dict[str, Any]]],
) -> NormalizedBucketData:
    rows: list[dict[str, str]] = []

    for study in raw_outputs["pubmed"]:
        rows.append(
            {
                "Study Title": required_value(study.get("title")),
                "Authors": required_value(study.get("authors")),
                "Journal": required_value(study.get("journal")),
                "Publication Date": normalize_date(study.get("pub_date")),
                "Plain-English Source Note": build_pubmed_note(study),
                "Confidence": infer_confidence(url=study.get("url"), from_pubmed=True),
                "Source Link": required_value(study.get("url")),
                "__origin": "pubmed",
                "__query": required_value(study.get("_query")),
            }
        )

    for article in raw_outputs["journals"]:
        rows.append(
            {
                "Study Title": required_value(article.get("title")),
                "Authors": required_value(article.get("authors")),
                "Journal": required_value(article.get("journal")),
                "Publication Date": normalize_date(article.get("pub_date")),
                "Plain-English Source Note": build_journal_note(article),
                "Confidence": infer_research_confidence(article),
                "Source Link": required_value(article.get("url")),
                "__origin": "journal",
                "__is_preprint": "true" if article.get("is_preprint") else "",
                "__query": required_value(article.get("_query")),
            }
        )

    return finalize_normalized_bucket(bucket_spec, rows, warnings=[])


def normalize_women_health_bucket(
    bucket_spec: BucketSpec,
    raw_outputs: dict[str, list[dict[str, Any]]],
) -> NormalizedBucketData:
    rows: list[dict[str, str]] = []
    warnings = collect_scrape_warnings(raw_outputs["scrapes"])

    for article in raw_outputs["news"]:
        text = " ".join(filter(None, [article.get("title"), article.get("description")]))
        rows.append(
            {
                "Topic": required_value(article.get("title")),
                "Category (Policy/Clinical/Market/Care Gap)": infer_women_health_category(text, article.get("url")),
                "Finding": summarize_text(article.get("description")) or PLACEHOLDER,
                "Who It Affects": PLACEHOLDER,
                "Policy/Market/Clinical Implication": PLACEHOLDER,
                "Confidence": infer_confidence(url=article.get("url"), source_name=article.get("source")),
                "Source Link": required_value(article.get("url")),
                "__origin": "news",
                "__source_name": required_value(article.get("source")),
                "__query": required_value(article.get("_query")),
            }
        )

    for scrape in valid_scrape_rows(raw_outputs["scrapes"]):
        text = " ".join(filter(None, [scrape.get("title"), summarize_text(scrape.get("text"))]))
        rows.append(
            {
                "Topic": required_value(scrape.get("title")),
                "Category (Policy/Clinical/Market/Care Gap)": infer_women_health_category(text, scrape.get("url")),
                "Finding": summarize_text(scrape.get("text")) or PLACEHOLDER,
                "Who It Affects": PLACEHOLDER,
                "Policy/Market/Clinical Implication": PLACEHOLDER,
                "Confidence": infer_confidence(url=scrape.get("url")),
                "Source Link": required_value(scrape.get("url")),
                "__origin": "scrape",
            }
        )

    for post in raw_outputs["reddit"]:
        text = " ".join(filter(None, [post.get("title"), post.get("selftext_preview")]))
        rows.append(
            {
                "Topic": required_value(post.get("title")),
                "Category (Policy/Clinical/Market/Care Gap)": infer_women_health_category(text, post.get("permalink")),
                "Finding": summarize_text(post.get("selftext_preview")) or PLACEHOLDER,
                "Who It Affects": PLACEHOLDER,
                "Policy/Market/Clinical Implication": PLACEHOLDER,
                "Confidence": "Low",
                "Source Link": required_value(post.get("permalink")),
                "__origin": "reddit",
                "__query": required_value(post.get("_query")),
            }
        )

    return finalize_normalized_bucket(bucket_spec, rows, warnings)


def finalize_normalized_bucket(
    bucket_spec: BucketSpec,
    rows: list[dict[str, str]],
    warnings: list[str],
) -> NormalizedBucketData:
    cleaned_rows = []
    seen_keys: set[tuple[str, str]] = set()

    for row in rows:
        populated_row = {column: row.get(column, PLACEHOLDER) or PLACEHOLDER for column in bucket_spec.columns}
        for extra_key, extra_value in row.items():
            if extra_key.startswith("__"):
                populated_row[extra_key] = extra_value
        source_link = populated_row.get("Source Link", PLACEHOLDER)
        primary_value = populated_row.get(bucket_spec.columns[0], PLACEHOLDER)
        dedupe_key = (primary_value, source_link)
        if dedupe_key in seen_keys:
            continue
        seen_keys.add(dedupe_key)
        cleaned_rows.append(populated_row)

    if not cleaned_rows and not warnings:
        cleaned_rows.append(build_placeholder_row(bucket_spec.columns, NO_RESULTS_MESSAGE))

    sources = [
        row["Source Link"]
        for row in cleaned_rows
        if row.get("Source Link") and row.get("Source Link") != PLACEHOLDER
    ]

    return NormalizedBucketData(
        rows=cleaned_rows,
        sources=unique_list(sources),
        warnings=unique_list(warnings),
    )


def generate_bucket_section(
    bucket_spec: BucketSpec,
    normalized_data: NormalizedBucketData,
    warnings: list[str],
) -> str:
    lines = [f"## Bucket: {bucket_spec.name}", ""]
    real_rows = get_meaningful_rows(bucket_spec, normalized_data.rows)

    lines.extend(
        [
            "### Summary",
            build_bucket_summary(bucket_spec, real_rows, warnings),
            "",
            "### Key Findings",
            *build_key_findings(bucket_spec, real_rows),
            "",
            "### What This Means",
            *build_what_this_means(bucket_spec, real_rows),
            "",
            "### Limitations",
            *build_limitations(bucket_spec, normalized_data.rows, warnings),
        ]
    )

    if real_rows:
        lines.extend(["", "### Backing Table (Optional)"])
        if len(real_rows) > MAX_BACKING_ROWS:
            lines.append(f"_Showing {MAX_BACKING_ROWS} of {len(real_rows)} normalized findings._")
            lines.append("")
        lines.append(render_backing_table(bucket_spec.columns, real_rows[:MAX_BACKING_ROWS]))

    return "\n".join(lines)


def build_master_report(
    run_metadata: dict[str, Any],
    bucket_sections: list[str],
    sources: list[str],
) -> str:
    lines = [
        "# Healthcare Research Intelligence Report",
        f"Run Date: {run_metadata['run_date']}",
        f"Run Time: {run_metadata['run_time']}",
        f"Run ID: {run_metadata['run_id']}",
        "",
    ]

    for section in bucket_sections:
        lines.append(section)
        lines.append("")

    lines.extend(["## Sources Cited", ""])
    unique_sources = unique_list(sources)
    if unique_sources:
        for index, source in enumerate(unique_sources, start=1):
            lines.append(f"{index}. {source}")
    else:
        lines.append("None")

    return "\n".join(lines).rstrip() + "\n"


def write_output_file(markdown_text: str, run_metadata: dict[str, Any]) -> Path:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUTS_DIR / f"{run_metadata['run_date']}_{run_metadata['run_id'].split('_', 1)[1]}_research_report.md"
    output_path.write_text(markdown_text, encoding="utf-8")
    return output_path


def generate_incomplete_section(bucket_name: str, reason: str) -> str:
    clean_reason = summarize_text(reason, max_length=240) or "Unknown error"
    return "\n".join(
        [
            f"## Bucket: {bucket_name}",
            "",
            "### Summary",
            f"INCOMPLETE — {clean_reason}",
            "",
            "### Key Findings",
            "- No structured findings were assembled for this bucket during this run.",
            "",
            "### What This Means",
            "- This bucket should be treated as incomplete coverage for the current report.",
            "",
            "### Limitations",
            f"- Retrieval failed: {clean_reason}",
        ]
    )


def extract_queries_from_workflow(workflow_text: str) -> list[str]:
    section_lines = extract_section_lines(workflow_text, (r"Search Queries",))
    queries: list[str] = []

    for line in section_lines:
        match = re.match(r"^\s*\d+\.\s+(.*)$", line.strip())
        if not match:
            continue
        query = match.group(1).strip().strip("`")
        if query:
            queries.append(query)

    return queries


def extract_source_urls_from_workflow(workflow_text: str) -> list[str]:
    section_lines = extract_section_lines(
        workflow_text,
        (r"Sources to Hit(?: \(in order\))?", r"Supported Sources to Hit"),
    )
    urls: list[str] = []

    for line in section_lines:
        for match in re.findall(r"https?://[^\s|)]+", line):
            urls.append(match.rstrip(".,"))

    return unique_list(urls)


def extract_subreddits(agent_text: str, workflow_text: str) -> list[str]:
    matches = re.findall(r"\br/([A-Za-z0-9_]+)\b", f"{agent_text}\n{workflow_text}")
    return unique_list(matches)


def extract_section_lines(workflow_text: str, heading_patterns: tuple[str, ...]) -> list[str]:
    lines = workflow_text.splitlines()
    capturing = False
    captured: list[str] = []
    compiled = [re.compile(rf"^##\s+{pattern}\s*$", re.IGNORECASE) for pattern in heading_patterns]

    for line in lines:
        stripped = line.strip()
        if not capturing and any(pattern.match(stripped) for pattern in compiled):
            capturing = True
            continue

        if capturing and re.match(r"^##\s+", stripped):
            break

        if capturing:
            captured.append(line)

    return captured


def render_markdown_table(columns: tuple[str, ...], rows: list[dict[str, str]]) -> str:
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("-" * len(column) for column in columns) + " |"
    body = [
        "| " + " | ".join(escape_markdown_cell(row.get(column, PLACEHOLDER)) for column in columns) + " |"
        for row in rows
    ]
    return "\n".join([header, separator, *body])


def escape_markdown_cell(value: str) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|")


def build_placeholder_row(columns: tuple[str, ...], first_column_value: str) -> dict[str, str]:
    row = {column: PLACEHOLDER for column in columns}
    row[columns[0]] = first_column_value
    if "Source Link" in row:
        row["Source Link"] = PLACEHOLDER
    return row


def collect_scrape_warnings(scrapes: list[dict[str, Any]]) -> list[str]:
    warnings: list[str] = []
    for scrape in scrapes:
        if scrape.get("error"):
            warnings.append(f"scrape_web: {scrape['url']} -> {scrape['error']}")
    return warnings


def valid_scrape_rows(scrapes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    valid_rows = []
    for scrape in scrapes:
        if scrape.get("error"):
            continue
        if not scrape.get("url") or not scrape.get("title"):
            continue
        valid_rows.append(scrape)
    return valid_rows


def build_pubmed_note(study: dict[str, Any]) -> str:
    summary_field = summarize_text(study.get("abstract_summary"))
    if summary_field and summary_field != study.get("journal"):
        return summary_field
    query = study.get("_query")
    if query:
        return f"PubMed metadata record returned for query '{query}'. Limited summary text is available from the current tool output."
    return "PubMed metadata record. Limited summary text is available from the current tool output."


def build_journal_note(article: dict[str, Any]) -> str:
    abstract_text = summarize_text(article.get("abstract"))
    if abstract_text:
        return abstract_text
    if article.get("is_preprint"):
        return "PREPRINT. Limited metadata returned by current tool output."
    return "Limited metadata returned by current tool output."


def infer_research_confidence(article: dict[str, Any]) -> str:
    if article.get("is_preprint"):
        return "Low"
    if summarize_text(article.get("abstract")):
        return "High"
    return "Medium"


def infer_ai_status(text: str) -> str:
    lowered = text.lower()
    failed_markers = ("warning", "failed", "failure", "bias", "biased", "harm", "hallucination", "recall", "pulled")
    experimental_markers = ("pilot", "experimental", "trial", "study", "research", "prototype")
    working_markers = ("production", "deployed", "implemented", "rollout", "live", "approved", "clearance")

    if any(marker in lowered for marker in failed_markers):
        return "Failed"
    if any(marker in lowered for marker in working_markers):
        return "Working"
    if any(marker in lowered for marker in experimental_markers):
        return "Experimental"
    return PLACEHOLDER


def summarize_failure_reason(text: str, status: str) -> str:
    if status != "Failed":
        return PLACEHOLDER
    return summarize_text(text) or PLACEHOLDER


def infer_women_health_category(text: str, url: str | None) -> str:
    lowered = f"{text} {url or ''}".lower()

    policy_markers = ("policy", "law", "bill", "medicaid", "regulation", "coverage", "legislation", "state")
    clinical_markers = ("guideline", "clinical", "study", "trial", "acog", "pubmed", "diagnosis")
    market_markers = ("funding", "startup", "femtech", "market", "investment", "launch", "product")
    care_gap_markers = ("desert", "access", "shortage", "mortality", "care gap", "underdiagnosis", "undertreatment")

    if any(marker in lowered for marker in policy_markers):
        return "Policy"
    if any(marker in lowered for marker in clinical_markers):
        return "Clinical"
    if any(marker in lowered for marker in market_markers):
        return "Market"
    if any(marker in lowered for marker in care_gap_markers):
        return "Care Gap"
    return PLACEHOLDER


def infer_confidence(
    url: str | None = None,
    source_name: str | None = None,
    from_pubmed: bool = False,
) -> str:
    if from_pubmed:
        return "High"

    lowered_source = (source_name or "").lower()
    lowered_url = (url or "").lower()
    domain = extract_domain(url or "")

    if "reddit.com" in lowered_url or lowered_source == "reddit":
        return "Low"
    if domain.endswith(".gov") or any(marker in lowered_url for marker in ("cms.gov", "whitehouse.gov", "fda.gov", "medicaid.gov", "cdc.gov")):
        return "High"
    if any(marker in lowered_source for marker in ("pubmed", "plos", "jama")):
        return "High"
    return "Medium"


def normalize_date(raw_value: Any) -> str:
    if not raw_value:
        return PLACEHOLDER
    text = str(raw_value).strip()
    match = re.search(r"\d{4}-\d{2}-\d{2}", text)
    if match:
        return match.group(0)
    if len(text) >= 10 and text[:4].isdigit():
        return text[:10]
    return text


def summarize_text(raw_value: Any, max_length: int = 220) -> str:
    if not raw_value:
        return ""
    text = re.sub(r"\s+", " ", str(raw_value)).strip()
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    truncated = text[: max_length - 3].rstrip()
    if " " in truncated:
        truncated = truncated.rsplit(" ", 1)[0]
    return truncated.rstrip(" ,;:-") + "..."


def required_value(raw_value: Any) -> str:
    text = str(raw_value).strip() if raw_value is not None else ""
    return text or PLACEHOLDER


def extract_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except ValueError:
        return ""


def unique_list(values: list[str]) -> list[str]:
    ordered = OrderedDict()
    for value in values:
        if value:
            ordered[value] = None
    return list(ordered.keys())


def get_meaningful_rows(bucket_spec: BucketSpec, rows: list[dict[str, str]]) -> list[dict[str, str]]:
    primary_column = bucket_spec.columns[0]
    meaningful_rows = []
    for row in rows:
        primary_value = row.get(primary_column, "")
        if normalize_missing_value(primary_value) == NO_RESULTS_MESSAGE:
            continue
        meaningful_rows.append(row)
    return meaningful_rows


def build_bucket_summary(
    bucket_spec: BucketSpec,
    rows: list[dict[str, str]],
    warnings: list[str],
) -> str:
    if not rows:
        if warnings:
            return (
                "This bucket did not produce a usable set of structured findings during the current deterministic pass. "
                "Retrieval warnings are preserved in the Limitations section."
            )
        return "This bucket did not return substantive findings from the current deterministic tool pass."

    themes = unique_list(
        [
            theme
            for theme in (build_theme_label(bucket_spec.bucket_id, row) for row in rows)
            if theme
        ]
    )[:SUMMARY_TOPIC_COUNT]
    source_page_count = sum(1 for row in rows if is_source_page_detection(row))
    low_detail_count = sum(1 for row in rows if is_low_detail_finding(bucket_spec.bucket_id, row))

    lines = []
    if themes:
        lines.append(f"The clearest themes in this bucket were {human_join(themes)}.")
    else:
        lines.append("This bucket returned a small set of findings, but the themes remain loosely defined because the current extraction was shallow.")

    if source_page_count >= max(1, len(rows) // 2):
        lines.append("Much of the accessible detail came from source-page detection rather than fully parsed article-level extraction.")
    elif low_detail_count:
        lines.append("Several findings are readable, but some still rely on headline-, snippet-, or metadata-level detail.")
    else:
        lines.append("Most surfaced items were specific enough to render as finding-level notes rather than generic landing-page detections.")

    if warnings:
        lines.append("Retrieval warnings are preserved in the Limitations section.")

    return " ".join(lines[:3]).strip()


def build_key_findings(bucket_spec: BucketSpec, rows: list[dict[str, str]]) -> list[str]:
    if not rows:
        return ["No substantive findings were available for this bucket."]

    lines: list[str] = []
    for index, row in enumerate(rows[:MAX_KEY_FINDINGS]):
        lines.extend(render_finding_block(bucket_spec, row))
        if index < min(len(rows), MAX_KEY_FINDINGS) - 1:
            lines.append("")
    return lines


def build_what_this_means(bucket_spec: BucketSpec, rows: list[dict[str, str]]) -> list[str]:
    if not rows:
        return ["- No clear decision-support implication can be drawn because the bucket did not return substantive findings."]

    bullets = unique_list(build_bucket_level_implications(bucket_spec.bucket_id, rows))
    return bullets[:MAX_IMPLICATIONS]


def build_limitations(
    bucket_spec: BucketSpec,
    all_rows: list[dict[str, str]],
    warnings: list[str],
) -> list[str]:
    rows = get_meaningful_rows(bucket_spec, all_rows)
    limitations: list[str] = []

    if not rows:
        limitations.append("- The current deterministic tool pass did not return substantive findings for this bucket.")

    if rows and has_shallow_extraction(rows, bucket_spec.columns[0]):
        limitations.append(
            "- Several findings are based on headlines, snippets, or source-page detection rather than deeper article-level extraction."
        )

    if rows and any(clean_row_value(row.get("Confidence")) == "Low" for row in rows):
        limitations.append(
            "- At least one finding remains low confidence and should be treated as a monitoring lead rather than a settled conclusion."
        )

    if bucket_spec.bucket_id == "research" and rows and any("PREPRINT" in build_row_text(row).upper() for row in rows):
        limitations.append("- Some research findings rely on preprint or limited-metadata records and should not be treated as settled clinical guidance.")

    if bucket_spec.bucket_id in {"policy", "industry", "reimbursement", "women_health"} and rows:
        limitations.append(
            "- Current deterministic tooling does not consistently infer framing, stakeholder impact, urgency, or recommended action from every source."
        )

    for warning in warnings:
        limitations.append(f"- Warning: {summarize_text(warning, max_length=220)}")

    if not limitations:
        limitations.append("- No additional bucket-specific limitations were surfaced beyond the current deterministic tool constraints.")

    return unique_list(limitations)


def render_backing_table(columns: tuple[str, ...], rows: list[dict[str, str]]) -> str:
    cleaned_rows: list[dict[str, str]] = []
    for row in rows:
        cleaned_row: dict[str, str] = {}
        for index, column in enumerate(columns):
            if index == 0:
                cleaned_row[column] = build_display_title_for_row(row, detect_bucket_id_from_columns(columns)) or "—"
            elif column == "Source Link":
                cleaned_row[column] = clean_row_value(row.get(column), max_length=500) or "—"
            else:
                cleaned_row[column] = clean_cell_for_backing_table(column, row) or "—"
        cleaned_rows.append(cleaned_row)
    return render_markdown_table(columns, cleaned_rows)


def render_finding_block(bucket_spec: BucketSpec, row: dict[str, str]) -> list[str]:
    title = build_display_title_for_row(row, bucket_spec.bucket_id)
    finding_note = build_finding_note(bucket_spec.bucket_id, row)
    why_it_matters = build_why_it_matters(bucket_spec.bucket_id, row)
    source_line = build_source_line(clean_row_value(row.get("Source Link"), max_length=500))

    return [
        f"**{title}**",
        finding_note,
        f"**Why it matters:** {why_it_matters}",
        source_line,
    ]


def summarize_confidence_distribution(rows: list[dict[str, str]]) -> str:
    counts = Counter(
        clean_row_value(row.get("Confidence"), max_length=20)
        for row in rows
        if clean_row_value(row.get("Confidence"), max_length=20)
    )
    if not counts:
        return "Most rows still require manual interpretation for confidence and extraction depth."

    if len(counts) == 1:
        level = next(iter(counts))
        return f"Accessible evidence in this bucket was mostly {level.lower()} confidence."

    dominant_level, dominant_count = counts.most_common(1)[0]
    high_count = counts.get("High", 0)
    return (
        f"Confidence was mixed, led by {dominant_count} {dominant_level.lower()}-confidence signal"
        f"{'' if dominant_count == 1 else 's'}"
        + (f" and {high_count} high-confidence item{'' if high_count == 1 else 's'}." if high_count else ".")
    )


def bucket_summary_noun(bucket_id: str, count: int) -> str:
    nouns = {
        "policy": "policy signals",
        "industry": "market signals",
        "jobs": "workforce signals",
        "ai": "AI signals",
        "reimbursement": "payment signals",
        "research": "research findings",
        "women_health": "women's health signals",
    }
    noun = nouns.get(bucket_id, "findings")
    if count == 1 and noun.endswith("s"):
        return noun[:-1]
    return noun


def clean_row_value(raw_value: Any, max_length: int = 180) -> str:
    text = normalize_missing_value(raw_value)
    if not text:
        return ""
    return summarize_text(text, max_length=max_length)


def normalize_missing_value(raw_value: Any) -> str:
    if raw_value is None:
        return ""
    text = re.sub(r"\s+", " ", str(raw_value)).strip()
    if not text or text == PLACEHOLDER:
        return ""
    return text


def human_join(values: list[str]) -> str:
    cleaned = [value for value in values if value]
    if not cleaned:
        return ""
    if len(cleaned) == 1:
        return cleaned[0]
    if len(cleaned) == 2:
        return f"{cleaned[0]} and {cleaned[1]}"
    return ", ".join(cleaned[:-1]) + f", and {cleaned[-1]}"


def ensure_sentence(text: str) -> str:
    clean_text = strip_trailing_punctuation(text)
    if not clean_text:
        return ""
    return clean_text + "."


def strip_trailing_punctuation(text: str) -> str:
    return text.strip().rstrip(".;:,")


def strip_www(domain: str) -> str:
    return domain[4:] if domain.startswith("www.") else domain


def build_row_text(row: dict[str, str]) -> str:
    return " ".join(str(value) for value in row.values())


def has_shallow_extraction(rows: list[dict[str, str]], primary_column: str) -> bool:
    shallow_rows = 0
    for row in rows:
        substantive_fields = 0
        for column, value in row.items():
            if column in {
                primary_column,
                "Source Link",
                "Confidence",
                "Source Quality Tier",
                "Urgency / Time Sensitivity",
                "Recommended Action",
            }:
                continue
            if clean_row_value(value, max_length=120):
                substantive_fields += 1
        if substantive_fields <= 1:
            shallow_rows += 1
    return shallow_rows >= max(1, len(rows) // 2)


def build_bucket_level_implications(bucket_id: str, rows: list[dict[str, str]]) -> list[str]:
    source_page_count = sum(1 for row in rows if is_source_page_detection(row))
    low_confidence_count = sum(1 for row in rows if clean_row_value(row.get("Confidence"), max_length=20) == "Low")
    top_theme = build_theme_label(bucket_id, rows[0]) if rows else ""
    bullets: list[str] = []

    if bucket_id == "policy":
        bullets.append("- Treat these as policy-monitoring leads first; confirm underlying rule text, effective dates, and payer/provider impact before acting.")
        if source_page_count:
            bullets.append("- Several policy items came from source or newsroom pages, so the current run is better for directional monitoring than precise rule extraction.")
        if top_theme:
            bullets.append(f"- The strongest near-term signal appears to be around {top_theme}, which is worth tracking for concrete downstream guidance.")
        return bullets

    if bucket_id == "industry":
        bullets.append("- Use these findings to track market direction and capital flow, not to assume durable adoption or operating performance.")
        if source_page_count:
            bullets.append("- Some market notes came from source-page detection, so article-level confirmation would improve specificity on the underlying deal or trend.")
        if top_theme:
            bullets.append(f"- The clearest current market thread is {top_theme}, which is most useful as a monitoring and briefing signal.")
        return bullets

    if bucket_id == "jobs":
        bullets.append("- Treat these findings as directional workforce signals rather than a full labor-market read.")
        bullets.append("- Skills, employer demand, and practitioner sentiment should be cross-checked against broader postings data before drawing strong career conclusions.")
        if low_confidence_count:
            bullets.append("- Community-heavy signals are useful for context, but they should not outweigh stronger labor or employer data.")
        return bullets

    if bucket_id == "ai":
        bullets.append("- Separate production deployments from pilots, warnings, and vendor claims before using these findings in strategy decisions.")
        if any(clean_row_value(row.get("Status (Working/Failed/Experimental)")) == "Failed" for row in rows):
            bullets.append("- Failure- and warning-oriented findings should be treated as governance and validation signals, not just product anecdotes.")
        if source_page_count:
            bullets.append("- Some AI items came from source-page detection, so exact deployment or regulatory details may still need article-level confirmation.")
        return bullets

    if bucket_id == "reimbursement":
        bullets.append("- Confirm exact model names, codes, and effective dates before treating these as actionable reimbursement changes.")
        bullets.append("- The most useful downstream action is usually reimbursement review, especially where coverage or incentive design could shift.")
        if source_page_count:
            bullets.append("- Several notes came from payer or policy landing pages, so deeper parsing is still needed for rule-level precision.")
        return bullets

    if bucket_id == "research":
        bullets.append("- Treat these as evidence-monitoring notes unless a study is clearly peer-reviewed, richly described, and strong enough to support practice change.")
        if any(is_metadata_only_finding(row) for row in rows):
            bullets.append("- Metadata-only or snippet-only research findings should be monitored, but not treated as complete evidence summaries.")
        if low_confidence_count:
            bullets.append("- Preprint or low-confidence evidence should be watched for peer review, replication, or stronger corroboration.")
        return bullets

    if bucket_id == "women_health":
        bullets.append("- Keep policy, clinical, market, and care-gap signals separate so one type of evidence does not overstate another.")
        bullets.append("- The most useful next step is usually to verify who is affected and whether the finding changes access, coverage, or clinical practice.")
        if source_page_count:
            bullets.append("- Some women’s health items came from broad source pages, so the current run may indicate direction more reliably than article-level detail.")
        return bullets

    return ["- These findings are best treated as monitoring inputs for the current brief."]


def build_display_title_for_row(row: dict[str, str], bucket_id: str) -> str:
    primary_title = clean_row_value(row.get(primary_column_for_bucket(bucket_id)), max_length=160)
    detail_text = get_detail_text(bucket_id, row)
    url = clean_row_value(row.get("Source Link"), max_length=500)

    if is_source_page_detection(row):
        cleaned_detail = clean_snippet_text(detail_text, primary_title)
        candidate = extract_candidate_snippet(cleaned_detail, primary_title)
        if candidate and is_bucket_relevant_text(bucket_id, candidate):
            return headlineize(candidate, max_length=88)
        return build_source_page_label(url, bucket_id)

    if is_reddit_signal(row):
        cleaned = clean_title_text(primary_title, url)
        return cleaned or "Community discussion"

    cleaned_title = clean_title_text(primary_title, url)
    if cleaned_title:
        return cleaned_title
    if detail_text:
        return headlineize(detail_text, max_length=88)
    return "Untitled finding"


def build_theme_label(bucket_id: str, row: dict[str, str]) -> str:
    title = build_display_title_for_row(row, bucket_id)
    if is_source_page_detection(row):
        return title
    category = clean_row_value(row.get("Category (Policy/Clinical/Market/Care Gap)"), max_length=40)
    if bucket_id == "women_health" and category:
        return f"{category.lower()} signals around {title}"
    return title


def build_finding_note(bucket_id: str, row: dict[str, str]) -> str:
    title = build_display_title_for_row(row, bucket_id)
    detail_text = get_detail_text(bucket_id, row)
    clean_detail = clean_snippet_text(detail_text, build_display_title_fallback(row, bucket_id))

    if is_source_page_detection(row):
        return build_source_page_note(bucket_id, row, clean_detail)

    if is_reddit_signal(row):
        if clean_detail:
            return f"{ensure_sentence(clean_detail)} This note comes from community discussion rather than verified reporting."
        return "A community discussion surfaced a relevant signal, but specific article-level detail was not available from the current extraction."

    if bucket_id == "research":
        if clean_detail:
            note = ensure_sentence(clean_detail)
        else:
            note = "This source surfaced a research record relevant to the current query."
        if is_metadata_only_finding(row):
            note += " Specific article-level detail was limited to metadata or snippet text from the current extraction."
        return note

    if clean_detail:
        note = ensure_sentence(clean_detail)
    else:
        note = "Specific article-level detail was not available from the current extraction."

    if is_low_detail_finding(bucket_id, row):
        if "Specific article-level detail was not available" not in note and "snippet" not in note.lower():
            note += " Specific article-level detail was limited to the title or snippet returned by the current extraction."
    return note


def build_why_it_matters(bucket_id: str, row: dict[str, str]) -> str:
    combined_text = build_row_text(row).lower()
    status = clean_row_value(row.get("Status (Working/Failed/Experimental)"), max_length=40)
    category = clean_row_value(row.get("Category (Policy/Clinical/Market/Care Gap)"), max_length=40)
    implication = clean_row_value(
        row.get("Implication for Women's Health/Chronic Pain") or row.get("Women's Health / Chronic Pain Relevance") or row.get("Policy/Market/Clinical Implication"),
        max_length=180,
    )

    if is_source_page_detection(row):
        return source_page_why_it_matters(bucket_id, row)

    if is_reddit_signal(row):
        return "This is useful as a practitioner or community signal, but it should be corroborated before it informs a stronger conclusion."

    if bucket_id == "policy":
        if any(marker in combined_text for marker in ("rule", "payment", "medicare", "medicaid", "prior authorization", "coverage", "fee schedule")):
            return "This could affect policy monitoring, implementation timing, or reimbursement exposure once the underlying text is confirmed."
        if any(marker in combined_text for marker in ("committee", "advisory", "executive", "announcement")):
            return "This looks like an administrative or governance signal worth monitoring, but not yet a concrete payment or coverage change."
        return "This is a policy-monitoring lead that needs underlying source text before it should drive action."

    if bucket_id == "industry":
        if implication:
            return ensure_sentence(implication)
        if any(marker in combined_text for marker in ("funding", "investment", "raised", "series", "acquisition", "merger")):
            return "This helps track where capital or consolidation is moving, but operating impact should be confirmed beyond the announcement."
        if any(marker in combined_text for marker in ("adoption", "deploy", "rollout", "implemented")):
            return "This may signal real market movement, but deployment scale and durability still need confirmation."
        return "This is most useful as a market-direction signal to monitor over the next few cycles."

    if bucket_id == "jobs":
        action = clean_row_value(row.get("Recommended Action"), max_length=140)
        if action:
            return ensure_sentence(action)
        if any(marker in combined_text for marker in ("fhir", "python", "sql", "databricks", "spark", "epic", "cerner")):
            return "This points to a skill or platform the market is watching, but broader employer data is still needed before treating it as a durable hiring shift."
        return "This is a directional workforce note that is best used alongside broader job-posting and salary evidence."

    if bucket_id == "ai":
        if status == "Failed":
            return "This is a validation or governance warning that should be reviewed before broader deployment or stronger product claims."
        if status == "Working":
            return "This may indicate real operational traction, but outcome quality and deployment scale should still be confirmed."
        if status == "Experimental":
            return "This appears to be early-stage evidence and should stay on the watchlist until stronger deployment or clinical proof emerges."
        return "This is an AI-monitoring note that still needs stronger validation before it supports a strategic conclusion."

    if bucket_id == "reimbursement":
        if implication:
            return ensure_sentence(implication)
        if any(marker in combined_text for marker in ("cpt", "hcpcs", "code", "payment", "aco", "cmmi", "prior authorization")):
            return "This could matter for reimbursement review, model exposure, or coding strategy once the exact policy language is confirmed."
        return "This is worth monitoring for downstream payment, coverage, or incentive changes."

    if bucket_id == "research":
        if is_metadata_only_finding(row):
            return "This is an evidence signal worth monitoring, but it is too thin or metadata-driven to treat as stand-alone clinical guidance."
        if clean_row_value(row.get("Confidence"), max_length=20) == "Low":
            return "This should stay on the evidence watchlist until peer review, richer detail, or stronger replication appears."
        return "This may inform evidence monitoring or future briefs, but it should still be weighed against broader literature before any practice-level conclusion."

    if bucket_id == "women_health":
        if implication:
            return ensure_sentence(implication)
        if category == "Policy":
            return "This could affect coverage, access, or the legal and regulatory environment for women’s health services."
        if category == "Clinical":
            return "This may matter for care guidance or evidence tracking, but the practical effect depends on the strength and scope of the underlying evidence."
        if category == "Market":
            return "This is useful as a market or investment signal, but real patient or care-delivery impact still needs confirmation."
        if category == "Care Gap":
            return "This highlights an access or underdiagnosis issue that may matter for care design, reimbursement, or population-health monitoring."
        return "This is a women’s health monitoring signal that should be verified for scope, affected groups, and downstream relevance."

    return "This finding warrants monitoring as part of the current research brief."


def primary_column_for_bucket(bucket_id: str) -> str:
    mapping = {
        "policy": "Policy Name",
        "industry": "Trend",
        "jobs": "Role/Skill",
        "ai": "AI Use Case",
        "reimbursement": "Payment Model",
        "research": "Study Title",
        "women_health": "Topic",
    }
    return mapping[bucket_id]


def detect_bucket_id_from_columns(columns: tuple[str, ...]) -> str:
    first_column = columns[0]
    mapping = {
        "Policy Name": "policy",
        "Trend": "industry",
        "Role/Skill": "jobs",
        "AI Use Case": "ai",
        "Payment Model": "reimbursement",
        "Study Title": "research",
        "Topic": "women_health",
    }
    return mapping.get(first_column, "policy")


def get_detail_text(bucket_id: str, row: dict[str, str]) -> str:
    if bucket_id == "policy":
        return clean_row_value(row.get("Summary"), max_length=320)
    if bucket_id == "industry":
        return clean_row_value(row.get("What's Shifting") or row.get("Key Data Point"), max_length=320)
    if bucket_id == "jobs":
        parts = [
            clean_row_value(row.get("Trend Direction (Growing/Declining)"), max_length=40),
            clean_row_value(row.get("Key Employers Hiring"), max_length=140),
        ]
        return " ".join(part for part in parts if part)
    if bucket_id == "ai":
        parts = [
            clean_row_value(row.get("What Went Wrong (if applicable)"), max_length=220),
            clean_row_value(row.get("Lesson Learned"), max_length=160),
        ]
        return " ".join(part for part in parts if part)
    if bucket_id == "reimbursement":
        return clean_row_value(row.get("What Changed"), max_length=320)
    if bucket_id == "research":
        return clean_row_value(row.get("Plain-English Source Note"), max_length=320)
    if bucket_id == "women_health":
        parts = [
            clean_row_value(row.get("Finding"), max_length=220),
            clean_row_value(row.get("Who It Affects"), max_length=120),
        ]
        return " ".join(part for part in parts if part)
    return ""


def is_source_page_detection(row: dict[str, str]) -> bool:
    origin = row.get("__origin", "")
    if origin == "scrape":
        return True
    url = clean_row_value(row.get("Source Link"), max_length=500).lower()
    title = build_row_text(row).lower()
    generic_markers = ("homepage", "source page", "newsroom", "presidential actions")
    return any(marker in url for marker in ("/newsroom", "/presidential-actions")) or any(marker in title for marker in generic_markers)


def is_reddit_signal(row: dict[str, str]) -> bool:
    return row.get("__origin") == "reddit" or "reddit.com" in clean_row_value(row.get("Source Link"), max_length=500).lower()


def is_metadata_only_finding(row: dict[str, str]) -> bool:
    combined = build_row_text(row).lower()
    return any(
        marker in combined
        for marker in (
            "limited metadata",
            "metadata record",
            "snippet text",
            "metadata-only",
            "preprint",
        )
    )


def is_low_detail_finding(bucket_id: str, row: dict[str, str]) -> bool:
    if is_source_page_detection(row) or is_metadata_only_finding(row):
        return True
    detail_text = get_detail_text(bucket_id, row)
    cleaned = clean_snippet_text(detail_text, build_display_title_fallback(row, bucket_id))
    if not cleaned:
        return True
    if len(cleaned.split()) < 8:
        return True
    if looks_like_navigation_text(cleaned):
        return True
    return False


def build_display_title_fallback(row: dict[str, str], bucket_id: str) -> str:
    return clean_row_value(row.get(primary_column_for_bucket(bucket_id)), max_length=160)


def build_source_page_note(bucket_id: str, row: dict[str, str], clean_detail: str) -> str:
    source_label = build_source_page_subject(clean_row_value(row.get("Source Link"), max_length=500), bucket_id)
    if clean_detail and is_bucket_relevant_text(bucket_id, clean_detail):
        return (
            f"The {source_label} surfaced a recent item about {strip_trailing_punctuation(clean_detail)}. "
            "This note is based on source-page detection rather than a fully parsed article."
        )
    return (
        f"The {source_label} surfaced relevant activity for this bucket, but the current extraction did not isolate a specific article-level item. "
        "This note is based on source-page detection."
    )


def source_page_why_it_matters(bucket_id: str, row: dict[str, str]) -> str:
    if bucket_id == "policy":
        return "This indicates current policy-related activity on an official or analyst source page, but it should not be treated as a discrete rule finding without deeper parsing."
    if bucket_id == "industry":
        return "This signals market activity worth monitoring, but it is still at the source-page level rather than a clearly parsed article or deal record."
    if bucket_id == "jobs":
        return "This points to workforce-related coverage or reference material, but it is not a clean, article-level hiring signal."
    if bucket_id == "ai":
        return "This suggests current AI-related activity on the source page, but it does not yet provide a fully parsed deployment, failure, or regulatory record."
    if bucket_id == "reimbursement":
        return "This may point to reimbursement or model activity, but deeper article- or rule-level extraction is still needed before acting on it."
    if bucket_id == "research":
        return "This is useful for evidence monitoring, but source-page detection is too shallow to stand in for a fully parsed study record."
    if bucket_id == "women_health":
        return "This indicates current activity relevant to women’s health, but the present extraction is better for directional monitoring than a precise finding."
    return "This is a source-level signal that still needs deeper parsing before it should drive a strong conclusion."


def build_source_line(url: str) -> str:
    if not url:
        return "**Source:** Not available"
    return f"**Source:** [{url}]({url})"


def clean_cell_for_backing_table(column: str, row: dict[str, str]) -> str:
    primary_title = detect_row_primary_title(row)
    if column in {
        "Summary",
        "What's Shifting",
        "What Changed",
        "Finding",
        "Plain-English Source Note",
        "What Went Wrong (if applicable)",
        "Lesson Learned",
    }:
        return clean_snippet_text(clean_row_value(row.get(column), max_length=220), primary_title)
    return clean_row_value(row.get(column), max_length=160)


def clean_title_text(title: str, url: str) -> str:
    text = normalize_missing_value(title)
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"^(newsroom homepage\s*\|\s*cms)\b", "", text, flags=re.IGNORECASE).strip(" -|:")
    text = re.sub(r"\bskip to main content\b", "", text, flags=re.IGNORECASE).strip()

    domain_label = infer_domain_label(url)
    parts = [part.strip() for part in re.split(r"\s+[|\-–]\s+", text) if part.strip()]
    if len(parts) > 1:
        filtered_parts = [part for part in parts if not looks_like_site_suffix(part, domain_label)]
        if filtered_parts:
            text = filtered_parts[0]
        else:
            text = parts[0]

    if looks_like_generic_page_title(text):
        return ""
    return headlineize(text, max_length=88)


def clean_snippet_text(text: str, title: str) -> str:
    cleaned = normalize_missing_value(text)
    if not cleaned:
        return ""

    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if title:
        title_pattern = re.escape(strip_trailing_punctuation(title))
        cleaned = re.sub(rf"^{title_pattern}\s*[:|.-]*\s*", "", cleaned, flags=re.IGNORECASE)

    boilerplate_patterns = [
        r"\bSkip to main content\b",
        r"\bREAD MORE\b",
        r"\bRead more\b",
        r"\bMenu\b",
        r"\bSubscribe\b",
        r"\bSign in\b",
        r"\bHome\b",
        r"\bLatest news\b",
        r"\bLatest\b",
    ]
    for pattern in boilerplate_patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r"^(Press Releases?|Presidential Actions?)\s+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^[A-Z][a-z]{2}\s+\d{1,2},\s+\d{4}\s+", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" -|:;")

    candidate = extract_candidate_snippet(cleaned, title)
    return summarize_text(candidate or cleaned, max_length=220)


def extract_candidate_snippet(text: str, title: str) -> str:
    cleaned = normalize_missing_value(text)
    if not cleaned:
        return ""
    parts = re.split(r"(?<=[.!?])\s+|(?<=\.)\s+(?=[A-Z])", cleaned)
    for part in parts:
        candidate = strip_trailing_punctuation(part.strip())
        if not candidate:
            continue
        if title and candidate.lower() == strip_trailing_punctuation(title).lower():
            continue
        if looks_like_navigation_text(candidate):
            continue
        if len(candidate.split()) < 4:
            continue
        return candidate
    return strip_trailing_punctuation(cleaned)


def headlineize(text: str, max_length: int = 88) -> str:
    cleaned = normalize_missing_value(text)
    if not cleaned:
        return ""
    cleaned = strip_trailing_punctuation(cleaned)
    cleaned = summarize_text(cleaned, max_length=max_length)
    if cleaned:
        cleaned = cleaned[0].upper() + cleaned[1:]
    return cleaned


def looks_like_navigation_text(text: str) -> bool:
    lowered = normalize_missing_value(text).lower()
    if not lowered:
        return True
    nav_markers = (
        "skip to main content",
        "subscribe",
        "sign in",
        "menu",
        "privacy",
        "terms",
        "cookies",
        "contact us",
        "latest news",
        "breadcrumb",
        "press releases",
        "presidential actions",
    )
    if any(marker in lowered for marker in nav_markers):
        return True
    return lowered.count("|") >= 2


def looks_like_generic_page_title(text: str) -> bool:
    lowered = normalize_missing_value(text).lower()
    generic_markers = (
        "homepage",
        "home",
        "newsroom",
        "presidential actions",
        "the independent source for",
        "news and insights",
    )
    return not lowered or any(marker == lowered or lowered.startswith(marker) for marker in generic_markers)


def looks_like_site_suffix(text: str, domain_label: str) -> bool:
    lowered = text.lower()
    if not lowered:
        return False
    site_markers = {
        domain_label.lower(),
        "cms",
        "the white house",
        "kff",
        "stat",
        "healthcare dive",
        "rock health",
        "himss",
        "mcdermott+",
    }
    return lowered in site_markers or lowered.startswith("the independent source for")


def infer_domain_label(url: str) -> str:
    domain = strip_www(extract_domain(url))
    mapping = {
        "cms.gov": "CMS",
        "whitehouse.gov": "White House",
        "kff.org": "KFF",
        "mcdermottplus.com": "McDermott+",
        "healthaffairs.org": "Health Affairs",
        "himss.org": "HIMSS",
        "rockhealth.com": "Rock Health",
        "statnews.com": "STAT News",
        "modernhealthcare.com": "Modern Healthcare",
        "healthcaredive.com": "Healthcare Dive",
        "medicaid.gov": "Medicaid",
        "cdc.gov": "CDC",
        "acog.org": "ACOG",
        "jamanetwork.com": "JAMA Network",
        "pubmed.ncbi.nlm.nih.gov": "PubMed",
        "medrxiv.org": "medRxiv",
    }
    return mapping.get(domain, domain or "source")


def build_source_page_label(url: str, bucket_id: str) -> str:
    domain_label = infer_domain_label(url)
    path = urlparse(url).path.lower().strip("/")

    if "newsroom" in path:
        return f"{domain_label} newsroom activity"
    if "presidential-actions" in path:
        return "White House executive-action page"
    if "womens-health-policy" in path:
        return f"{domain_label} women's health policy coverage"
    if "priorities/innovation" in path:
        return f"{domain_label} innovation-model coverage"
    if path == "ooh":
        return "BLS occupational outlook coverage"
    if bucket_id == "jobs" and "himss" in domain_label.lower():
        return "HIMSS workforce coverage"
    if bucket_id == "research":
        return f"{domain_label} research coverage page"
    return f"{domain_label} source-page coverage"


def detect_row_primary_title(row: dict[str, str]) -> str:
    for column in (
        "Policy Name",
        "Trend",
        "Role/Skill",
        "AI Use Case",
        "Payment Model",
        "Study Title",
        "Topic",
    ):
        value = clean_row_value(row.get(column), max_length=160)
        if value:
            return value
    return ""


def build_source_page_subject(url: str, bucket_id: str) -> str:
    domain_label = infer_domain_label(url)
    path = urlparse(url).path.lower().strip("/")

    if "newsroom" in path:
        return f"{domain_label} newsroom page"
    if "presidential-actions" in path:
        return "White House presidential actions page"
    if "womens-health-policy" in path:
        return f"{domain_label} women's health policy page"
    if "priorities/innovation" in path:
        return f"{domain_label} innovation-model page"
    if path == "ooh":
        return "BLS occupational outlook page"
    if bucket_id == "jobs" and "himss" in domain_label.lower():
        return "HIMSS workforce page"
    if bucket_id == "research":
        return f"{domain_label} research page"
    return f"{domain_label} source page"


def is_bucket_relevant_text(bucket_id: str, text: str) -> bool:
    lowered = normalize_missing_value(text).lower()
    keyword_map = {
        "policy": ("health", "medicare", "medicaid", "cms", "patient", "hospital", "hhs", "drug", "policy", "care"),
        "industry": ("health", "digital", "funding", "market", "care", "ai", "startup", "femtech"),
        "jobs": ("job", "career", "hiring", "skill", "workforce", "analyst", "informatics", "epic", "python", "fhir"),
        "ai": ("ai", "model", "clinical", "documentation", "device", "diagnostic", "automation", "bias"),
        "reimbursement": ("payment", "reimbursement", "medicare", "medicaid", "cpt", "hcpcs", "aco", "cmmi", "coverage"),
        "research": ("study", "trial", "outcome", "clinical", "patients", "evidence", "review", "meta-analysis"),
        "women_health": ("women", "maternal", "menopause", "fertility", "pcos", "endometriosis", "fibromyalgia", "health"),
    }
    return any(keyword in lowered for keyword in keyword_map.get(bucket_id, ()))


if __name__ == "__main__":
    raise SystemExit(main())
