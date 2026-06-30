# Skill 02 — Lead Enrichment

## Purpose
Take Skill 01 JSON output and run deep company and contact enrichment.
Fills NULL fields, confirms category, assigns product match.

## Schema
Read and write using master record defined in .claude/schema.json.
Flatten to sheet using sheet_mappings for this skill's output sheet.

---

## Trigger
Always runs after Skill 01. Input is Skill 01 JSON output.
Operator can also pass manual JSON following the same schema.

---

## Input
Skill 01 JSON array. Each object must have at minimum:
- contact.name
- company.name

If neither is present, skip the record and flag to operator.

---

## Enrichment Waterfall

Enrichment confirmed behavior: POST /api/enrichments reliably
returns work_email but consistently returns null for name, title,
and company. Do not request or expect those fields from enrichment.

Run in this sequence per contact:

**Tier 1 — POST /api/v1/platform/scrapers/linkedin/profile [SYNC]**
Purpose: get name, title, company, headline, about section.
Body: {username:'linkedin-public-id'}
Extract username from the LinkedIn URL: the part after /in/
Read: data.full_name, data.headline, data.current_company,
data.about, data.experience[0]
This is the source of truth for name, title, and company.
If this returns null for a contact, set status = Needs Review.

**Tier 2 — POST /api/enrichments [ASYNC or SYNC]**
Purpose: get verified work email only.
Single contact: {identifier:{linkedin_url:'...'}, fields:['contact.email','work_email']}
Batch (up to 100): {identifiers:[{linkedin_url:'...'},...], fields:['contact.email','work_email']}
Do NOT request profile, company, title, name — those return null.
If 202 async: poll GET /api/enrichments/:id until succeeded.
If 200 sync: read data immediately.
Read: data.work_email or data.contact?.email
If email is null after enrichment: set email = null,
status = Needs Review. Flag reason: missing email. Never drop the row.

**Tier 3 — No further enrichment calls**
If both Tier 1 and Tier 2 return null for email:
Record what was found from Tier 1 (name/title/company),
set email = null, status = Needs Review. Flag reason: missing email.
Flag for manual follow-up. Do not burn more credits.

After all tiers: write every contact that has at minimum a name
and company. Never write a row where both are null.

---

## Raw Dump — Write After Each API Call
Immediately after each enrichment API call returns:

- After each LinkedIn profile scrape (Tier 1): write raw response to
  `raw-02-{YYYYMMDD}-linkedin_profile_{contact_slug}.json`
- After enrichment call (Tier 2): write raw response to
  `raw-02-{YYYYMMDD}-enrichment_{contact_slug}.json`

Write raw response as-is before extracting any fields.

---

## Step 3 — Data Quality Check
After enrichment, validate each record:

Verified — has verified email OR LinkedIn, confirmed category,
           confirmed channel presence
Needs Review — missing email AND LinkedIn, OR unconfirmed category
Incomplete — missing company name or contact name entirely → flag, do not output

Update status field in JSON accordingly.

---

## Step 4 — Product Match Assignment
Assign based on the confirmed category, using the product / proof-point
mapping defined in BRAND.md:

Category A → Product A (per BRAND.md)
Category B → Product B (per BRAND.md)
Multiple categories confirmed → "Dual Opportunity" — flag separately

Update gtm.product_match in JSON. Never invent a product not in BRAND.md.

---

## Step 5 — Output JSON
Return fully enriched JSON using same schema as Skill 01.
All previously NULL fields filled where Hog returned data.
Fields Hog could not confirm remain null — never guess.

Append "skill_02" to meta.skills_run.
Set meta.last_updated = today.

```json
{
  "contact": {
    "name": "",
    "title": "",
    "email": "",
    "linkedin": "",
    "seniority": "",
    "tenure_months": 0,
    "recent_linkedin_activity": ""
  },
  "company": {
    "name": "",
    "size": "",
    "revenue_range": "",
    "hq_location": "",
    "channel_presence": true,
    "categories": [],
    "active_products": [],
    "current_solution": "",
    "open_relevant_roles": true,
    "recent_press": ""
  },
  "gtm": {
    "icp_score": 0,
    "product_match": "",
    "signal_flags": [],
    "enrichment_date": ""
  },
  "status": "Verified | Needs Review | Incomplete"
}
```

---

## Step 6 — Write to Google Sheets
Run scripts/sheets_write.py to persist enriched contacts to Enriched Contacts tab.

  python scripts/sheets_write.py "Enriched Contacts" '<json_rows>'

Format <json_rows> as a JSON array of arrays matching column order:
[Name, Title, Email, LinkedIn, Company, Size, Revenue, Channel, Category,
ICP Score, Product Match, Date, Signals, Status]

The script deduplicates on email (col index 2) — safe to run more than once.
Flag Needs Review rows for operator attention in your MEMORY.md log.
Dual Opportunity records: note separately in MEMORY.md — high priority.
Confirm the script logs "wrote N row(s)" to confirm success.
If the script errors, log the error in MEMORY.md and continue.

---

## Step 7 — Write Output and Log Session
Write to memory/output/:
For each contact processed, write the fully enriched JSON object to:
`memory/output/output-02-{YYYYMMDD}-{company_name_slug}-{contact_slug}.json`
Flag: Dual Opportunity records get a separate file prefixed DUAL-:
`memory/output/DUAL-output-02-{YYYYMMDD}-{company_name_slug}.json`

Append to MEMORY.md (index only):
```
[DATE] — Skill 02 Lead Enrichment
Ran: Skill 02
Raw files: [list raw-02 files written]
Output files: [list output-02 files written]
Sheets updated: Enriched Contacts — N rows
Blockers added: [count] — see memory/todos/todos.md
Next: Pass Verified output files to Skill 05 or 06
```

Append Needs Review contacts to memory/todos/todos.md.
