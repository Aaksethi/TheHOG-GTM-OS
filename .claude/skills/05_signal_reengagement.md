# Skill 05 — Signal Re-engagement

## Purpose
Monitor enriched contacts and known accounts for live signals that
justify re-engagement. Produces a prioritized outreach queue with
context for Skill 06 to draft from.

## Schema
Read and write using master record defined in .claude/schema.json.
Flatten to sheet using sheet_mappings for this skill's output sheet.

---

## Trigger
Operator says: "any signals on existing contacts" / "who should we
re-engage" / "check signals on [company or contact name]"

---

## Step 1 — Input
Accept either:
- Full enriched contact list from Skill 02
- Specific company or contact name from operator
- Signal feed from Skill 03 or 04

---

## Step 2 — Signal Retrieval Sequence

1. GET /api/v1/monitors/:id/events [SYNC] — pull all unactioned events from Signal Log.
   Get monitor ids first from GET /api/v1/monitors.
   Read events and filter for: buying signals and product match signals flagged by Skill 03.

2. POST /api/v1/platform/scrapers/linkedin/company [SYNC] — for the triggering company, pull latest company context.
   Body: {username:'company-linkedin-slug'}
   Read: data.description, data.employee_count, recent context.

3. POST /api/v1/platform/scrapers/linkedin/keyword-posts [SYNC] — search for the specific post or announcement that triggered the signal to get exact wording and date.
   Body: {query:'[company name] [signal keyword]', max_results:5, match_mode:'broad', date_filter:'past-week'}

Pass signal context and company context to draft step.
Draft must reference the specific signal by name.
No draft without a confirmed signal source — never fabricate triggers.

---

## Raw Dump — Write After Each Call

- After monitor events pull: `raw-05-{YYYYMMDD}-monitor_events.json`
- After LinkedIn company scrape: `raw-05-{YYYYMMDD}-linkedin_company_{slug}.json`
- After keyword-posts call: `raw-05-{YYYYMMDD}-keyword_posts_{slug}.json`

---

## Step 3 — Signal Scoring
Score each signal before adding to outreach queue:

HOT — Job change to a new target company, new product launch, funding announced
      → Outreach within 24 hours
WARM — LinkedIn post about product development, trade show participation,
       press coverage → Outreach within 72 hours
COLD — General brand activity, no direct commercial signal
      → Hold, do not queue for outreach

Only HOT and WARM signals enter the outreach queue.

---

## Step 4 — Outreach Queue Output
For each HOT or WARM contact produce JSON by merging the incoming
master record with signal data:

- signals[].type
- signals[].detail
- signals[].date
- signals[].classification
- signals[].counter (one sentence from BRAND.md proof points)
- signals[].triggered_workflow = "skill_06"

Pass full merged master record to Skill 06.

---

## Step 5 — Write to Google Sheets
Run scripts/sheets_write.py to persist signals to Signal Log tab.

  python scripts/sheets_write.py "Signal Log" '<json_rows>'

Format <json_rows> as a JSON array of arrays:
[Company, Contact, Type, Detail, Date, Classification, Counter, Triggered Workflow]

The script deduplicates on company+detail (cols 0 and 3) — safe to run more than once.
Confirm the script logs "wrote N row(s)" to confirm success.
If the script errors, log the error in MEMORY.md and continue.
Do not abort if Sheets write fails — signals are in MEMORY.md as backup.

---

## Step 6 — Log Session
Append to MEMORY.md (index only):
```
[DATE] — Skill 05 Signal Re-engagement
Ran: Skill 05
Raw files: [list raw-05 files written]
Output files: none — signals written directly to Signal Log sheet
Sheets updated: Signal Log — N rows
Blockers added: 0
Next: HOT contacts to Skill 06 within 24h, WARM within 72h
```