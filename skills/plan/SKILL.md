---
name: plan
description: Use when writing or revising an AcqDemo contribution plan, meaning the cycle's objectives, including for a new position or a position change. Typical requests are write my contribution plan, draft my objectives from my PRD, or update my plan. Produces objectives labeled by factor (JA1, CT1, MS1) with KPIs and PRD duty tiebacks, plus Key Performance Objectives (KPO1, KPO2) when the pay pool requires them.
---

# AcqDemo Contribution Plan

Drafts a contribution plan from the Position Requirements Document (PRD) plus expected work for the cycle. Never invents duties or numbers.

## Inputs
- `<workspace>/profile.md`: career path, level, `target_level`, organization, mission statements, `prd_path`, `plan_detail` (`lean` or `full`; `lean` when absent).
- `<workspace>/paypool.md`: `min_plan_objectives_per_factor`, `plan_due_days`, `plan_change_lock_days`, `char_limit`, and the KPO fields `kpo_required`, `kpo_count`, `kpo_labels`, `kpo_factor`, `plan_label_style`.
- KPO reference: `../start/references/kpo.md` (read it only when `kpo_required` is `yes`). It points at two companions: `../start/references/kpo-library.md` (the model objectives by functional area) and `../start/references/kpo-guidance.md` (the SMART table and the performance information types).
- Program rules: `../start/references/rules/ccas-core.md` ("Contribution plans").
- Descriptor language for the target level: `../start/references/descriptors/` (the file for the user's career path).
- KPI examples: `../start/references/question-bank.md`.
- Templates for field names, if the workspace lacks a profile or overlay yet: `../start/templates/profile.md`, `../start/templates/paypool.md`.

If there is no workspace or profile, offer the `acqdemo:start` skill's first-time setup first.

## Step 1: Load
Read `profile.md` and `paypool.md`. If either is missing required fields (`prd_path`, `min_plan_objectives_per_factor`, `plan_due_days`, `plan_change_lock_days`), ask for them and update the files. Read the KPO fields too. If they are absent, treat them as the defaults: `kpo_required: no`, `plan_label_style: colon`. When `kpo_required` is `yes`, the plan carries exactly `kpo_count` KPOs, with the labels in `kpo_labels`, written under the `kpo_factor` heading after that factor's regular objectives. Ask the user to confirm the values if the overlay is silent and the position is acquisition-coded in the FY27 cycle or later.

## Step 2: Read the PRD
Run the shared document reader at `../start/scripts/doc_text.py` (handles pdf, docx, pptx, txt, and md):

```
python "<this skill folder>/../start/scripts/doc_text.py" --file "<prd_path>"
```

Number the duties in the output as you present them back to the user, so later steps can cite "PRD 3" or "PRD 3, 4". If it exits 2 (unsupported file, or `pdftotext` missing for a `.pdf` PRD), tell the user what to install or convert and stop.

## Step 3: Gather this cycle's work
Ask, in a numbered round: what work is expected this cycle (ramble is fine); the prior plan's text, if any (for continuity, not for copying; if it was written in C-R-I form, its format does not carry over, and mandatory objectives such as a certification self-certification are inserted by CAS2Net, not drafted); supervisor priorities or guidance; and the mission statements one and two levels up from `profile.md`, if not already recorded.

## Step 4: Draft objectives
For each factor (Job Achievement and/or Innovation, Communication and/or Teamwork, Mission Support), draft at least `min_plan_objectives_per_factor` objectives (the example pay pool requires 2). Each objective:
- Is labeled sequentially by factor: `JA1`, `JA2`, ..., `CT1`, ..., `MS1`, ... Future ledger entries and assessments tie back to these labels.
- Uses language from the target level's descriptor file in `../start/references/descriptors/` (the career path file, at `target_level`, not `level`, when they differ).
- Carries exactly one measurable KPI: a count, percent, hours, or other number with a target (people trained, tool users, senior-leader briefings, estimates supported and dollar value, hours saved; see `question-bank.md`).
- Cites the PRD duty numbers it maps to.

Plans reflect expected contribution, not exceeded performance. Set each target at what the user is expected to deliver; inflated plans set targets that cannot be met.

## Step 4b: Use the room (`plan_detail`)
Each factor is its own CAS2Net field. `plan_detail` sets how much of it the plan uses: `lean` aims for an average of at least 200 characters per objective, about what pay pool template examples run, `full` for at least 300, KPOs included, and every factor stays under `char_limit`. So a factor's floor grows with its objective count: three objectives is 600 characters under `lean` and 900 under `full`, and Mission Support with two KPOs is 1,000 or 1,500. A single sentence past 450 characters, or a KPO past 600, reads as a run-on (`SENTENCE_TOO_LONG`): cut a clause or split the work into two objectives.

Reach the length with context, never with commitments or filler. Every number or deliverable in a plan is a bar the user is measured against at the annual, so length comes from:
- Why it matters: the mission tie, the decision it informs, who benefits. This pre-writes the Impact of the annual statement.
- Scope: which commodities, teams, programs, or systems it reaches.
- How it will be shown: the artifact, log, or feedback that proves it was met.
- Target-level descriptor language, where it fits naturally.

Never reach the length with adjectives, invented methods or events, or targets the user has not confirmed. Keep one sentence per label; a longer sentence, not a second one. Show every clause you add that the user did not say and ask them to confirm it. If a factor is still short after that, ask the user what more the work involves, or propose one more objective from an unused PRD duty and say that it is one more commitment. Leave it short rather than pad it.

## Step 4a: Draft KPOs (only when `kpo_required` is `yes`)
Read `../start/references/kpo.md` first. Then draft exactly `kpo_count` Key Performance Objectives, labeled as `kpo_labels` says (the example overlay is `KPO1` Strategic Outcome and `KPO2` Workforce Behavioral), and place them under the `kpo_factor` heading after that factor's regular objectives.

For each KPO:
1. Start from the library model objective for the user's functional area (the tables in `../start/references/kpo-library.md`; use its cross-functional menu if no area fits). Take the SMART table and the performance information types from `../start/references/kpo-guidance.md`. Strategic Outcome KPOs say what the user delivers; Workforce Behavioral KPOs say how.
2. Tailor it to the user's actual work from the PRD and Step 3, using the SMART formula: KPO category + specific task or behavior + measurable outcome + timeframe. Never copy a library objective unchanged.
3. Write it as one sentence with the measure and the timeframe embedded in it. Avoid vague verbs such as "assist" and "participate"; say what the user does.
4. Set two checkpoints: a midpoint milestone and a year-end target, because the midpoint review is where progress is discussed.
5. Name the performance information that will show it was met (a metric, a work product, stakeholder input, a process indicator, a competency demonstration, or a learning outcome). Prefer outcomes over process compliance.
6. Keep the target within the user's grade and authority.
7. Mark every proposed number as a target to agree with the supervisor, never as a fact, and ask the user to confirm it. If the user cannot supply a basis for a number, leave a labeled placeholder, never an invented figure.
8. Cite the PRD duty numbers it maps to in the working file only.

## Step 5: Save and check
Write two files in `FY<yy>/plan/`:

- `Contribution Plan - working.txt`: the working file. It carries the KPI and PRD tiebacks so traceability is not lost, in this format:

```
Job Achievement and/or Innovation
JA1: <objective>
KPI: <measure and target>
PRD: <duty numbers>

Communication and/or Teamwork
CT1: ...

Mission Support
MS1: ...
KPO1: <KPO sentence with its measure and timeframe embedded>
KPI: <midpoint milestone, year-end target, performance information>
PRD: <duty numbers>
```

- `Contribution Plan.txt`: the paste-ready plan for CAS2Net. Generate it from the working file. It matches the pay pool's format exactly: labels in the `plan_label_style` (`colon` writes `JA1: text`, `parentheses` writes `(JA1) text`), one objective sentence per label with its measure embedded, factor headings, and no `KPI:` or `PRD:` lines. If a regular objective's measure is not already inside its sentence, move it in. Use the same label style in the working file.

Run the checker at `scripts/plan_check.py` against the working file, the one that carries the KPI lines. Pass the KPO flags from the overlay:

```
python "<this skill folder>/scripts/plan_check.py" --file "<working file>" --min-objectives <min_plan_objectives_per_factor> --kpo-count <kpo_count> --kpo-factor <kpo_factor> --char-limit <char_limit> --plan-detail <plan_detail>
```

Omit `--kpo-count` and `--kpo-factor` when `kpo_required` is `no`. `--char-limit` defaults to 3900 when the overlay has no `char_limit`. Each factor is its own CAS2Net field capped at 4,000 characters, and the check counts what goes into that field: the objective sentences, KPOs included, without the `KPI:` and `PRD:` lines. Fix every CRITICAL finding (`MIN_OBJECTIVES`, `DUPLICATE_LABEL`, `LABEL_FACTOR_MISMATCH`, `MISSING_FACTOR`, `MISSING_KPO`, `KPO_COUNT`, `FACTOR_TOO_LONG`) before saving. `PLACEHOLDER` is the exception that proves the rule in Step 4a: a labeled placeholder is the right thing to write while a number waits on the user or their supervisor, so save the files with it and list every remaining placeholder for the user by label. What it may never do is reach CAS2Net, so the plan is not ready to paste until `PLACEHOLDER` is gone. It also catches a template slot left unfilled, such as `<Insert Program(s) Here>`. Address WARNING findings (`NO_KPI`, `KPI_NOT_MEASURABLE`, `NO_PRD_TIEBACK`, `EM_DASH`, `KPO_FACTOR`, `KPO_ORDER`, `FACTOR_TOO_SHORT`, `SENTENCE_TOO_LONG`) unless the user has a reason not to; a template may let an employee place a KPO under another factor when it fits better. Check the paste-ready file for em dashes and for any leftover `KPI:` or `PRD:` line before handing it over.

## Step 6: Remind the user
- The plan must be approved (in CAS2Net) within `plan_due_days` of the cycle start or the position/appraisal change.
- No changes to an approved plan in the last `plan_change_lock_days` of the cycle.
- From now on, tag new ledger entries and deep-dives (`acqdemo:annual`) with the objective label they support, for example `plan_tag: JA1`. `KPO1` and `KPO2` are valid `plan_tag` values.

## Rules
- Never invent PRD duties, KPIs, or targets the user has not confirmed.
- Objective text and KPIs contain no people's names.
- Each factor's paste-ready text fits `char_limit` (3,900 by default). Mission Support carries the KPOs as well, so it runs out first: tighten wording rather than drop a required objective. No objective runs past 450 characters, no KPO past 600.
