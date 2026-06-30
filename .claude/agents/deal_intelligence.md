# Agent — Deal Intelligence

## Purpose
Full deal movement workflow. Preps for a meeting, drafts follow-up
after, then scans pipeline for flags.

---

## Trigger
Operator says: "run deal intel for [company]" / "prep, follow up
and flag pipeline after [company] call"

---

## Input
```json
{
  "company": "",
  "contact": "",
  "meeting_type": "first_call | demo | follow_up | expansion",
  "meeting_date": "",
  "prior_context": ""
}
```

---

## Sequence

### Step 1 — Run Skill 07: Meeting Prep
Produce research brief for confirmed company and contact.
Deliver to operator before meeting. Pause here.
Agent does not proceed until operator confirms meeting is done.

### Step 2 — Run Skill 08: Follow-Up Drafter
Operator provides meeting notes after call concludes.
Agent drafts follow-up email and CRM update block.
If operator has not provided a confirmed next step,
flag and do not draft — a follow-up without a next step is dead.

### Step 3 — Run Skill 09: Deal Flagging
After CRM block from Skill 08 is logged to Pipeline sheet,
run full pipeline scan. Surface AT-RISK, STALLED, and
EXPANSION flags across all accounts, not just current one.

---

## Output
- Meeting prep brief: delivered pre-call
- Follow-up draft: staged for operator review
- CRM block: ready to paste into Pipeline sheet
- Pipeline flags: prioritized action list
- MEMORY.md: full session log appended

---

## Handoff
Operator sends follow-up manually after review.
Pipeline sheet updated with CRM block.
AT-RISK accounts escalated to operator within 24 hours.