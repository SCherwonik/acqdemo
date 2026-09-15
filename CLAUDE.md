# CLAUDE.md

Guidance for Claude Code sessions in this repository.

## What this repo is
An AcqDemo evaluation toolkit: a design and recipe for writing contribution plans, midpoint and annual self-assessments, a planned Claude Code plugin (router skill plus harvest, log, annual, midpoint, plan, and review skills sharing one evidence ledger), and tooling that keeps personal information out of git. Read `README.md` first, then the design spec in `docs/superpowers/specs/`.

## Two repositories, one source of truth
- Work happens in a **private workspace**. The **public repo** is a generated mirror: identical files minus personal paths (`tools/sync/personal-paths.txt`) and personal blocks inside shared files.
- Never edit the public clone by hand. Change the private workspace, then run `python tools/sync/sync_public.py --dst <public clone> --dry-run`, then without `--dry-run`, then commit and push in the public clone.
- Personal blocks: a line containing only an HTML-comment or `#`-comment START marker, the personal text, and a line containing only the matching END marker (see README Section 12.1 for exact syntax). Markers inside fenced code blocks are ignored.
- When adding a general file, write it generically so it needs no personal blocks. When adding a personal file, add its path to `tools/sync/personal-paths.txt` in the same change.

## Never commit (enforced by `.gitignore` and `tools/hooks/scan_pii.py`)
- Personnel forms (SF-50, SF-52), appraisal PDFs, resumes, `Important, Current Documents/`, `**/Actual Appraisal/`.
- Anything containing an SSN, a date of birth, or a PII/CUI banner.
- Do not bypass the hook with `--no-verify`. If it blocks, remove the file from the commit.
- Every clone needs `git config core.hooksPath tools/hooks`.

## Conventions
- Python 3.11+, standard library only for tools; tests with `python -m pytest` (config in `pytest.ini`, tests under `tools/*/tests/`).
- Test-first for tool changes. Tests must build sensitive-looking values at runtime (for example `"123" + "-45-" + "6789"`) so test files never trip the PII hook.
- Paste-ready assessment text is plain text: `C:` `R:` `I:` labels, no em dashes, no Markdown, at most 3,900 characters per factor.
- Final assessment text never contains people's names; names live only in private notes.
- Rules differ by pay pool and year. Local rules belong in a pay pool overlay, not in skill code.
- Design specs go in `docs/superpowers/specs/`, implementation plans in `docs/superpowers/plans/`. Check there before non-trivial work.

