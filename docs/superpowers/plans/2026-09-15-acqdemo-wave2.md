# AcqDemo Wave 2 Skills and Validation Plan

**Goal:** Add the three remaining skills from the design spec (`acqdemo:log`, `acqdemo:midpoint`, `acqdemo:plan`), wire them into the router, and run the Wave 1 validation tasks (Tasks 21-25 in `2026-09-15-acqdemo-wave1/phase-5-validation-and-release.md`).

**Approach:** Each Wave 2 skill is built by one worker in its own git worktree, test-first for scripts, following the patterns of the Wave 1 skills (`skills/annual/SKILL.md`, `skills/review/scripts/check.py`). Validation Tasks 21, 23 and 24 run in parallel with the build. Reviews run in batches of three finished tasks. The maintainer integrates (Task W2-4), then runs the trigger check (Task 22) across all seven skills and the dry run (Task 25) with a real user.

**Conventions for every task:** Python 3.11+ standard library only; scripts reconfigure stdout to UTF-8 (Windows consoles); tests under `skills/<skill>/scripts/tests/` or `tests/`; tests build sensitive-looking values at runtime; SKILL.md frontmatter `description` starts with "Use when"; shared files are referenced as `../start/references/...` or `../start/templates/...`; paste-ready text uses `C:` `R:` `I:` labels, no em dashes, no Markdown, no people's names.

---

## Task W2-1: `acqdemo:log` (capture one win)

**Files:** `skills/log/SKILL.md`, `skills/start/scripts/ledger_check.py`, `skills/log/scripts/tests/test_ledger_check.py`

**Skill flow:**
1. Find the workspace and current `FY<yy>/` the same way the router does; create `FY<yy>/ledger.md` and `FY<yy>/rambles/` if missing.
2. Take the ramble (voice dictation, pasted praise email, release note, or slide title). Save it unedited to `FY<yy>/rambles/<YYYY-MM-DD>-<slug>.md`.
3. Extract facts into a draft entry using `../start/references/ledger-format.md`. Ask at most six targeted questions, only for missing fields, in this order: numbers with basis, audience (highest rank, headcount), role, decision fed, obstacle, plan objective tag. Estimates are allowed with a one-line basis; never invent events, audiences, or awards.
4. Put people's names in `roster.md` only; the ledger uses roles and organizations.
5. Get the next id with `python scripts/ledger_check.py --file <ledger> --next-id`, append the entry (`status: candidate`, or `ready` when every field is filled), then run `python scripts/ledger_check.py --file <ledger>` and fix any CRITICAL finding.
6. Confirm in two lines: the entry id and title, and the single most useful missing fact to capture later.

**`ledger_check.py` contract:** `--file PATH` (required), `--next-id`, `--json`. Parses `## L-<digits> <title>` sections and `- key: value` fields (with indented sub-items for `numbers` and `lenses`).
- CRITICAL `BAD_ID` (heading not `L-` plus digits), `DUPLICATE_ID`, `MISSING_FIELD` (status, dates, what, role), `BAD_VALUE` (status not in candidate/ready/allocated/submitted/rejected; role not in owned/co-owned/owned-a-piece/supported; sustained not yes/one-time), `NUMBER_NO_SOURCE` (a numbers item without `source:`), `ESTIMATE_NO_BASIS` (`source: estimate` without `basis:`).
- WARNING `READY_INCOMPLETE` (status ready but audience, numbers, or lenses missing), `OVERLAP_NO_DELTA` (`prior_cycle_overlap: continuing` without a delta).
- `--next-id` prints the next id, zero-padded to at least three digits (`L-001` for an empty or missing ledger).
- Exit 1 when any CRITICAL, else 0. Text report first line: `ledger_check: N CRITICAL, M WARNING`.

**Tests:** one test per finding code with a single planted defect, a clean ledger with zero findings, `--next-id` on empty/missing/non-empty ledgers, JSON output shape, exit codes.

---

## Task W2-2: `acqdemo:midpoint` (midpoint and closeout)

**Files:** `skills/midpoint/SKILL.md`, `tests/test_midpoint_skill.py`

**Skill flow:** Reuse the annual engine by reference instead of copying it: gate, brain dump, recall sweeps, deep-dives, allocate, draft, review (point to `../annual/SKILL.md` step names and the shared references). Differences to state explicitly:
- Period: cycle start to today. Minimum per factor from `paypool.md` `min_entries_midpoint` (example 1); aim for two strong entries per factor.
- Tie entries to plan objectives (JA1, CT2) when the plan has labels.
- No scores, no Very High language, no crib sheet, no PAQL.
- Write each factor independently; never paste the same text into two factors. Run `python ../review/scripts/check.py --dir <final folder> --mode midpoint` and fix every CRITICAL, including `CROSS_FACTOR_REPEAT`.
- Save final text to `FY<yy>/midpoint/final/` and mark used ledger entries `status: submitted` with `evidence` noting "midpoint". The annual uses the midpoint as its jump point: continuing work needs a cycle delta, not repeated text.
- Closeout variant: when the supervisor or position changes, cover only the partial period, use `--mode closeout`, save to `FY<yy>/closeout-<YYYY-MM-DD>/final/`, and remind the user the closeout is due within 30 days of the change.

