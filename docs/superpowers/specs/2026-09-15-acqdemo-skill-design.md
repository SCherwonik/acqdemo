# AcqDemo Evaluation Skill Suite: Design

- **Date:** 2026-09-15
- **Status:** Draft for review
- **Audience:** Maintainers of this repo; any AcqDemo employee (NH, NJ, NK) who wants help writing contribution plans, midpoint and annual self-assessments.

---

## 1. Goal and scope

### 1.1 Problem
Writing an AcqDemo self-assessment is mostly a **recall** problem, not a writing problem. A year of work is too much to remember unaided, the details that win points at pay pool panels (numbers, audiences, scope, decisions fed) are rarely written down, and existing paste-in prompts ask one round of questions and stop.

### 1.2 Goal
A Claude Code **plugin** containing a primary skill plus smaller single-purpose skills that together:
1. Harvest evidence (git history, prior documents) and pull memories out of free-form voice rambles.
2. Ask as many targeted questions as it takes, including structured memory sweeps (timeline, people, artifacts).
3. Keep a year-round **evidence ledger** that every skill reads and writes.
4. Draft CAS2Net-ready C-R-I statements per factor, calibrated to the employee's career path and target broadband level.
5. Check drafts against the program rules and a "panel read" before submission.
6. Hand the supervisor a crib sheet that helps them defend the rating at panel.

### 1.3 Non-goals (this version)
- Writing the supervisor's official narrative (may be added later).
- A copy-paste prompt version for other chat platforms (possible later export).
- Handling classified information. Users must never enter it.

---

## 2. Design principles
1. **Recall first.** Rambling is encouraged; questions keep coming until the ledger is rich.
2. **One contract.** The evidence ledger is the only interface between skills. Any skill can run alone if the ledger holds what it needs.
3. **Max framing, true events.** Push scope, level and impact language hard. Estimated numbers are allowed with a recorded basis. Events, audiences and awards are never invented.
4. **Nothing personal in this repo.** Personal data lives in a separate private workspace (Section 10).
5. **Rules as data.** Pay-pool-specific dates and rules live in a per-user overlay file, not in skill code.
6. **Deterministic where possible.** Countable rules (character limits, statement counts, repeated text) are checked by a script, not by model judgment.

---

## 3. Architecture

### 3.1 Plugin layout (this public repo)
```
skills/
  start/                   primary: detects cycle stage + available inputs, routes
    references/            shared by all skills
      descriptors/nh.md    full transcription of factor descriptors + discriminators
      descriptors/nj.md
      descriptors/nk.md
      levels.md            score ranges per career path/level, Very High gates
      rules/ccas-core.md   rules common to all pay pools (verify vs. Operating Guide)
      question-bank.md
      writing-style.md         writing rules (Section 6)
      ledger-format.md     data contracts (Section 3.4)
      cert-templates.md    acquisition + DoD FM self-certification templates
      examples/            fully fictional personas only
  harvest/         git + document mining -> candidate ledger entries
  log/             capture one accomplishment any time -> ledger entry
  annual/          intake + drafting for the annual self-assessment
  midpoint/        same engine, midpoint minimums and framing
  plan/            contribution plan with labeled objectives (JA1, CT1, MS1)
  review/          compliance + panel-read check on any draft
    scripts/check.py       deterministic checks (Section 8.1)
templates/
  profile.md               blank personal profile
  paypool.md               blank pay pool overlay
docs/
```
Shared references live under the primary skill. Other skills reference them by relative path; the implementation plan must verify path resolution for installed plugins and fall back to duplicating small files if needed.

### 3.2 Skills

| Skill | Purpose | Reads | Writes | Standalone use |
|---|---|---|---|---|
| `acqdemo:start` | Detect stage (date vs. calendar in overlay), inventory inputs, resume sessions, route | profile, paypool, session-state, ledger | session-state | "Where am I in the cycle?" |
| `acqdemo:harvest` | Mine git repos, calendar exports, and prior documents for the rating period | profile (repo list), `FY<yy>/evidence/` calendar exports, prior-cycle submissions | ledger (`candidate` entries), harvest snapshots | "Pull what I did from git and my calendar" |
| `acqdemo:log` | Capture a single win from a ramble | ledger | ledger | "Log a win" |
| `acqdemo:annual` | Gate, dump, recall sweeps, deep-dives, allocate, draft, finalize | all | ledger, roster, drafts, final outputs | "Let's do my annual" |
| `acqdemo:midpoint` | Same flow, minimum 1 C-R-I per factor, no scores | all | same | "Midpoint time" |
| `acqdemo:plan` | Contribution plan from PRD duties + expected work, labeled objectives, KPIs | profile, PRD, prior plan | plan draft | "Write my plan" |
| `acqdemo:review` | Script checks + judgment checks, fix loop | any draft, prior-cycle text, current midpoint, roster, ledger | findings, fixed draft | "Check my draft" |

