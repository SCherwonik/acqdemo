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
