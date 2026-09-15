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
