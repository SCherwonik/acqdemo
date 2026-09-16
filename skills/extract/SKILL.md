---
name: extract
description: Use when pulling, mining, or gathering a whole rating period of work out of git repositories, an Outlook calendar export, or prior assessment documents, to build many candidate entries at once. Typical requests are pull what I did this year from git and my calendar, mine my repos for the rating period, gather my AcqDemo evidence, and what did I work on this year.
---

# AcqDemo Harvest

Turns raw evidence into `candidate` ledger entries that the user confirms. Harvest never marks anything `ready`; deep-dives do that.

## Inputs
- Documents: the CAS2Net export for the last completed cycle, and this cycle's midpoint or closeout, if saved in the workspace. What each buys and where the rest of the checklist goes: `../start/references/intake-checklist.md`. See Step 1.
- `<workspace>/profile.md`: `rating_period` and the "Repositories to harvest" table (one row per
  repository: `local` rows give a filesystem path for `--local`, `github` rows give `owner/repo`
  for `--github`).
- `FY<yy>/evidence/calendar-*.txt`: calendar exports.
- `<workspace>/prior/`: previous cycles, including a freshly split CAS2Net export, used only to flag overlap.
- Ledger format: `../start/references/ledger-format.md`.

If there is no workspace, ask for the rating period and sources, and offer the `acqdemo:start` skill's first-time setup.

When harvesting mid-cycle, pass `--until` as the earlier of today and the rating period's end
date, for both `git_harvest.py` and `calendar_harvest.py`, so the harvest never asks about
commits or meetings that have not happened yet.

## Step 0: Check the scope
This skill mines a whole rating period. When the user is handing over one item instead, a praise email, a single briefing, one release, append it to `FY<yy>/ledger.md` as a single `candidate` entry the way `../start/SKILL.md` does in its one-win step, ask only for what that entry is missing, and stop. Run the full period harvest below only when the user wants the year covered.

## Step 1: Documents
Documents come first: the last CAS2Net export shows what the pay pool must not see repeated, and
the current midpoint or closeout is the starting point everything else builds on. Do not repeat
the full checklist here; point the user at `../start/references/intake-checklist.md` for what
each document is, why it matters, and what to do when they have none of it.
When a document is not saved anywhere, offer to walk the CAS2Net retrieval steps with them
(`../start/references/getting-your-documents.md`) before falling back to the sweeps.

Read every document with the toolkit's shared reader, `../start/scripts/doc_text.py` (pdf,
docx, pptx, txt, md). It supports --pages N-M for long files and --out PATH to save what it
extracts; read a short page range first to find where each part starts, then pull the range you
need:
```
python ../start/scripts/doc_text.py --file "<document path>" --pages 1-15
python ../start/scripts/doc_text.py --file "<document path>" --pages <start>-<end> --out "FY<yy>/harvest/<today>-<label>.txt"
```

Check `profile.md` first and ask only for documents that can exist:
- `first_cycle: yes`, or no prior cycle in this position: skip 1.1 entirely. Say so out loud ("your first cycle, so there is no prior assessment to compare against") and lean on the contribution plan, the PRD, and the sweeps instead.
- No midpoint written this cycle: skip 1.2 and say the annual will cover the whole cycle from scratch.
- A position or supervisor change this cycle: also ask for any closeout the losing supervisor wrote, and treat it like 1.2.
Never ask a user twice for a document they have already said does not exist; record the answer in `profile.md` when the triage has not already.

1. **The CAS2Net export for the last completed cycle** (usually one long PDF: the full appraisal
   package).
   - Read it in page ranges as above; these exports run long, so find the assessment section
     first, then pull it.
   - Split the employee's submitted assessment into the three factor files `../review/scripts/check.py`
     expects, and save them under `prior/FY<yy>/` for that completed cycle (never this cycle's
     `FY<yy>/`):
     - `Job Achievement and Innovation.txt`
     - `Communication and Teamwork.txt`
     - `Mission Support.txt`
   - Pull the scores, EOCS, and value of position into `profile.md` (`eocs` and `value_of_position`
     fields; note the score itself as a dated line since the template has no separate field for it).
   - If the export also carries objective labels (JA1, CT1, MS1...) still in force for this cycle's
     plan, put those into `FY<yy>/plan/`; a completed cycle's own plan, now closed, stays with its
     text in `prior/FY<yy>/` instead.
   - Do not create ledger candidates from anything filed under `prior/`; it is for overlap-flagging
     only, the same as any other prior cycle.
   - The source PDF itself never goes into git: keep it outside the workspace, or in a folder the
     workspace's PII guard or `.gitignore` excludes. Say this out loud once, the same rule as any
     other appraisal document.

