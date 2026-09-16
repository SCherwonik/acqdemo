# Validation: Fictional Personas (Test D, Task 21)

Date: 2026-09-15. Every name, organization, program, and number in the personas is invented.

## How the sessions were run
The sessions were **simulated by an agent**, not run as live Claude Code sessions with the installed plugin. The agent read `skills/annual/SKILL.md` and followed Steps 0 through 8 in order, opening each reference the skill names (`question-bank.md`, `writing-style.md`, `ledger-format.md`, `levels.md`, `rules/ccas-core.md`, `cert-templates.md`, the persona's descriptor file, and the templates), and ran `acqdemo:review` (checker plus judgment checks) at Step 7.

- Workspace: each persona folder copied to a scratch folder outside the repo, plus `skills/start/templates/paypool.md` unchanged.
- The simulated user answered every question only from the persona's `ramble.md`. Anything the ramble does not cover was answered "I don't know". Proposed estimates were approved and recorded in the ledger with a basis. "What else does that bring to mind?" was always answered "I don't know", which the agent treated as "enough" for the Step 4 stop rule.
- Each session produced `FY26/ledger.md`, `FY26/session-state.md`, `FY26/rambles/`, draft versions, `FY26/final/` (three factor files and `FY26 working doc.md`), and a session log. Only the three final factor files are committed, to `skills/start/references/examples/<persona>/final/`.
- Checker flags: `--mode annual --min-entries 3 --what-label C --roster <roster.md>` plus the persona's `flags.txt`.

## Results

| Persona | Descriptor file | Level / target | C-R-I per factor (JA / CT / MS) | Mandatory paragraphs | Final CRITICAL / WARNING | Draft history |
|---|---|---|---|---|---|---|
| nj3-engineer | `descriptors/nj.md` | NJ III / IV | 3 / 3 / 3 | MS: acquisition "Met or current" | 0 / 0 | v1 0/0; v2 judgment fixes |
| nk2-admin | `descriptors/nk.md` | NK II / III | 3 / 3 / 3 | none | 0 / 0 | v1 1 CRITICAL (CROSS_FACTOR_REPEAT); v2 0/0; v3 judgment fix |
| nh2-supervisor | `descriptors/nh.md` | NH II / III | 3 / 3 / 3 | JA: supervisory; MS: DoD FM "Active cycle" | 0 / 0 | v1 0/0; v2 and v3 judgment fixes |

Character counts (line breaks count as 2): nj3-engineer JA 1202, CT 1279, MS 1319; nk2-admin JA 1108, CT 1045, MS 915; nh2-supervisor JA 1373, CT 1014, MS 1226.

`python -m pytest tests/test_examples.py`: 4 passed.

## Acceptance

| Criterion | nj3-engineer | nk2-admin | nh2-supervisor |
|---|---|---|---|
| Correct descriptor file and target level | Pass (nj, IV) | Pass (nk, III) | Pass (nh, III) |
| Mandatory openings | Pass: MS opens with the acquisition "Met or current" statement (ENG (Practitioner), 12 Mar 2025, 42 CLPs) | N/A (none required) | Pass: JA opens "I supervise 0 military, 4 civilians, and manage 1 contractors." then a supervisory paragraph; MS opens with the DoD FM "Active cycle" statement |
| At least three C-R-I per factor | Pass (exactly 3) | Pass (exactly 3) | Pass (exactly 3) |
| No fictional person names in factor files | Pass (checker with roster; manual scan of all roster and profile names and "Example" organization names) | Pass | Pass |
| Every number traces to the ramble or an approved estimate | Pass (certification values come from `profile.md` via the template) | Pass | Pass (counts in the supervisory and certification paragraphs come from `profile.md`) |
| `check.py` with persona flags: 0 CRITICAL | Pass | Pass | Pass |

Approved estimates, all recorded in the ledgers with a basis:
- nj3-engineer: "two-thirds reduction" = (3 - 1) / 3 days; "over 40 technician-days, about 350 labor hours" = 2 technicians x 2 days saved x 11 aircraft = 44, x 8 hours = 352 (assumes the new process still uses two technicians).
- nk2-admin: "roughly three quarters" = (25 - 6) / 25; "about 19 fewer a month" = 25 - 6.
- nh2-supervisor: "21 days faster" = 30 - 9; "less than a third of the usual time" = 9 / 30; "nearly two a month" = 23 / 12; "two-thirds reduction" = (12 - 4) / 12; "half of the team's four specialists" = 2 / 4.

## Skill instruction changes made to reach acceptance
None. No `SKILL.md` or reference file was edited. Every persona reached acceptance with the skills as written. The findings below are suggested changes for the maintainer.

## Findings: unclear instructions and weak output
Ordered by effect on output quality.

1. **Thin rambles cannot fill nine slots under the two-factor cap.** Step 4 continues "until every factor has at least four `ready` entries or the user says enough"; Step 5 allows an entry in at most two factors. The rambles yielded 6, 5, and 5 entries. Result: three or four entries per persona appear in two factors, and in nk2-admin a thin entry (the director's calendar, where every drill-down answer was "I don't know") had to become MS entry 3, which reads at NK II with no result. The skill gives no instruction for this case. Suggested change: at Step 5, count slots (entries x 2 >= 9) before allocating; if short, run one recall round aimed at the empty slots, allow splitting an entry with separable deliverables (the building move's seating plan and phone list), and tell the user plainly when a statement will be thin.
2. **Step 5 conflicts with `writing-style.md`.** "One project, three angles" gives JA, CT, and MS angles for one project; Step 5 says "may appear in a second factor only". The agent followed Step 5. For the custodial protest (solved it, worked with legal, no service gap), three angles would have produced stronger text than forcing mentoring into MS. Suggested change: state one rule in both files.
3. **Same facts in two factors pass silently unless the wording repeats.** The checker caught one real repeat (nk2-admin v1: a 10-word run describing the offsite in CT and MS). The same numbers in two factors (25 to 6 overdue taskers in JA, "19 fewer" in MS) and the same mission phrases pass. Suggested change: in Step 5, assign each number to one factor (for example, count in JA and dollars in MS) and record that split in the ledger.
4. **Impacts converge on the mission statements.** Step 6 asks for "a mission tie drawn from the profile's mission statements", and the impact ladder asks for two rungs above the Result. For a technician or an admin assistant, two rungs above a branch or front office result is command or headquarters level, which the rambles never support, so the agent leaned on the mission statements instead. Output repeated the same phrase: "informed and on schedule" three times in nk2-admin v2 (one was reworded in v3), "installation operations" five times in nh2-supervisor. Suggested change: say that a tie to the one-level-up or two-levels-up mission satisfies the ladder for field positions, and use each mission phrase at most once across the three factors.
5. **The supervisory paragraph body has no guidance.** `ccas-core.md` fixes the counts sentence and says "describe how the supervisory objective was met"; `cert-templates.md` has no supervisory template. It is unclear what facts belong there and whether they may repeat JA C-R-I facts. The nh2-supervisor paragraph summarizes three C-R-I entries. Suggested change: add a two-sentence template (team composition, then how the objective was met without restating C-R-I numbers).
6. **Ledger `allocated` is single-valued.** `ledger-format.md` allows `JA`, `CT`, `MS`, `bench`, or empty, but Step 5 allows a second factor. The agent recorded the second factor in `notes`. Suggested change: allow `JA, MS` or add `allocated_second`.
7. **Target-level language cannot always be supported.** Steps 4 and 6 say to use the target level's descriptors; `levels.md` says to borrow from the high end of the current level and the next level up. When the facts only support the current level (nh2-supervisor: two informational briefings, no decision stated, so NH III "briefings to obtain consensus/approval" does not fit), the skill does not say to keep current-level wording and flag the gap. The agent did that and noted it in the crib sheet.
8. **Estimate protocol vs. an unknown input.** "Propose the top of the plausible range" gives 55 technician-days if the new rig needs one technician and 44 if it needs two; crew size was unknown. The agent chose the defensible 44 and wrote "over 40". Suggested change: when an input is unknown, ask the user to confirm the assumption and put it in the basis line.
9. **Certification "Active cycle" template is not sanity-checked.** On 15 Sep the template asserts the user is "on track to complete the remaining 10 CETs" by 30 Sep. Suggested change: when points remain and the cycle end is within 30 days, ask the user to confirm "on track" before using the template.
10. **Smaller gaps.** Step 0 does not say how to derive `FY<yy>` (the agent used the rating period end year). Step 3b's office map has no path for "I don't know". The question bank says roster counts become statement numbers, but roster frequencies ("3 sessions", "monthly") were not in the rambles, so the agent left them out to meet the traceability rule. The working doc asks for a punchier and a safer alternate "for each final statement" (18 alternates for 9 statements) without saying whether an alternate is a whole C-R-I or one line; the agent wrote one line each. With the DoD FM statement as the only certification, it becomes MS paragraph 1 even though `ccas-core.md` calls it "the second statement"; the checker handles this through flag order, but the rule text does not say so.

## Post-review edit
A review after the writing-style update (mission-statement phrase at most once per factor) found the same mission phrase in several Mission Support Impacts for nk2-admin (3) and nh2-supervisor (2). Those Impacts were reworded using only facts already in each entry; `check.py` still reports 0 CRITICAL and 0 WARNING.
