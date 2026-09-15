---
name: acqdemo
description: Use when the user mentions AcqDemo, CCAS, CAS2Net, a contribution plan, a midpoint or closeout, an annual self-assessment, C-R-I statements, or asks where they are in the appraisal cycle - finds or sets up the private workspace, detects the cycle stage, resumes unfinished work, and routes to the right AcqDemo skill.
---

# AcqDemo

Front door for the toolkit. Finds the user's private workspace, sets it up the first time, works out where they are in the cycle, and hands off to the right skill.

## Step 1: Find the workspace
1. If the current directory contains `profile.md`, use it.
2. Otherwise ask: "Where is your private AcqDemo workspace folder?" If the user has none, run first-time setup.
3. Use only that folder. Never search the disk for a workspace, and never reuse a path from memory, an earlier session, or another project's notes without the user confirming it in this conversation. Writing into a folder the user did not name is a bug.
4. Never treat this skill's own folder, or the plugin folder above it (the one holding `skills/`), as the workspace, even when it contains `profile.md`. When the current directory has no `profile.md`, ask and wait for the answer before creating or writing any file.

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
| Cycle start to plan due (about 30 days) | Contribution plan | `acqdemo-plan` |
| After plan due, before midpoint window | Capture | `acqdemo-log` for each win (monthly, and after any briefing, release, or praise email) |
| Midpoint window | Midpoint | `acqdemo-midpoint` |
| After midpoint, before mid-August | Capture | as above; warn when the plan-change lock or the 90-day plan rule is near |
| Mid-August to employee due date | Annual | `acqdemo-harvest`, then `acqdemo-annual` |
| Employee due date to supervisor due date | Handoff | confirm the crib sheet reached the supervisor; offer `acqdemo-review` on the final text |
| After the cycle ends | Next cycle | read next-cycle seeds from the working doc, then contribution plan |

Always mention: days until the employee due date; any promotion inside the pay pool's promotion window; any position or supervisor change that needs a closeout (`acqdemo-midpoint` handles closeouts).

## Step 4: Inventory and resume
When `FY<yy>/session-state.md` has a `next_action`, that comes first: open with the unfinished work (step, `current_entry`, round, pending questions, what the ledger already holds) and the offer to resume, then the inventory, then dates.

Report briefly: profile completeness; pay pool overlay present; roster rows; for the current `FY<yy>/`: ledger entries by status, open fields per entry (the `OPEN_FIELDS` lines from `python ../acqdemo-log/scripts/ledger_check.py --file FY<yy>/ledger.md`), harvest snapshots, draft versions, final files. Resume with the skill that owns the saved `step`, not the one that produced the data:

| Saved step | Resume with |
|---|---|
| 2 harvest, or harvest snapshots missing | `acqdemo-harvest` |
| 3 dump, 3b sweeps, 4 deep-dive, 5 allocate, 6 draft, 8 finalize | `acqdemo-annual`, or `acqdemo-midpoint` when the state names a midpoint or closeout |
| 7 review | `acqdemo-review` |

Blank fields in ledger entries (`OPEN_FIELDS`) are deep-dive work, so they resume in `acqdemo-annual` or `acqdemo-midpoint`. `acqdemo-harvest` only gathers new evidence; never send the user there to finish an entry.

## Step 5: Route
Invoke the matching skill: `acqdemo-plan`, `acqdemo-log`, `acqdemo-midpoint`, `acqdemo-harvest`, `acqdemo-annual`, or `acqdemo-review`.

## Safety
- The workspace is private; names never appear in paste-ready text; classified information never enters any file or conversation.
- If the workspace is a git repository without the PII guard, recommend enabling it.
