---
name: acqdemo-harvest
description: Use when gathering evidence of a year's work for an AcqDemo self-assessment from git repositories, a calendar export, or midpoint and closeout documents, to create candidate entries in the evidence ledger. Fires on requests like pull what I did this year from git and my calendar, mine my repos for the rating period, gather my AcqDemo evidence, or what did I work on this year.
---

# AcqDemo Harvest

Turns raw evidence into `candidate` ledger entries that the user confirms. Harvest never marks anything `ready`; deep-dives do that.

## Inputs
- `<workspace>/profile.md`: `rating_period` and the "Repositories to harvest" table (one row per
  repository: `local` rows give a filesystem path for `--local`, `github` rows give `owner/repo`
  for `--github`).
- `FY<yy>/evidence/calendar-*.txt`: calendar exports.
- The current cycle's midpoint and closeout text, if saved in the workspace.
- `<workspace>/prior/`: previous cycles, used only to flag overlap.
- Ledger format: `../acqdemo/references/ledger-format.md`.

If there is no workspace, ask for the rating period and sources, and offer the `acqdemo` skill's first-time setup.

When harvesting mid-cycle, pass `--until` as the earlier of today and the rating period's end
date, for both `git_harvest.py` and `calendar_harvest.py`, so the harvest never asks about
commits or meetings that have not happened yet.

## Step 1: Git
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

## Step 2: Calendar
1. If no export exists, give the user the calendar export steps from `../acqdemo/references/question-bank.md` (section "Calendar export") and continue with other sources meanwhile.
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

Ask: keep, reject, or merge ("merge 2 and 3", "reject 5"). Then append kept candidates to `FY<yy>/ledger.md` with the next `L-###` ids, `status: candidate`, and only the fields the evidence supports. Leave every other field, including `role`, blank rather than a placeholder; nobody knows the role until a deep-dive fills it in. Record numbers with the source matching where they came from: `source: git` with `basis: harvest <date>` for git counts, `source: calendar` with `basis: calendar export <date>` for calendar counts, `source: document` with `basis: <midpoint or closeout> <date>` for counts pulled from midpoint or closeout text. Update `FY<yy>/session-state.md`.

Running `ledger_check.py` right after a harvest will report `OPEN_FIELDS` (INFO) on every new candidate; that is expected at this stage and is not something to fix before moving on.

## Rules
- Harvest snapshots and the ledger stay in the private workspace.
- Merge commits are never counted; dates are never guessed. A commit cherry-picked or ported between branches (same author date and subject) counts once per repository, not once per branch.
- Calendar titles may contain names and program details; they may go in ledger `evidence` and `notes`, never into factor files.
