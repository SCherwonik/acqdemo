---
name: acqdemo-midpoint
description: Use when the user wants to write or draft a midpoint self-assessment (mid-year review) or a closeout after a supervisor change or new position mid-cycle - reuses the annual engine to draft C-R-I statements for the partial period, with no scores and no crib sheet. To check an existing midpoint or closeout draft, use acqdemo-review instead.
---

# AcqDemo Midpoint and Closeout

Reuses `../acqdemo-annual/SKILL.md` end to end for the mechanics: Load, Gate,
Harvest, Brain dump, Recall sweeps, Deep-dives, Allocate, Draft, Review. Read
that skill first; this file states only what differs for a midpoint or a
closeout. Do not re-copy its step bodies here.

## References
- Annual engine (step names below refer to this): `../acqdemo-annual/SKILL.md`
- Checker: `../acqdemo-review/scripts/check.py`
- Pay pool overlay fields: `../acqdemo/templates/paypool.md`
- Program rules (Midpoint, Closeout sections): `../acqdemo/references/rules/ccas-core.md`

## Which variant
- **Midpoint**: inside the pay pool's `midpoint_window` (`paypool.md`), no supervisor
  or position change since the plan was approved.
- **Closeout**: the supervisor or the employee's position changed. Required within
  30 calendar days of the change date. State that deadline as soon as this starts.

The annual's operating rules apply unchanged, including **Save before you ask** (write `session-state.md` before any message that waits on the user).

## Differences from the annual (`../acqdemo-annual/SKILL.md`)
1. **Period.** Cycle start to today (midpoint) or cycle start to the change date
   (closeout), never the full cycle and never a prior cycle.
2. **Minimum entries.** Not the annual's three per factor. Use `paypool.md`
   `min_entries_midpoint` (toolkit default 1 when the field is blank); aim for two
   strong entries per factor. Skip Step 4's target of four ready entries per primary
   factor and Step 6's length check; stop once the minimum is met and the user is
   satisfied.
3. **Plan tiebacks.** In Step 4 and Step 5, tie each entry to a plan objective label
   (JA1, CT2, ...) when `FY<yy>/plan/Contribution Plan.txt` has labels.
4. **No scores, no Very High.** Never mention a score, band, or Very High language;
   the supervisor's feedback at this stage carries no scores either.
5. **No crib sheet, no PAQL.** Skip Step 8's crib sheet and next-cycle-seeds work
   entirely: not a crib sheet exercise, no PAQL prefix, no working doc. Save straight
   to final text (below).
6. **Independent factors.** Draft each factor in Step 6 on its own. Never paste the
   same sentence, or a close paraphrase, into two factors: that is exactly what
   `CROSS_FACTOR_REPEAT` catches.
7. **Review command.** In Step 7, call the checker directly with midpoint flags
   instead of the `acqdemo-review` skill's default flags, then run its judgment
   checks (`../acqdemo-review/SKILL.md` Step 2) as the annual does:
   ```
   python ../acqdemo-review/scripts/check.py --dir <final folder> \
       --min-entries <min_entries_midpoint> --mode midpoint
   ```
   Omit `--min-entries` when the field is blank (the checker defaults to 1 in both
   modes). Use `--mode closeout` for a closeout. Fix every CRITICAL, including
   `CROSS_FACTOR_REPEAT`.
8. **Save location.** Midpoint: `FY<yy>/midpoint/final/`. Closeout:
   `FY<yy>/closeout-<YYYY-MM-DD>/final/` (change date). Mark every used ledger entry
   `status: submitted` with `evidence` noting "midpoint" or "closeout <date>".
9. **Jump point for the annual.** This text becomes the annual's starting point.
   Continuing work at annual time needs a cycle delta describing what changed since;
   never repeat this text verbatim.

## After saving
Tell the user: the supervisor gives feedback with no scores and documents the date
and method of the discussion in CAS2Net. For a closeout, restate the 30-day deadline
and note that the gaining supervisor reads this document when recommending the
annual score.
