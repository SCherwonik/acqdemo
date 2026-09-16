# Ledger, Roster, Session State, Profile, and Pay Pool Overlay

> Platform note. This copy is for an agent with no file system. Where the text below names a
> workspace file or folder such as `profile.md`, `paypool.md`, `roster.md`, `ledger.md`, or
> `FY<yy>/evidence/`, read it as a block of text kept in the conversation: the assistant
> shows those blocks at each checkpoint and the user keeps them in a document of
> their own. Source documents are uploaded in the chat rather than saved into folders. Field
> names, allowed values, and every rule below are unchanged.

The ledger is the only interface between skills. Every skill that learns something writes it here; every skill that drafts reads from here.

## What the conversation holds
There is no file system here. Everything the toolkit keeps in files lives in the conversation as
text, and the user keeps their own copy of it:

- The **ledger block** and the **workspace block**, described below and re-emitted at the end of
  every round. Together they are the workspace.
- Brain dumps: what the user said when asked what they did this cycle, one block per session.
  Each one ends with its own `## Term glossary` section (wrote -> meant); see
  `question-bank.md`, Terms, names, and numbers.
- Uploads: the calendar export, prior-cycle assessments, the contribution plan, the position
  requirements document. These arrive in the chat rather than in folders.
- Finished factor text: one plain text block per factor, ready to paste into CAS2Net.

Nothing is written to disk by anyone but the user, so anything that is not re-emitted in a block
is lost when the conversation ends.

## Ledger entry
`ledger.md` starts with `# Ledger FY<yy>` and holds one `##` section per entry. Ids increase and are never reused. Only `status`, `dates`, and `what` are required to create an entry; every other field, including `role`, may start blank and gets filled in by a later deep-dive.

```markdown
## L-001 Automated regression tool
- status: ready
- dates: 2025-11 to 2026-06
- project: Regression tool
- what: Built a tool that tests every combination of cost drivers and ranks candidate relationships.
- role: owned
- audience: 14 analysts in 3 divisions; demo to division chief (GS-15 equivalent)
- numbers:
  - 40 relationships tested | source: stated | basis: user count from tool log
  - about 3 weeks to 4 days per estimate | source: estimate | basis: 2 analysts x 15 working days before vs 4 days after, user approved
  - 12 releases, v1.0 to v2.3 | source: document | basis: release notes, uploaded 2026-08-20
- decision_fed: FY budget estimates for 6 programs
- obstacle: legacy workbook had two unit errors
- sustained: yes
- lenses:
  - JA: new automated method; found legacy errors
  - CT: trained 14 analysts; user guide
  - MS: cut estimate cycle time for program customers
- descriptor_hits: NH IV JA "works with senior management to establish new ... methodologies"; NH IV MS "promulgates innovative solutions and methodologies"
- prd_duty: 3
- plan_tag: JA1
- evidence: repo regression-tool@v2.3; slides "Regression Tool Demo" (Mar)
- prior_cycle_overlap: continuing (cycle delta: v2 interaction terms, adoption by 2 more divisions)
- allocated: JA
- notes:
```

Field rules:
- `role`: blank on a fresh `candidate` (harvest creates entries before anyone knows the role); once known, exactly one of `owned`, `co-owned`, `owned-a-piece`, `supported`.
- `numbers`: every number that may appear in text needs a line with `source:` (`stated`, `estimate`, `calendar`, or `document`) and `basis:`.
- `sustained`: `yes` or `one-time`.
- `prior_cycle_overlap`: `none`, or `continuing (cycle delta: ...)`. An entry that repeats a prior-cycle achievement with no delta is `rejected`.
- `allocated`: `JA`, `CT`, `MS`, `bench`, or empty. An entry whose project appears in more than one factor lists each, primary factor first: `JA, MS`.
- Blank means not asked yet; `none` means asked and does not apply. List the blank fields of every entry when the entry is shown, and say so when a `ready` entry still has any, so nothing stays blank by accident.
- Names of people may appear in `audience`, `notes`, and `evidence`; they never pass into factor files.

## Status lifecycle
`candidate` (from harvest or a quick capture; not yet explored) > `ready` (drill-down complete; enough for a full C-R-I) > `allocated` (chosen for a factor or the bench) > `submitted` (in final text). Any status can move to `rejected` with a note.

## Roster
`roster.md`:

```markdown
# Roster

| Ring | Name | Organization | Role | Worked on | Frequency | Ledger |
|---|---|---|---|---|---|---|
| own office: estimating | Pat Example | Estimating branch | analyst | trained on regression tool | 4 sessions | L-001 |
```

Rings: `own office: <section>`, `other division`, `external government`, `contractor: <company>`, `leadership`.

## The two blocks the user saves
The workspace is two fenced blocks in the conversation. Show both in full at each checkpoint,
so the user can read what was recorded and keep a copy to paste back. There is no third block,
and nothing else is saved.

**1. The ledger block.** It may open with its `# Ledger FY<yy>` title line, and after that it
holds `## L-NNN` entries in the format below and nothing else. Session state, profile, pay pool,
and roster material never appears inside it: anything else starting with `##` is read as an
entry, and an entry with an id that is not `L-NNN` is a CRITICAL error on every round after it.

```ledger
# Ledger FY26
## L-001 Automated regression tool
- status: ready
```

**2. The workspace block.** Exactly four sections, in this order, spelled and capitalized
exactly as shown. `# Session state` has a lowercase "state".

```workspace
# Profile
- career_path, level, target_level, rating_period, supervisor counts, certifications and their
  dates, EOCS, and the projects the user works in (fields below)

# Pay pool
- due dates, minimum entries, mandatory paragraph order, the `C:` or `W:` label, the promotion
  window, the character limit, allow-phrases (fields below)

# Roster
- one table row per person, by ring (format above)

# Session state
- step: 4 deep-dives
- current_entry: L-007
- round: 3
- pending_questions:
  - 1. How many analysts used the tool in the second half of the cycle?
  - 2. Who asked for the rebuild, and what were they unable to do before it?
- next_action: deep-dive on L-007, then coverage grid
- open_questions:
  - EOCS after the promotion
- updated: 2026-09-03
```

The workspace block is what makes resume work. Without it a saved ledger loses the career path
and the target level, and drafting stops until they are asked for again.

## Profile fields
These are the fields of the `# Profile` section of the workspace block. Required for drafting: `career_path`, `level`, `target_level`, `rating_period`. Everything else improves quality and is asked for if missing.

## Pay pool overlay fields
These are the fields of the `# Pay pool` section of the workspace block. Read due dates, minimums, mandatory paragraph order, the promotion window, the plan-days requirement, the character limit, and allow-phrases from it instead of assuming defaults.