**Tests (`tests/test_midpoint_skill.py`):** the SKILL.md contains the anchors `--mode midpoint`, `--mode closeout`, `min_entries_midpoint`, `CROSS_FACTOR_REPEAT`, `FY<yy>/midpoint/final/`, and does not contain `crib sheet` as an instruction to produce one (only as an exclusion). The structure tests in `tests/test_plugin_structure.py` cover frontmatter and paths.

---

## Task W2-3: `acqdemo:plan` (contribution plan)

**Files:** `skills/plan/SKILL.md`, `skills/plan/scripts/prd_text.py`, `skills/plan/scripts/plan_check.py`, tests for both under `skills/plan/scripts/tests/`

**Skill flow:**
1. Read `profile.md` (career path, level, target level, organization, mission statements, `prd_path`) and `paypool.md` (`min_plan_objectives_per_factor`, `plan_due_days`, `plan_change_lock_days`).
2. Extract PRD text with `python scripts/prd_text.py --file <prd_path>`; list the duties with numbers.
3. Ask for expected work this cycle (ramble), prior plan text if any, and supervisor priorities.
4. Draft objectives per factor at the target level's descriptor language (`../start/references/descriptors/<path>.md`), labeled `JA1`, `JA2`, `CT1`, ..., each with one measurable KPI (examples in `../start/references/question-bank.md` and the spec: people trained, tool users, senior-leader briefings, estimates supported and dollar value, hours saved). Map each objective to PRD duty numbers.
5. Save to `FY<yy>/plan/Contribution Plan.txt`, run `python scripts/plan_check.py --file <plan> --min-objectives <N>`, fix CRITICAL findings.
6. Remind: approval due within `plan_due_days` of cycle start or position change; no changes in the last `plan_change_lock_days`; tag future ledger entries with the objective labels.

**Plan file format:**
```
Job Achievement and/or Innovation
JA1: <objective>
KPI: <measure and target>
PRD: <duty numbers>

Communication and/or Teamwork
CT1: ...
```

**`prd_text.py` contract:** `--file PATH`; `.docx` via `zipfile` reading `word/document.xml` paragraphs (`w:p` joined text of `w:t`), `.txt`/`.md` read directly, `.pdf` via `pdftotext` when available (reuse the lookup in `tools/hooks/scan_pii.py` style: PATH, then the Git for Windows location) else a clear error with exit 2. Prints plain text, one paragraph per line.

**`plan_check.py` contract:** `--file PATH` (required), `--min-objectives N` (default 2), `--json`.
- CRITICAL `MIN_OBJECTIVES` (per factor), `DUPLICATE_LABEL`, `LABEL_FACTOR_MISMATCH` (for example `CT1` under the JA heading), `MISSING_FACTOR` (a factor heading absent).
- WARNING `NO_KPI` (objective without a following `KPI:` line), `KPI_NOT_MEASURABLE` (KPI line without a digit or a count word such as number, count, percent, hours), `NO_PRD_TIEBACK`, `EM_DASH`.
- Exit 1 when any CRITICAL.

**Tests:** planted-defect test per code, clean plan, docx extraction from a docx built in the test with `zipfile`, missing pdftotext handled.

---

## Task W2-4: Integration (maintainer)

- Router `skills/start/SKILL.md`: replace the "when available; until then" fallbacks with the new skills.
- `README.md`: status table, Section 5.1 skill list, install notes unchanged.
- `.claude-plugin/plugin.json` and `marketplace.json`: version `0.2.0`.
- Full `python -m pytest`, sync the public mirror, run the public tests, push both repositories, tag `acqdemo--v0.2.0`.

## Validation (Wave 1 plan Tasks 21-25)

- **Task 21** personas: an agent follows `acqdemo:annual` step by step and answers only from each persona's ramble; the record says the sessions were simulated.
- **Task 22** trigger check runs after W2-4 and adds three prompts: "Log a win: I briefed the new tool to 40 analysts today" (`acqdemo:log`), "Midpoint time, help me write it" (`acqdemo:midpoint`), "Write my contribution plan from my PRD" (`acqdemo:plan`). Each prompt runs in a headless session; the first `Skill` tool call in the event stream decides pass or fail.
- **Tasks 23 and 24** use maintainer-local data; committed summaries contain finding codes and scores only.
- **Task 25** runs with a real user after W2-4, using the installed plugin.
