# AcqDemo Toolkit Wave 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship an installable Claude Code plugin with the `acqdemo:start` router, `acqdemo:extract`, `acqdemo:annual`, and `acqdemo:review` skills, their shared references, and three tested scripts (`check.py`, `git_harvest.py`, `calendar_harvest.py`), validated on fictional personas and a real private backtest.

**Architecture:** The repository root is the plugin root (`.claude-plugin/plugin.json` + `marketplace.json`). Skills live in `skills/<name>/SKILL.md`; shared references and templates live under `skills/start/` and are referenced by other skills through `../start/...` paths. Deterministic rules are Python scripts with pytest suites; judgment rules live in skill instructions. All work happens in the private workspace and is mirrored to the public repo with `tools/sync/sync_public.py` at the end of each phase.

**Tech Stack:** Claude Code plugins and skills (Markdown with YAML frontmatter), Python 3.11+ standard library, pytest, git, GitHub CLI (`gh`, optional for harvesting GitHub repos), pdftotext (descriptor verification).

**Spec:** `docs/superpowers/specs/2026-09-15-acqdemo-skill-design.md`

---

## Phases

| Phase | File | Tasks | Produces |
|---|---|---|---|
| 1 | [phase-1-scaffold-and-references.md](2026-09-15-acqdemo-wave1/phase-1-scaffold-and-references.md) | 1-7 | Plugin manifests, structure tests, shared references (levels, descriptors, rules, certification templates, question bank, writing style, ledger format), templates |
| 2 | [phase-2-check-script.md](2026-09-15-acqdemo-wave1/phase-2-check-script.md) | 8-11 | `skills/review/scripts/check.py` with full tests |
| 3 | [phase-3-harvest-scripts.md](2026-09-15-acqdemo-wave1/phase-3-harvest-scripts.md) | 12-15 | `git_harvest.py` and `calendar_harvest.py` with full tests |
| 4 | [phase-4-skills.md](2026-09-15-acqdemo-wave1/phase-4-skills.md) | 16-20 | Four `SKILL.md` files, local plugin install |
| 5 | [phase-5-validation-and-release.md](2026-09-15-acqdemo-wave1/phase-5-validation-and-release.md) | 21-26 | Personas (test D), trigger check (E), known-problem review (B), backtest (C), dry run (F), README install section, release sync |

Execute phases in order. Tasks inside a phase are ordered; each ends in a commit.

---

## File map (what each new file is responsible for)

```
.claude-plugin/
  plugin.json                          plugin identity (name acqdemo, version, description)
  marketplace.json                     single-plugin marketplace pointing at "./"
pytest.ini                             MODIFY: testpaths add skills and tests
tests/
  test_plugin_structure.py             manifests valid; every SKILL.md has frontmatter name == folder;
                                       every relative path a SKILL.md mentions exists
  test_references.py                   levels, rules, templates contain required anchors
  test_descriptors.py                  descriptor files structurally complete and faithful to the PDF
skills/
  acqdemo/
    SKILL.md                           router: workspace discovery, first-time setup, stage detection, resume, routing
    references/
      levels.md                        score ranges, Very High values and EOCS gates per career path
      descriptors/nh.md                full NH descriptors and discriminators, all factors and levels
      descriptors/nj.md                same for NJ
      descriptors/nk.md                same for NK
      rules/ccas-core.md               program rules summary, each marked common or pay-pool-specific
      cert-templates.md                acquisition and DoD FM self-certification templates
      question-bank.md                 question types, per-discriminator questions, drill-down ladder,
                                       recall sweeps, estimate protocol
      writing-style.md                     writing rules for paste-ready text
      ledger-format.md                 ledger entry schema, statuses, roster, session-state, profile, paypool fields
    templates/
      profile.md                       blank personal profile
      paypool.md                       blank pay pool overlay
      roster.md                        blank people roster table
      session-state.md                 blank session state
      working-doc.md                   annual working doc skeleton with crib sheet
  acqdemo-review/
    SKILL.md                           runs check.py with profile/overlay flags, judgment checks, fix loop
    scripts/check.py                   deterministic draft checks (CLI + importable functions)
    scripts/tests/test_check.py
  acqdemo-harvest/
    SKILL.md                           runs both harvest scripts, clusters results into candidate ledger entries
    scripts/git_harvest.py             git/GitHub activity for a period -> Markdown summary
    scripts/calendar_harvest.py        calendar list export (Subject, Start) -> monthly meetings + recurring series
    scripts/tests/test_git_harvest.py
    scripts/tests/test_calendar_harvest.py
  acqdemo-annual/
    SKILL.md                           annual workflow steps 0-8
```

## Conventions for every task

- Run commands from the repository root of the **private workspace**.
- Run tests with `python -m pytest` (quiet mode is configured).
- Commit with the PII hook active (`git config --get core.hooksPath` prints `tools/hooks`). Never use `--no-verify`.
- Commit message trailer: `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`.
- New files are general unless the task says personal. A personal file's path must be added to `tools/sync/personal-paths.txt` in the same commit.
- Public text must not contain any term in `tools/sync/denylist.txt`. Fictional examples use invented names and programs.
- If git fails inside a Bash tool wrapper on Windows, run git and gh through PowerShell.

## Phase-end sync (repeat at the end of every phase)

- [ ] **Dry run:** `python tools/sync/sync_public.py --dst "<public clone>" --dry-run`
  Expected: `sync: DRY RUN: ...` with no `ABORTED` line. If it aborts, fix the listed files in the private workspace and rerun.
- [ ] **Sync:** `python tools/sync/sync_public.py --dst "<public clone>"`
- [ ] **Test public clone:** in the public clone, `python -m pytest`. Expected: all pass.
- [ ] **Commit and push public:** in the public clone, `git add -A`, `git commit -m "<phase summary>"`, `git push`.
- [ ] **Push private:** in the private workspace, `git push`.

---

## Self-review record

Spec coverage (spec section -> task):
- 3.1 plugin layout -> Tasks 1, 16-19 (templates moved under `skills/start/templates/` so every skill reaches them through the same `../start/` prefix; spec 3.1 listed root `templates/`)
- 3.2 skills (Wave 1 subset) -> Tasks 16-19
- 3.3 personal workspace layout -> Task 7 (templates), Task 19 (router first-time setup)
- 3.4 data contracts -> Task 7 (`ledger-format.md`, templates)
- 4.1-4.5 recipe -> Task 5 (`question-bank.md`, including calendar export), Tasks 14-15 (calendar harvest), Task 18 (annual skill)
- 5 annual workflow -> Task 18
- 6 writing rules -> Task 6 (`writing-style.md`), Tasks 8-11 (mechanical checks)
- 7 outputs -> Task 7 (`working-doc.md`), Task 18 (finalize)
- 8 review skill -> Tasks 8-11, 16
- 9 calendar -> Task 7 (`paypool.md`), Task 19 (stage detection)
- 10 privacy -> existing `tools/`; Task 19 (setup guidance); conventions above
- 11 testing A-F -> Tasks 8-15 (A), 23 (B), 24 (C), 21 (D), 22 (E), 25 (F)
- 12 build phases -> Wave 1 only; Wave 2 (`acqdemo:capture`, `acqdemo:midpoint`, `acqdemo:plan`) gets its own plan
- 13 open questions -> Task 20 verifies plugin path resolution; character counting stays conservative (Task 9)

Deviations from spec, recorded:
1. Templates live in `skills/start/templates/` instead of root `templates/`.
2. Cross-factor repeat check uses 8-word runs (prior-cycle check keeps 6) to avoid false positives on shared organization names; both accept an allow-phrase list.
