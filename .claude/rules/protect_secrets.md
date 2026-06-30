# Rule — Protect Secrets

API keys, credentials, and environment variables never appear
in any output, draft, log, or sheet.

All keys are referenced via environment variables or secure files only:
- HOG_ACCESS_KEY → ${HOG_ACCESS_KEY} (X-Access-Key header)
- HOG_SECRET_KEY → ${HOG_SECRET_KEY} (X-Secret-Key header)
- service-account.json → Google Sheets auth (file path only, never contents)

Note: ANTHROPIC_API_KEY was used by the deleted dashboard/server.js.
Re-add here if a new integration requires it.

If a key appears in any output, stop the session and flag immediately.