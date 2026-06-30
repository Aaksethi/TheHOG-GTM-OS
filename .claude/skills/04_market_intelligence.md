# Skill 04 — Market Intelligence

## Purpose
Surface category-level trends in your market that inform targeting,
messaging, and outreach timing. Not company-specific.

---

## Trigger
Operator says: "what's trending in [your market]" / "any new category signals"
/ "what should we know about the [segment] market"

---

## Step 1 — Confirm Scope
Confirm with operator:
- Category focus: one of the segments in BRAND.md, or all
- Time window: last 30 days (default), last 90 days, or last 6 months

---

## Schema
Read and write using master record defined in .claude/schema.json.
Flatten to sheet using sheet_mappings for this skill's output sheet.

---

## Step 2 — Research Sequence

1. POST /api/deep-research [ASYNC] — primary call.
   Body: {
     prompt: 'Research [your category/product space from BRAND.md] [year]. Cover: market size (TAM), CAGR, top claims, top brands, competitive offerings, regulatory environment, whitespace opportunities.',
     schema: {type:'object', properties:{tam:{type:'string'}, cagr:{type:'string'}, top_claims:{type:'array',items:{type:'string'}}, competitive_landscape:{type:'array',items:{type:'string'}}, whitespace:{type:'string'}, regulatory_note:{type:'string'}}}
   }
   Poll: GET /api/operations/:id from pollUrl until succeeded.

2. POST /api/v1/search [ASYNC] — supplement with live data points not in deep research.
   Body: {type:'web_search', query:'[your market] market size [year] [category trend from BRAND.md]', max_results:15}
   Poll: GET /api/v1/search/:id from poll_url.

3. POST /api/v1/platform/scrapers/web/scrape [SYNC] — scrape specific trade sources if identified in step 2 (industry publications and association reports relevant to your market).
   Body: {url:'[target URL]', renderJs:false}
   Returns data.text immediately.

4. POST /api/deep-research [ASYNC] — spot-check up to 3 named competitors that appear in the brief to verify their current positioning.
   Body: {prompt:'Research [company name] — their strategy, current product claims, and competitive positioning in [your market].', schema:{type:'object', properties:{strategy:{type:'string'}, current_claims:{type:'array',items:{type:'string'}}, competitive_position:{type:'string'}}}}
   Poll: GET /api/operations/:id from pollUrl until succeeded.

Output a structured brief with sections: TAM, CAGR, Top Claims,
Competitive Landscape, Whitespace, Regulatory Note.
Save to /memory/wiki/ as evergreen reference.

---

## Raw Dump — Write After Each Call

- After deep-research call (step 1): `raw-04-{YYYYMMDD}-deep_research_market.json`
- After web_search call (step 2): `raw-04-{YYYYMMDD}-web_search_market.json`
- After web scrape calls (step 3): `raw-04-{YYYYMMDD}-scrape_{source_slug}.json`
- After competitor spot-check (step 4): `raw-04-{YYYYMMDD}-deep_research_{competitor_slug}.json`

---

## Step 3 — Filter for Relevance
Only surface findings that are actionable for your company. Discard:
- Trends in categories outside your ICP (per BRAND.md disqualifiers)
- Consumer/brand news with no implication for your offering
- Generic industry size statistics with no timing signal

---

## Step 4 — Output Format
Produce a structured brief:

**Category:** [confirmed scope]
**Period:** [time window]
**Top 3 trends:** one sentence each, with source
**Channel signals:** top movers in your channel (per BRAND.md) with direction
**Brands to watch:** any brand showing expansion signal in this category
**Implication:** one paragraph — what this means for targeting and which
  proof points are most relevant given current category momentum

Also output a structured array:
```json
brands_to_watch: ["Brand Name 1", "Brand Name 2", "Brand Name 3"]
```

This array passes directly to Skill 01 as input, bypassing the
keyword search step and going straight to contact search inside
these specific companies.

---

## Step 5 — Save to Wiki
Write the structured brief from Step 4 to memory/wiki/:
Filename: `market-intel-{category_slug}-{YYYYMMDD}.md`
Format: full structured brief (TAM, CAGR, Top Claims, Competitive
Landscape, Whitespace, Regulatory Note, Brands to Watch array).
No Google Sheets write for this skill.

---

## Step 6 — Log Session
Append to MEMORY.md (index only):
```
[DATE] — Skill 04 Market Intelligence
Ran: Skill 04
Raw files: [list raw-04 files written]
Output files: [wiki filename written]
Sheets updated: none
Blockers added: [count of new brands flagged for Skill 01 queue] — see todos.md
Next: Feed brands_to_watch into Skill 01
```
Append brands_to_watch to memory/todos/todos.md as:
`[OPEN] Skill 01 queue — {Brand Name} — flagged from Skill 04 market intel {date}`
