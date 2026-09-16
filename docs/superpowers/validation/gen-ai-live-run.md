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

0. **A mid-cycle promotion went unnoticed, with the evidence in hand.** The extractor read a prior
   appraisal written at one broadband level and a contribution plan written at the next level up,
   recorded `level` from the first and `target_level` from the second, and asked nothing. The
   employee had in fact been promoted inside the rating period, 108 days before the due date and
   inside the pay pool's promotion window. Three things follow from that and all three were lost:
   the drafting descriptors come from the wrong level, the expected contribution score changed at
   the promotion and the profile held one blended value plus a third figure from the plan, and the
   assessment needs substantial justification and continuity shown on both sides of the effective
   date. A promotion is the special situation the toolkit exists to handle, and this is the most
   expensive miss of the run. *Fix: `document-extractor.md` reports a broadband level appearing at
   two different values across documents as a conflict rather than resolving it silently, and
   `orchestrator.md` treats any level difference, any supervisor difference, and any closeout
   document as a special-situation question asked before deep-dives begin.*
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
10. **A profile correction did not reach the entry that restated the same fact.** Certifications
    were corrected in Profile while the ledger entry describing that professional development kept
    the superseded wording, so the two blocks disagreed and only a note recorded it. *Fix:
    `ledger-keeper.md` checks entries for text restating a profile fact that just changed, and
    either updates them or lists them for the user.*
11. **Two expected contribution scores were held in one field** with a third figure from the plan
    appended in parentheses, none of them reconciled. The score drives the panel read and the Very
    High judgment. *Fix: the Profile skeleton carries dated values when a score changes mid-cycle,
    as the promotion case requires, and a conflict between documents is asked about rather than
    concatenated.*

12. **Evidence lines do not track where a fact came from.** Three instances, one shape. A calendar
    entry cited a filename the agent had not read. An entry corrected from the user's own answers
    kept an `evidence:` line naming the document that does not contain them. A transition date was
    inferred from the date a document was created and written as fact. A claim the employee will
    defend in a panel has to say where it came from, and "the user said so on this date" is a
    legitimate source that the format allows and the agent does not reach for. *Fix:
    `ledger-keeper.md` and `document-extractor.md` require the evidence line to name the actual
    origin, including the user and the date when the user is the origin, and forbid inferring a
    date from a document's own date.*
13. **`current_entry` held a value that is not an entry id.** Minor, but the resume path reads it.
    *Fix: the workspace skeleton says it is one id or blank.*

## Watch, not yet a finding
A supervisor's full name appeared that the user had not supplied, in a run where other full names
plausibly came from an uploaded PDF. Unverified either way. If the name was not in a document it is
a fabrication of a person's name, which is the one thing the never-miss rules forbid outright, and
it would be the most serious finding of the run.

## What the run has proved about the deterministic layer
Every defect above is one a well-formed document passes cleanly: a stale certification statement, a
wrong broadband level, an invented date, a role verb the calendar does not support. None of them can
be caught by a character counter or a repeat detector. They are caught by asking the employee, which
is why the question rounds are the product and the checker is only the last gate.

## Method note
The employee answers deep-dive questions from memory rather than from the finished annual. Feeding
the answer key back in would measure nothing about what the pipeline recovers on its own.