### 3.3 Personal workspace layout (NOT in this repo)
```
<private workspace>/
  profile.md              career path, level, target level, EOCS, value of position, PRD path,
                          certs, supervisors, office map, repos to mine, mission statements
  paypool.md              pay pool overlay: deadlines, lead-ins, cert statement order, local rules
  roster.md               people helped, by ring (names allowed here only)
  FY<yy>/
    ledger.md
    session-state.md
    rambles/              raw dictation, dated
    evidence/             calendar exports and other raw evidence files
    harvest/
    drafts/
    final/                Job Achievement and Innovation.txt
                          Communication and Teamwork.txt
                          Mission Support.txt
                          FY<yy> working doc.md
  prior/                  previous cycles' submitted text (for no-repeat checks)
```

### 3.4 Data contracts

**Ledger entry** (`ledger.md`, one Markdown section per entry):
```
## L-042 <short title>
- status: candidate | ready | allocated | submitted | rejected
- dates: 2026-03 to 2026-07
- project: <name>
- what: <plain facts>
- role: owned | co-owned | owned-a-piece | supported
- audience: <who, highest rank, headcount, internal/external>
- numbers:
  - <value> | source: stated | git | estimate | basis: <one line>
- decision_fed: <POM, FYDP, acquisition strategy, none>
- obstacle: <shutdown, deadline, bad data, none>
- sustained: yes | one-time
- lenses:
  - JA: <angle>
  - CT: <angle>
  - MS: <angle>
- descriptor_hits: <factor/level lines matched>
- prd_duty: <duty number(s)>
- plan_tag: <JA1, CT2, ... or none>
- evidence: <repo@commit, file, email subject>
- prior_cycle_overlap: none | continuing (cycle delta: <what is new>)
```

**session-state.md:** current step, next action, open questions, last updated.

**roster.md:** ring (own office section, other divisions, external government, contractors, leadership), name, organization, role, what was done together, frequency, linked ledger ids.

---

## 4. The recipe

### 4.1 Inputs (tiers)
| Tier | Items |
|---|---|
| 0: gate | Career path and level on the last day of the cycle; EOCS; rating period; current contribution plan text; certification status (acquisition level + CLPs, DoD FM level + CETs, dates); supervisor(s) of record; closeouts; promotions or position changes with effective dates |
| 1: evidence | Git harvest; calendar export (Subject and Start columns, tab-separated, from a list view); current-cycle midpoint; briefings (audience, highest rank, headcount); training and mentoring counts; programs and dollar values; decisions fed; recognition (awards, time off awards, praise) |
| 2: framing | Mission statements (one and two levels up); organizational priorities; value of position; PRD duties |

Unknown Tier 0 items do not block drafting; they are flagged in the working doc.

### 4.2 Question bank
- Organized by the **discriminators** of each factor, because panels read the descriptors side by side with the text:
  - JA: Leadership Role, Mentoring/Employee Development, Accountability, Complexity/Difficulty, Creativity, Scope/Impact
  - CT: Oral, Written, Contribution to Team, Effectiveness
  - MS: Independence, Customer Needs, Planning/Budgeting, Execution/Efficiency
- Question types: scope, audience, role, before/after, obstacle, decision fed, significance (first time, one of a kind, interagency, short deadline, competing priorities), sustained vs. one-time.
- **Drill-down ladder** on every answer: what > so what > who used it > what changed > will it keep happening.
- Questions are **numbered** so voice answers can reference them ("number four: ...").
- No fixed cap. After every round: "What else does that bring to mind?"

### 4.3 Recall sweeps
0. **Calendar export first:** the user exports calendar Subject and Start columns to a text file (classic desktop Outlook: Calendar > View > Change View > List; filter or sort by Start; keep Subject and Start; select all in range; copy; paste into a text editor; save as `.txt`). The harvest filters to the rating period, skips canceled meetings, lists meetings by month, and counts recurring series.
1. **Timeline walk:** month by month through the cycle, seeded with known anchors (calendar meetings, git releases, midpoint, awards, promotions, shutdowns, budget milestones).
2. **People rings:** (1) own office, section by section from a saved office map, (2) other divisions, (3) government outside the organization, (4) contractor companies and their people, (5) leadership briefed or advised. Ask for names explicitly.
3. **Artifact prompts:** calendar meeting titles, sent mail, chat threads, slide decks, shared drive.