2. **This cycle's midpoint or closeout** (pdf, docx, txt, or md).
   - Read it the same way, then split it per factor and save under `FY<yy>/midpoint/final/` (or
     `FY<yy>/closeout-<date>/final/` for a closeout), using the same three factor file names as
     above.
   - Create a `candidate` ledger entry for each C-R-I it contains, with the note "from midpoint" or
     "from closeout". Mark every one `prior_cycle_overlap: continuing (cycle delta: unknown)`, since
     the current midpoint is the starting point and the annual builds on it with a delta rather than
     repeating it; the deep-dive fills in what changed.
   - Record any counts pulled from this text as `source: document` with `basis: midpoint <date>` or
     `basis: closeout <date>`; counts pulled from the CAS2Net export use `basis: cas2net export <date>`.

3. **If a file will not open** (a format the reader does not handle, a scan, a password), ask the
   user to paste the text into the conversation and continue from the paste; never make them retype
   a document by hand.

## Step 2: Git
1. Ask which author names are the user's (commit names often differ between machines). Keep commits from other authors in the output; they show collaboration.
2. Run the git harvester at `scripts/git_harvest.py`. `<end>` is the earlier of today and the rating period's end date:
   ```
   python "<this skill folder>/scripts/git_harvest.py" --since <start> --until <end> --local <paths...> --github <owner/repo...> --out "FY<yy>/harvest/<today>-git.md"
   ```
3. Read the output and cluster commits into candidates:
   - Group within a repository by feature or milestone: version bumps, tags, shared prefixes ("feat(x):"), phase words, the same screen or module.
   - For each candidate record: title; first and last date; what, in plain words; git numbers (commits, version from and to, tags, numbered findings or defects closed); other authors as collaborators; evidence as `<repo>@<tag or first..last date>`.
   - Watch for high-value signals in subjects: defects found in legacy products, validation or tie-out against published results, new capabilities, performance gains, documentation, tests, releases.
   - Do not infer role, audience, or impact from git. Deep-dives supply those.

## Step 3: Calendar
1. If no export exists, give the user the calendar export steps from `../start/references/question-bank.md` (section "Calendar export") and continue with other sources meanwhile.
2. Run the calendar harvester at `scripts/calendar_harvest.py`. `<end>` is the earlier of today and the rating period's end date:
   ```
   python "<this skill folder>/scripts/calendar_harvest.py" --file "FY<yy>/evidence/<export>.txt" --since <start> --until <end> --out "FY<yy>/harvest/<today>-calendar.md"
   ```
3. Read the output and propose candidates:
   - Each recurring series becomes a team or working-group candidate with its occurrence count and date range.
   - One-off meetings whose titles suggest a briefing, demonstration, review, training, site visit, or senior leader become briefing candidates.
   - Skip routine administration (all-hands, holidays, leave, personal appointments) unless the user wants them.
   - Keep the month of every meeting for the timeline walk.
4. If the export has no meetings in some months of the rating period, tell the user which months are missing and suggest re-exporting.

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

Ask: keep, reject, or merge ("merge 2 and 3", "reject 5"). Then append kept candidates to `FY<yy>/ledger.md` with the next `L-###` ids, `status: candidate`, and only the fields the evidence supports. Leave every other field, including `role`, blank rather than a placeholder; nobody knows the role until a deep-dive fills it in. Record numbers with the source matching where they came from: `source: git` with `basis: harvest <date>` for git counts, `source: calendar` with `basis: calendar export <date>` for calendar counts, `source: document` with `basis: <midpoint, closeout, or cas2net export> <date>` for counts pulled from document text. Update `FY<yy>/session-state.md`.

Running `ledger_check.py` right after a harvest will report `OPEN_FIELDS` (INFO) on every new candidate; that is expected at this stage and is not something to fix before moving on.

## Rules
- Harvest snapshots and the ledger stay in the private workspace.
- Source documents (the CAS2Net export, a midpoint or closeout file) never go into git; only the extracted, split text does.
- Merge commits are never counted; dates are never guessed. A commit cherry-picked or ported between branches (same author date and subject) counts once per repository, not once per branch.
- Calendar titles may contain names and program details; they may go in ledger `evidence` and `notes`, never into factor files.
