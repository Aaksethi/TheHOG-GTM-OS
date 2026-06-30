# GTM Agent OS

A go-to-market operating system you point at **your own ICP**. It runs as a
[Claude Code](https://claude.com/claude-code) agent: a layered set of instruction
files, skills, sub-agents, and hard rules that turn live web/social intelligence
(via [The Hog API](https://developer.thehog.ai)) into ICP-matched, enriched,
draft-ready outbound — written to Google Sheets as the source of truth.

The agent ships **company-neutral**. You don't edit code to use it — you fill in
one file (`BRAND.md`) with your products, ICP, and proof points, add your API keys,
and the same skills run against your market.

> **Draft-only by design.** The agent never sends a single email or message. Every
> output is staged for a human operator to review and send manually.

---

## What it does

Given a market segment from your `BRAND.md`, the agent will:

1. **Discover** target companies via a company-first search waterfall (live web
   search → page scrapes → LinkedIn resolution).
2. **Filter** every company against your ICP (category, revenue band, channel)
   *before* any contact is touched.
3. **Find & enrich** the right decision-maker (the personas you define) and pull a
   verified email or LinkedIn.
4. **Score** each record and mark it `Verified`, `Needs Review`, or `Incomplete`.
5. **Draft** cold outreach pairing a real, observed signal with one of *your* proof
   points — never fabricated.
6. **Persist** processed results to Google Sheets and log the session to memory.

Quality over volume is enforced at every step: *8 verified, ICP-matched contacts
beats 80 unvetted ones.*

---

## Add your ICP and inputs

This is the whole setup. Two files define everything about *your* business; nothing
about the agent's machinery needs to change.

### 1. Fill in `BRAND.md` — your ICP layer
`BRAND.md` ships as a template of `<placeholders>`. Replace them with your own:

| Section | What you provide |
|---|---|
| Products in Scope | What the agent is allowed to sell |
| ICP — Hard Criteria | Category, revenue band, channel, geography (pass/fail gates) |
| Disqualifiers | What to drop on sight |
| Target Segments & Keywords | The terms discovery (Skill 01) searches on |
| Buyer Personas | Who you write to, tied to company size |
| **Proof Points** | The *only* claims outreach may cite — never fabricated |
| Outreach Signals | What makes an account worth contacting now |
| Competitors to Monitor | What Skill 03 watches, and your edge |

The agent treats `BRAND.md` proof points as the only claims it may make. It never
invents numbers or fills gaps — so the quality of your `BRAND.md` is the quality of
your outreach.

### 2. Provide your keys — `.env`
```bash
cp .env.example .env
```

| Variable | Description |
|---|---|
| `HOG_ACCESS_KEY` | The Hog API access key (`X-Access-Key` header) |
| `HOG_SECRET_KEY` | The Hog API secret key (`X-Secret-Key` header) |
| `GOOGLE_SHEET_ID` | Target spreadsheet ID from its URL |
| `GOOGLE_SERVICE_ACCOUNT_PATH` | Path to your service-account JSON key |

That's it. With `BRAND.md` filled in and `.env` set, the agent runs against your
market — no code changes required.

> Optional deeper customization: `CLAUDE.md` (agent identity/operating rules) and
> `SOUL.md` (tone & defaults) are also editable, but the defaults work for most B2B
> GTM use cases.

---

## How it's structured

This repo is configuration-as-code for an agent, not a traditional application.
The "program" is the set of markdown contracts the model reads and executes.

```
.
├── CLAUDE.md            # Master system prompt: identity, operating rules, directory
├── BRAND.md             # YOUR ICP: criteria, personas, proof points, competitors
├── HOG_API.md           # Full Hog REST API reference (async/sync rules, endpoints)
├── SOUL.md              # Behavioral defaults, tone, decision posture
├── MEMORY.md            # Append-only session index (read at session start)
├── .claude/
│   ├── settings.json    # Agent config (Hog provider, Sheets schema, defaults)
│   ├── schema.json      # Master record schema all skills read/write
│   ├── skills/          # 10 single-purpose workflows (01–10)
│   ├── agents/          # 3 multi-skill chains
│   └── rules/           # Hard constraints loaded every session
├── scripts/             # Python helpers for Hog API + Google Sheets
├── memory/              # Runtime state (raw/, output/, wiki/, todos/)
├── requirements.txt     # Python deps (Google Sheets client)
└── .env.example         # Environment variable template
```

### Skills (`.claude/skills/`)

| File | Workflow |
|---|---|
| `01_icp_builder.md` | Build target lists of ICP-matched decision-makers |
| `02_lead_enrichment.md` | Enrich contacts and companies via Hog |
| `03_competitor_monitor.md` | Track competitor moves and signals |
| `04_market_intelligence.md` | Category trends and market landscape |
| `05_signal_reengagement.md` | Re-engage from job changes, posts, press |
| `06_outreach_drafter.md` | Cold email and LinkedIn drafts |
| `07_meeting_prep.md` | Pre-meeting research brief |
| `08_followup_drafter.md` | Post-meeting follow-up draft |
| `09_deal_flagging.md` | Flag stalled, at-risk, and expansion deals |
| `10_validation_db.md` | Keep proof points current |

### Agents (`.claude/agents/`)

Chains that orchestrate skills end-to-end:

| File | Chains |
|---|---|
| `outbound_pipeline.md` | `01 → 02 → 06` (discover → enrich → draft) |
| `deal_intelligence.md` | `07 → 08 → 09` (prep → follow-up → flag) |
| `market_monitor.md` | `03 → 04 → 05` (competitors → market → re-engage) |

### Rules (`.claude/rules/`)

Non-negotiable constraints loaded on every session:

- **`no_live_sends.md`** — the agent never sends anything live, ever.
- **`icp_filter.md`** — no contact enters a workflow without passing the ICP filter.
- **`data_quality.md`** — `Verified` / `Needs Review` / `Incomplete` gating; null means null.
- **`protect_secrets.md`** — credentials never appear in any output, draft, or sheet.

---

## Intelligence layer — The Hog API

All external intelligence comes from direct REST calls to `https://developer.thehog.ai`,
authenticated with `X-Access-Key` / `X-Secret-Key` headers. The full endpoint
contract — async vs. sync behavior, poll paths, and the company-first discovery
waterfall — lives in [`HOG_API.md`](HOG_API.md).

The Python helpers in [`scripts/`](scripts/) wrap the most-used calls:

| Script | Purpose |
|---|---|
| `hog_search.py` | Async web / LinkedIn keyword search |
| `hog_company.py` | LinkedIn company scrape |
| `hog_profile.py` | LinkedIn profile scrape |
| `hog_enrich.py` | Contact enrichment (work email) |
| `sheets_write.py` | Write processed rows to Google Sheets (dedups on email) |

---

## Setup

### Prerequisites
- [Claude Code](https://claude.com/claude-code)
- Python 3.11+
- A [Hog API](https://developer.thehog.ai) account (access + secret keys)
- A Google Cloud service account with the Sheets API enabled

### Install & configure
```bash
pip install -r requirements.txt   # Python deps
cp .env.example .env              # then fill in your keys
# then open BRAND.md and replace every <placeholder> with your ICP
```
Place your service-account JSON at the path set in `GOOGLE_SERVICE_ACCOUNT_PATH`
(default `service-account.json`), and share your target Google Sheet with the service
account's `client_email`.

> `.env` and `service-account.json` are gitignored. **Never commit them.**

### Run
Open the project in Claude Code and trigger an agent or skill, e.g.:
```
run outbound for <your segment>
```

---

## Memory protocol

- **`MEMORY.md`** — append-only session index. One block per session; read at start.
- **`memory/raw/`** — every raw Hog response, verbatim. *(gitignored)*
- **`memory/output/`** — final processed outputs. *(gitignored)*
- **`memory/wiki/`** — evergreen briefs (market intel, meeting preps). *(gitignored)*
- **`memory/todos/todos.md`** — append-only blockers, never overwritten.

Google Sheets is the source of truth for deal and contact status; memory is the
working record. Runtime memory is gitignored — your leads and session data never
enter version control.

---

## Hard limits

- 🚫 **No live sends** under any circumstances — drafts only.
- 🚫 **No fabricated** enrichment data or proof-point claims — claims come from
  [`BRAND.md`](BRAND.md) only.
- 🚫 **No unfiltered contacts** entering any workflow.
- 🚫 **No secrets** in any output, draft, log, or sheet.

---

## Tech stack

- **Runtime:** Claude Code (Anthropic)
- **Intelligence:** The Hog API (web/social/LinkedIn/enrichment)
- **Output store:** Google Sheets (`google-api-python-client`)
- **Glue:** Python 3.11 standard library + Google API client

---

*This repository is GTM tooling and is not affiliated with The Hog or Google.*
