# Gen AI Live Run (Run A)

A real employee running the Gemini pack against his own documents on a government network,
2026-09-16. Inputs: a CAS2Net Salary Appraisal export for the prior cycle, this cycle's midpoint
and contribution plan, and a 363-row Outlook calendar export. The same person's finished annual,
written earlier with the Claude Code plugin, is held back as an answer key.

Findings are recorded as they appear and fixed **after** the run finishes. Changing the agents
mid-run would make the comparison against the answer key meaningless.

## Confirmed working, do not regress
| Behavior | Evidence |
|---|---|
| Stops and waits | Ended every turn on a question. Never drafted unasked |
| Two blocks, kept apart | The `ledger` block holds only `## L-` entries; `workspace` carries Profile, Pay pool, Roster, Session state |
| Bucketing | Plan produced objectives and duties but no candidates; the prior appraisal produced facts and prior text but no candidates. Both correct |
| Numbers carry provenance | Every number has `source` and `basis` |
| Id discipline | "Started at L-001 because no ledger and no highest id were supplied." Merges kept ids stable rather than renumbering |
| Self-criticism | Flagged its own overlaps and marked four claims vague on metrics |
| Coverage gap detection | Found a near-empty October 2025 and said to verify the export |
| User correction sticks | Two candidates created on request, merges applied with notes recording what was absorbed |
| Drill-down from evidence | Asked whether Sprint 10 and Sprint 11 moved a pipeline into production, using sprint dates read from the calendar |

## Fixed during the run
| # | Defect | Fix |
|---|---|---|
| 1 | Copied base pay, locality, the pay increase, the contribution award and an employee ID out of the appraisal export | `document-extractor.md` said "pull and report only" and then "report the rest as PRIOR CYCLE FACTS", which cancelled it. The list is now exhaustive and compensation is explicitly excluded. Commit 95f69b2 |

## To fix after the run
Ranked. Each names the file that owns it.

1. **Certifications are never refreshed.** The extractor pulls the prior cycle's certification
   statements, and nothing afterwards asks whether they changed. The run carried FY25 values
   (one certification level, an in-progress second, a CLP count) into an FY26 profile where all
   three were out of date. Certification statements are a mandatory Mission Support paragraph and
   a well-formed stale statement passes every deterministic check. *Fix: `orchestrator.md` queues
   a certification-refresh question whenever prior-cycle certification statements were found, and
   marks them unconfirmed in Profile until answered.*
2. **Recurring calendar series are under-harvested.** The two largest stakeholder blocks, 29
   meetings with one platform partner and 10 sessions demonstrating the employee's own tool,
   produced no candidates until the user asked for them by name. Both were Communication and
   Teamwork evidence. *Fix: `document-extractor.md` makes a candidate for any recurring series
   above a small occurrence threshold that no document candidate already covers.*
3. **A source file was cited by the wrong name.** The extractor reported reading a file whose
   name differed from the one supplied, while quoting content only the supplied file contains.
   Every calendar-sourced entry then carried an `evidence:` line pointing at a file that does not
   hold the evidence. *Fix: `document-extractor.md` echoes each filename exactly as given in the
   inventory and reuses that string verbatim in every `evidence:` and `basis:` line.*
4. **A date was invented.** Session state recorded `updated:` as a date two weeks in the future.
   *Fix: a rule in `orchestrator.md` and `ledger-keeper.md` that a date not supplied by the user
   or read from a document is left blank and asked about, never estimated.*
5. **`pending_questions` held a count, not the questions.** The field exists so a resumed session
   can re-ask exactly what was outstanding; a count cannot do that. *Fix: `ledger-keeper.md` and
   the workspace skeleton state that the questions are stored verbatim.*
6. **An unevidenced role verb.** A calendar-derived candidate said the employee led a series the
   calendar only shows attendance at, with `role` left blank. *Fix: `document-extractor.md`
   requires neutral verbs for calendar-derived candidates, attended or participated in, until a
   role is confirmed.*
7. **Date ranges extended without confirmation.** Entries moved from ending at the midpoint to
   ending at cycle end before the user had answered whether the work continued. *Fix: leave the
   end date as read and ask.*
8. **`supervises` recorded as yes or no.** The supervisory paragraph needs counts by category.
   *Fix: the Profile skeleton in `ledger-keeper.md` asks for counts.*
9. **An occurrence count changed between two messages** without explanation, from the inventory's
   figure to a higher one in the candidate. *Fix: a number restated later must either match or
   say why it changed.*

## Method note
The employee answers deep-dive questions from memory rather than from the finished annual. Feeding
the answer key back in would measure nothing about what the pipeline recovers on its own.
