# Agent — Outbound Pipeline

## Purpose
Full top-of-funnel execution. Takes a segment and size input and
produces drafted outreach for verified ICP-matched contacts.

---

## Trigger
Operator says: "run outbound for [segment]" / "build and draft
outreach for [category]" / "full pipeline run for [segment]"

---

## Input
```json
{
  "segment": "<segment from BRAND.md> | all",
  "company_size": "emerging | scaling | all",
  "persona_priority": "innovation_lead | commercial_lead | founder_ceo",
  "outreach_format": "email | linkedin"
}
```

---

## Sequence

### Step 1 — Run Skill 01: ICP Builder
Build verified company and contact list for confirmed segment.
Do not proceed to Step 2 until Skill 01 outputs at least one
Verified record. If zero verified records, stop and report to operator.

### Step 2 — Run Skill 02: Lead Enrichment
Enrich all Verified records from Skill 01.
Flag Needs Review records separately — do not pass to Step 3.
Only Verified records from Skill 02 move forward.

### Step 3 — Run Skill 06: Outreach Drafter
Draft outreach for each Verified enriched record.
If Skill 05 signal exists for a contact, use it as the hook.
If no signal, ICP score 3 is sufficient trigger — draft proceeds.
Produce one draft per contact. Flag any draft that required
an assumption for operator review before use.

---

## Output
- Enriched Contacts sheet: all records from Skill 02
- Pipeline sheet: all contacts with stage = Identified
- Outreach drafts: one per contact, staged for operator review
- MEMORY.md: full session log appended

---

## Handoff
Operator reviews drafts, approves, and sends manually.
Approved contacts move to Pipeline stage = Contacted.
Needs Review records held for operator decision.