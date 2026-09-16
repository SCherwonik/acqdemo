---
name: start
description: Use when an AcqDemo, CCAS, or CAS2Net request is general rather than one specific task, for example where am I in the appraisal cycle, help me with my self-assessment, I am new to AcqDemo, or set up my workspace. Prefer this skill over the task skills whenever the user has not named a specific task. Finds or creates the private workspace, walks first-time intake, works out the cycle stage from the pay pool calendar, resumes unfinished work, and routes to harvest, annual, midpoint, plan, log, or review.
---

# AcqDemo

Front door for the toolkit. Finds the user's private workspace, sets it up the first time, works out where they are in the cycle, and hands off to the right skill.

## Step 1: Find the workspace
1. If the current directory contains `profile.md`, use it.
2. Otherwise ask: "Where is your private AcqDemo workspace folder?" If the user has none, run first-time setup.
3. Use only that folder. Never search the disk for a workspace, and never reuse a path from memory, an earlier session, or another project's notes without the user confirming it in this conversation. Writing into a folder the user did not name is a bug.
4. Never treat this skill's own folder, or the plugin folder above it (the one holding `skills/`), as the workspace, even when it contains `profile.md`. When the current directory has no `profile.md`, ask and wait for the answer before creating or writing any file.

## Step 2: First-time setup (guided)
Walk this out loud, one item at a time; never dump the whole list and wait. Checklist with reasons and how to get each item: `references/intake-checklist.md`.

1. **Say what this is and where it lives.** Two sentences: the workspace is one private folder holding the profile, evidence, drafts, and the names of people worked with; none of it belongs in a public repository. Ask where to create it and create it; a private git repository is ideal but a plain folder is fine.
2. **Copy the templates** into the workspace root: `templates/profile.md`, `templates/paypool.md`, `templates/roster.md`.
3. **Ask which situation they are in** before asking for any document (`references/intake-checklist.md`, Which situation is the user in): have they been through a cycle before and submitted a self-assessment, did they write a midpoint this cycle, and did they change position or supervisor mid-cycle. A first-cycle employee has no prior assessment and often no midpoint; do not ask them for either. Record the answer in `profile.md`.
4. **Fill `profile.md`** with the gate questions (`references/question-bank.md`). Five minutes, no documents needed. Unknowns go to session-state `open_questions`; never block.
5. **Ask for the two documents that matter most** (`references/intake-checklist.md`): the CAS2Net export for the last completed cycle (usually a PDF holding prior assessments, scores, EOCS, value of position, often the prior plan) and this cycle's midpoint review (any format). Read whatever they give you and fill `profile.md`, `prior/`, and `FY<yy>/midpoint/final/` from it; if a file will not open, ask for a paste. If they cannot find either document, offer to walk the CAS2Net retrieval steps with them (`references/getting-your-documents.md`). Then walk the rest of the checklist one line at a time: name the item, say what it buys, ask whether they have it, say where it goes. Never ask for the descriptors, CCAS guidance, or example business rules; the toolkit ships those. Skipping is always fine.
6. **Fill `paypool.md`:** show the example defaults, ask the user to confirm them or share their pay pool's business rules and current guidance; read what they share and fill the fields from it. Background: `references/rules/ccas-core.md`.
7. **Create the folders** they will need: `prior/` (one folder per previous cycle), `FY<yy>/evidence/`, `FY<yy>/plan/`, `FY<yy>/midpoint/final/`. Put the documents they named into them, or tell them the exact paths to drop files into.
8. **Calendar export.** Give the steps (`references/question-bank.md`, Calendar export) and offer to wait while they do it; it is the single biggest memory jog.
9. **Offer the PII guard** if the workspace is a git repository: copy the toolkit's `../../tools/hooks/scan_pii.py` and `../../tools/hooks/pre-commit` into `<workspace>/tools/hooks/` and run `git config core.hooksPath tools/hooks`.
10. **Show the path** (Step 2b) and say which stage they are in today, then route.

