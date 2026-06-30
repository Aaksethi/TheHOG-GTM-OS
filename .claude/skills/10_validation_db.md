# Skill 10 — Validation DB Updater

## Purpose
Keep your proof points, channel/performance data, and customer retention
stats current. Ensures every other skill is drafting from accurate,
up-to-date evidence.

## Schema
Read and write using master record defined in .claude/schema.json.
Flatten to sheet using sheet_mappings for this skill's output sheet.

---

## Trigger
Operator says: "update proof points" / "check if our stats are current"
/ "we published a new study"
Recommended cadence: once per month or when new evidence is published.

---

## Step 1 — Input
Operator provides one or more of:
- New study or evidence (paste key findings or upload)
- Updated channel/ranking/performance data
- Updated customer retention or expansion numbers
- New press coverage with a quotable claim

If no input is provided, run Step 2 to check for new public data.

---

## Validation Research Sequence

Before logging any claim:

1. POST /api/deep-research [ASYNC] — cross-check the claim against the brand's public positioning and product pages.
   Body: {
     prompt: 'Cross-check this claim against [brand name] public positioning: [claim text]. Does their website or press support this type of claim in [your market]?',
     schema: {type:'object', properties:{claim_supported:{type:'boolean'}, evidence:{type:'string'}, source_urls:{type:'array',items:{type:'string'}}}}
   }
   Poll: GET /api/operations/:id from pollUrl.

2. POST /api/deep-research [ASYNC] — for outcome claims, verify the claim type is supported by published evidence in your market.
   Body: {
     prompt: 'Verify whether this claim type is supported by published evidence in [your market]: [claim text]. Is this a recognized claim category? Are there published studies?',
     schema: {type:'object', properties:{claim_type_recognized:{type:'boolean'}, published_evidence_exists:{type:'boolean'}, evidence_summary:{type:'string'}, verification_status:{type:'string'}}}
   }
   Poll: GET /api/operations/:id from pollUrl.

Only log claims that survive both checks. Set status = Verified.
Claims that cannot be checked externally: log with status =
Needs Operator Verification. Never use unverified claims as
proof points in any draft or brief.

---

## Raw Dump — Write After Each Call

- After each deep-research cross-check:
  `raw-10-{YYYYMMDD}-deep_research_{claim_slug}.json`

---

## Step 3 — Validation Check
Cross-check current BRAND.md proof points table against findings:

Current and confirmed → mark as verified, no change needed
Outdated or superseded → flag with new data, await operator approval
New proof point found → draft addition for operator to review

Never remove an existing proof point without operator confirmation.
Never add a new claim without operator confirmation.

---

## Step 4 — Output Format
Produce a validation report:

**Checked:** [date]
**Proof points reviewed:** [count]
**Confirmed current:** [count]
**Flagged for update:** [list with old claim vs. new finding]
**New additions pending approval:** [list]

Operator reviews, approves changes, then updates BRAND.md manually.

---

## Step 5 — Write Output and Log Session
Write to memory/wiki/:
Write the full validation report to:
`memory/wiki/validation-report-{YYYYMMDD}.md`
Format: include all proof points reviewed, confirmed/flagged/pending status.

Write to Google Sheets (processed results only):
Run scripts/sheets_write.py "Validation Log" to write only Verified
and Needs Operator Verification entries. Raw evidence text goes in
the wiki file, not the sheet.

  python scripts/sheets_write.py "Validation Log" '<json_rows>'

Format <json_rows> as a JSON array of arrays:
[Company, Contact, Type, Claim Text, Date, Verification Status, Evidence Summary, Source]

The script deduplicates on company+detail (cols 0 and 3) — safe to run more than once.
Confirm the script logs "wrote N row(s)" to confirm success.
If the script errors, log the error in MEMORY.md and continue.

Append to MEMORY.md (index only):
```
[DATE] — Skill 10 Validation DB
Ran: Skill 10
Raw files: [list raw-10 files written]
Output files: validation-report-{YYYYMMDD}.md in memory/wiki/
Sheets updated: Validation Log — N rows
Blockers added: [count of claims flagged for operator approval]
Next: Operator reviews, approves changes, updates BRAND.md manually
```