**Names rule:** names are encouraged in conversation and in local `roster.md`, ledger and working doc. Final paste-ready text never contains names; convert to title, organization and counts. Roster counts become hard numbers ("mentored 9 analysts across 3 divisions").

### 4.4 Answer strategy
1. **Extract** facts from rambles into ledger entries, source-tagged.
2. **"I don't know" ladder:** git/files > proxy count (versions, users, sessions) > estimate the user approves (recorded basis, phrased "over" or "approximately") > scope and audience framing.
3. **Rank** entries: scope x organizational level x novelty. Biggest first.
4. **Allocate** each entry to its strongest factor; a secondary factor gets a different angle. No sentence reused.
5. **Write** per Section 6.
6. **Arm the supervisor** via the crib sheet (Section 7).

### 4.5 Next-cycle capture
- Monthly 5-minute ramble (`acqdemo:log`), plus after any briefing, release or praise email.
- Brag folder: praise emails, slide titles, attendance counts, award notices.
- Contribution plan with labeled objectives (JA1-3, CT1-3, MS1-3); tag every ledger entry.
- KPIs chosen at plan time (for example: people trained, tool users, senior-leader briefings, estimates supported and dollar value, defects found, hours saved per cycle).
- Midpoint written per factor independently (avoid duplicate factor text).
- Git: tag releases at milestones; note audience or customer in release notes.

---

## 5. Annual session workflow

| # | Step | Skill | Output | Checkpoint |
|---|---|---|---|---|
| 0 | Load profile, overlay, session-state; detect stage; resume | acqdemo | stage + input inventory | |
| 1 | Gate: Tier 0 questions (never blocks on unknowns) | annual | profile updates | |
| 2 | Harvest: git + prior documents for the period | harvest | candidate entries | user confirms, rejects or merges |
| 3 | Brain dump | annual | inventory with JA/CT/MS coverage grid | user corrects inventory |
| 3b | Recall sweeps (Section 4.3) | annual | new entries, roster | |
| 4 | Deep-dives per project, biggest first; entries saved to disk after each | annual | `ready` entries | user approves estimates |
| 5 | Allocate top 3-4 per factor, distinct angles, no prior-cycle overlap | annual | allocation table | user approves allocation |
| 6 | Draft | annual | drafts/vN | |
| 7 | Review + auto-fix loop | review | findings, diff | user edits by voice |
| 8 | Finalize | annual | final outputs, ledger `submitted` | |

- **Stop rule for deep-dives:** each factor has at least 4 `ready` entries (3 plus a spare), or the user says enough.
- **Resume:** session-state records step, next action and open questions; any new session continues from it.

---

## 6. Writing rules

### 6.1 Format
- Labels `C:` `R:` `I:` (Contribution-Result-Impact, the current method; older guidance calls it W-R-I with `W:`, accepted when the pay pool overlay sets `what_label: W`). Contribution = 1 sentence, at most 35 words. Result and Impact = 1-2 sentences each and carry the detail.
- Budget: at most 3,900 characters per factor (CAS2Net field is about 4,000), counting each line break as 2. Typically 3-4 C-R-I.
- Order: greatest impact first.
- Mandatory non-C-R-I paragraphs (do not count toward the minimum), in the order the pay pool overlay specifies:
  - Supervisors: personnel counts ("I supervise X military, Y civilians, and manage Z contractors.") + supervisory objective paragraph, first under JA.
  - Acquisition-coded positions: self-certification statement, first under MS.
  - DoD FM certification-coded positions: self-certification + CET status, typically second under MS.
- Plain text only: straight quotes, no em dashes, no bullets, no Markdown.

### 6.2 Embellishment policy
| Allowed | Never |
|---|---|
| Strongest verb the recorded role supports | Invented events, audiences, awards or recognition |
| Stacked scope (dollar value, portfolio, organization level) | Ownership verbs for efforts the user did not own |
| Descriptor language for the target level | Names in final text |
| Impact that climbs at least two rungs: team > division > agency > HQ staff > service > DoD/Congress | |
| Estimated numbers: top of plausible range, rounding up, favorable framing (percent vs. absolute, cumulative vs. per cycle) with a recorded one-line basis | |

