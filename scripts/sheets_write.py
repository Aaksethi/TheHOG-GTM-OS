import json
import os
import sys
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
# Read from environment (see .env.example). Never hardcode credentials or IDs.
SERVICE_ACCOUNT_FILE = os.environ.get(
    "GOOGLE_SERVICE_ACCOUNT_PATH",
    os.path.join(os.path.dirname(__file__), "..", "service-account.json"),
)
SHEET_ID = os.environ.get("GOOGLE_SHEET_ID")
if not SHEET_ID:
    sys.exit("ERROR: GOOGLE_SHEET_ID is not set. Copy .env.example to .env and fill it in.")

# Dedup key columns per tab (zero-indexed)
# Enriched Contacts sheet column order: [0]Name [1]Title [2]Email [3]LinkedIn [4]Company ...
KEY_COLS_BY_TAB = {
    "Enriched Contacts":    [2],     # email (col 2 in Name-first sheet order)
    "GTM Pipeline":         [2],     # email
    "Signal Log":           [0, 3],  # company + detail
    "Validation Log":       [0, 3],  # company + detail
    "Outreach Draft":       [4],     # email
}

def get_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds)

def append_rows_idempotent(service, sheet_name, rows, key_cols):
    """Append only rows whose composite key (values at key_cols) is not already in the sheet."""
    existing_result = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=f"{sheet_name}!A:Z"
    ).execute()
    existing_rows = existing_result.get("values", [])

    def get_key(row):
        return tuple(str(row[i]) if i < len(row) else "" for i in key_cols)

    existing_keys = {get_key(r) for r in existing_rows}
    new_rows = [r for r in rows if get_key(r) not in existing_keys]

    if not new_rows:
        return {"updatedRows": 0, "skipped": len(rows)}

    result = service.spreadsheets().values().append(
        spreadsheetId=SHEET_ID,
        range=f"{sheet_name}!A1",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": new_rows}
    ).execute()
    updates = result.get("updates", {})
    updates["skipped"] = len(rows) - len(new_rows)
    return updates

def cli_write(tab_name, rows_json):
    """
    CLI entry point for skill files.
    Usage: python scripts/sheets_write.py "<Tab Name>" '<json_rows>'
    rows_json must be a JSON array of arrays: [["col1","col2",...], ...]
    """
    rows = json.loads(rows_json)
    if not isinstance(rows, list) or not rows:
        print(f"ERROR: rows_json must be a non-empty JSON array of arrays")
        sys.exit(1)
    key_cols = KEY_COLS_BY_TAB.get(tab_name, [0])
    svc = get_service()
    result = append_rows_idempotent(svc, tab_name, rows, key_cols)
    updated = result.get("updatedRows", 0)
    skipped = result.get("skipped", 0)
    print(f"{tab_name}: wrote {updated} row(s), skipped {skipped} duplicate(s)")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python sheets_write.py <tab_name> '<json_rows>'")
        print("Example: python sheets_write.py \"Enriched Contacts\" '[[\"Acme Inc\",\"Jane Doe\",...]]'")
        sys.exit(1)
    cli_write(sys.argv[1], sys.argv[2])
