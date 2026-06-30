# Skill 01 — ICP Builder

## Purpose
Build a verified list of ICP-matched contacts at target companies using
company-first sequencing. Output is structured JSON passed to Skill 02.

## Schema
Read and write using master record defined in .claude/schema.json.
Flatten to sheet using sheet_mappings for this skill's output sheet.

---

## Trigger
Operator says: "build a target list" / "find brands in [category]"
Confirm segment and size before running.

---

## Input
```json
{
  "segment": "<segment from BRAND.md> | all",
  "company_size": "emerging | scaling | all (bands defined in BRAND.md)",
  "persona_priority": "<persona from BRAND.md>"
}
```

---

## Step 1 — Company Discovery (Waterfall)

Rule: skip database endpoints if they do not index your ICP's size band.
Many databases do not index small/mid-market brands and instead return
enterprise accounts that fail the ICP immediately and waste credits.
Start discovery from live web search unless BRAND.md says otherwise.

Async/sync rules and poll paths: see HOG_API.md.

Attempt sources in order. Stop when you have enough companies to
meet the requested list size. Merge and deduplicate across sources
by company domain before moving to Step 2.

**Attempt 1 — POST /api/v1/search [ASYNC]**
Body: {type:'web_search', query:'[segment keywords from BRAND.md] [channel/market terms from BRAND.md]', max_results:20}
Poll: GET /api/v1/search/:id from poll_url (snake_case) until succeeded.
Extract company names and domains from result.results[].url and result.results[].title.

**Attempt 2 — POST /api/v1/platform/scrapers/web/scrape [SYNC]**
For each high-value URL surfaced in Attempt 1 (brand list pages,
marketplace category pages, channel directories from BRAND.md):
Body: {url:'[target URL]', renderJs:false}
Returns data.text immediately.
Extract additional brand names and domains from data.text.
Add any new domains not already found in Attempt 1.

**Attempt 3 — POST /api/v1/platform/scrapers/linkedin/finder [SYNC]**
*** ONE BATCH CALL — NOT ONE CALL PER DOMAIN ***
Collect ALL domains discovered in Attempts 1 and 2 first.
Then make a SINGLE call: {domains:['a.com','b.com','c.com'...]}
Max 50 domains per call. Returns data:[{domain, linkedin_url,
company_name}] for each domain.
This replaces multiple sequential calls. Do not loop.

**Attempt 4 — POST /api/v1/people/search [ASYNC]**
Body: {
  query:'[persona titles from BRAND.md] [segment] [geography from BRAND.md]',
  filters:{
    titles:[<persona titles from BRAND.md>],
    titleMatch:'similar',
    locations:[<geography from BRAND.md>],
    company:{domains:['domain1.com','domain2.com']}
  },
  limit:25,
  includeContacts:true,
  includeSignals:true
}
Use the domains confirmed in Attempt 3.
Poll: GET /api/operations/:id from pollUrl until succeeded.

Segment keywords: pull from the Target Segments and Search Keywords table in BRAND.md.

Run all discovery calls sequentially. Never in parallel.

---

## Raw Dump — Write After Each API Call
Immediately after each API call in Step 1 returns data, write the
raw response to memory/raw/:

- After web_search call: write full result to `raw-01-{YYYYMMDD}-web_search.json`
- After each web scrape: append to `raw-01-{YYYYMMDD}-scrape.json`
- After linkedin/finder: write to `raw-01-{YYYYMMDD}-linkedin_finder.json`
- After people/search: write to `raw-01-{YYYYMMDD}-people_search.json`

Write the raw response as-is. Do not filter or process before writing.
This is the source record — processing happens in Steps 2–5.

---

## Step 2 — Company ICP Filter
Score each company before touching any contacts, against the ICP hard
criteria in BRAND.md.

PASS — right category, right size band, required channel/market presence (per BRAND.md)
FAIL — retailer, distributor, contract manufacturer, wrong category,
       missing required channel presence, or any disqualifier in BRAND.md

Drop FAIL companies immediately. Log count.
Only run Step 3 on PASS companies.

---

## Step 3 — Contact Search Inside Passing Companies

Async/sync rules and poll paths: see HOG_API.md.

For each company that passed Step 2, find the right contact using
this waterfall:

