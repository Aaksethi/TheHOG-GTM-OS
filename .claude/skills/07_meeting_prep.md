# Skill 07 — Meeting Prep

## Purpose
Produce a focused pre-meeting research brief for any prospect or
customer call. Gives the rep everything they need, nothing they don't.

## Schema
Read and write using master record defined in .claude/schema.json.
Flatten to sheet using sheet_mappings for this skill's output sheet.

---

## Trigger
Operator says: "prep me for [company] call" / "research brief for
meeting with [contact]" / "what do I need to know before [company]"

---

## Step 1 — Input
Confirm with operator:
- Company name and contact name
- Meeting type: first call, demo, follow-up, or expansion discussion
- Any prior context from MEMORY.md or Pipeline sheet

---

## Research Sequence

Run all steps before generating the brief:

1. POST /api/deep-research [ASYNC] — deep company research: recent product launches, R&D activity, strategy, leadership changes, news.
   Body: {
     prompt: 'Research [company name]. Cover: recent product launches, R&D activity, strategy, leadership changes, news in the last 90 days.',
     schema: {type:'object', properties:{recent_launches:{type:'array',items:{type:'string'}}, rd_activity:{type:'string'}, strategy:{type:'string'}, leadership_changes:{type:'string'}, recent_news:{type:'array',items:{type:'string'}}}},
     urls: ['[company website URL if known]']
   }
   Poll: GET /api/operations/:id from pollUrl.

2. POST /api/deep-research [ASYNC] — research the specific person being met: background, career, stated priorities, known positions.
   Body: {
     prompt: 'Research [person name], [title] at [company]. Cover: career history, what they have worked on publicly, stated priorities, known perspectives relevant to your offering.',
     schema: {type:'object', properties:{career_summary:{type:'string'}, current_focus:{type:'string'}, known_priorities:{type:'array',items:{type:'string'}}, talking_points:{type:'array',items:{type:'string'}}}}
   }
   Poll: GET /api/operations/:id from pollUrl.

3. POST /api/v1/platform/scrapers/linkedin/company-posts [SYNC] — pull last 10 company posts.
   Body: {username:'company-linkedin-slug', max_results:10}
   Read last 10 posts for recent announcements and conversation starters.

4. POST /api/v1/platform/scrapers/linkedin/profile [SYNC] — pull the person's recent posts and activity since the last touch to find fresh conversation starters.
   Body: {username:'contact-linkedin-id'}
   Read: data.about, recent activity.

5. GET /api/v1/monitors/:id/events [SYNC] — check for any new signals on this account from the monitoring layer since last session.
   Get monitor id from GET /api/v1/monitors — find the monitor for this account.
   Read latest events for fresh signals.

Output brief sections: Company snapshot, Who you're meeting,
Recent moves (last 30 days), Product match rationale,
3 talking points, 1 risk to address.

---

## Raw Dump — Write After Each Call

- After company deep-research: `raw-07-{YYYYMMDD}-deep_research_{company_slug}.json`
- After person deep-research: `raw-07-{YYYYMMDD}-deep_research_{contact_slug}.json`
- After company-posts scrape: `raw-07-{YYYYMMDD}-company_posts_{company_slug}.json`
- After profile scrape: `raw-07-{YYYYMMDD}-linkedin_profile_{contact_slug}.json`
- After monitor events pull: `raw-07-{YYYYMMDD}-monitor_events_{company_slug}.json`

---

## Step 3 — Brief Structure
Produce exactly this format, no additions:

**Company snapshot:** 3 sentences — what they make, where they sell, stage
**Contact snapshot:** 2 sentences — role, background, what they care about
**Their likely priority:** one sentence — what they will want from this call
**Your angle:** which product, which proof point, why now
**Their current solution:** what they likely use now and your counter
**One risk:** what could stall this deal and how to handle it
**Suggested opening:** one sentence to open the call with

---

## Step 4 — Save to Wiki
Write the research brief to memory/wiki/:
Filename: `meeting-prep-{company_slug}-{YYYYMMDD}.md`
Format: full brief (Company snapshot, Contact snapshot, Their likely
priority, Your angle, Current solution, One risk, Suggested opening).
No Google Sheets write for this skill.

---

## Step 5 — Log Session
Append to MEMORY.md (index only):
```
[DATE] — Skill 07 Meeting Prep
Ran: Skill 07
Raw files: [list raw-07 files written]
Output files: [wiki filename written]
Sheets updated: none
Blockers added: 0
Next: Skill 08 after meeting concludes
```