# Skill 03 — Competitor Monitor

## Purpose
Track competitors and surface signals the company should know about or
act on. Feeds Skill 05 (re-engagement) and informs outreach positioning
in Skill 06.

## Schema
Read and write using master record defined in .claude/schema.json.
Flatten to sheet using sheet_mappings for this skill's output sheet.

---

## Trigger
Operator says: "check competitor activity" / "what are [competitor] doing"
/ "any new moves in the space"

---

## Competitors to Monitor
Use the competitor list defined in the "Competitors to Monitor" table in BRAND.md.

---

## Step 1 — Monitoring Sequence

Run in this order every time the skill is triggered:

1. GET /api/v1/monitors [SYNC] — returns list of monitors with their ids.
   Check which entities are already being watched.

2. For any target brand or competitor NOT already monitored:
   POST /api/v1/monitors [SYNC, returns 201]
   For LinkedIn keyword monitoring: {name:'[brand] LinkedIn', type:'linkedin_keyword', config:{query:'[brand name]'}, cadence_minutes:60, max_results:10}
   For web monitoring: {name:'[brand] web', type:'web_search', config:{query:'[brand name] [category from BRAND.md]'}, cadence_minutes:60, max_results:10}
   Save the returned monitor id for subsequent event calls.

3. POST /api/v1/monitors/:id/run-now [SYNC] — trigger an immediate sweep across all monitors.

4. GET /api/v1/monitors/:id/events [SYNC] — pull all new events since last run.
   Returns list of events. Read each event's content and date.

5. POST /api/v1/platform/scrapers/linkedin/keyword-posts [SYNC] — keyword search for competitor
   announcements, product launches, hiring signals not caught by monitors.
   Body: {query:'[competitor name] OR [category keywords from BRAND.md]', max_results:10, match_mode:'broad', date_filter:'past-week'}

6. POST /api/v1/search [ASYNC] — scan for press, PR, trade publications not on LinkedIn.
   Body: {type:'web_search', query:'[brand] [category from BRAND.md] announcement', max_results:10}
   Poll: GET /api/v1/search/:id from poll_url.

Classify each event:
- Buying signal: target brand hiring R&D/innovation, new product launch,
  funding announcement
- Competitive signal: competitor announcement, new claim, new customer win
- Product match signal: target brand launching something that matches
  one of your products in BRAND.md

Write all events to Signal Log tab. Flag buying signals and product
match signals for Skill 05 re-engagement.

---

## Raw Dump — Write After Each Call

- After monitor events pull: `raw-03-{YYYYMMDD}-monitor_events_{competitor_slug}.json`
- After keyword-posts call: `raw-03-{YYYYMMDD}-keyword_posts_{competitor_slug}.json`
- After web_search call: `raw-03-{YYYYMMDD}-web_search_{competitor_slug}.json`

---

## Step 2 — Signal Classification
Classify each signal found:

HIGH — New study/claim published, new partnership announced,
       direct claim that overlaps with your positioning
MEDIUM — Trade press mention, new relevant job posting, conference presence
LOW — General brand content, social activity with no commercial signal

Surface HIGH signals immediately. Batch MEDIUM and LOW into session log.

---

## Step 3 — Counter-Position
For every HIGH signal, produce one sentence the company can use in outreach
to counter or differentiate. Pull only from BRAND.md proof points.

Example: a competitor publishes a new study →
counter with the matching proof point from BRAND.md that beats or
contextualizes their claim. Never fabricate a number.

---

## Step 4 — Output Format
For each signal found, output a JSON signal object appended to the
master record signals[] array:

- signals[].type = competitor name
- signals[].detail = signal description
- signals[].date = date detected
- signals[].classification = HIGH | MEDIUM | LOW
- signals[].counter = one sentence counter from BRAND.md proof points
- signals[].triggered_workflow = "skill_05"

Write to Signal Log sheet using sheet_mappings.
Pass HIGH signals immediately to Skill 05 as merged master records.

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
[DATE] — Skill 03 Competitor Monitor
Ran: Skill 03
Raw files: [list raw-03 files written]
Output files: none — signals written directly to Signal Log sheet
Sheets updated: Signal Log — N rows
Blockers added: 0
Next: HIGH signals passed to Skill 05
```
