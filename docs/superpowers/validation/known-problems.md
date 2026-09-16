# Known Problems Validation (Test B)

Validates the review skill (`skills/review/`) against two real prior
submissions that are known to have specific problems: a deterministic-checker
pass (`check.py`) plus the judgment layer described in `SKILL.md` Step 2.
Each folder was compared against a pre-recorded table of expected findings.

## Results summary

| Cycle | Layer | Expected finding codes | Result |
|---|---|---|---|
| Cycle A (a mid-cycle draft) | checker | `CROSS_FACTOR_REPEAT` x2, `PRIOR_REPEAT`, `ACQ_CERT`, `FM_CERT`, `BANNED_WORD` (3 factors), `CONTRIBUTION_TOO_LONG` (3 factors), `LABEL_STYLE` correctly absent | PASS 6/6 |
| Cycle A (a mid-cycle draft) | judgment | prior-cycle achievement overlap (1 item), adjective-heavy phrasing (1 item) | PASS 2/2 |
| Cycle B (an end-of-cycle draft) | checker | `CONTRIBUTION_TOO_LONG` (3 factors), `ACQ_CERT`, `FM_CERT`, `CHAR_LIMIT`, `CHAR_SOFT_LIMIT` | PASS 5/5 |

Overall: 13/13 expected findings reported. No misses.

## Extra findings (not in the expected table, not gaps)

- Cycle A: `OVERUSED_WORD`, `SMART_QUOTES`
- Cycle B: `SMART_QUOTES`

## Checker gaps

None. `check.py` was not modified.

## Judgment-layer misses

None. `SKILL.md` was not modified.

## Changes made

None required.

## Scope note

This run covered detection coverage only (checker findings + judgment-layer
findings against the expected table). The fix loop (Step 4 of `SKILL.md`,
producing a revised draft with 0 CRITICAL) was not exercised in this pass.

