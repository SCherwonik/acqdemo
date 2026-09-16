# Backtest (test C)

Date: 2026-09-15. Skill under test: `acqdemo:annual` with `acqdemo:review`. One prior cycle, one employee. Scorecard from the design spec, Section 11.

## Method
- Drafting ran in a subagent that saw only an employee-side packet (contribution plan, midpoint and closeout self-assessment, question-and-answer notes, gate answers) plus the skills. It played both the skill and the employee, answering only from the packet.
- Scoring compared the final text with the supervisor's annual narrative and with the employee's original submission.
- Blind preference ran in two further subagents that saw only the two texts per factor, unlabeled. The second run swapped positions to control for order bias.

## Scorecard

| Metric | Pass bar | Result | Pass |
|---|---|---|---|
| CRITICAL findings in final text | 0 | 0 CRITICAL, 0 WARNING (original submission: 3 CRITICAL) | Pass |
| Supervisor-added facts surfaced by questions | at least two-thirds | 1 of 6 fully (17%), 4 of 6 partially, 1 of 6 not at all (50% counting partials as half) | Fail |
| Numbers per C-R-I vs. the original | higher | 1.11 vs. 0.18 | Pass |
| Characters per factor | at most 3,900 | about half of the budget in every factor | Pass |
| Blind side-by-side preference | new wins at least 2 of 3 factors | 3 of 3 in both position orders | Pass |

Result: 4 of 5 metrics pass.

## Run statistics
- Question rounds: 23. Numbered questions: 134. Answered "I don't know" or "skip": 77 (57%).
- C-R-I per factor: 3, 3, 3 (original: 4, 4, 3). Bench entries: 1.
- Estimates approved: 2. Estimates declined: 4.
- Blindness: partial. Answer-key files were withheld by instruction, and the drafting subagent reported opening none of them. It could not be verified independently, and the session's standing context gave the drafter some general background about the employee.

## Step 5 (Improve)
No skill files were changed in this run. Proposed changes for the failed metric are recorded in the maintainer's private notes. The rerun is pending until those changes are made.

Follow-up: proposals 1 to 6, 8, and 9 were applied to the skills and references after this run (question bank roll-up and confirmation questions, primary-factor stop rule, length check, two-layer review exit). Proposal 7 is still open. The rerun has not been done.

