# Ledger, Roster, Session State, Profile, and Pay Pool Overlay

The ledger is the only interface between skills. Every skill that learns something writes it here; every skill that drafts reads from here.

## Workspace layout
The user's private workspace (never the public toolkit repo):

```
<workspace>/
  profile.md              who the user is (fields below)
  paypool.md              local rules and dates (fields below)
  roster.md               people, by ring (names allowed only here and in the ledger)
  prior/                  submitted text from previous cycles, one folder per cycle
  FY<yy>/
    ledger.md
    session-state.md
    rambles/              raw dictation, one file per session: YYYY-MM-DD-<topic>.md
    evidence/             raw evidence files: calendar-YYYY-MM-DD.txt (calendar export), others
    harvest/              harvest snapshots: YYYY-MM-DD-git.md, YYYY-MM-DD-calendar.md
    drafts/               v1/, v2/ ... each holding the three factor files
    final/                Job Achievement and Innovation.txt
                          Communication and Teamwork.txt
                          Mission Support.txt
                          FY<yy> working doc.md
```

Every file in `rambles/` ends with its own `## Transcription glossary` section (heard -> meant); see `question-bank.md`, Voice and transcription.

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
  - 52 commits, v1.0 to v2.3 | source: git | basis: harvest 2026-08-20
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
- `numbers`: every number that may appear in text needs a line with `source:` (`stated`, `git`, `estimate`, `calendar`, or `document`) and `basis:`.
- `sustained`: `yes` or `one-time`.
- `prior_cycle_overlap`: `none`, or `continuing (cycle delta: ...)`. An entry that repeats a prior-cycle achievement with no delta is `rejected`.
- `allocated`: `JA`, `CT`, `MS`, `bench`, or empty. An entry whose project appears in more than one factor lists each, primary factor first: `JA, MS`.
- Blank means not asked yet; `none` means asked and does not apply. `ledger_check.py` lists blank fields as `OPEN_FIELDS` (INFO) on every entry and warns (`READY_INCOMPLETE`) when a `ready` entry still has any, so nothing stays blank by accident.
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

## Session state
`FY<yy>/session-state.md`:

```markdown
# Session State
- step: 4 deep-dives
- next_action: deep-dive on L-007, then coverage grid
- open_questions:
  - EOCS after the promotion
- updated: 2026-09-03
```

## Profile fields
See `templates/profile.md`. Required for drafting: `career_path`, `level`, `target_level`, `rating_period`. Everything else improves quality and is asked for if missing.

## Pay pool overlay fields
See `templates/paypool.md`. Skills read due dates, minimums, mandatory paragraph order, the promotion window, the plan-days requirement, the character limit, and allow-phrases from here instead of assuming defaults.
