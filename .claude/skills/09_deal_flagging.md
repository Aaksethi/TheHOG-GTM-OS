# Skill 09 — Deal Flagging

## Purpose
Scan Pipeline sheet for deals needing attention using Fit Score
and Engagement Score. Produces prioritized action list.

## Schema
Read and write using master record defined in .claude/schema.json.
Flatten to sheet using sheet_mappings for this skill's output sheet.

---

## Trigger
Operator says: "check pipeline" / "run deal flags" / "what needs attention"
Recommended cadence: every 7 days.

---

## Input
Operator pastes or exports Pipeline sheet. Required columns:
Company, Contact, Deal Stage, Fit Score, Engagement Score,
Last Touch, Next Step, Flag.

---

## Scoring Model

### Fit Score (set by Skill 01, 1–3)
3 — Perfect ICP match
2 — Partial fit, operator reviewed
1 — Weak fit (should not be in pipeline — flag for removal)

### Engagement Score (operator-logged, 0–10)
Operator updates this column manually after each touch:

| Action | Points |
|---|---|
| Replied to outreach | +3 |
| Attended meeting | +3 |
| Requested case study or spec sheet | +2 |
| Opened email (if tracked) | +1 |
| LinkedIn engagement | +1 |
| No response after 2 touches | -1 |
| Meeting no-show | -2 |

Score caps at 10. Floors at 0.

### Combined Priority Score
Multiply: Fit Score × Engagement Score

6–10 → HOT — active deal, prioritize
3–5  → WARM — nurture, check for signals
1–2  → COLD — re-evaluate or drop
0    → INACTIVE — no engagement, run Skill 05 signal check

---

## Flag Rules

AT-RISK — Next Step date passed, no update, Engagement Score dropping
STALLED — Last Touch over 14 days, no Next Step set
EXPANSION — Closed Won + second product category unaddressed
WARM — Next Step upcoming within 7 days, Engagement Score 3+
COLD — Last Touch 30+ days, no signal, Engagement Score 0–1

---

## Signal Check Before Flagging

Before applying rules, run a quick signal check on all pipeline accounts:

1. GET /api/v1/monitors/:id/events [SYNC] — check if any pipeline account has had a new event since last session.
   Get all monitor ids from GET /api/v1/monitors first.
   For each pipeline account, find the matching monitor and check for new events.
   A new event on a stalled account = override STALLED flag with SIGNAL RECEIVED.

2. POST /api/v1/platform/scrapers/linkedin/keyword-posts [SYNC] — search for recent posts from pipeline contacts by name.
   Body: {query:'[contact name] OR [company name]', max_results:5, match_mode:'broad', date_filter:'past-week'}
   A recent post = engagement signal, reduces stall severity.

Then apply the existing rules engine to the Pipeline tab as normal.
Signal data from above can upgrade or downgrade a flag.

---

## Raw Dump — Write After Each Call

- After monitor events pulls: `raw-09-{YYYYMMDD}-monitor_events.json`
- After keyword-posts calls: `raw-09-{YYYYMMDD}-keyword_posts.json`

---

## Step 2 — Output
Output using master record schema. Update deal.* fields and signals[].
Set meta.last_updated and append "skill_09" to meta.skills_run.

---

## Step 3 — Sheet Output
Write flagged records to Pipeline sheet with updated flag column.
Color coding for VP visibility:
- AT-RISK → red
- STALLED → orange
- EXPANSION → green
- WARM → yellow
- COLD/INACTIVE → grey

Produce prioritized action list in this order:
1. AT-RISK (immediate action)
2. EXPANSION (revenue opportunity)
3. STALLED (needs signal check)
4. WARM (upcoming touchpoint)

---

## Step 4 — Write to Google Sheets
Run scripts/sheets_write.py to persist new signals detected during the signal check to Signal Log tab.

  python scripts/sheets_write.py "Signal Log" '<json_rows>'

Format <json_rows> as a JSON array of arrays:
[Company, Contact, Type, Detail, Date, Classification, Counter, Triggered Workflow]

The script deduplicates on company+detail (cols 0 and 3) — safe to run more than once.
Note: flag updates to the GTM Pipeline are written by the operator directly
after reviewing the flagged action list produced in Step 3.
Confirm the script logs "wrote N row(s)" to confirm success.
If the script errors, log the error in MEMORY.md and continue.

---

## Step 5 — Write Output and Log Session
Write to memory/output/:
Write the full prioritized flag action list to:
`memory/output/output-09-{YYYYMMDD}-pipeline-flags.md`
Include: AT-RISK list, EXPANSION list, STALLED list, WARM list with
combined priority scores.

Append to MEMORY.md (index only):
```
[DATE] — Skill 09 Deal Flagging
Ran: Skill 09
Raw files: [list raw-09 files written]
Output files: output-09-{YYYYMMDD}-pipeline-flags.md
Sheets updated: Signal Log — N rows
Blockers added: [count of AT-RISK accounts]
Next: Operator reviews within 24 hours
```
Append AT-RISK accounts to memory/todos/todos.md:
`[URGENT] AT-RISK — {Company} — {Contact} — next step overdue as of {date}`