## Step 2b: The path, start to finish
Say this once, in plain words, so the user knows what they are signing up for:

| Stage | What happens | Skill | Roughly |
|---|---|---|---|
| Setup | This checklist; profile and pay pool filled | `acqdemo:start` | 10 to 20 minutes |
| Gather | Mine git, the calendar export, the midpoint, prior cycles into candidate entries | `acqdemo:extract` | 5 minutes, mostly automatic |
| Remember | Brain dump, timeline walk, people sweep, artifact prompts | `acqdemo:annual` | 20 to 40 minutes of talking |
| Dig | Project deep-dives: numbered questions per project until each entry holds facts, numbers, and audience | `acqdemo:annual` | 10 to 20 minutes per project |
| Choose | Allocate the strongest entries across the three factors, with the rest on the bench | `acqdemo:annual` | 10 minutes |
| Write | Paste-ready C-R-I text for each factor | `acqdemo:annual` | automatic, then edits |
| Check | Deterministic checks plus a panel-style read, then fixes | `acqdemo:review` | 5 to 10 minutes |
| Hand off | Final files, working doc, and a crib sheet for the supervisor | `acqdemo:annual` | 5 minutes |

Then: during the year, add a ledger entry for each win as it happens, `acqdemo:plan` writes the contribution plan, and `acqdemo:midpoint` handles the midpoint and any closeout.

## Step 3: Detect the stage
Compare today's date with `paypool.md`:

| Window | Stage | Next skill |
|---|---|---|
| Cycle start to plan due (about 30 days) | Contribution plan | `acqdemo:plan` |
| After plan due, before midpoint window | Capture | Append a `candidate` entry to `FY<yy>/ledger.md` for each win (monthly, and after any briefing, release, or praise email) |
| Midpoint window | Midpoint | `acqdemo:midpoint` |
| After midpoint, before mid-August | Capture | as above; warn when the plan-change lock or the 90-day plan rule is near |
| Mid-August to employee due date | Annual | `acqdemo:extract`, then `acqdemo:annual` |
| Employee due date to supervisor due date | Handoff | confirm the crib sheet reached the supervisor; offer `acqdemo:review` on the final text |
| After the cycle ends | Next cycle | read next-cycle seeds from the working doc, then contribution plan |

Always mention: days until the employee due date; any promotion inside the pay pool's promotion window; any position or supervisor change that needs a closeout (`acqdemo:midpoint` handles closeouts).

## Step 4: Inventory and resume
When `FY<yy>/session-state.md` has a `next_action`, that comes first: open with the unfinished work (step, `current_entry`, round, pending questions, what the ledger already holds) and the offer to resume, then the inventory, then dates.

Report briefly: profile completeness; pay pool overlay present; roster rows; for the current `FY<yy>/`: ledger entries by status, open fields per entry (the `OPEN_FIELDS` lines from `python scripts/ledger_check.py --file FY<yy>/ledger.md`), harvest snapshots, draft versions, final files. Resume with the skill that owns the saved `step`, not the one that produced the data:

| Saved step | Resume with |
|---|---|
| 2 harvest, or harvest snapshots missing | `acqdemo:extract` |
| 3 dump, 3b sweeps, 4 deep-dive, 5 allocate, 6 draft, 8 finalize | `acqdemo:annual`, or `acqdemo:midpoint` when the state names a midpoint or closeout |
| 7 review | `acqdemo:review` |

Blank fields in ledger entries (`OPEN_FIELDS`) are deep-dive work, so they resume in `acqdemo:annual` or `acqdemo:midpoint`. `acqdemo:extract` only gathers new evidence; never send the user there to finish an entry.

## Step 5: Route
Invoke the matching skill: `acqdemo:plan`, `acqdemo:midpoint`, `acqdemo:extract`, `acqdemo:annual`, or `acqdemo:review`.

## Safety
- The workspace is private; names never appear in paste-ready text; classified information never enters any file or conversation.
- If the workspace is a git repository without the PII guard, recommend enabling it.
