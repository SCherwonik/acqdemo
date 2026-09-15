# AcqDemo Evaluation Toolkit

A recipe, a set of Claude Code skills, and supporting tools that help a Department of Defense AcqDemo employee capture a year of contributions and turn them into strong, compliant contribution plans, midpoint assessments, and annual self-assessments.

You talk (voice-to-text rambling is encouraged). The assistant asks a lot of questions, reminds you of work you forgot, keeps a running evidence ledger, and writes paste-ready C-R-I statements for each of the three AcqDemo factors, plus a crib sheet your supervisor can use at the pay pool panel.

---

## Table of contents

1. [Project status](#1-project-status)
2. [Why this exists](#2-why-this-exists)
3. [Who this is for](#3-who-this-is-for)
4. [AcqDemo in ten minutes](#4-acqdemo-in-ten-minutes)
5. [How the toolkit works](#5-how-the-toolkit-works)
6. [The recipe](#6-the-recipe)
7. [Writing rules](#7-writing-rules)
8. [Yearly calendar](#8-yearly-calendar)
9. [Repository layout](#9-repository-layout)
10. [Getting started](#10-getting-started)
11. [Privacy and safety](#11-privacy-and-safety)
12. [Private workspace and public mirror](#12-private-workspace-and-public-mirror)
13. [Testing](#13-testing)
14. [Reference documents included](#14-reference-documents-included)
15. [Glossary](#15-glossary)
16. [FAQ](#16-faq)
17. [Disclaimer](#17-disclaimer)

---

## 1. Project status

| Piece | Status |
|---|---|
| Design spec (`docs/superpowers/specs/2026-09-15-acqdemo-skill-design.md`) | Done |
| PII pre-commit guard (`tools/hooks/`) with tests | Done |
| Private-to-public mirror tool (`tools/sync/`) with tests | Done |
| Reference documents (descriptors, CCAS guidance, business rules, training deck) | Included |
| Implementation plan for Wave 1 | Done |
| **Wave 1 skills:** `acqdemo` (router), `acqdemo-harvest`, `acqdemo-annual`, `acqdemo-review` + shared references | Done |
| Validation records (`docs/superpowers/validation/`): personas, trigger tests, backtest, dry run | Planned |
| **Wave 2 skills:** `acqdemo-log`, `acqdemo-midpoint`, `acqdemo-plan` | Planned |

Wave 1 skills are installable as a Claude Code plugin (Section 10.5). Wave 2 skills and the validation records come next. The repo is also useful on its own as a reference (the design, the recipe, the rules summaries, and the source documents) and as a template for keeping your own evaluation workspace safe in git.

---

## 2. Why this exists

Writing an AcqDemo self-assessment is mostly a **recall** problem, not a writing problem.

- A year of work is too much to remember in September.
- The details that win points at the pay pool panel are rarely written down: dollar values, who was in the room, how many people used your work, what decision it fed, what it replaced.
- Paste-in prompts ask one round of questions and stop. If you did not remember it before the prompt, it does not make it into the assessment.

Copy-paste prompt tools for C-R-I statements work, but they stop too early. This toolkit keeps what works in that approach (strict C-R-I format, no invented facts, CAS2Net-ready plain text) and adds:

- **Conversation instead of a form.** Ramble by voice; the assistant extracts the facts.
- **Unlimited, deeper questions.** Numbered so you can answer by voice ("number four: ...").
- **Memory sweeps.** A month-by-month timeline walk and a people sweep through your office, other divisions, outside government organizations, and contractors, by name.
- **Evidence harvesting.** Git commit history and prior documents become candidate accomplishments with dates and counts.
- **A year-round evidence ledger** so next year starts with notes instead of a blank page.
- **Calibration to the level above you** using the full factor descriptors for NH, NJ, and NK.
- **A supervisor crib sheet** so your supervisor can defend the rating in the panel room.
- **Automated checks** for character limits, statement counts, repeated text from prior years, and names in the final text.

---

## 3. Who this is for

- **Employees** in any AcqDemo career path (NH, NJ, NK) who write contribution plans, midpoint assessments, closeouts, and annual self-assessments in CAS2Net.
- **Supervisors** who want a clearer picture of an employee's year (the crib sheet), although this toolkit does not write the official supervisor narrative.
- **Anyone maintaining their own evaluation notes in git** who wants guardrails that keep personal information out of public repositories.

You do not need to be technical to use the skills once they ship: you install them once and then talk. Setting up the repository tooling (Section 10) requires basic comfort with a terminal.

---

## 4. AcqDemo in ten minutes

> Rules differ by pay pool and change every year. Everything below is a summary to orient you. Your pay pool's current business rules and guidance always win. This repo includes one pay pool's 2025 business rules and 2026 guidance as examples (Section 14).

### 4.1 The cycle
| Event | Typical timing | What happens |
|---|---|---|
| **Contribution plan** | Within 30 days of cycle start (1 Oct), a new position, or a new supervisor | You and your supervisor agree on expected contributions per factor, based on your Position Requirements Document (PRD) |
| **Midpoint review** | March/April | You write at least one C-R-I per factor; supervisor writes an assessment without scores and meets with you |
| **Closeout** | Within 30 days of a change of supervisor or position | You and the departing supervisor document contributions so far; no scores |
| **Annual self-assessment** | Due to your supervisor before the supervisor deadline (example pay pool: employee 15 Sep, supervisor 30 Sep) | You write at least three C-R-I per factor |
| **Pay pool panels** | October to November | Supervisors and senior leaders review every narrative side by side and calibrate scores |
| **Results** | January | Pay changes effective the first full pay period; a reconsideration window follows |

### 4.2 The three factors
| Factor | What it captures | Discriminators panels look for |
|---|---|---|
| **Job Achievement and/or Innovation (JA)** | Qualifications, critical thinking, problem solving, leadership, accountability | Leadership Role, Mentoring/Employee Development, Accountability, Complexity/Difficulty, Creativity, Scope/Impact |
| **Communication and/or Teamwork (CT)** | Verbal and written communication, interactions with customers, coworkers, and groups, cross-functional work | Oral, Written, Contribution to Team, Effectiveness |
| **Mission Support (MS)** | Understanding and executing organizational goals, working with customers, monitoring cost, setting priorities | Independence, Customer Needs, Planning/Budgeting, Execution/Efficiency |

### 4.3 Career paths, levels, and score ranges
| Career path | Level I | Level II | Level III | Level IV | Very High |
|---|---|---|---|---|---|
| **NH** Business Management and Technical Management | 0-29 | 22-66 | 61-83 | 79-100 | 105, 110, 115 |
| **NJ** Technical Management Support | 0-29 | 22-51 | 43-66 | 61-83 | 87, 91, 95 |
| **NK** Administrative Support | 0-29 | 22-46 | 38-61 | n/a | 64, 67, 70 |

Descriptors are written to the **high end** of each level and are read **as a whole**, not as a checklist. Very High scores are available only to employees in the top level of their career path with an expected score at the top of that level (for NH, an EOCS of 96-100 in the example business rules).

### 4.4 C-R-I (Contribution-Result-Impact)
Every self-assessment entry uses this structure. Entries are labeled `C:`, `R:`, `I:`. Older program guidance and business rules (including the example documents in this repo) call the same structure W-R-I, What-Result-Impact; the content is identical and only the first label differs.
- **Contribution:** what you did this cycle.
- **Result:** the immediate outcome or deliverable (quality, quantity, cost, timeliness).
- **Impact:** why it mattered to the mission, as broadly as you can honestly climb.

Apply the "so what?" test to every entry.

### 4.5 The scores that decide pay
| Term | Meaning |
|---|---|
| **EOCS** (Expected Overall Contribution Score) | The score your current salary implies. The pay pool's pay line converts base pay into an expected score. Higher pay means a higher expected score. |
| **OCS** (Overall Contribution Score) | Your actual score after the panel. |
| **Delta** | OCS minus EOCS. Positive deltas drive raises and awards and must be justified in the narratives. |
| **Value of Position** | The target (ceiling) expected score for the job itself. |
| **PAQL** (Performance Appraisal Quality Level) | A separate 1-5 quality rating per factor. A 1 in any factor makes the rating of record Unacceptable. |
| **GPI / CRI / CA** | General pay increase / contribution rating increase (raise to base pay) / contribution award (one-time bonus). Time off can be requested in lieu of part of an award. |

**Salary increase vs. bonus event:** panels consider whether a contribution will continue at that level (supports a raise) or was a one-time "big rock" (supports an award). Write accordingly.

### 4.6 Rules that trip people up
- **Minimum three C-R-I per factor** at the annual; at least one per factor at the midpoint.
- **No copying** from prior years' assessments, and no identical C-R-I across factors. Duplicates may lower scores.
- **Mandatory objectives** go first and do not count toward the minimum:
  - Supervisors state personnel counts ("I supervise X military, Y civilians, and manage Z contractors.") and describe how the supervisory objective was met, in paragraph form, first under JA.
  - Acquisition-coded positions give a certification self-statement first under MS.
  - DoD FM certification-coded positions give a certification and CET status statement, typically second under MS.
- **Approved plan for 90 consecutive days** before the cycle ends to be eligible for a payout.
- **Late-cycle promotions:** in the example business rules, employees promoted within 150 days of the cycle end receive their EOCS unless substantial justification is provided.
- **Supervisor narratives** must open with one of four lead-ins: Meeting, Exceeding, Partially meeting, or Not meeting expected contributions.
- **CAS2Net fields** hold about 4,000 characters per factor and time out after about 15 minutes without saving.

---

## 5. How the toolkit works

### 5.1 Skills (a Claude Code plugin)
| Skill | What you say | What it does |
|---|---|---|
| `acqdemo` (primary) | "Where am I in the cycle?" | Reads your profile and pay pool calendar, lists what inputs exist, resumes an unfinished session, and routes to the right skill |
| `acqdemo-harvest` | "Pull what I did from git and my calendar" | Mines your git repos, calendar export, and prior documents for the rating period and creates candidate ledger entries |
| `acqdemo-log` | "Log a win" | Turns a quick ramble into one ledger entry any time during the year |
| `acqdemo-annual` | "Let's do my annual" | Runs the full annual intake and drafting workflow (Section 5.3) |
| `acqdemo-midpoint` | "Midpoint time" | Same engine with midpoint minimums and framing |
| `acqdemo-plan` | "Write my plan" | Drafts a contribution plan from your PRD duties with labeled objectives (JA1, CT1, MS1) and KPIs |
| `acqdemo-review` | "Check my draft" | Runs deterministic checks plus a panel-style read, then offers to fix what it finds |

Each smaller skill runs on its own when you only have part of the inputs.

### 5.2 The evidence ledger
Every skill reads and writes one file per cycle, `ledger.md`. Each entry records what you did, your role (owned, co-owned, owned a piece, supported), the audience and highest rank involved, numbers with their source (stated, git, or estimate with a one-line basis), the decision it fed, whether it is sustained or one-time, a separate angle for each factor, matching descriptor lines, PRD duty, plan objective tag, and evidence pointers. The ledger is what lets the skills work independently and what makes next year easier.

### 5.3 The annual workflow
| Step | What happens | You do |
|---|---|---|
| 0. Load | Reads profile, pay pool overlay, session state; detects cycle stage; resumes | Nothing |
| 1. Gate | Asks the must-know items: level, EOCS, plan, certifications, closeouts, promotions | Answer or say "unknown" |
| 2. Harvest | Git history, calendar export (Section 6.4), and prior documents for the period | Confirm, reject, or merge candidates |
| 3. Brain dump | You ramble the whole year; you get an inventory and a JA/CT/MS coverage grid | Ramble, fix the inventory |
| 3b. Recall sweeps | Timeline walk; people sweep by ring; artifact prompts | Name names, answer |
| 4. Deep-dives | Project by project, biggest first; numbered questions; estimates proposed; each entry saved immediately | Ramble, answer, approve estimates |
| 5. Allocate | Picks the top 3-4 entries per factor with distinct angles and no prior-year overlap | Approve or swap |
| 6. Draft | Writes C-R-I statements and mandatory paragraphs | Read |
| 7. Review | Automated checks plus a panel read; fixes and shows the diff | Edit by voice |
| 8. Finalize | Writes the paste-ready files and working doc; marks entries submitted | Paste into CAS2Net |

Deep-dives continue until each factor has at least four ready entries (three plus a spare) or you say "enough."

### 5.4 Outputs
- `Job Achievement and Innovation.txt`, `Communication and Teamwork.txt`, `Mission Support.txt`: plain text, C-R-I labeled, character counts verified, ready to paste.
- `FY<yy> working doc.md`: status and gaps, final text with counts, evidence table (every claim with its source and basis), bench of unused entries and alternate phrasings, descriptor coverage map, next-cycle seeds, and the **supervisor and panel crib sheet**:
  - three "big rock" one-liners
  - hard counts in one list
  - contributions the supervisor can add (supervisors are expected to add what the employee omitted)
  - an "Exceeding expected contributions" rationale per factor in descriptor language
  - a substantial-justification paragraph when a special situation (such as a late-cycle promotion) applies
  - reminders to concur with certification statements and to document the midpoint discussion
  - raise vs. award tags

---

## 6. The recipe

### 6.1 What you need (in tiers)
| Tier | Items | If missing |
|---|---|---|
| **0: gate** | Career path and level on the last day of the cycle; EOCS; rating period; contribution plan text; certification status and dates; supervisor(s) of record; closeouts; promotions or position changes with dates | Drafting continues; the gap is flagged |
| **1: evidence** | Git history; current midpoint; briefings (audience, highest rank, headcount); training and mentoring counts; program names and dollar values; decisions fed; recognition | Recall sweeps and questions fill it |
| **2: framing** | Mission statements one and two levels up; organizational priorities; value of position; PRD duties | Impact statements stay more generic |

### 6.2 Questions that get asked
Questions map to each factor's discriminators and come in types:
- **Scope:** dollar value, number of programs, users, analysts.
- **Audience:** highest rank in the room, headcount, inside or outside the organization.
- **Role:** who asked, whether you owned it, who worked with you.
- **Before and after:** how it was done before and how long it took.
- **Obstacle:** shutdowns, deadlines, bad data, broken legacy models.
- **Decision:** budget, program, or acquisition decisions it fed.
- **Significance:** first time, one of a kind, interagency, short deadline, competing priorities.
- **Sustained or one-time:** decides raise vs. award framing.

Every answer gets a drill-down ladder: **what > so what > who used it > what changed > will it keep happening?** After every round: "What else does that bring to mind?"

### 6.3 Recall sweeps
1. **Timeline walk:** month by month, seeded with known anchors (releases, midpoint, awards, promotions, shutdowns, budget milestones).
2. **People sweep, in rings:** your own office section by section (from an office map you draw once and reuse), other divisions, government organizations outside yours, contractor companies and their people, and leadership you briefed or advised. Names are asked for explicitly because they anchor memories.
3. **Artifact prompts:** calendar meeting titles, sent mail, chat threads, slide decks, shared drives.

**Names rule:** names are welcome in conversation and in your private notes. The final paste-ready text never contains names; they become titles, organizations, and counts ("mentored 9 analysts across 3 divisions").

### 6.4 Export your calendar first (strongly recommended)

Your calendar is the best memory aid you have. Every briefing, working group, training session, and customer meeting is already there, with a date. Export it before the annual (and again before the midpoint). The toolkit turns it into a month-by-month timeline for the recall sweep and counts recurring meetings, which become hard numbers ("led 32 working group sessions").

**Classic desktop Outlook (Windows):**

| Step | Action | Instructions |
|---|---|---|
| 1 | Change the calendar view | Open **Calendar** in desktop Outlook. On the **View** tab of the ribbon, click **Change View**, then choose **List**. |
| 2 | Filter or sort by date | Click the **Start** column header to sort chronologically, or use **View Settings > Filter** to set start and end dates covering your rating period. |
| 3 | Trim columns (optional) | Right-click any column header and choose **Remove This Column** for fields you do not need. Keep **Subject** and **Start**; the dates are what place each meeting on the timeline. |
| 4 | Copy the entries | Click the first meeting in your range, hold **Shift**, click the last meeting, and press **Ctrl + C**. |
| 5 | Save as a text file | Open Notepad (or another text editor), press **Ctrl + V**, and save as a `.txt` file in your private workspace, for example `FY26/evidence/calendar-2026-09-01.txt`. |

The saved file has a header line, then one meeting per line: the subject, a tab, and the start date and time. Fictional example:

```
Subject	Start	
Estimating working group	Tue 10/14/2025 10:00 AM	
Canceled: Branch staff meeting	Mon 12/8/2025 11:00 AM	
Regression tool demo for program office	Thu 3/12/2026 1:30 PM	
```

Tips:
- Export a little wider than the rating period. The harvest keeps only meetings inside the period.
- Leave canceled meetings in; lines starting with "Canceled:" are skipped automatically.
- Order does not matter; the harvest sorts by date.
- The newer Outlook app and Outlook on the web may not offer the List view. If yours does not, use classic desktop Outlook, or any calendar that can produce "Subject, tab, Start" lines.
- **Privacy:** calendar exports contain coworker names, program names, and meeting details. Keep them in your private workspace only. Never export from a classified system, and delete any line whose title is sensitive before saving.

### 6.5 Turning answers into statements
1. Extract facts into ledger entries with sources.
2. When you do not know a number: check git or files, then a proxy count, then an estimate you approve (with a recorded basis, phrased "over" or "approximately"), then fall back to scope and audience.
3. Rank entries by scope, organizational level, and novelty.
4. Allocate each entry to its strongest factor; give other factors a different angle.
5. Write (Section 7) and review.
6. Arm your supervisor with the crib sheet.

### 6.6 What to capture next year
- Export your calendar at the midpoint and again before the annual (Section 6.4).
- A five-minute ramble each month and right after any briefing, release, or praise email.
- A brag folder: praise emails, slide titles, attendance counts, award notices.
- A contribution plan with labeled objectives (JA1-3, CT1-3, MS1-3); tag every ledger entry.
- KPIs chosen at plan time (people trained, tool users, senior-leader briefings, estimates supported and their value, defects found, hours saved).
- A midpoint written separately for each factor.
- Git release tags at milestones with the audience or customer in the release notes.

---

## 7. Writing rules

### 7.1 Format
- Labels `C:`, `R:`, `I:` (set `what_label: W` in `paypool.md` if your pay pool still uses `W:`). The Contribution is one sentence of at most 35 words; the Result and Impact carry the detail.
- At most 3,900 characters per factor (CAS2Net allows about 4,000), counting each line break as two characters. Usually three or four C-R-I.
- Greatest impact first.
- Mandatory paragraphs (supervisory objective, certification statements) in the order your pay pool requires.
- Plain text only: straight quotes, no em dashes, no bullets, no Markdown.

### 7.2 Framing policy
| Allowed and encouraged | Never |
|---|---|
| The strongest verb your actual role supports | Invented events, audiences, awards, or recognition |
| Stacked scope: dollar value, portfolio, organizational level | Ownership verbs for work someone else owned |
| Language from the descriptors of your target level | Names in the final text |
| Impact that climbs at least two rungs (team, division, agency, headquarters, service, DoD or Congress) | |
| Estimated numbers at the top of a plausible range, rounded up, framed favorably, each with a recorded basis | |

### 7.3 Role verbs
| Your role | Verbs |
|---|---|
| Owned | led, directed, spearheaded, architected |
| Co-owned | co-led, partnered with (role) to |
| Owned a piece | drove, built, delivered (the piece) for |
| Supported | describe the specific piece you delivered |

**Shrink the noun, keep the verb strong:** "Directed the subsystem reconciliation for the program estimate" beats "Supported the program estimate."

### 7.4 Words
- Banned: seamlessly, friction-free, perfectly, unbroken, synergy, cutting-edge, world-class. "Robust" and "leverage" at most once per factor.
- If a number or a noun can replace an adjective, replace it.

### 7.5 One project, three angles
- **JA:** what you built or solved and why it was hard or new.
- **CT:** who you briefed, trained, or aligned, and what they adopted.
- **MS:** the customer need met, resources saved, or schedule and budget effect.

### 7.6 Repeats
- Your **current-cycle midpoint is the starting point**: reuse and upgrade it.
- **Prior cycles are off limits**, both the wording and the same claimed achievement. Continuing projects claim only what is new this cycle.

---

## 8. Yearly calendar

Dates come from your pay pool overlay (`paypool.md`); the defaults below match the example pay pool.

| When | What | Skill |
|---|---|---|
| 1 Oct | Cycle starts | `acqdemo` |
| By 30 Oct | Contribution plan approved | `acqdemo-plan` |
| Monthly and after any win | Five-minute capture | `acqdemo-log` |
| Mar/Apr | Midpoint | `acqdemo-midpoint` |
| About 2 Jul | 90-day plan cutoff; plan changes locked | `acqdemo` warns |
| 15-31 Aug | Harvest and recall sweeps (prep, no writing) | `acqdemo-harvest` |
| 1-5 Sep | Deep-dives | `acqdemo-annual` |
| 8-10 Sep | Allocate, draft, review | `acqdemo-annual`, `acqdemo-review` |
| 12 Sep | Submit (three-day buffer) | |
| 15 Sep | Employee self-assessment due | |
| 30 Sep | Supervisor narrative due; hand over the crib sheet by 15 Sep | |
| Oct-Nov | Pay pool panels | |
| Jan | Results; reconsideration window follows | |

---

## 9. Repository layout

```
.
├── README.md                       this file
├── CLAUDE.md                       guidance for Claude Code sessions in this repo
├── pytest.ini                      test configuration
├── .gitignore / .gitattributes     never-commit rules; line endings for hooks
├── docs/
│   └── superpowers/
│       ├── specs/                  design specs
│       └── plans/                  implementation plans
├── tools/
│   ├── hooks/
│   │   ├── pre-commit              runs the PII guard on every commit
│   │   ├── scan_pii.py             blocks SSNs, dates of birth, PII/CUI banners, sensitive file names
│   │   └── tests/
│   └── sync/
│       ├── sync_public.py          mirrors a private workspace into a public repo
│       ├── personal-paths.example.txt
│       ├── denylist.example.txt
│       └── tests/
├── AcqDemo Factor Descriptors and Discriminators.pdf
├── 2026 AcqDemo_CCAS_Assessments_Guidance.pdf
├── 2026 AcqDemo_CCAS_Assessments_Checklist.pdf
├── Acqdemo Business Rules/2025 AcqDemo Business Rules.pdf
├── MidPoint Review - 2023.pptx
└── Important Rules to Consider.txt
```

Planned plugin layout (Wave 1 and 2):
```
skills/
  acqdemo/            primary router + shared references (descriptors, levels, rules,
                      question bank, writing style, ledger format, certification templates)
  acqdemo-harvest/
  acqdemo-log/
  acqdemo-annual/
  acqdemo-midpoint/
  acqdemo-plan/
  acqdemo-review/     includes scripts/check.py
templates/            profile.md, paypool.md
```

---

## 10. Getting started

### 10.1 Prerequisites
| Tool | Why | Check |
|---|---|---|
| [Claude Code](https://claude.com/claude-code) (desktop app or CLI) | Runs the skills | `claude --version` |
| Git | Version control and the PII hook | `git --version` |
| Python 3.11+ | Hook, sync tool, tests | `python --version` |
| pytest | Tests | `python -m pytest --version` |
| pdftotext | Lets the PII guard read PDFs | Included with Git for Windows (`C:\Program Files\Git\mingw64\bin`); on macOS `brew install poppler`; on Linux `apt install poppler-utils` |
| GitHub CLI (optional) | Creating your private repo | `gh --version` |

### 10.2 Use the reference material now
Clone the repo and read the design spec, the recipe (Section 6), and the source documents:
```bash
git clone https://github.com/SCherwonik/acqdemo.git
```

### 10.3 Turn on the PII guard in any clone
The hook is not active until you point git at it. Do this once per clone:
```bash
git config core.hooksPath tools/hooks
```
Then run the tests:
```bash
python -m pytest
```

### 10.4 Set up your own private workspace (recommended)
1. Create a **private** repository for your own notes (for example with `gh repo create <you>/acqdemo-personal --private`).
2. Copy this repo's contents into it and run `git config core.hooksPath tools/hooks`.
3. Copy `tools/sync/personal-paths.example.txt` to `tools/sync/personal-paths.txt` and `tools/sync/denylist.example.txt` to `tools/sync/denylist.txt`; fill in your own paths and terms (name, birth year, contact details, IDs, salary figures, coworker names, program names).
4. Put your own documents in the workspace, including a calendar export (Section 6.4). Keep personnel forms (SF-50, SF-52), appraisal PDFs, and resumes out of git entirely; the `.gitignore` and hook block the common ones. The hook does not detect coworker names, so list personal files in `tools/sync/personal-paths.txt` before syncing anything public.
5. Once the skills ship, add `profile.md` and `paypool.md` from `templates/`.

### 10.5 Install the skills

From a terminal with Claude Code installed:

    claude plugin marketplace add SCherwonik/acqdemo
    claude plugin install acqdemo@acqdemo

Restart Claude Code, open your private workspace folder, and say: "Where am I in the AcqDemo cycle?"

To update later:

    claude plugin marketplace update acqdemo
    claude plugin update acqdemo@acqdemo

Maintainers testing local changes can add the repository folder instead: `claude plugin marketplace add "<path to your clone>"`, or load it for one session with `claude --plugin-dir "<path to your clone>"`.

---

## 11. Privacy and safety

- **Never enter classified information** in any session or file.
- Performance information about a real person should be treated as **CUI** once it is written down. Keep it in a private workspace, not a public repo.
- **Two layers keep sensitive files out of git:**
  1. `.gitignore` excludes personnel forms, appraisal folders, resumes, and Office lock files.
  2. `tools/hooks/scan_pii.py` runs before every commit. It extracts text from `.txt`, `.md`, `.pdf`, `.docx`, `.pptx`, and `.xlsx` files and blocks the commit if it finds an SSN pattern, a date-of-birth label with a date, a PII/CUI banner, or a sensitive file name. It never prints the matched value.
- **Do not bypass the hook** with `--no-verify`. If it blocks a commit, remove the file from the commit.
- **Names rule:** names help recall in private notes but never appear in paste-ready text.
- **Calendar exports** carry names, program names, and meeting details. Keep them private, never export from a classified system, and remove sensitive titles before saving.
- **You are responsible for accuracy.** Every fact and number you submit is signed by you and defended by your supervisor.

---

## 12. Private workspace and public mirror

This project is maintained as two repositories that are **1:1 except for personal content**:

| Repository | Visibility | Contains |
|---|---|---|
| Private workspace | Private | Everything: the toolkit, reference documents, and the maintainer's personal files and personal README sections |
| Public mirror (`SCherwonik/acqdemo`) | Public | The same files minus personal paths and personal sections |

Work happens in the private workspace. The public mirror is regenerated by a script, never edited by hand.

### 12.1 Marking personal content inside shared files
Wrap personal text in a block whose first and last lines contain only a marker. In Markdown use HTML comments; in code or config use `#` comments. The marker words are `PERSONAL:START` and `PERSONAL:END`. A marker that appears in the middle of a sentence (like this one) is ignored.

Markdown:
```
<!-- PERSONAL:START -->
Private status notes.
<!-- PERSONAL:END -->
```

Python, shell, or config:
```
# PERSONAL:START
LOCAL_PATH = "C:/Users/me/private"
# PERSONAL:END
```

### 12.2 Personal paths and the denylist
- `tools/sync/personal-paths.txt`: files and folders that never sync. A trailing `/` means a folder (wildcards allowed, anchored at the repo root); a leading `/` means a file at the repo root only (use it for `/profile.md`, `/paypool.md`, `/roster.md`, whose blank templates under `skills/` must stay public); a pattern containing `/` matches the full path; anything else matches file names in any folder.
- `tools/sync/denylist.txt`: terms that must never appear in a public file, matched as whole words, case-insensitive. A GitHub handle that merely contains a surname does not match.

Both files are always excluded from the mirror. Example versions ship publicly.

### 12.3 Running a sync
From the private workspace root:
```bash
python tools/sync/sync_public.py --dst "<path to public clone>" --dry-run
python tools/sync/sync_public.py --dst "<path to public clone>"
```
Then review, commit, and push inside the public clone (its own PII hook runs on that commit).

What the script guarantees:
- Only files **tracked by git** in the private workspace are candidates, so ignored files never leak.
- Personal paths are skipped; personal blocks are removed.
- Every output file is scanned for denylist terms and PII (including text inside PDFs and Office files). **Any finding aborts before a single file is written.**
- Files in the public clone that are no longer part of the mirror are deleted, keeping the two repositories 1:1.
- It never commits or pushes.

---

## 13. Testing

Run everything from the repo root:
```bash
python -m pytest
```

| Suite | Covers |
|---|---|
| `tools/hooks/tests/test_scan_pii.py` | Clean files pass; SSNs, dates of birth, banners, sensitive names, and SSNs inside `.docx` and `.pdf` block; the scanner does not match its own source |
| `tools/sync/tests/test_sync_public.py` | Marker stripping (including malformed blocks), path exclusion (folders, wildcards, file globs), tracked-files-only mirroring, denylist and PII aborts with nothing written, stale-file deletion, dry run |

Planned skill validation (from the design spec):
- **A.** Unit tests for the deterministic draft checker.
- **B.** The review skill must catch known problems in real prior submissions (run privately).
- **C.** Backtest: prior-year inputs only, compared with the actual appraisal.
- **D.** Fictional personas (NJ-III engineer, NK-II administrative, NH-II supervisor).
- **E.** Trigger checks for each skill.
- **F.** A dry run on one real project, including closing and reopening a session.

---

## 14. Reference documents included

| File | What it is | Notes |
|---|---|---|
| `AcqDemo Factor Descriptors and Discriminators.pdf` | Official factor descriptors and discriminators for NH, NJ, and NK, every level plus Very High | The basis for level calibration |
| `2026 AcqDemo_CCAS_Assessments_Guidance.pdf` | One pay pool's 2026 guidance for employee self-assessments and supervisor narratives, including certification templates and PAQL examples | Verify against your own pay pool |
| `2026 AcqDemo_CCAS_Assessments_Checklist.pdf` | Quick-check list matching the guidance | Useful before submitting |
| `Acqdemo Business Rules/2025 AcqDemo Business Rules.pdf` | One pay pool's signed 2025 business rules: roles, funding, CAS2Net rules, special situations, compensation, timeline | Rules change yearly; get your pay pool's current version |
| `MidPoint Review - 2023.pptx` | Training deck on writing CCAS assessments, C-R-I examples, and significant-accomplishment characteristics | Older but still instructive |
| `Important Rules to Consider.txt` | Short writing tips and a continuous-learning status template | |

---

## 15. Glossary

| Term | Meaning |
|---|---|
| AcqDemo | DoD Civilian Acquisition Workforce Personnel Demonstration Project |
| CAS2Net | The system where plans and assessments are entered |
| CCAS | Contribution-based Compensation and Appraisal System |
| CA | Contribution Award (one-time bonus) |
| CET | Continuing Education and Training (DoD FM certification maintenance) |
| CIP | Contribution Improvement Plan |
| CLP | Continuous Learning Points (acquisition certification maintenance) |
| CRI | Contribution Rating Increase (raise to base pay) |
| CT | Communication and/or Teamwork factor |
| EOCS | Expected Overall Contribution Score |
| GPI | General Pay Increase |
| JA | Job Achievement and/or Innovation factor |
| MS | Mission Support factor |
| OCS | Overall Contribution Score |
| PAQL | Performance Appraisal Quality Level |
| PRD | Position Requirements Document |
| RoR | Rating of Record |
| SPPP | Sub-Pay Pool Panel |
| TOA | Time Off Award |
| VoP | Value of Position |
| C-R-I | Contribution-Result-Impact |

---

## 16. FAQ

**Can it make up numbers for me?**
It can help you estimate numbers you do not have exact figures for, and it records how each estimate was reached so you can defend it. It will not invent events, audiences, awards, or recognition.

**Will my coworkers' names end up in my assessment?**
No. Names are used during recall and stay in your private notes. Final text converts them to titles, organizations, and counts.

**Can I reuse last year's statements?**
No. Prior cycles' wording and achievements are off limits. Continuing work can be described only in terms of what is new this cycle. Your current midpoint, however, is meant to be built on.

**What if I was promoted late in the cycle?**
Check your pay pool's business rules. In the example rules, a promotion within 150 days of cycle end defaults to your expected score unless substantial justification is provided. The toolkit builds the package around that justification and gives your supervisor a ready paragraph.

**Does this replace my supervisor's narrative?**
No. It gives your supervisor a crib sheet with facts, counts, and descriptor-aligned rationale. The official narrative is theirs.

**Does this work for NJ and NK?**
Yes. Level calibration uses the descriptors for your career path and target level from your profile.

**Is anything sent anywhere?**
The skills run in your Claude Code session. Your files stay where you keep them. Follow your organization's policies on which AI tools may process work information, and never include classified information.

---

## 17. Disclaimer
- **This is not an official DoD or Department of the Air Force product.** Rules summarized here are for orientation only and vary by pay pool and year. Always follow your pay pool's current business rules, guidance, and your supervisor's direction. You are responsible for the accuracy of everything you submit.
