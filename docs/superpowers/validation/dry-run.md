# Dry Run (Test F)

Status: **done.** Two runs cover it. An agent-driven run proved the session reset path on 2026-09-15, and a real user then wrote a complete annual self-assessment with the toolkit on 2026-09-15 into 2026-09-16, ending in paste-ready text.

## Run 1: session reset, agent answering from project files
Plugin loaded from the repository, a scratch copy of a private workspace, one project.
- Session 1: "Let's do my annual, but only one project for a dry run." Gate unknowns parked, deep-dive round 1 asked and answered.
- Session 2, a brand new session in the same folder: "Where am I in the AcqDemo cycle?"

| Check | Result |
|---|---|
| Session state written before questions | FAIL, then PASS after the fix below |
| Router reports the cycle stage | PASS |
| Router finds session state and summarizes the unfinished deep-dive | PASS, reported step, entry, round, open fields |
| Resume offered | PASS |
| No lost answers | PASS, round 1 answers were already in the ledger |
| Questions numbered | PASS |
| Recall prompt each round | PARTIAL, present in round 1, missing from a later round |

The first attempt asked eight questions and saved nothing, so a closed window would have restarted at the gate. Fixed with a "save before you ask" rule and a richer session-state template (current entry, round, pending questions). Retested and passed.

## Run 2: a real user, real workspace, whole cycle
An NH-IV employee wrote the FY26 annual end to end in one working session: intake, evidence extraction from four repositories and a 344 meeting calendar export, five rounds of deep-dive questions answered by voice, allocation across the three factors, five drafts, both review layers, and a final package.

| Check | Result |
|---|---|
| Estimates proposed with a basis | PASS, every hedged number recorded as an estimate with its wording preserved |
| Names kept out of factor text | PASS, names live only in the roster and the ledger |
| Minimum entries per factor | PASS, five per factor against a minimum of three |
| Character budget respected | PASS, 3,419 to 3,542 against a 3,900 cap |
| Deterministic checker clean at the end | PASS, 0 CRITICAL and 0 WARNING |
| Judgment review applied | PASS, two passes, evidence audit and panel read, both acted on |
| Prior-cycle repeats avoided | PASS, the checker plus a manual comparison against the prior annual and the midpoint |
| Finalize step completed | FAIL, see below |

Output: three paste-ready factor files, a working doc with an evidence table for every claim, a bench, a descriptor map, and a separate supervisor brief.

## What the real run exposed, and what changed
1. **Documents were never requested up front.** A returning user goes straight into questions without being told to pull the prior cycle's salary appraisal, this cycle's midpoint and plan, and a calendar export. The annual and midpoint skills now open with that list in plain language, with the reason for each, before any gate question.
2. **Retrieval was undocumented.** Users had no idea which CAS2Net menus produce those files. Added a retrieval reference with the exact path, which form sections to include, and which to leave unchecked.
3. **Evidence discipline broke under conversation pressure.** Several answers given by voice were drafted straight into text without being written to the ledger first, and a later review flagged them as unsourced. The fix is procedural: answers reach the ledger before they reach a draft, and the skill says so.
4. **The finalize step did not run.** Every entry stayed `candidate` after the text was final, so a later cycle would not know what had already been claimed. Entries that reach the submitted text must be marked `submitted` with their factors recorded, which the annual's finalize step already specifies and which was skipped in practice.
5. **Voice transcription mangles domain terms.** Program names, acronyms, and people's names arrived garbled and differently each time. Added a rule to match unfamiliar words against the user's own documents, correct silently, say the term back once, never guess a name, and keep a glossary at the end of each saved ramble.
6. **Allocation needed the user's judgment.** The panel read and the user disagreed about ordering inside Mission Support. The skill proposes an order and the user decides; that stayed a proposal, not a rule.

## Harness notes
- Headless multi-turn: pass the prompt as the positional argument after `-p`, since stdin input breaks `--resume`, and use a fresh folder per run because per-folder memory can carry answers between runs.
- When testing a repository copy of the plugin, disable the installed release for that session, or both copies load and results reflect whichever descriptions the session preferred.
- Do not point `--plugin-dir` at a folder that also contains a workspace `profile.md`. A skill found that profile and wrote to it; skills now refuse their own plugin folder as a workspace.
- All three notes above are now enforced by `tools/probe/run_probe.py`, which is the only sanctioned way to run a headless probe. It copies `.claude-plugin/` and `skills/` to a temp sandbox, refuses to start if that sandbox or the working directory sits inside the repository, disables the installed release, and hashes the repository before and after the run. A probe that writes anything into the workspace now ends with a `TRIPWIRE` listing and a non-zero exit instead of going unnoticed until a later `git status`. It also covers the parts of `.git` a commit moves, so a probe that runs `git add -A && git commit` is caught even though every worktree file is byte-identical, along with empty folders left behind, new checkouts under `.worktrees/`, and permission changes. The tripwire compares paths, permission bits, and hashes; it never deletes and never judges what a file is for.