### 6.3 Role verbs
| Recorded role | Verbs |
|---|---|
| owned | led, directed, spearheaded, architected |
| co-owned | co-led, partnered with <role> to |
| owned-a-piece | drove, built, delivered <the piece> for |
| supported | rewrite as the specific piece delivered |

Technique: shrink the noun, keep the verb strong ("Directed the subsystem reconciliation for the X estimate" instead of "Supported the X estimate").

### 6.4 Vocabulary
- Target phrases come from the descriptors file for the **target level** in the profile, not hardcoded lists.
- Banned: seamlessly, friction-free, perfectly, unbroken, synergy, cutting-edge, world-class. "Robust" and "leverage" at most once per factor.
- Adjective test: if a number or a noun can replace an adjective, replace it.

### 6.5 Same project, different angle per factor
JA = what was built or solved and why it was hard or new. CT = who was briefed, trained or aligned, and what they adopted. MS = customer need met, resources saved, schedule or budget effect.

### 6.6 CRI vs. CA framing
Sustained contributions ("institutionalized", "now standard each cycle") support a salary increase (CRI); one-time "big rocks" support an award (CA). Each allocated entry is tagged in the working doc.

### 6.7 Repeat rule
- **Current-cycle midpoint is the starting point:** reuse, expand and upgrade freely.
- **Prior cycles are off limits:** neither the wording nor the same claimed contribution. Continuing projects claim only what is new this cycle.

### 6.8 Special situations (rules vary by pay pool; values come from the overlay)
- **Promotion inside a late-cycle window** (for example, a local rule that promotions within N days of cycle end default to EOCS unless substantial justification is provided): the package argues continuity of higher-level contribution before and after the promotion; the crib sheet includes a "substantial justification" paragraph.
- **Position or supervisor change:** closeout assessments exist and feed the annual; the supervisor of record on the last day rates.
- **Minimum time on an approved plan** before cycle end: router warns when the window is at risk.
- **Very High scores:** only when the overlay's EOCS gate is met.

---

## 7. Outputs

### 7.1 Paste-ready files
`Job Achievement and Innovation.txt`, `Communication and Teamwork.txt`, `Mission Support.txt`: plain text, C-R-I labeled, character count verified.

### 7.2 Working doc (`FY<yy> working doc.md`)
1. Status and gaps (unknown Tier 0 items, flags)
2. Final text per factor with character counts
3. Evidence table: claim > ledger id > source > basis
4. Bench: unused entries; punchier and safer alternates per statement
5. Descriptor map: descriptor lines hit per statement; discriminators with no coverage
6. **Supervisor and panel crib sheet** (standalone, exportable to .docx):
   - 3 "big rocks" one-liners
   - Hard counts in one list
   - Contributions to add (bench entries; supervisors are expected to add omitted contributions)
   - Suggested "Exceeding expected contributions" rationale per factor in descriptor language
   - Substantial-justification paragraph when a special situation requires it
   - Reminder to state concurrence with certification statements
   - CRI/CA tags
   - Reminder to document the midpoint discussion date and method
7. Next-cycle seeds: KPIs, plan objective ideas, capture reminders

---

## 8. Review skill

### 8.1 Layer 1: `scripts/check.py` (deterministic)
| Severity | Check |
|---|---|
| CRITICAL | Every entry has W, R and I |
| CRITICAL | Minimum C-R-I per factor (annual 3, midpoint 1; overlay may change); mandatory paragraphs excluded from count |
| CRITICAL | Mandatory certification and supervisory paragraphs present and in overlay order |
| CRITICAL | Characters per factor at most 4,000 (WARNING above 3,900) |
| CRITICAL | Prior-cycle wording: any run of 6+ identical words |
| CRITICAL | Identical wording across factors |
| CRITICAL | Any roster name in final text |
| WARNING | Banned words, em dashes, smart quotes, Markdown characters |
| WARNING | Contribution longer than 35 words |

### 8.2 Layer 2: judgment
| Severity | Check |
|---|---|
| CRITICAL | Same achievement as a prior cycle without a current-cycle delta |
| WARNING | Number without a basis in the ledger |
| WARNING | Verb stronger than the ledger role |
| WARNING | Impact climbs fewer than 2 rungs or lacks a mission tie |
| WARNING | Reads below target level (no descriptor hits) |
| WARNING | Not ordered by impact |
| INFO | Passive voice; discriminator gaps; CRI/CA balance; missing plan tags |

### 8.3 Loop
Findings (CRITICAL first) > "Fix all?" > apply > show diff > re-run script until 0 CRITICAL.

