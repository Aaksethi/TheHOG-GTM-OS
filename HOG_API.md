# HOG_API.md — GTM Hog API Reference

All Hog calls are direct REST API calls.
Base URL: https://developer.thehog.ai
Auth headers on every request: X-Access-Key and X-Secret-Key (from .env)

---

## Async vs Sync — read this before every call

ASYNC endpoints return 202 with {operationId, pollUrl, status:'queued'}.
Poll GET {pollUrl} every 2-3 seconds until status = 'succeeded'.
Read the result from the 'result' field of the poll response.
Never move to the next step until the current async call resolves.
Never run two async calls at the same time.

Poll status values: queued → processing → succeeded (read result) or failed (read error)

SYNC endpoints return 200 with data immediately.
Read from the 'data' field. No polling needed.

Note: POST /api/v1/search is async but polls a different path.
It returns poll_url (snake_case) pointing to GET /api/v1/search/:id,
not /api/operations/:id.

---

## REST Endpoint Reference

ASYNC — Web and Social Search:
- POST /api/v1/search
  Body: {type:'web_search'|'linkedin_keyword'|'site_search', query:string, max_results:number, exclude_domains:[], sort_by:'relevance'|'recent'}
  Poll: GET /api/v1/search/:id from poll_url (snake_case)

ASYNC — People Discovery:
- POST /api/v1/people/search
  Body: {query:string, limit:number, filters?:{titles:[], titleMatch:'similar', locations:[], industries:[], company:{domains:[], names:[], employeeCount:{min,max}}}, includeContacts:bool, includeSignals:bool}
  Poll: GET /api/operations/:id from pollUrl
  Note: set filters.company.domains to scope search within known companies
  Warning: returns zero results on current Hog plan — use as fallback only

ASYNC — Enrichment:
- POST /api/enrichments
  Single: {identifier:{linkedin_url:string}, fields:[]}
  Batch: {identifiers:[{linkedin_url:string}], fields:[]}
  Correct fields: 'contact.email', 'work_email', 'contact.phone', 'profile'
  NEVER use: company_name or company_size (rejected with 400)
  Returns 200 sync for single, 202 async for batch
  If 202: Poll GET /api/enrichments/:id
  Known behavior: reliably returns work_email only — name/title/company return null

ASYNC — Research:
- POST /api/deep-research
  Body: {prompt:string, schema:{type:'object', properties:{...}}, urls?:[], maxCredits?:number}
  Poll: GET /api/operations/:id from pollUrl
  Warning: rate-limited at ~300 credits, 429 on concurrent calls — run sequentially

SYNC — LinkedIn Scrapers (200, no polling):
- POST /api/v1/platform/scrapers/linkedin/finder
  Body: {domains:['https://example.com']}
  Returns: data:[{domain, linkedin_url, company_name}]
  Rule: ONE batch call — never loop per domain. Max 50 domains.

- POST /api/v1/platform/scrapers/linkedin/profile
  Body: {username:'linkedin-public-id'}
  Returns: data:{full_name, headline, about, current_company, experience, ...}
  Note: username is the part after /in/ in the LinkedIn URL

- POST /api/v1/platform/scrapers/linkedin/company
  Body: {username:'company-slug'} or {url:'https://linkedin.com/company/...'}
  Returns: data:{name, description, employee_count, ...}

- POST /api/v1/platform/scrapers/linkedin/company-posts
  Body: {username:'company-slug', max_results:10}
  Returns: data:[{text, published_at, post_url, ...}]

- POST /api/v1/platform/scrapers/linkedin/profile-posts
  Body: {username:'linkedin-public-id', max_results:10}
  Returns: data:[{text, published_at, ...}]

- POST /api/v1/platform/scrapers/linkedin/keyword-posts
  Body: {query:string, max_results:10, match_mode:'broad'|'exact', date_filter:'past-24h'|'past-week'}
  Returns: data:[{text, author_name, author_headline, post_url, ...}]

SYNC — Web Scraper (200, no polling):
- POST /api/v1/platform/scrapers/web/scrape
  Body: {url:string, renderJs:bool}
  Returns: data:{url, text, statusCode}

SYNC — Monitors (200 or 201, no polling):
- POST /api/v1/monitors
  Body: {name:string, type:'linkedin_keyword'|'linkedin_company'|'web_search', config:{query:string}, cadence_minutes:60, max_results:10}
  Returns 201 with monitor object including id
- GET /api/v1/monitors — list all monitors with ids
- GET /api/v1/monitors/:id/events — events detected by monitor
- POST /api/v1/monitors/:id/run-now — trigger immediate sweep

SYNC — Poll operations (200):
- GET /api/operations/:id
  Terminal: 'succeeded' (read result) or 'failed' (read error)
  Do not poll more than once every 2 seconds

---

## Discovery Waterfall — Company-First Sequencing

Run in this order. Stop when you have enough companies.
Skip companies/search if it does not index your ICP's company-size band
(small and mid-market brands are often absent from it).

1. POST /api/v1/search type:web_search [ASYNC] — live web search for brands in segment
2. POST /api/v1/platform/scrapers/web/scrape [SYNC] — scrape brand list pages from step 1
3. POST /api/v1/platform/scrapers/linkedin/finder [SYNC] — batch convert all domains in one call
4. POST /api/v1/people/search with filters.company.domains [ASYNC] — fallback only, expect zero
5. POST /api/v1/platform/scrapers/linkedin/profile [SYNC] — scrape individual profiles directly

Merge and deduplicate by domain before proceeding to contact search.

---

## API Hard Rules
- Never hallucinate API responses — null means null, surface it
- All async calls must fully resolve before the next call starts
- Never request company_name or company_size in enrichment fields
- Never run two async calls simultaneously
- Write every raw API response to memory/raw/ immediately after the call
