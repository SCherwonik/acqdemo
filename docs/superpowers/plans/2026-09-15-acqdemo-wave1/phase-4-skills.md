# Phase 4: Skills (Tasks 16-20)

Back to [plan index](../2026-09-15-acqdemo-wave1.md).

Four `SKILL.md` files turn the references and scripts into guided sessions. The structure test from Task 1 (`tests/test_plugin_structure.py`) checks each file's frontmatter and that every backticked relative path it mentions exists. Behavior is validated in Phase 5 (personas, triggers, known problems, backtest, dry run).

Path convention inside skills: paths are relative to the skill's own folder. Shared material is reached through `../acqdemo/references/...` and `../acqdemo/templates/...`. Workspace paths (the user's private folder) are written as `<workspace>/...` or `FY<yy>/...` and are never backticked relative paths.

---

### Task 16: Review skill

**Files:**
- Create: `skills/acqdemo-review/SKILL.md`

- [ ] **Step 1: Create the skill**

Create `skills/acqdemo-review/SKILL.md`:

````markdown
---
name: acqdemo-review
description: Use when checking an AcqDemo self-assessment draft (annual, midpoint, or closeout C-R-I statements) before it goes into CAS2Net, or when the user asks to review, audit, or fix a draft.
---

# AcqDemo Review

Checks the three paste-ready factor files against the program rules and a pay pool panel's eye, then offers fixes. Never adds facts.

