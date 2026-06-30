# Agent — Market Monitor

## Purpose
Full intelligence and re-engagement workflow. Tracks competitor
moves, surfaces category trends, and queues warm contacts
for outreach based on live signals.

---

## Trigger
Operator says: "run market monitor" / "check signals and re-engage"
/ "competitor and category check"
Recommended cadence: every 7 days.

---

## Input
```json
{
  "category": "<segment from BRAND.md> | all",
  "time_window": "30_days | 90_days",
  "contacts_to_monitor": "all_enriched | specific_company"
}
```

---

## Sequence

### Step 1 — Run Skill 03: Competitor Monitor
Check all competitors defined in BRAND.md for new signals.
Classify HIGH, MEDIUM, LOW.
HIGH signals produce a counter-position immediately.
Pause and surface HIGH signals to operator before continuing.

### Step 2 — Run Skill 04: Market Intelligence
Run category deep research for confirmed segment and time window.
Extract brands to watch and pass as input to Step 3.
If new brands identified, add to Skill 01 queue for next
outbound pipeline run — log in MEMORY.md todos.

### Step 3 — Run Skill 05: Signal Re-engagement
Monitor all enriched contacts for live signals.
Incorporate any competitor HIGH signals from Step 1 as
additional context for re-engagement hooks.
Queue HOT contacts for outreach within 24 hours.
Queue WARM contacts for outreach within 72 hours.
Produce outreach queue with suggested hooks for Skill 06.

---

## Output
- Signal Log sheet: all competitor and contact signals
- Outreach queue: HOT and WARM contacts with hooks for Skill 06
- Brands to watch: logged to MEMORY.md todos for next Skill 01 run
- MEMORY.md: full session log appended

---

## Handoff
Outreach queue handed to operator for Skill 06 approval.
New brands from Skill 04 queued for next outbound pipeline run.
HIGH competitor signals escalated to operator immediately.