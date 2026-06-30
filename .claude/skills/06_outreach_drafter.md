# Skill 06 — Outreach Drafter

## Purpose
Write cold email and LinkedIn outreach drafts using enriched contact
data and live signals. Draft only — never send.

## Schema
Read and write using master record defined in .claude/schema.json.
Flatten to sheet using sheet_mappings for this skill's output sheet.

---

## Trigger
Operator says: "draft outreach for [contact]" / "write a cold email to
[company]" / "draft LinkedIn message for this list"

Always pulls from Skill 02 enrichment and Skill 05 signal queue.
Never drafts without enriched context.

---

## Pre-Draft Research Sequence

Before drafting anything, run this research sequence on the contact:

1. POST /api/deep-research [ASYNC] — pull background, career history, publicly worked on, stated interests or priorities.
   Body: {
     prompt: 'Research [person name] at [company]. Cover: career background, current role focus, publicly stated priorities, any recent publications or talks.',
     schema: {type:'object', properties:{background:{type:'string'}, current_focus:{type:'string'}, stated_priorities:{type:'array',items:{type:'string'}}, recent_activity:{type:'string'}}}
   }
   Poll: GET /api/operations/:id from pollUrl until succeeded.

2. POST /api/v1/platform/scrapers/linkedin/profile [SYNC] — pull recent LinkedIn activity: posts, comments, about section.
   Body: {username:'linkedin-public-id'}
   Read: data.headline, data.about, data.experience, data.top_skills.
   Look for signals about current priorities.

3. POST /api/v1/platform/scrapers/linkedin/company [SYNC] — pull company context: recent posts, description, size, any public announcements.
   Body: {username:'company-linkedin-slug'}
   Read: data.description, recent context for personalization.

Draft only after all three steps complete.
Draft must include: one specific signal from step 2 or 3, one matched
proof point from BRAND.md, one soft call to action.
No generic drafts. Every draft is personalized to that contact's context.

---

## Raw Dump — Write After Each Call

- After deep-research call: `raw-06-{YYYYMMDD}-deep_research_{contact_slug}.json`
- After LinkedIn profile scrape: `raw-06-{YYYYMMDD}-linkedin_profile_{contact_slug}.json`
- After LinkedIn company scrape: `raw-06-{YYYYMMDD}-linkedin_company_{company_slug}.json`

---

## Step 1 — Input Check
Before drafting confirm:
- Contact name, title, company
- Enriched category and product match (from BRAND.md mapping)
- Signal from Skill 05 OR ICP score of 3 from Skill 01
  (ICP score 3 is sufficient to justify cold outreach without a signal)
- Format: email or LinkedIn

If any of the above is missing, stop and ask operator before proceeding.

---

## Step 2 — Select Proof Point
Match the proof point to the contact's category and persona, pulling only
from the Proof Points table in BRAND.md:

- Match the persona (per BRAND.md) to the proof point that persona cares about.
- Innovation/technical personas → the strongest evidence/claim proof point.
- Commercial personas → the strongest traction/market proof point.
- Founder/CEO → lead with the traction proof point, then one supporting number;
  keep it under 5 sentences.

Never use a proof point outside BRAND.md. Never fabricate a number.

---

## Step 3 — Draft Structure

Cold Email:
- Subject: [specific signal or category reference — never generic]
- Line 1: one sentence on their product or signal — shows you know them
- Line 2: one proof point from BRAND.md matched to their category
- Line 3: what other companies in their category are doing with your product
- Line 4: single clear ask — 15-min call or send the evidence/study

LinkedIn:
- Line 1: signal reference
- Line 2: one proof point
- Line 3: single ask
- Hard limit: 3 sentences, no exceptions

---

## Step 4 — Output Format
For each draft produce:

**Contact:** name, title, company
**Signal used:** what triggered this outreach
**Product match:** the product from BRAND.md
**Format:** email or LinkedIn
**Draft:** full text ready for review

Flag anything that needed an assumption — operator reviews before use.

---

## Step 5 — Write to Google Sheets
Run scripts/sheets_write.py to persist drafts to Outreach Draft tab.

  python scripts/sheets_write.py "Outreach Draft" '<json_rows>'

Format <json_rows> as a JSON array of arrays:
[Date, Name, Title, Company, Email, Product Match, Format, Signal Used,
Draft Body, Signals, Proof Point Used, Status]

The script deduplicates on email (col index 4) — safe to run more than once.
Confirm the script logs "wrote N row(s)" to confirm success.
If the script errors, log the error in MEMORY.md and continue.
Do not abort if Sheets write fails — draft is in MEMORY.md as backup.

---

## Step 6 — Write Output and Log Session
Write to memory/output/:
For each draft produced, write the full draft object to:
`memory/output/output-06-{YYYYMMDD}-{contact_slug}-draft.md`
Format: include Contact, Signal Used, Product Match, Format, and full Draft Body.

Append to MEMORY.md (index only):
```
[DATE] — Skill 06 Outreach Drafter
Ran: Skill 06
Raw files: [list raw-06 files written]
Output files: [list output-06 draft files written]
Sheets updated: Outreach Draft — N rows
Blockers added: [count of drafts flagged for operator review]
Next: Operator reviews and sends manually
```
