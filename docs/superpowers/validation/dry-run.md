# Dry Run with a Session Reset (Test F)

Status: **partial.** A quick agent-driven run on 2026-09-15 proved the resume path after one fix. The full run with the real user answering (Task 25 as written) is still to do.

## Quick run (agent answering from project files only)
- Plugin loaded from the repository (`claude -p --plugin-dir <repo>`, installed release disabled for the session), a scratch copy of the private workspace, one project.
- Session 1: "Let's do my annual, but only one project for a dry run." Gate unknowns parked; deep-dive round 1 asked and answered.
- Session 2 (brand new session, same folder): "Where am I in the AcqDemo cycle?"

| Check | Result | Notes |
|---|---|---|
| Session state written before questions | FAIL, then PASS after fix | First attempt asked 8 questions without saving; new "Save before you ask" rule fixed it |
| Router reports the annual stage | PASS | |
| Router finds session state and summarizes the unfinished deep-dive | PASS | Reported step 4, current entry, round 2, open fields |
| Resume offered | PASS | Offered to resume the deep-dive |
| No lost answers | PASS | Round 1 answers were in the ledger entry before the session ended |
| Questions numbered | PASS | |
| "What else does that bring to mind?" asked each round | PARTIAL | Asked in round 1, missing from the round 2 message |
| Estimates proposed with a basis | not reached | |
| Names kept out of factor text | not reached | No drafting in this run |
| Deep-dive finished to `status: ready` | not reached | |

## Open issues to fix
1. Deep-dive wrote values outside the allowed lists (`role: sole developer`, `sustained: no`). Map answers to allowed values and run `ledger_check.py` after every ledger save, not only before `ready`.
2. Deep-dive asked the user to paste PRD duties although `../acqdemo-plan/scripts/prd_text.py` can read the PRD; point the annual skill at it for `prd_duty`.
3. "What else does that bring to mind?" was dropped from a later round.
4. The router suggested `acqdemo-harvest` to finish open ledger fields; unfinished deep-dives should resume in `acqdemo-annual` (or `acqdemo-midpoint`).
5. The router led with the due-date warning and inventory; lead with the resume summary when `next_action` exists.
6. Test isolation: headless test sessions started in an empty folder still found and wrote to the real workspace (trigger-check "log a win" runs). Future tests must name a scratch workspace explicitly, and skills should use only the workspace the user names or confirms.

## Retest after the fixes (2026-09-15)
- Resume: a new session on a paused workspace opened directly on the unfinished deep-dive (entry, round 2), read the PRD duties itself with `prd_text.py`, and ended with the recall prompt. It did not send the user to `acqdemo-harvest`.
- Workspace scope: "log a win" in a folder with no `profile.md` now asks for the workspace path and writes nothing.

## Bug found during the retest
The log skill treated the plugin's own folder as the workspace because that folder contained a `profile.md` (the toolkit repository doubles as the maintainer's workspace, and the test loaded the plugin from it). It blanked the real ledger, which git restored. Fixed: the router, annual, and log skills never use their own skill folder or the plugin folder above it as a workspace, and they wait for the user's answer before writing. Tests that load the plugin from a directory must use a copy holding only `.claude-plugin/` and `skills/`.

## Harness notes
- Headless multi-turn: pass the prompt as the positional argument after `-p` (stdin input breaks `--resume`), and use a fresh folder per run because Claude's per-folder memory can carry answers between runs.