---

## 9. Cycle calendar (overlay-driven)
Defaults below are examples; each pay pool's overlay sets real dates.

| When | What | Skill |
|---|---|---|
| Cycle start (1 Oct) | New cycle | acqdemo |
| Within 30 days | Contribution plan approved | acqdemo:plan |
| Monthly | 5-minute capture | acqdemo:log |
| Mar/Apr | Midpoint | acqdemo:midpoint |
| ~90 days before cycle end | Plan-change lock and eligibility cutoff warning | acqdemo |
| Mid to late Aug | Harvest + recall sweeps (prep, no writing) | acqdemo:harvest |
| Early Sep | Deep-dives | acqdemo:annual |
| About 1 week before due | Allocate, draft, review | acqdemo:annual, acqdemo:review |
| **3 days before due** | Submit (buffer) | |
| Employee due date (example: 15 Sep) | Self-assessment to supervisor | |
| Supervisor due date (example: 30 Sep) | Supervisor narrative; crib sheet delivered by the employee due date | |
| Oct-Nov | Pay pool panels | |
| Jan | Results; reconsideration window follows | |

---

## 10. Security, privacy and development model
- **Public repo (this one):** method only. No real names, programs, dollar values, performance text, or pay pool documents that name officials. Examples are fully fictional.
- **Private workspace:** profile, overlay, ledger, roster, rambles, drafts, submitted text.
  - Git-ignored and pre-commit-blocked even in the private workspace: SF-50/SF-52, appraisal forms, resumes, and any document containing SSNs, dates of birth, or PII/CUI banners.
  - The pre-commit scanner extracts text from txt, pdf, docx, pptx and xlsx before checking.
- **Development model:** maintainers may develop in a private workspace and port changes here with generalized language. Every port runs the PII scanner plus a denylist scan (names from the roster, program names and organization-specific terms from the maintainer's profile) before commit.
- Never enter classified information in any session.

---

## 11. Testing
| # | Test | Proves |
|---|---|---|
| A | `pytest` unit tests for `check.py`, each fixture with one planted defect | Every countable rule is enforced |
| B | Review skill on real prior submissions with known issues (maintainer-local, not committed) | Judgment layer catches real problems |
| C | **Backtest:** prior-cycle inputs only, compared with the actual appraisal | Level calibration and quality are measurable |
| D | Fictional personas (NJ-III engineer, NK-II administrative, NH-II supervisor) | Descriptor selection, supervisory paragraph, minimums; these become public examples |
| E | Trigger check ("let's do my annual", "log a win", "check my draft", "where am I in the cycle") | Correct skill activates |
| F | Dry run on one real project, including closing and reopening a session | Intake and resume work |

**Backtest scorecard:** 0 CRITICAL; at least two-thirds of the facts the supervisor added (that the employee omitted) are surfaced by the question loop; more numbers per statement than the original; at most 3,900 characters per factor; blind side-by-side preference in at least 2 of 3 factors. Backtest drafts are stored where harvest never reads them.

**Acceptance bar for real use:** 0 CRITICAL; at most 3,900 characters per factor; at least 3 C-R-I per factor plus 2 bench entries; every number has a basis; special-situation paragraphs present when triggered; user sign-off.

---

## 12. Build phases
1. **Wave 1:** shared references (full descriptor transcription for NH, NJ, NK; levels; core rules; question bank; style; ledger format; cert templates), `acqdemo:start`, `acqdemo:harvest`, `acqdemo:annual`, `acqdemo:review` + `check.py`. Tests A and B during build; C, D and E after; F before first real use.
2. **Wave 2:** `acqdemo:log`, `acqdemo:midpoint`, `acqdemo:plan`, each with its own tests.

---

## 13. Assumptions and open questions
1. **CAS2Net character counting** is unverified; counting line breaks as 2 characters and capping at 3,900 is the safe assumption.
2. **Plugin shared-reference paths** must be verified during planning (relative paths vs. duplication).
3. **Rules drift yearly and by pay pool.** `ccas-core.md` holds only rules common to all pay pools and must be verified against the DoD AcqDemo Operating Guide; everything local goes in the overlay and should be refreshed from each year's business rules.
4. **Categorical score ceiling:** interpreted as bounded by the employee's broadband level (per guidance that categorical scores be consistent with broadband level). Verify per pay pool.
5. **Employee vs. supervisor due dates** differ from some published guidance; the overlay is the source of truth, set by the user.
