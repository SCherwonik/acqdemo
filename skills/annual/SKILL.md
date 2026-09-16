---
name: annual
description: Use when writing an AcqDemo annual self-assessment - runs recall-first intake (brain dump, calendar and people sweeps, project deep-dives), builds the evidence ledger, and drafts paste-ready C-R-I statements for all three factors plus a supervisor crib sheet.
---

# AcqDemo Annual Self-Assessment

## References (open when a step needs them)
- Questions, sweeps, estimates: `../start/references/question-bank.md`
- Writing rules: `../start/references/writing-style.md`
- Data formats: `../start/references/ledger-format.md`
- Levels and Very High: `../start/references/levels.md`
- Program rules: `../start/references/rules/ccas-core.md`
- Certification statements: `../start/references/cert-templates.md`
- Descriptors (use the file for the user's career path): `../start/references/descriptors/`
- Templates: `../start/templates/working-doc.md`, `../start/templates/session-state.md`, `../start/templates/roster.md`

## Operating rules
- **Recall first.** Ask many numbered questions. No cap. End every message that asks questions, including later rounds and single follow-ups, with "What else does that bring to mind?"
- **Save constantly.** Write ledger, roster, rambles, and session state after every meaningful exchange; the session can end at any moment.
- **Save before you ask.** Before sending any message that waits on the user, write `FY<yy>/session-state.md`: `step`, `current_entry`, `round`, `pending_questions` (the numbered questions you are about to ask, verbatim), `next_action`, `updated`. Write answers already given into the ledger first. A message that asks questions without this save is a bug.
- **Allowed values only.** `status`, `role`, `sustained`, and number `source` use the lists in `../start/references/ledger-format.md`. Translate what the user says into a list value ("I built it myself" is `owned`, "one and done" is `one-time`) and keep their words in `notes`. Run `python ../start/scripts/ledger_check.py --file FY<yy>/ledger.md` after every ledger save and fix each CRITICAL before the next question.
- **Names** are welcome in conversation, `roster.md`, and the ledger; never in factor files.
- **Voice transcription.** Treat every answer as dictation: resolve garbled terms against the user's own material before asking, correct silently and confirm once, and never guess a name or drop an unmatched term (question bank, Voice and transcription).
- **Never invent** events, audiences, awards, or recognition. Numbers follow the estimate protocol: proposed, approved by the user, and recorded with a basis.
- **Repeats:** the current cycle's midpoint is the starting point; prior cycles are off limits.
- **Output** factor files follow `writing-style.md` exactly.
- **Classified information:** if the user begins to share it, stop them and move on.

## Step 0: Load
1. Find the workspace: the current directory if it holds `profile.md`, otherwise ask. If there is no profile, run the `acqdemo:start` skill's first-time setup first.
2. Work only in the workspace the user named or confirmed in this conversation; never search the disk for another one, and never use this skill's own folder or the plugin folder above it, even when it contains `profile.md`. Read `profile.md`, `paypool.md`, and `FY<yy>/session-state.md`. If session state shows unfinished work, summarize it in two lines (step, current entry, what is already answered in the ledger) and continue from `next_action`; re-ask only the `pending_questions` that the ledger does not yet answer.
3. Create any missing pieces: `FY<yy>/rambles/`, `evidence/`, `harvest/`, `drafts/`, `final/`; `FY<yy>/ledger.md` starting with `# Ledger FY<yy>`; `FY<yy>/session-state.md` and `<workspace>/roster.md` from the templates.

## Step 0b: Documents to gather, said first
Before the gate questions, tell the user what to put in the workspace and why, in two or three short paragraphs of plain speech. Offer to walk the retrieval steps (`../start/references/getting-your-documents.md`), take whatever they already have, and keep going whether they fetch the rest now or later. Never block on a missing document. Skip the prior-cycle paragraph entirely when `profile.md` says `first_cycle: yes`.

Say it roughly this way, in your own words:

"Pull one file from CAS2Net for your last completed cycle: the **Salary Appraisal**, exported with **Check All**. That single file carries that cycle's employee assessment, your supervisor's narrative, the midpoint, any closeout, the contribution plan it ran under, and the scores including your expected contribution score. It tells me what you already claimed, so this year's writing does not repeat it, what language your pay pool rewarded, and where your score sat."

"Then pull three things from this cycle: the **Midpoint Assessment**, the **Contribution Plan**, and the **Closeout Assessment** if your supervisor or your position changed. The midpoint is the jump-off point for the annual, since the annual builds on it with what changed since; the plan carries the duty language the panel expects to hear back."

"Last, export your Outlook calendar for the rating period and drop it in `FY<yy>/evidence/`. It is the best memory jog there is: it recovers the briefings, working groups, trips, and training nobody remembers in September. The steps are short and I can walk you through them."

Then read whatever they provide (documents step of `../extract/SKILL.md`) before asking the gate questions, because a prior appraisal answers several of them outright.

## Step 1: Gate
1. Ask only the gate questions (question bank) that `profile.md` does not already answer. Update the profile. Put unknowns in session-state `open_questions`. Never block on an unknown.
2. Decide and record:
   - Descriptor file: the career path file (nh, nj, or nk). Current level and `target_level`.
   - Special situations: a promotion inside `paypool.md` `promotion_window_days` (needs substantial justification), a position or supervisor change (closeouts exist), supervisory duties (supervisory paragraph), certifications (certification statements).

## Step 2: Harvest
Run the `acqdemo:extract` skill for git, the calendar export, and midpoint or closeout documents. If the user wants to skip, continue. A harvested claim the user cannot expand on is confirmed with yes/no questions before it is dropped (Step 4).

## Step 3: Brain dump
1. Ask the question bank's Brain dump prompts: 8 to 10 numbered prompts, the first few built from this user's PRD duties, plan objectives, and harvest anchors. Invite a long ramble in any order. Save the raw text to `FY<yy>/rambles/<date>-dump.md`.
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
3. If the user cannot expand on a claim from the midpoint, a closeout, or the plan, ask yes/no questions built from its named entities (meetings led, budget rounds, audiences; question bank, Confirm before dropping) before dropping it. If answers conflict, the later answer wins and the entry's `notes` record the conflict.
4. Resolve numbers with the estimate protocol; confirm each; record source and basis.
5. Fill `lenses` for all three factors, `descriptor_hits` from the target level, `sustained`, `prior_cycle_overlap` (compare with `prior/`), `prd_duty`, and `plan_tag`. Read the duties yourself with `python ../plan/scripts/prd_text.py --file "<profile prd_path>"` and the plan from `FY<yy>/plan/`; ask the user to paste a document only when the file is missing or unreadable.
6. Run `python ../start/scripts/ledger_check.py --file FY<yy>/ledger.md` and ask about every field its `OPEN_FIELDS` line lists for this entry (write `none` when a field does not apply; blank means not asked yet). Set `status: ready` only when the entry has no `READY_INCOMPLETE` warning, save, and show the coverage grid.

Continue until every factor has at least four `ready` entries counted by primary factor (each entry once, under its strongest lens), the sweeps turn up nothing new, or the user says "enough." Aim the next deep-dive at the weakest factor. Then run the question bank's Portfolio roll-up and record the confirmed totals.

## Step 5: Allocate
Propose, then get approval:

| Factor | Order | Entry | Angle | Why this factor | Raise or award |
|---|---|---|---|---|---|

Rules: three or four entries per factor, greatest impact first. Each entry is primary in one factor. Its project may appear in other factors only from a different angle with different wording (`writing-style.md`, One project, three angles), and no fact or number appears in more than one factor. No entry whose prior-cycle overlap has no delta. Remaining `ready` entries go to the bench. Record `allocated` in the ledger, primary factor first (`JA, MS`).

Thin material: if primary entries cannot fill a factor's minimum, return to Step 3b sweeps and targeted questions aimed at that factor before reusing a project from another angle. Never turn an entry with no result into a C-R-I; tell the user plainly which factor is thin.

## Step 6: Draft
Write `FY<yy>/drafts/v1/` with the three factor files:
1. Mandatory paragraphs first, in `paypool.md` order: the supervisory paragraph (exact counts from the profile, then the scope of supervision per `writing-style.md`, Special situations) and certification statements (templates filled from the profile; ask for any missing value).
2. C-R-I statements per `writing-style.md`: the Contribution in at most 35 words with a verb that matches the role; the Result with the entry's numbers; the Impact tied to the level the work actually reaches, with a mission tie from the profile's mission statements, worded differently in each entry; phrasing from the target level's descriptors; at most 3,900 characters per factor.
3. If a promotion falls inside the pay pool's window, make continuity visible: higher-level contributions before and after the effective date, and sustained strategic work.
4. Length check: if a factor is under about 3,000 characters, enrich Results and Impacts from the ledger (numbers, audience, scope, roll-up totals) or promote a bench entry, then recount. Never pad with adjectives. If the ledger holds nothing more, leave the factor short and say so.

## Step 7: Review
Run the `acqdemo:review` skill on `FY<yy>/drafts/v1/`: both the checker (its Step 1) and the judgment checks (its Step 2). A clean checker alone does not end the review. The review writes fixes to new versions. Then take the user's edits by voice, write a new version, and review again with both layers. Exit only when both layers show 0 CRITICAL, every remaining WARNING is fixed or accepted by the user, and the user approves the text.

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
