# Phase 5: Validation and Release (Tasks 21-26)

Back to [plan index](../2026-09-15-acqdemo-wave1.md).

Scripts are covered by unit tests (test A). This phase validates the **skills**: fictional personas (D), triggers (E), known problems in real prior submissions (B), a backtest against a real appraisal (C), and a live dry run with a session reset (F). It ends with the install documentation and the release sync.

Validation records go in `docs/superpowers/validation/` (general, mirrored). Anything built from real personal documents goes in `tests/backtest-*/` or the private workspace's `FY<yy>/` folders, which `tools/sync/personal-paths.txt` keeps private.

---

### Task 21: Fictional personas and example regression test (test D)

**Files:**
- Create: `skills/acqdemo/references/examples/nj3-engineer/profile.md`
- Create: `skills/acqdemo/references/examples/nj3-engineer/ramble.md`
- Create: `skills/acqdemo/references/examples/nk2-admin/profile.md`
- Create: `skills/acqdemo/references/examples/nk2-admin/ramble.md`
- Create: `skills/acqdemo/references/examples/nh2-supervisor/profile.md`
- Create: `skills/acqdemo/references/examples/nh2-supervisor/ramble.md`
- Create: `skills/acqdemo/references/examples/<persona>/final/` (three factor files each, produced in Step 4)
- Create: `skills/acqdemo/references/examples/<persona>/flags.txt`
- Create: `tests/test_examples.py`
- Create: `docs/superpowers/validation/personas.md`

Every name, organization, program, and number in the personas is invented.

- [ ] **Step 1: Write the regression test for example outputs**

Create `tests/test_examples.py`:

```python
"""Committed persona outputs keep passing the draft checker."""
import shlex
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "skills" / "acqdemo" / "references" / "examples"
CHECK = ROOT / "skills" / "acqdemo-review" / "scripts" / "check.py"
PERSONAS = sorted(p for p in EXAMPLES.iterdir() if (p / "final").is_dir()) if EXAMPLES.exists() else []

def test_three_personas_exist():
    assert {p.name for p in PERSONAS} == {"nj3-engineer", "nk2-admin", "nh2-supervisor"}

@pytest.mark.parametrize("persona", PERSONAS, ids=lambda p: p.name)
def test_example_passes_checker(persona):
    flags = shlex.split((persona / "flags.txt").read_text(encoding="utf-8").strip())
    res = subprocess.run([sys.executable, str(CHECK), "--dir", str(persona / "final"), *flags,
                          "--roster", str(persona / "roster.md")],
                         capture_output=True, text=True)
    assert res.returncode == 0, res.stdout
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest tests/test_examples.py`
Expected: FAIL in `test_three_personas_exist` (no examples yet).

- [ ] **Step 3: Create the persona inputs**

Create `skills/acqdemo/references/examples/nj3-engineer/profile.md`:

```markdown
# Profile
- name_for_notes: Riley Tran (fictional)
- career_path: NJ
- level: III
- target_level: IV
- series_and_title: 0802 Engineering Technician
- organization: Test Instrumentation Branch, Example Test Wing (fictional)
- rating_period: 2025-10-01 to 2026-09-30
- eocs: 58
- supervises: no
- certifications:
  - type: acquisition
    certification: ENG (Practitioner)
    status: met
    cert_date: 12 Mar 2025
    points_earned: 42
    points_required: 40
    cycle_end: 30 Sep 2026

## Mission statements
- one_level_up: Deliver accurate, on-time flight test data for aircraft programs.
- two_levels_up: Provide developmental test capabilities that keep weapon systems on schedule.
```

Create `skills/acqdemo/references/examples/nj3-engineer/ramble.md`:

```markdown
So this year the big thing was the telemetry calibration rig. The old process took two technicians about three days per aircraft and I built a fixture plus a script that cut it to one day. We ran it on 11 aircraft for the Example Trainer program. I also found that two of the old reference sensors were drifting, which would have thrown off load data, and we swapped them before the March test window.
I trained four technicians on the new rig, two from our branch and two from the range support contractor, Example Range Services. Wrote the procedure, 14 pages, and the branch chief signed it as the standard.
Supported the June surge when three test points got pulled forward two weeks. Worked weekends twice to get the instrumentation installed.
Presented the rig at the quarterly test community meeting, about 40 people, including the wing technical director.
```

Create `skills/acqdemo/references/examples/nk2-admin/profile.md`:

```markdown
# Profile
- name_for_notes: Casey Morgan (fictional)
- career_path: NK
- level: II
- target_level: III
- series_and_title: 0303 Program Support Assistant
- organization: Directorate Front Office, Example Logistics Center (fictional)
- rating_period: 2025-10-01 to 2026-09-30
- eocs: 40
- supervises: no
- certifications: none

## Mission statements
- one_level_up: Keep directorate leadership informed and on schedule.
- two_levels_up: Sustain logistics readiness for field units.
```

