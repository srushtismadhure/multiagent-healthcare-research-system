# Tracking

This folder holds the master research log.

## research_log (Google Sheet)

Create this Google Sheet manually (or let `tools/log_to_sheets.py` append rows to the Google Sheet).

### Column Schema

| Column | Type | Description |
|--------|------|-------------|
| Run Date | Date (YYYY-MM-DD) | Date of research run |
| Run Time | Time (HH:MM UTC) | Time run completed |
| Bucket | String | e.g. "Policy and Regulation" |
| Document Title | String | Title of the output document |
| Key Findings Summary | String | 1–2 sentence summary |
| Source Count | Integer | Number of unique sources cited |
| Doc Link | URL | Link to Google Doc or local .md file |

## Setup

1. Create a Google Sheet named `research_log`
2. Add the column headers in row 1
3. Copy the Sheet ID from the URL into `.env` as `GOOGLE_SHEET_ID`
4. Share the sheet with your service account email (from `GOOGLE_SERVICE_ACCOUNT_JSON`)
