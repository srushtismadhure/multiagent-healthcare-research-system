"""
log_to_sheets.py
Appends a research run row to the master Google Sheets tracking log.

Sheet columns:
Run Date | Run Time | Bucket | Document Title | Key Findings Summary | Source Count | Doc Link
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
SHEET_RANGE = "research_log!A:G"


def _get_sheets_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds)


def log_research_run(
    bucket: str,
    document_title: str,
    key_findings_summary: str,
    source_count: int,
    doc_link: str,
) -> None:
    """
    Appends one row to the master research log sheet.

    Args:
        bucket: e.g. "Policy and Regulation"
        document_title: Title of the output document
        key_findings_summary: 1-2 sentence summary of top findings
        source_count: Number of sources cited
        doc_link: URL to the Google Doc
    """
    service = _get_sheets_service()
    now = datetime.utcnow()

    row = [
        now.strftime("%Y-%m-%d"),          # Run Date
        now.strftime("%H:%M:%S UTC"),       # Run Time
        bucket,                             # Bucket
        document_title,                     # Document Title
        key_findings_summary,               # Key Findings Summary
        source_count,                       # Source Count
        doc_link,                           # Doc Link
    ]

    body = {"values": [row]}
    service.spreadsheets().values().append(
        spreadsheetId=SHEET_ID,
        range=SHEET_RANGE,
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body=body,
    ).execute()

    print(f"[LOGGED] {bucket} — {document_title}")


if __name__ == "__main__":
    log_research_run(
        bucket="Test Bucket",
        document_title="Test Run",
        key_findings_summary="This is a test log entry.",
        source_count=0,
        doc_link="https://docs.google.com/document/d/test",
    )