Create `skills/acqdemo/references/examples/nk2-admin/ramble.md`:

```markdown
I run the director's calendar and the suspense tracker. This year I moved the tracker from a shared spreadsheet to a SharePoint list with automatic reminders. Overdue taskers went from around 25 a month to about 6.
I coordinated the spring leadership offsite for 60 people, three days, handled the venue request, travel orders for 18 people, and the agenda book.
I trained the three new admin assistants in the division offices on the tracker and on travel orders.
When the building move happened in August I made the seating plan for 140 people and kept the phone list updated every day for two weeks.
```

Create `skills/acqdemo/references/examples/nh2-supervisor/profile.md`:

```markdown
# Profile
- name_for_notes: Jordan Avery (fictional)
- career_path: NH
- level: II
- target_level: III
- series_and_title: 1102 Contract Specialist (Team Lead)
- organization: Services Contracting Section, Example Contracting Squadron (fictional)
- rating_period: 2025-10-01 to 2026-09-30
- eocs: 60
- supervises: 0 military, 4 civilians, 1 contractors
- certifications:
  - type: dod-fm
    certification: DoD FM Level 1
    status: active-cycle
    points_earned: 30
    points_required: 40
    points_remaining: 10
    cycle_end: 30 Sep 2026

## Mission statements
- one_level_up: Award and administer mission support contracts that meet customer needs on time.
- two_levels_up: Deliver acquisition solutions that sustain installation operations.
```

Create `skills/acqdemo/references/examples/nh2-supervisor/ramble.md`:

```markdown
I lead a team of four contract specialists plus one contractor who does closeouts. We awarded 23 service contracts worth about $41M this year, including the base custodial recompete that was at risk of a gap.
On the custodial one the incumbent protested and I worked with legal to answer the protest in 9 days instead of the usual 30. No gap in service.
I set up a weekly pipeline review so the customer squadrons see status every Monday; late requirements packages dropped from 12 to 4 over the year.
I mentored two of my specialists through their Level II certification and both finished.
I briefed the mission support group commander twice on the contract pipeline.
```

Create a roster for each persona. These fictional names must never appear in that persona's factor files; the regression test passes the roster to the checker to prove it.

`skills/acqdemo/references/examples/nj3-engineer/roster.md`:

```markdown
# Roster

| Ring | Name | Organization | Role | Worked on | Frequency | Ledger |
|---|---|---|---|---|---|---|
| own office: instrumentation | Morgan Pike | Test Instrumentation Branch | technician | trained on calibration rig | 3 sessions | |
| contractor: Example Range Services | Taylor Brandt | Example Range Services | range technician | trained on calibration rig | 3 sessions | |
| leadership | Dana Whitcomb | Example Test Wing | technical director | quarterly test community briefing | once | |
```

`skills/acqdemo/references/examples/nk2-admin/roster.md`:

```markdown
# Roster

| Ring | Name | Organization | Role | Worked on | Frequency | Ledger |
|---|---|---|---|---|---|---|
| own office: front office | Jesse Okafor | Directorate Front Office | director | calendar and suspense tracker | daily | |
| other division | Robin Castellano | Maintenance Division | admin assistant | tracker and travel order training | 2 sessions | |
```

`skills/acqdemo/references/examples/nh2-supervisor/roster.md`:

```markdown
# Roster

| Ring | Name | Organization | Role | Worked on | Frequency | Ledger |
|---|---|---|---|---|---|---|
| own office: services contracting | Alex Brennan | Services Contracting Section | contract specialist | Level II certification mentoring | monthly | |
| own office: services contracting | Sydney Marsh | Services Contracting Section | contract specialist | Level II certification mentoring | monthly | |
| leadership | Chris Delgado | Mission Support Group | commander | contract pipeline briefings | 2 briefings | |
```

Create `skills/acqdemo/references/examples/nj3-engineer/flags.txt` with `--mode annual --acq-cert`, `skills/acqdemo/references/examples/nk2-admin/flags.txt` with `--mode annual`, and `skills/acqdemo/references/examples/nh2-supervisor/flags.txt` with `--mode annual --fm-cert --supervisor`.

- [ ] **Step 4: Run each persona through the annual skill**

For each persona, in a fresh Claude Code session with the plugin installed (Task 20):
1. Copy the persona folder to a scratch workspace outside the repo and copy `skills/acqdemo/templates/paypool.md` into it unchanged.
2. Say: "Let's do my annual. My workspace is <scratch path>."
3. Answer the brain dump with the persona's `ramble.md` text. Answer later questions only from the ramble; say "I don't know" for anything else; approve reasonable estimates.
4. Continue to Step 8 (finalize).

