# Trigger Check (Test E)

Date: 2026-09-15. Plugin loaded with `claude -p --plugin-dir <repo>` in an empty folder, one headless session per prompt, only the `Skill` tool allowed. Loading it from the repository was a mistake that cost two workspace cleanups; rerun these with `python tools/probe/run_probe.py "<prompt>"`, which sandboxes the plugin and hashes the repository around the run. The first `Skill` tool call in the `stream-json` event stream decides the result; the harness stops reading at that call because a loaded skill keeps working afterward. Each run uses a fresh folder so Claude's per-folder memory cannot carry over between runs.

| # | Prompt | Expected | Result |
|---|---|---|---|
| 1 | Where am I in the AcqDemo cycle? | acqdemo | PASS |
| 2 | Help me with my CCAS self-assessment | acqdemo | PASS |
| 3 | Let's do my annual self-assessment | acqdemo:annual or acqdemo | PASS (acqdemo:annual) |
| 4 | Pull what I did this year from git and my calendar | acqdemo:extract | PASS |
| 5 | Check my C-R-I draft before I paste it into CAS2Net | acqdemo:review | PASS |
| 6 | Review these statements for repeats from last year | acqdemo:review | PASS |
| 7 | Write a Python function to parse dates | none | PASS |
| 8a | Log a win: I briefed the new tool to 40 analysts today | acqdemo:log | 4 of 7 runs (others saved a general Claude memory) |
| 8b | Log a win for my AcqDemo self-assessment: I briefed the new tool to 40 analysts today | acqdemo:log | PASS (4 of 4) |
| 9 | Midpoint time, help me write it | acqdemo:midpoint or acqdemo | PASS (acqdemo:midpoint) |
| 10 | Write my contribution plan from my PRD | acqdemo:plan or acqdemo | PASS (acqdemo:plan) |
| 11 | Check my closeout draft before I send it to my supervisor | acqdemo:review | PASS |

## Open item
- Prompt 8a, the plain "Log a win: ..." wording from the Task 22 list, is still unreliable (4 of 7 runs) in a folder with no AcqDemo context because Claude's general memory feature competes for it. Workaround until a better fix: include "AcqDemo" in the request or run `/acqdemo:log`.

## Rechecked at 0.2.1 (2026-09-15)
Reran every prompt against the released skills with the plugin loaded from a copy holding only `.claude-plugin/` and `skills/`. All pass except two, both collisions with other software on the tester's machine rather than skill defects:
- Prompt 4 ("Pull what I did this year from git and my calendar") lands on an unrelated locally installed skill about half the time, apparently on the word "pull". Naming AcqDemo fixes it: "Pull what I did this year from git and my calendar for my AcqDemo self-assessment" and "Gather my AcqDemo evidence from git and my calendar" both hit `acqdemo:extract` in about 4 seconds.
- Prompt 8 stays as recorded below.
Where a prompt competes with other installed skills, saying "AcqDemo" or invoking the skill directly (`/acqdemo:extract`) always works.

## Rechecked after the skill rename (0.3.0)
Skills are now `acqdemo:start`, `acqdemo:annual`, `acqdemo:midpoint`, `acqdemo:plan`, `acqdemo:log`, `acqdemo:extract`, and `acqdemo:review`. All eleven prompts were rerun against the renamed skills.
- Renaming the router from `acqdemo` to `start` cost it the name match, and "where am I in the cycle" briefly landed on `acqdemo:plan`. Fixed by naming the general cases in the router's description and telling the reader to prefer it whenever the user has not named a specific task.
- "Help me with my CCAS self-assessment" lands on `acqdemo:annual`, which is accepted: that skill's first step sends a user with no workspace into the router's first-time setup.
- Everything else passes as recorded below.

## Fixes made during the check
- `acqdemo:midpoint` description narrowed to drafting, pointing checks of existing drafts to `acqdemo:review` (prompt 11 guards this).
- `acqdemo:log` description now says "AcqDemo self-assessment evidence" and "instead of saving a general memory". A bare "log a win" in a folder with no AcqDemo context stays ambiguous with Claude's memory feature, so the README tells users to say "AcqDemo" or run `/acqdemo:log`.
- Harness: an early version waited for each session to finish and timed out on prompt 4 even though `acqdemo:extract` had loaded in 7 seconds; the harness now streams events and stops at the first `Skill` call.
