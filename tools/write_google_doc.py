"""
write_google_doc.py
Creates or updates a Google Doc with research output.
Uses a service account for authentication.
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file",
]

SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
FOLDER_ID = os.getenv("GOOGLE_DOC_FOLDER_ID")


def _get_docs_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("docs", "v1", credentials=creds)


def _get_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds)


def create_research_doc(title: str, markdown_content: str) -> str:
    """
    Creates a new Google Doc with the given title and content.
    Moves it into the configured Drive folder.

    Returns the document URL.
    """
    docs = _get_docs_service()
    drive = _get_drive_service()

    # Create blank doc
    doc = docs.documents().create(body={"title": title}).execute()
    doc_id = doc["documentId"]

    # Insert content
    requests_body = [
        {
            "insertText": {
                "location": {"index": 1},
                "text": markdown_content,
            }
        }
    ]
    docs.documents().batchUpdate(
        documentId=doc_id, body={"requests": requests_body}
    ).execute()

    # Move to folder
    if FOLDER_ID:
        file = drive.files().get(fileId=doc_id, fields="parents").execute()
        previous_parents = ",".join(file.get("parents", []))
        drive.files().update(
            fileId=doc_id,
            addParents=FOLDER_ID,
            removeParents=previous_parents,
            fields="id, parents",
        ).execute()

    url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(f"[DOC CREATED] {url}")
    return url


if __name__ == "__main__":
    sample = f"""# Test Research Doc
Generated: {datetime.utcnow().isoformat()}

## Summary
This is a test document created by the Health Researcher system.
"""
    url = create_research_doc("Test Research Doc", sample)
    print(url)