Acceptance for each persona:
- The skill used the correct descriptor file (`nj`, `nk`, or `nh`) and target level.
- NH-II persona: JA opens with "I supervise 0 military, 4 civilians, and manage 1 contractors." followed by a supervisory paragraph. NJ-III persona: MS opens with an acquisition statement. NH-II persona: MS opens with a DoD FM "active cycle" statement.
- At least three C-R-I per factor; no fictional person names in the factor files; every number traces to the ramble or an approved estimate recorded in the ledger.
- `check.py` with the persona's flags reports 0 CRITICAL.

Copy each scratch workspace's `FY26/final/` three factor files into `skills/acqdemo/references/examples/<persona>/final/`.

- [ ] **Step 5: Run the regression test**

Run: `python -m pytest tests/test_examples.py`
Expected: 4 passed.

- [ ] **Step 6: Record results and commit**

Create `docs/superpowers/validation/personas.md` with a table of persona, descriptor file used, target level, C-R-I per factor, CRITICAL/WARNING counts, and any skill instruction changes made to reach acceptance (with the reason for each).

```bash
git add skills/acqdemo/references/examples tests/test_examples.py docs/superpowers/validation/personas.md
git commit -m "test: add fictional persona examples and checker regression test"
```

---

### Task 22: Trigger check (test E)

**Files:**
- Create: `docs/superpowers/validation/triggers.md`
- Modify (only if a trigger fails): the `description` line of the affected `SKILL.md`

- [ ] **Step 1: Run the prompts**

In a fresh Claude Code session with the plugin installed, send each prompt in its own new session and note which skill loads first:

| # | Prompt | Expected skill |
|---|---|---|
| 1 | "Where am I in the AcqDemo cycle?" | acqdemo |
| 2 | "Help me with my CCAS self-assessment" | acqdemo |
| 3 | "Let's do my annual self-assessment" | acqdemo-annual (or acqdemo, which routes to it) |
| 4 | "Pull what I did this year from git and my calendar" | acqdemo-harvest |
| 5 | "Check my C-R-I draft before I paste it into CAS2Net" | acqdemo-review |
| 6 | "Review these statements for repeats from last year" | acqdemo-review |
| 7 | "Write a Python function to parse dates" | none of the AcqDemo skills |

- [ ] **Step 2: Fix and re-run failures**

For each mismatch, edit only that skill's `description` to add the missing trigger words, run `python -m pytest tests/test_plugin_structure.py` (descriptions must still start with "Use when" and stay under 1,024 characters), refresh the install (Task 20 Step 5), and rerun the prompt.

- [ ] **Step 3: Record and commit**

Create `docs/superpowers/validation/triggers.md` with the table above plus an "Actual" column and the date.

```bash
git add docs/superpowers/validation/triggers.md skills/*/SKILL.md
git commit -m "test: record skill trigger check"
```

---

### Task 23: Known problems in real prior submissions (test B)

**Files:**
- Create: `docs/superpowers/validation/known-problems.md` (general summary: finding codes and pass/fail only, no document text)
- Private working files only under `tests/backtest-*/` (kept out of the public mirror)

- [ ] **Step 1: Prepare the inputs**

Use a real prior submission with known problems (your own, in your private workspace). Put employee self-assessment text only (no supervisor narrative, no headers) into three factor files named as the checker expects, in `tests/backtest-known/<cycle>/`.

- [ ] **Step 2: Run the review skill on each folder**

In a Claude Code session: "Review the draft in `tests/backtest-known/<cycle>/` as a <midpoint or annual>. Prior cycles are in <prior folder>." Answer the skill's questions from the real documents.

- [ ] **Step 3: Evaluate**

Pass if every expected finding is reported and the fix loop produces a new version with 0 CRITICAL without inventing facts. For each miss, adjust `skills/acqdemo-review/SKILL.md` (judgment instructions) or, for a countable rule, add a failing unit test to `test_check.py` and fix `check.py`.

- [ ] **Step 4: Record and commit**

Write `docs/superpowers/validation/known-problems.md` with finding codes, pass/fail, and changes made. No document text.

```bash
git add docs/superpowers/validation/known-problems.md skills/acqdemo-review
git commit -m "test: validate review skill against known problems in prior submissions"
```

---

### Task 24: Backtest against a real appraisal (test C)

**Files:**
- Private only: `tests/backtest-fy25/inputs/`, `tests/backtest-fy25/workspace/`, `tests/backtest-fy25/scorecard.md`
- Create: `docs/superpowers/validation/backtest.md` (general summary: scores only)

- [ ] **Step 1: Prepare a prior-cycle workspace**

In `tests/backtest-fy25/inputs/`, place only what the employee had before writing that cycle's annual: the contribution plan, the midpoint and closeout self-assessment text, any question-and-answer notes. In `tests/backtest-fy25/workspace/`, create `profile.md` and `paypool.md` for that cycle (career path, level, EOCS, rating period).