**Primary: POST /api/v1/people/search [ASYNC] with filters.company.domains set to the passing company domains and filters.titles set to persona titles from BRAND.md**
Body: {query:'[persona description] at target company', limit:5, filters:{titles:[<persona titles from BRAND.md>], titleMatch:'similar', company:{domains:['company-domain.com']}}, includeContacts:true}
Poll GET /api/operations/:id until succeeded.
Attempt first. On the current Hog plan this often returns zero — if empty, fall through to the next method immediately. Do not retry.

**Fallback: POST /api/v1/people/search [ASYNC] with filters.company.names set to the company name**
If domain-scoped search returns no results:
Body: {query:'[persona description]', limit:5, filters:{titles:[<persona titles from BRAND.md>], titleMatch:'similar', company:{names:['Company Name']}}, includeContacts:true}
Poll GET /api/operations/:id until succeeded.

**Last resort: POST /api/v1/platform/scrapers/linkedin/company [SYNC] then POST /api/v1/platform/scrapers/linkedin/profile [SYNC] — body: {username: linkedin-public-id}**
If both above return empty:
1. POST /api/v1/platform/scrapers/linkedin/company — body: {username:'company-slug'} to get company context.
2. Identify the most senior matching profile from company data.
3. POST /api/v1/platform/scrapers/linkedin/profile — body: {username:'linkedin-public-id'} to pull the contact.

**Confirmed reliable path (from prior sessions):**
The most reliable contact discovery sequence is:
POST /api/v1/search type:web_search → find LinkedIn URLs from results →
POST /api/v1/platform/scrapers/linkedin/profile → POST /api/enrichments for email.
Use this if Primary and Fallback both return empty.

Persona titles: use the buyer personas defined in BRAND.md, in priority order.

Pull one primary contact per company matching persona priority.
If primary persona not found, pull next persona in sequence.
Contact fields returned: name, title, linkedinUrl, location.
Company fields (domain, industry, size): use values from Step 1.
Do not attempt to re-populate company fields from contact search results.

---

## Step 4 — Contact ICP Score
Score each contact 1-3:

3 — Exact title match, confirmed category, verified channel presence
2 — Adjacent title or unconfirmed channel — flag for operator review
1 — Weak title match or wrong category — drop

---

## Step 5 — Output JSON
One object per passing contact:

```json
{
  "contact": {
    "name": "",
    "title": "",
    "email": "",
    "linkedin": "",
    "seniority": ""
  },
  "company": {
    "name": "",
    "size": "",
    "revenue_range": "",
    "hq_location": "",
    "channel_presence": true,
    "categories": [],
    "active_products": []
  },
  "gtm": {
    "icp_score": 0,
    "product_match": "",
    "signal_flags": [],
    "enrichment_date": ""
  },
  "status": "Verified | Needs Review"
}
```

Set meta.record_id using format:
GTM-{YYYYMMDD}-{company_name_slug}-{contact_name_slug}
Set meta.created_date = today
Set meta.skills_run = ["skill_01"]

Missing field → set as null, set status as Needs Review. Never drop a row.

---

## Step 6 — Write to Google Sheets
Run scripts/sheets_write.py to persist contacts to Enriched Contacts tab.

  python scripts/sheets_write.py "Enriched Contacts" '<json_rows>'

Format <json_rows> as a JSON array of arrays matching column order:
[Name, Title, Email, LinkedIn, Company, Size, Revenue, Channel, Category,
ICP Score, Product Match, Date, Signals, Status]

The script deduplicates on email (col index 2) — safe to run more than once.
Confirm the script logs "wrote N row(s)" to confirm success.
If the script errors, log the error in MEMORY.md and continue.
Do not abort if Sheets write fails — output is in MEMORY.md as backup.

---

## Step 7 — Write Output and Log Session
Write to memory/output/:
For each Verified contact, write the full JSON object from Step 5 to:
`memory/output/output-01-{YYYYMMDD}-{company_name_slug}.json`

Append to MEMORY.md (index only):
```
[DATE] — Skill 01 ICP Builder
Ran: Skill 01
Raw files: [list raw-01 files written]
Output files: [list output-01 files written]
Sheets updated: Enriched Contacts — N rows
Blockers added: [count] — see memory/todos/todos.md
Next: Pass output files to Skill 02
```

Append new blockers to memory/todos/todos.md:
Any contact marked Needs Review with a specific reason gets a numbered
entry in todos.md. Format:
`[OPEN] {Company} — {Contact} — {specific reason}`
