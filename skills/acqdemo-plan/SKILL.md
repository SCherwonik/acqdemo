---
name: acqdemo-plan
description: Use when writing an AcqDemo contribution plan or performance plan objectives - for a new position, a new cycle, or a position change, drafts PRD-based objectives labeled by factor (JA1, CT1, MS1) with KPIs and PRD duty tiebacks.
---

# AcqDemo Contribution Plan

Drafts a contribution plan from the Position Requirements Document (PRD) plus expected work for the cycle. Never invents duties or numbers.

## Inputs
- `<workspace>/profile.md`: career path, level, `target_level`, organization, mission statements, `prd_path`.
- `<workspace>/paypool.md`: `min_plan_objectives_per_factor`, `plan_due_days`, `plan_change_lock_days`.
- Program rules: `../acqdemo/references/rules/ccas-core.md` ("Contribution plans").
- Descriptor language for the target level: `../acqdemo/references/descriptors/` (the file for the user's career path).
- KPI examples: `../acqdemo/references/question-bank.md`.
- Templates for field names, if the workspace lacks a profile or overlay yet: `../acqdemo/templates/profile.md`, `../acqdemo/templates/paypool.md`.

If there is no workspace or profile, offer the `acqdemo` skill's first-time setup first.

## Step 1: Load
Read `profile.md` and `paypool.md`. If either is missing required fields (`prd_path`, `min_plan_objectives_per_factor`, `plan_due_days`, `plan_change_lock_days`), ask for them and update the files.

## Step 2: Read the PRD
Run the extractor at `scripts/prd_text.py`:

```
python "<this skill folder>/scripts/prd_text.py" --file "<prd_path>"
```

Number the duties in the output as you present them back to the user, so later steps can cite "PRD 3" or "PRD 3, 4". If it exits 2 (unsupported file, or `pdftotext` missing for a `.pdf` PRD), tell the user what to install or convert and stop.

## Step 3: Gather this cycle's work
Ask, in a numbered round: what work is expected this cycle (ramble is fine); the prior plan's text, if any (for continuity, not for copying); supervisor priorities or guidance; and the mission statements one and two levels up from `profile.md`, if not already recorded.

## Step 4: Draft objectives
For each factor (Job Achievement and/or Innovation, Communication and/or Teamwork, Mission Support), draft at least `min_plan_objectives_per_factor` objectives (the example pay pool requires 2). Each objective:
- Is labeled sequentially by factor: `JA1`, `JA2`, ..., `CT1`, ..., `MS1`, ... Future ledger entries and assessments tie back to these labels.
- Uses language from the target level's descriptor file in `../acqdemo/references/descriptors/` (the career path file, at `target_level`, not `level`, when they differ).
- Carries exactly one measurable KPI: a count, percent, hours, or other number with a target (people trained, tool users, senior-leader briefings, estimates supported and dollar value, hours saved; see `question-bank.md`).
- Cites the PRD duty numbers it maps to.

## Step 5: Save and check
Write `FY<yy>/plan/Contribution Plan.txt` in this format:

```
Job Achievement and/or Innovation
JA1: <objective>
KPI: <measure and target>
PRD: <duty numbers>

Communication and/or Teamwork
CT1: ...
```

Run the checker at `scripts/plan_check.py`:

```
python "<this skill folder>/scripts/plan_check.py" --file "<plan file>" --min-objectives <min_plan_objectives_per_factor>
```

Fix every CRITICAL finding (`MIN_OBJECTIVES`, `DUPLICATE_LABEL`, `LABEL_FACTOR_MISMATCH`, `MISSING_FACTOR`) before saving. Address WARNING findings (`NO_KPI`, `KPI_NOT_MEASURABLE`, `NO_PRD_TIEBACK`, `EM_DASH`) unless the user has a reason not to.

## Step 6: Remind the user
- The plan must be approved (in CAS2Net) within `plan_due_days` of the cycle start or the position/appraisal change.
- No changes to an approved plan in the last `plan_change_lock_days` of the cycle.
- From now on, tag new ledger entries (`acqdemo-log`) and deep-dives (`acqdemo-annual`) with the objective label they support, for example `plan_tag: JA1`.

## Rules
- Never invent PRD duties, KPIs, or targets the user has not confirmed.
- Objective text and KPIs contain no people's names.