- [ ] **Step 2: Create the simulated employee**

Write `tests/backtest-fy25/simulated-employee.md`: instructions for a subagent that plays the employee. It may read the inputs and the supervisor's annual narrative for that cycle as hidden memory. It answers only the question asked, briefly, in a rambling voice; says "I don't know" when the hidden memory lacks the answer; and never volunteers a fact that was not asked about.

- [ ] **Step 3: Run the annual skill against the simulated employee**

Dispatch one subagent running the `acqdemo-annual` skill in `tests/backtest-fy25/workspace/` and relay each question to a second subagent following `simulated-employee.md`. Continue to Step 8 (finalize).

- [ ] **Step 4: Score**

Fill `tests/backtest-fy25/scorecard.md`:

| Metric | Pass bar | Result |
|---|---|---|
| CRITICAL findings in final text | 0 | |
| Supervisor-added facts surfaced by questions | at least two-thirds | |
| Numbers per C-R-I vs. the original self-assessment | higher | |
| Characters per factor | at most 3,900 | |
| Blind side-by-side preference by the employee | new wins at least 2 of 3 factors | |

- [ ] **Step 5: Improve and record**

For each failed metric, change the question bank or the annual skill, rerun Steps 3-4 once, and note the change. Write `docs/superpowers/validation/backtest.md` with scores only (no document text).

```bash
git add docs/superpowers/validation/backtest.md skills/acqdemo skills/acqdemo-annual
git commit -m "test: backtest annual skill against a prior-cycle appraisal"
```

---

### Task 25: Dry run with a session reset (test F)

**Files:**
- Private only: the real workspace's `FY<yy>/` folder
- Create: `docs/superpowers/validation/dry-run.md`

- [ ] **Step 1: Start a real session on one project**

In the real private workspace: "Let's do my annual, but only one project for a dry run." Complete Steps 0-2 (load, gate, harvest), then start a deep-dive on one project.

- [ ] **Step 2: Interrupt mid-deep-dive**

After answering two question rounds, close the Claude Code window.

- [ ] **Step 3: Resume in a new session**

Open a new session in the workspace and say: "Where am I in the AcqDemo cycle?"
Expected: the router reports the annual stage, finds `FY<yy>/session-state.md`, summarizes the unfinished deep-dive, and offers to resume from `next_action`. The ledger entry contains everything answered before the interruption.

- [ ] **Step 4: Finish the project and record**

Complete the deep-dive to `status: ready`. Write `docs/superpowers/validation/dry-run.md` with pass/fail for: resume offered, no lost answers, questions numbered, "What else does that bring to mind?" asked each round, estimates proposed with a basis, names kept out of factor text.

```bash
git add docs/superpowers/validation/dry-run.md
git commit -m "test: record dry run with session reset"
```

---

### Task 26: Install documentation and release

**Files:**
- Modify: `README.md` (Section 1 status table; Section 10.5 install instructions)
- Modify: `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` only if the version changes

- [ ] **Step 1: Update the status table in README Section 1**

Change the rows for "Implementation plan for Wave 1" and "Wave 1 skills" to `Done`, and add a row: `| Validation records (docs/superpowers/validation/) | Done |`.

- [ ] **Step 2: Replace README Section 10.5 with install instructions**

Replace the body of "### 10.5 Install the skills (once Wave 1 ships)" and rename the heading to "### 10.5 Install the skills":

```markdown
### 10.5 Install the skills

From a terminal with Claude Code installed:

    claude plugin marketplace add SCherwonik/acqdemo
    claude plugin install acqdemo@acqdemo

Restart Claude Code, open your private workspace folder, and say: "Where am I in the AcqDemo cycle?"

To update later:

    claude plugin marketplace update acqdemo
    claude plugin update acqdemo@acqdemo

Maintainers testing local changes can add the repository folder instead: `claude plugin marketplace add "<path to your clone>"`.
```

If Task 20 Step 4 was needed (shared paths did not resolve for plugin installs), add the personal-skills copy command from that step as the recommended install and note why.

- [ ] **Step 3: Run the full suite**

Run: `python -m pytest`
Expected: all pass.

- [ ] **Step 4: Commit in the private workspace**

```bash
git add README.md .claude-plugin
git commit -m "docs: add install instructions and mark Wave 1 complete"
git push
```

- [ ] **Step 5: Sync, tag, and push the public release**

Run the phase-end sync (plan index). Then in the public clone:
```
claude plugin tag . --dry-run
claude plugin tag . --push
```
Expected: tag `acqdemo--v0.1.0` created and pushed to the public repository.

- [ ] **Step 6: Verify a clean public install**

On a machine or user profile without the local marketplace: run the two install commands from README Section 10.5 and repeat Task 20 Step 3.
Expected: all three checks pass.