## Inputs
- A draft folder containing exactly `Job Achievement and Innovation.txt`, `Communication and Teamwork.txt`, and `Mission Support.txt` (usually `FY<yy>/drafts/v<N>/` or `FY<yy>/final/` in the user's private workspace). If the user pasted text instead, save it into those three files in a new `FY<yy>/drafts/v<N>/` folder first. Ask where the workspace is if unknown.
- From the workspace when present: `profile.md`, `paypool.md`, `roster.md`, `FY<yy>/ledger.md`, `prior/`, and the current cycle's midpoint text.
- Rules: `../acqdemo/references/writing-style.md`, `../acqdemo/references/rules/ccas-core.md`, `../acqdemo/references/levels.md`, and the user's career path file in `../acqdemo/references/descriptors/`.

## Step 1: Run the deterministic checker
Build flags from the workspace:

| Source | Flag |
|---|---|
| Annual or midpoint | `--mode annual` or `--mode midpoint` |
| `paypool.md` `min_entries_annual` / `min_entries_midpoint` | `--min-entries N` |
| `profile.md` certification of type `acquisition` | `--acq-cert` |
| `profile.md` certification of type `dod-fm` | `--fm-cert` |
| `profile.md` `supervises` with any count above 0 | `--supervisor` |
| `prior/` (previous cycles only; never the current midpoint) | `--prior "<workspace>/prior"` |
| `roster.md` | `--roster "<workspace>/roster.md"` |
| `paypool.md` `allow_phrases` (write them one per line to `FY<yy>/drafts/allow-phrases.txt`) | `--allow-phrases <that file>` |
| `paypool.md` `what_label` (`C` unless the pay pool uses `W`) | `--what-label C` or `--what-label W` |

Run the checker at `scripts/check.py` in this skill's folder:

```
python "<this skill folder>/scripts/check.py" --dir "<draft folder>" <flags>
```

The checker expects acquisition before DoD FM when both apply. If `paypool.md` orders them differently, report `ACQ_CERT`/`FM_CERT` ordering findings as INFO instead of CRITICAL.

## Step 2: Judgment checks
Match each C-R-I to its ledger entry by content.

| Severity | Check | How to decide |
|---|---|---|
| CRITICAL | Same achievement as a prior cycle with no current-cycle delta | Compare against `prior/` meaningfully, not just wording, and against the entry's `prior_cycle_overlap` |
| WARNING | Number without a basis | Every number in the text must appear in the entry's `numbers` with a `basis` |
| WARNING | Verb stronger than the recorded role | Role verbs table in `writing-style.md` |
| WARNING | Impact climbs fewer than two rungs or lacks a mission tie | Impact ladder in `writing-style.md`; mission statements in `profile.md` |
| WARNING | Reads below the target level | Compare with the target level's descriptors; no recognizable descriptor language or scope |
| WARNING | Not ordered by impact | Scope x organizational level x novelty |
| INFO | Passive voice; uncovered discriminators per factor; raise vs. award balance; missing plan tags | |

With no ledger, turn the number-basis and role checks into questions for the user.

## Step 3: Report
Number every finding so the user can answer by voice ("fix 1 and 3, skip 2"):

```
Review: <n> CRITICAL, <n> WARNING, <n> INFO
Character counts: JA <n> | CT <n> | MS <n>

CRITICAL
1. [JA] PRIOR_REPEAT: "<run>" also in FY25. Fix: reword from ledger L-004 using the FY26 delta.
WARNING
2. [CT] Number "over 200 attendees" has no basis in the ledger. Fix: confirm the count or remove.
INFO
3. [MS] No coverage of Planning/Budgeting.
```

## Step 4: Fix loop
1. Ask: "Fix all, or which numbers?"
2. Write fixes to a new version folder `FY<yy>/drafts/v<N+1>/`; never overwrite the reviewed version.
3. Fix rules: keep every fact and number; cut adjectives before facts; reword repeats with fresh wording from the ledger; replace names with title, organization, or a count from the roster; change verbs to match the role; never invent a number (ask instead).
4. Show changed sentences as before and after, per factor.
5. Rerun Step 1 on the new folder. Repeat until 0 CRITICAL, then ask about remaining WARNINGs.

## Rules
- Never add accomplishments, numbers, audiences, or awards that are not in the ledger or stated by the user.
- Names never go into factor files.
- If a draft appears to contain classified information, stop and tell the user to remove it before continuing.
````

- [ ] **Step 2: Run the structure tests**

Run: `python -m pytest tests/test_plugin_structure.py`
Expected: 4 passed (manifest, marketplace, and the two parametrized checks for `acqdemo-review`).

- [ ] **Step 3: Commit**

```bash
git add skills/acqdemo-review/SKILL.md
git commit -m "feat(review): add acqdemo-review skill"
```

---

### Task 17: Harvest skill

**Files:**
- Create: `skills/acqdemo-harvest/SKILL.md`

- [ ] **Step 1: Create the skill**

Create `skills/acqdemo-harvest/SKILL.md`:

````markdown
---
name: acqdemo-harvest
description: Use when gathering evidence of a year's work for an AcqDemo assessment from git repositories, a calendar export, or midpoint and closeout documents, to create candidate entries in the evidence ledger.
---

# AcqDemo Harvest

Turns raw evidence into `candidate` ledger entries that the user confirms. Harvest never marks anything `ready`; deep-dives do that.

## Inputs
- `<workspace>/profile.md`: `rating_period` and the "Repositories to harvest" table.
- `FY<yy>/evidence/calendar-*.txt`: calendar exports.
- The current cycle's midpoint and closeout text, if saved in the workspace.
- `<workspace>/prior/`: previous cycles, used only to flag overlap.
- Ledger format: `../acqdemo/references/ledger-format.md`.

If there is no workspace, ask for the rating period and sources, and offer the `acqdemo` skill's first-time setup.

## Step 1: Git
1. Ask which author names are the user's (commit names often differ between machines). Keep commits from other authors in the output; they show collaboration.
2. Run the git harvester at `scripts/git_harvest.py`:
   ```
   python "<this skill folder>/scripts/git_harvest.py" --since <start> --until <end> --local <paths...> --github <owner/repo...> --out "FY<yy>/harvest/<today>-git.md"
   ```
3. Read the output and cluster commits into candidates:
   - Group within a repository by feature or milestone: version bumps, tags, shared prefixes ("feat(x):"), phase words, the same screen or module.
   - For each candidate record: title; first and last date; what, in plain words; git numbers (commits, version from and to, tags, numbered findings or defects closed); other authors as collaborators; evidence as `<repo>@<tag or first..last date>`.
   - Watch for high-value signals in subjects: defects found in legacy products, validation or tie-out against published results, new capabilities, performance gains, documentation, tests, releases.
   - Do not infer role, audience, or impact from git. Deep-dives supply those.

## Step 2: Calendar
1. If no export exists, give the user the calendar export steps from `../acqdemo/references/question-bank.md` (section "Calendar export") and continue with other sources meanwhile.
2. Run the calendar harvester at `scripts/calendar_harvest.py`:
   ```
   python "<this skill folder>/scripts/calendar_harvest.py" --file "FY<yy>/evidence/<export>.txt" --since <start> --until <end> --out "FY<yy>/harvest/<today>-calendar.md"
   ```
3. Read the output and propose candidates:
   - Each recurring series becomes a team or working-group candidate with its occurrence count and date range.
   - One-off meetings whose titles suggest a briefing, demonstration, review, training, site visit, or senior leader become briefing candidates.
   - Skip routine administration (all-hands, holidays, leave, personal appointments) unless the user wants them.
   - Keep the month of every meeting for the timeline walk.
4. If the export has no meetings in some months of the rating period, tell the user which months are missing and suggest re-exporting.

## Step 3: Documents
- Each C-R-I in the current midpoint or a closeout becomes a candidate with the note "from midpoint" or "from closeout". The current midpoint is the starting point, so these are expected to carry forward.
- Do not create candidates from `prior/`. When any candidate matches an achievement already claimed in a prior cycle, set `prior_cycle_overlap: continuing (cycle delta: unknown)` so the deep-dive asks what is new.

## Step 4: Confirm with the user
Present one numbered list grouped by source:

```
Git
1. Regression tool v2 release (2026-02 to 2026-06): 52 commits, v2.0 to v2.3, 3 tags
2. ...
Calendar
7. Estimating working group (32 sessions, 2025-10 to 2026-09)
Documents
12. From midpoint: data pipeline automation
```

Ask: keep, reject, or merge ("merge 2 and 3", "reject 5"). Then append kept candidates to `FY<yy>/ledger.md` with the next `L-###` ids, `status: candidate`, and only the fields the evidence supports. Record numbers as `source: git` with `basis: harvest <date>` (or `basis: calendar export <date>`). Update `FY<yy>/session-state.md`.

## Rules
- Harvest snapshots and the ledger stay in the private workspace.
- Merge commits are never counted; dates are never guessed.
- Calendar titles may contain names and program details; they may go in ledger `evidence` and `notes`, never into factor files.
````

- [ ] **Step 2: Run the structure tests**

Run: `python -m pytest tests/test_plugin_structure.py`
Expected: 6 passed.

- [ ] **Step 3: Commit**

```bash
git add skills/acqdemo-harvest/SKILL.md
git commit -m "feat(harvest): add acqdemo-harvest skill"
```

---

### Task 18: Annual skill

**Files:**
- Create: `skills/acqdemo-annual/SKILL.md`

- [ ] **Step 1: Create the skill**

Create `skills/acqdemo-annual/SKILL.md`:

````markdown
---
name: acqdemo-annual
description: Use when writing an AcqDemo annual self-assessment - runs recall-first intake (brain dump, calendar and people sweeps, project deep-dives), builds the evidence ledger, and drafts paste-ready C-R-I statements for all three factors plus a supervisor crib sheet.
---

# AcqDemo Annual Self-Assessment

## References (open when a step needs them)
- Questions, sweeps, estimates: `../acqdemo/references/question-bank.md`
- Writing rules: `../acqdemo/references/writing-style.md`
- Data formats: `../acqdemo/references/ledger-format.md`
- Levels and Very High: `../acqdemo/references/levels.md`
- Program rules: `../acqdemo/references/rules/ccas-core.md`
- Certification statements: `../acqdemo/references/cert-templates.md`
- Descriptors (use the file for the user's career path): `../acqdemo/references/descriptors/`
- Templates: `../acqdemo/templates/working-doc.md`, `../acqdemo/templates/session-state.md`, `../acqdemo/templates/roster.md`

## Operating rules
- **Recall first.** Ask many numbered questions. No cap. End every round with "What else does that bring to mind?"
- **Save constantly.** Write ledger, roster, rambles, and session state after every meaningful exchange; the session can end at any moment.
- **Names** are welcome in conversation, `roster.md`, and the ledger; never in factor files.
- **Never invent** events, audiences, awards, or recognition. Numbers follow the estimate protocol: proposed, approved by the user, and recorded with a basis.
- **Repeats:** the current cycle's midpoint is the starting point; prior cycles are off limits.
- **Output** factor files follow `writing-style.md` exactly.
- **Classified information:** if the user begins to share it, stop them and move on.

## Step 0: Load
1. Find the workspace: the current directory if it holds `profile.md`, otherwise ask. If there is no profile, run the `acqdemo` skill's first-time setup first.
2. Read `profile.md`, `paypool.md`, and `FY<yy>/session-state.md`. If session state shows unfinished work, summarize it in two lines and continue from `next_action`.
3. Create any missing pieces: `FY<yy>/rambles/`, `evidence/`, `harvest/`, `drafts/`, `final/`; `FY<yy>/ledger.md` starting with `# Ledger FY<yy>`; `FY<yy>/session-state.md` and `<workspace>/roster.md` from the templates.

## Step 1: Gate
1. Ask only the gate questions (question bank) that `profile.md` does not already answer. Update the profile. Put unknowns in session-state `open_questions`. Never block on an unknown.
2. Decide and record:
   - Descriptor file: the career path file (nh, nj, or nk). Current level and `target_level`.
   - Special situations: a promotion inside `paypool.md` `promotion_window_days` (needs substantial justification), a position or supervisor change (closeouts exist), supervisory duties (supervisory paragraph), certifications (certification statements).

## Step 2: Harvest
Run the `acqdemo-harvest` skill for git, the calendar export, and midpoint or closeout documents. If the user wants to skip, continue.

## Step 3: Brain dump
1. Say: "Tell me everything you worked on this cycle, in any order. Ramble; I'll organize it." Save the raw text to `FY<yy>/rambles/<date>-dump.md`.
2. Show the inventory:

   | # | Workstream | Evidence | JA | CT | MS |
   |---|---|---|---|---|---|
   | 1 | Regression tool | strong | ● | ● | ○ |

   Evidence is strong, some, or thin. ● likely strong angle, ○ possible angle.
3. Ask the user to correct and add. Create `candidate` ledger entries for new items.

## Step 3b: Recall sweeps
Run the sweeps in the question bank, in order: calendar export (if still missing), timeline walk, people rings (draw the office map the first time and save it to `profile.md`), artifact prompts. Update candidates and `roster.md` as you go. End each sweep with "What else does that bring to mind?"

## Step 4: Deep-dives
Order candidates by likely impact (scope x organizational level x novelty). For each one:
1. Ask the user to ramble about it; save to `FY<yy>/rambles/`.
2. Update the entry. Ask numbered drill-down ladder and discriminator questions for whatever is missing (5-8 per round, as many rounds as needed).
3. Resolve numbers with the estimate protocol; confirm each; record source and basis.
4. Fill `lenses` for all three factors, `descriptor_hits` from the target level, `sustained`, `prior_cycle_overlap` (compare with `prior/`), `prd_duty`, and `plan_tag`.
5. Set `status: ready`, save, and show the coverage grid.

Continue until every factor has at least four `ready` entries or the user says "enough." Aim the next deep-dive at the weakest factor.

## Step 5: Allocate
Propose, then get approval:

| Factor | Order | Entry | Angle | Why this factor | Raise or award |
|---|---|---|---|---|---|

Rules: three or four entries per factor; each entry is primary in one factor and may appear in a second factor only with a different angle and different wording; no entry whose prior-cycle overlap has no delta; greatest impact first; remaining `ready` entries go to the bench. Record `allocated` in the ledger.

## Step 6: Draft
Write `FY<yy>/drafts/v1/` with the three factor files:
1. Mandatory paragraphs first, in `paypool.md` order: the supervisory paragraph (exact counts from the profile) and certification statements (templates filled from the profile; ask for any missing value).
2. C-R-I statements per `writing-style.md`: the Contribution in at most 35 words with a verb that matches the role; the Result with the entry's numbers; the Impact climbing at least two rungs with a mission tie drawn from the profile's mission statements; phrasing from the target level's descriptors; at most 3,900 characters per factor.
3. If a promotion falls inside the pay pool's window, make continuity visible: higher-level contributions before and after the effective date, and sustained strategic work.

## Step 7: Review
Run the `acqdemo-review` skill on `FY<yy>/drafts/v1/`. It writes fixes to new versions. Then take the user's edits by voice, write a new version, and review again. Loop until 0 CRITICAL and the user approves the text.

## Step 8: Finalize
1. Copy the approved version's three files to `FY<yy>/final/`.
2. Build `FY<yy>/final/FY<yy> working doc.md` from the template:
   - Status and gaps.
   - Final text with character counts (from the checker).
   - Evidence table: every claim, its ledger id, source, and basis.
   - Bench: unused `ready` entries, plus a punchier and a safer alternate for each final statement.
   - Descriptor map and uncovered discriminators.
   - Crib sheet: three big rocks; hard counts; contributions to add (the bench); an "Exceeding expected contributions" rationale per factor in descriptor language; a substantial-justification paragraph when a special situation applies; reminders (concur with certification statements, document the midpoint discussion); raise or award tags.
   - Next-cycle seeds: KPIs, plan objective ideas from coverage gaps, capture reminders (including a calendar export at the midpoint).
3. Set allocated entries to `submitted`; mark session state complete.
4. Tell the user: paste each factor file into its CAS2Net field, check every fact before saving, save often (CAS2Net times out after about 15 minutes), and give the crib sheet section to the supervisor before the employee due date.
````

- [ ] **Step 2: Run the structure tests**

Run: `python -m pytest tests/test_plugin_structure.py`
Expected: 8 passed.

- [ ] **Step 3: Commit**

```bash
git add skills/acqdemo-annual/SKILL.md
git commit -m "feat(annual): add acqdemo-annual skill"
```

---

### Task 19: Router skill

**Files:**
- Create: `skills/acqdemo/SKILL.md`

- [ ] **Step 1: Create the skill**

Create `skills/acqdemo/SKILL.md`:

````markdown
---
name: acqdemo
description: Use when the user mentions AcqDemo, CCAS, CAS2Net, a contribution plan, a midpoint or closeout, an annual self-assessment, C-R-I statements, or asks where they are in the appraisal cycle - finds or sets up the private workspace, detects the cycle stage, resumes unfinished work, and routes to the right AcqDemo skill.
---

# AcqDemo

Front door for the toolkit. Finds the user's private workspace, sets it up the first time, works out where they are in the cycle, and hands off to the right skill.

## Step 1: Find the workspace
1. If the current directory contains `profile.md`, use it.
2. Otherwise ask: "Where is your private AcqDemo workspace folder?" If the user has none, run first-time setup.

## Step 2: First-time setup
1. Explain in two sentences: the workspace is a private folder (a private git repository is recommended) that holds the user's profile, evidence, drafts, and names of people they worked with; none of it belongs in a public repository.
2. Copy the templates into the workspace root: `templates/profile.md`, `templates/paypool.md`, `templates/roster.md` (paths relative to this skill's folder).
3. Fill `profile.md` by asking the gate questions from `references/question-bank.md`.
4. Fill `paypool.md`: show the example defaults and ask the user to confirm them or share their pay pool's current business rules and guidance. If they share a document, read it and fill the fields from it. Rule background: `references/rules/ccas-core.md`.
5. Create `prior/` and ask for previous cycles' submitted self-assessment text, one folder per cycle.
6. Recommend exporting the calendar (see "Calendar export" in the question bank).
7. If the workspace is a git repository, recommend the PII guard: copy the toolkit's `../../tools/hooks/scan_pii.py` and `../../tools/hooks/pre-commit` into `<workspace>/tools/hooks/` and run `git config core.hooksPath tools/hooks`.

## Step 3: Detect the stage
Compare today's date with `paypool.md`:

| Window | Stage | Next skill |
|---|---|---|
| Cycle start to plan due (about 30 days) | Contribution plan | `acqdemo-plan` when available; until then, draft objectives from the PRD duties using the question bank and `references/writing-style.md`, with labeled objectives (JA1, CT1, MS1) |
| After plan due, before midpoint window | Capture | `acqdemo-log` when available; until then, add `candidate` entries to `FY<yy>/ledger.md` directly |
| Midpoint window | Midpoint | `acqdemo-midpoint` when available; until then, run `acqdemo-annual` with a minimum of one C-R-I per factor and no crib sheet |
| After midpoint, before mid-August | Capture | as above; warn when the plan-change lock or the 90-day plan rule is near |
| Mid-August to employee due date | Annual | `acqdemo-harvest`, then `acqdemo-annual` |
| Employee due date to supervisor due date | Handoff | confirm the crib sheet reached the supervisor; offer `acqdemo-review` on the final text |
| After the cycle ends | Next cycle | read next-cycle seeds from the working doc, then contribution plan |

Always mention: days until the employee due date; any promotion inside the pay pool's promotion window; any position or supervisor change that needs a closeout.

## Step 4: Inventory and resume
Report briefly: profile completeness; pay pool overlay present; roster rows; for the current `FY<yy>/`: ledger entries by status, harvest snapshots, draft versions, final files. If `FY<yy>/session-state.md` has a `next_action`, offer to resume it.

## Step 5: Route
Invoke the matching skill: `acqdemo-harvest`, `acqdemo-annual`, or `acqdemo-review`. For stages whose skill is not available yet, follow the interim approach in the table.

## Safety
- The workspace is private; names never appear in paste-ready text; classified information never enters any file or conversation.
- If the workspace is a git repository without the PII guard, recommend enabling it.
````

- [ ] **Step 2: Run the structure tests**

Run: `python -m pytest tests/test_plugin_structure.py`
Expected: 10 passed.

- [ ] **Step 3: Run the full suite and commit**

Run: `python -m pytest`
Expected: all pass.

```bash
git add skills/acqdemo/SKILL.md
git commit -m "feat: add acqdemo router skill"
```

---

### Task 20: Install locally and verify path resolution

**Files:**
- None created. Verification only (records results in the commit message of Task 26 if fixes are needed).

- [ ] **Step 1: Validate the manifests with Claude Code**

Run from the repository root (working tree committed and clean): `claude plugin tag . --dry-run`
Expected: it prints the tag it would create, `acqdemo--v0.1.0`, with no validation error about `plugin.json` and the marketplace entry disagreeing. No tag is created.

- [ ] **Step 2: Add the repository as a local marketplace and install**

Run from any directory:
```
claude plugin marketplace add "<absolute path to the private workspace>"
claude plugin install acqdemo@acqdemo
claude plugin list
```
Expected: `claude plugin list` shows `acqdemo` as installed and enabled.

- [ ] **Step 3: Verify skills load and shared paths resolve**

Start a new Claude Code session in an empty scratch folder and send:
1. "Where am I in the AcqDemo cycle?" Expected: the `acqdemo` skill loads and asks for the workspace folder.
2. "Open the levels reference the acqdemo-annual skill uses and tell me the NH Level IV range." Expected: Claude reads `../acqdemo/references/levels.md` relative to the `acqdemo-annual` skill folder and answers `79-100`.
3. "Run the review skill's checker with --help." Expected: `check.py` usage text.

- [ ] **Step 4: If shared paths do not resolve**

Record the base directory the skill loader reports for `acqdemo-annual`. If `../acqdemo/` does not exist next to it, install as personal skills instead (keeps the sibling layout):
```
python -c "import shutil, pathlib; src=pathlib.Path('skills'); dst=pathlib.Path.home()/'.claude'/'skills'; [shutil.copytree(p, dst/p.name, dirs_exist_ok=True) for p in src.iterdir() if p.is_dir()]"
```
and note the limitation for the README install section (Task 26).

- [ ] **Step 5: After later edits, refresh the install**

```
claude plugin marketplace update acqdemo
claude plugin update acqdemo@acqdemo
```
Restart Claude Code to apply.

- [ ] **Step 6: Phase-end sync** (see plan index, "Phase-end sync")
