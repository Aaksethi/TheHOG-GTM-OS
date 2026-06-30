# Skill 08 — Follow-Up Drafter

## Purpose
Write a post-meeting follow-up email using meeting notes provided
by the operator. Draft only — never send.

## Schema
Read and write using master record defined in .claude/schema.json.
Flatten to sheet using sheet_mappings for this skill's output sheet.

---

## Trigger
Operator says: "draft follow-up for [company]" / "write follow-up
from today's call with [contact]"
Always runs after Skill 07 meeting concludes.

---

## Step 1 — Input
Operator must provide:
- Contact name, title, company
- Meeting type: first call, demo, follow-up, expansion
- Key points discussed (bullet notes are fine)
- Any commitments made by either side
- Agreed next step

If next step is missing, flag it before drafting.
A follow-up without a clear next step is a dead email.

---

## Pre-Draft Research Sequence

1. POST /api/deep-research [ASYNC] — refresh context on the contact. Check for any role changes, new posts, or stated priorities since the meeting.
   Body: {
     prompt: 'Research [person name] at [company]. Has their role or stated priorities changed recently? Any new posts, publications, or announcements since [meeting date]?',
     schema: {type:'object', properties:{role_changes:{type:'string'}, recent_activity:{type:'string'}, new_priorities:{type:'string'}}}
   }
   Poll: GET /api/operations/:id from pollUrl.

2. POST /api/v1/platform/scrapers/linkedin/profile [SYNC] — pull any LinkedIn activity posted since the meeting date.
   Body: {username:'contact-linkedin-id'}
   Read: recent posts, headline changes since last session.
   Note anything relevant to reference in the draft.

Draft must include: meeting recap in one sentence, agreed next step,
one forward reference (study pack, sample request, or intro offer).
Reference any LinkedIn activity found in step 2 if relevant.

---

## Raw Dump — Write After Each Call

- After deep-research refresh: `raw-08-{YYYYMMDD}-deep_research_{contact_slug}.json`
- After LinkedIn profile scrape: `raw-08-{YYYYMMDD}-linkedin_profile_{contact_slug}.json`

---

## Step 2 — Draft Structure
- Line 1: one sentence referencing a specific thing they said
- Line 2: recap of what was agreed — crisp, no filler
- Line 3: any materials being sent (case study, evidence pack, product spec)
- Line 4: next step with specific date or timeframe
- Sign off: name only, no fluff

Hard limits:
- Under 150 words
- No "great to meet you" or "as discussed" openers
- No generic closing lines

---

## Step 3 — CRM Update Block
After the draft, produce a separate CRM block for Pipeline sheet:

**Company:** 
**Contact:**
**Deal Stage:** [move to: Contacted / Meeting Done / Proposal / Stalled]
**Last Touch:** [date]
**Next Step:** [exact action and date]
**Notes:** [one sentence on where the deal stands]
**Fit Score:** [carry forward from Skill 01 gtm.icp_score]
**Engagement Score:** [current score] + [points for this interaction] = [new score]
**Flag:** [AT-RISK | STALLED | WARM | NULL]

Operator pastes this directly into Pipeline sheet.

---

## Step 4 — Write to Google Sheets
Run scripts/sheets_write.py to persist the follow-up draft to Outreach Draft tab.

  python scripts/sheets_write.py "Outreach Draft" '<json_rows>'

Format <json_rows> as a JSON array of arrays:
[Date, Name, Title, Company, Email, Product Match, Format, Signal Used,
Draft Body, Signals, Proof Point Used, Status]

The script deduplicates on email (col index 4) — safe to run more than once.
Confirm the script logs "wrote N row(s)" to confirm success.
If the script errors, log the error in MEMORY.md and continue.
Do not abort if Sheets write fails — draft is in MEMORY.md as backup.

---

## Step 5 — Write Output and Log Session
Write to memory/output/:
Write the full follow-up draft and CRM block to:
`memory/output/output-08-{YYYYMMDD}-{company_slug}-followup.md`
Format: include Draft Body and CRM Update Block (both sections).

Append to MEMORY.md (index only):
```
[DATE] — Skill 08 Follow-Up Drafter
Ran: Skill 08
Raw files: [list raw-08 files written]
Output files: [output-08 filename written]
Sheets updated: Outreach Draft — N rows
Blockers added: [1 if next step date within 48h — mark urgent in todos.md]
Next: Operator sends manually. Pipeline sheet updated with CRM block.
```
If next step date is within 48 hours:
Append to memory/todos/todos.md:
`[URGENT] {Company} — follow-up next step due {date}. Draft in output-08-{YYYYMMDD}-{slug}.md`