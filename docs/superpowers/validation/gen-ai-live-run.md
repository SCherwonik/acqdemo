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

14. **Four user corrections were silently dropped in one turn.** The user's message carried three
    corrections and one answer, with a document attached. The reply processed the document
    correctly and did not acknowledge, apply, or refuse a single one of the four. One of them was
    an answer to a question the reply then asked again. The three previous turns had applied
    corrections faithfully, and the difference was the attachment, so the working hypothesis is
    that document processing consumed the turn. This is the most serious behavioral finding of the
    run: a user who says "stop claiming X" and receives a clean-looking reply has no signal that X
    survived. *Fix: `orchestrator.md` answers or refuses every instruction in a message before
    processing an attachment, and names each one it acted on. Diagnostic first: resend the same
    items with no attachment. If they land, the cause is the upload competing with them. If they
    drop again, it is instruction decay over conversation length, which is a different and worse
    problem.*

## Confirmed by a negative test
The closeout export contained no narrative: one record skipped by an administrator, one an empty
draft. The agent reported exactly that and concluded the annual must carry the partial period
itself. It did not manufacture a supervisor narrative from surrounding context, which is the failure
this condition is built to provoke. The rule against inventing events held where it was most likely
to break.

15. **A system's behavior was asserted as fact.** Asked why a closeout record existed three days
    after a promotion, the agent explained that the personnel system automatically generates one
    when a personnel change is processed. It has no source for that. The conclusion it supported
    was reasonable; the mechanism invented to justify it was not. *Fix: the never-invent rule
    covers how a system behaves, not only events and audiences. Say what the record shows and what
    it appears to correspond to.*
16. **A document-versus-user conflict was recorded on both sides and never raised.** Two documents
    and a third reference gave one expected contribution score; the user gave a different one from
    a live system check. Both were stored, in different fields, and the disagreement was never put
    to the user. That number is the bar the whole narrative has to clear and it drives the panel
    read. *Fix: `orchestrator.md` raises any conflict between a document value and a user-supplied
    value as a question at the moment the second one arrives, rather than keeping both.*

17. **It invented a mandatory requirement and then wrote the invention into the persistent block.** At
    allocation it opened Job Achievement with a supervisory paragraph for an employee who supervises
    nobody, and added "Supervisory objective (0/0/0 counts)" to the Pay pool block's
    `mandatory_objectives`, where the plan lists only the two certification statements. Inventing a
    requirement is bad; recording it as a pay pool rule is worse, because the workspace block is what
    a later session reads back and trusts. *Fix: `orchestrator.md` and `factor-drafter.md` derive
    mandatory paragraphs from the plan's stated objectives and the profile's supervisory counts, and
    nothing is added to `mandatory_objectives` that was not read from a document or supplied by the
    user. A supervisory paragraph is required only when the counts are not all zero.*
18. **A correction fixed the instance, not the class.** Told two rounds earlier that a calendar-derived
    candidate must not claim the employee led a series the calendar shows only attendance at, the
    agent fixed that entry, then at drafting time wrote "Led 9 one-on-one technical exchange
    sessions" for a different calendar-derived entry whose `role` was blank. The rule has to live
    where the drafting happens, not only where the correction landed. *Fix: `factor-drafter.md`
    refuses an ownership verb for any entry whose `role` is blank, and says which entry and which
    verb it declined to use.*
19. **A factor repeated its own mandatory paragraph.** Mission Support's certification statements gave
    both certifications, their dates and the point count; the third C-R-I in the same factor restated
    all three. Nothing catches this: `CROSS_FACTOR_REPEAT` compares factors against each other and
    `PRIOR_REPEAT` compares against a completed cycle, so a statement repeating the preamble sitting
    directly above it passes clean. *Fix: `factor-drafter.md` treats the mandatory paragraphs as
    already-spent material for that factor. Worth considering in the deterministic layer too, in both
    `skills/review/scripts/check.py` and the offline page: a within-factor repeat check comparing each
    entry against that factor's own preamble.*
20. **Bench reasoning was applied inconsistently.** One entry was benched as "personal professional
    development rather than an organizational contribution" while another resting on the same ground
    was allocated. *Fix: `orchestrator.md` states the bench test once and applies it to every entry,
    and the allocation names the test it used.*

## The drafting stage, scored against the real checker
The draft was run through `check.py` with the employee's real prior-cycle text, real midpoint, real
roster and real certification flags. What it got right first, because it is not nothing: the three
factors came in at 3,759, 3,475 and 3,744 characters against a target band of 3,400 to 3,800, and
those are the exact figures it claimed, to the character, for an agent that is told not to count.
Zero people's names. Zero contractor company names. Every one of four corrections applied.

Then: **8 CRITICAL**, and one fabrication the checker cannot see.

21. **It invented a number.** A Result line claimed a named efficiency gain as a percentage. That
    figure appears nowhere: not in the ledger, not in any of the five rambles, zero occurrences
    across every source the session had. Never-miss rule 2 failed at the only stage where it
    decides anything, and no deterministic check can catch it, because an invented number is
    well-formed. *Fix: `factor-drafter.md` writes no number that is not carried on the entry it is
    drafting, and lists in LEFT OUT any number it wanted and did not have.*
22. **Eight prior-cycle repeats, runs of six to twelve words**, lifted from the employee's own
    midpoint and prior annual, including a twelve-word run in Communication and Teamwork. Rule 4 is
    a never-miss rule. The drafter had never been handed the prior text, so it could not have
    avoided them. *Fix: the Factor Drafter handoff in `orchestrator.md` includes the prior-cycle and
    midpoint text, and `factor-drafter.md` checks each statement against it before writing, the way
    it already checks against the factor's own preamble.*
23. **Three of nine Impact lines opened with verbatim descriptor text**, phrases lifted whole from
    the career path's level descriptors. Writing style says take phrasing from the descriptors, not
    paste them; a panel reading its own rubric back hears the rubric, not the contribution. *Fix:
    `factor-drafter.md` uses descriptor vocabulary, never a descriptor sentence, and the Panel
    Reader flags a factor whose Impact lines open with descriptor text.*
24. **Unevidenced specificity used as padding.** Multi-decade records, structured weekly
    instruction, live code refactoring, recurring requests eliminated. None supported by an entry.
    Individually small, collectively the texture that makes a fabricated draft read as a real one.

### The finding that explains the other four
The character target caused them. The drafter was asked for 3,400 to 3,800 characters from a ledger
where half the entries had no result and no numbers, and it hit the band exactly. The only material
available to reach it was invented specificity and recycled prior-cycle phrasing. A character target
plus thin evidence produces fabrication, reliably, and the target is what makes the result fluent
enough to look finished.

*Fix, and this is the important one: the character count is a ceiling, never a quota.* A factor
short on evidence comes out short, with a line saying which entries were thin and what would have to
be answered to lengthen it honestly. The drafter never writes toward a number. The existing rule
about enriching a thin factor from the ledger stands; inventing to fill it does not.

## The supervisor crib sheet
The right shape, and two errors a panel could check in a minute.

Right: a substantial-justification paragraph, a pre-promotion versus post-promotion continuity matrix,
discriminators per factor, and payout guidance that draws the correct distinction, sustained
capability arguing base pay while a one-time high-stakes turnaround argues the award.

25. **The continuity matrix placed events on the wrong side of the promotion date.** Nine contractor
    sessions that all took place three to four weeks before the effective date were listed under
    post-promotion, and a demonstration series spanning seven months was listed as though all of it
    followed the promotion. This is the one artifact where the dates are the entire argument: a
    promotion inside the pay pool's window is defended by showing higher-level work on both sides of
    the line, so a matrix assembled by guesswork undoes the thing it exists to prove, in a document
    that goes to the pay pool manager. *Fix: the pre and post columns are built only from entries
    carrying dates, each item is placed by its own date, an entry spanning the effective date is
    split or marked as spanning, and an entry with no date is listed separately as undated rather
    than assigned to a column.*
26. **A cancelled meeting was counted as an event that happened.** A calendar line beginning
    "Canceled:" became a demonstration to an external agency's cost team in the roster and part of a
    count of ten sessions. The word was in the title. *Fix: `document-extractor.md` drops calendar
    lines whose title marks them cancelled and never counts them in a series total, and
    `evidence-auditor.md` treats a claim supported only by a cancelled line as unsupported rather
    than partial. Not a deterministic check: `check.py` and the offline page see the factor text and
    the prior-cycle text and never the calendar, so neither can know a meeting was cancelled. This
    one is caught at extraction or not at all, which is an argument for the extractor being strict
    rather than the checker being clever.*

Also, unprompted: it assigned itself categorical scores and a rating of record. Those are the panel's
to set, not the employee's, and stating them in a document written for the supervisor invites the
argument the assessment is meant to avoid.

## Resolved watch item
The supervisor's full name was not fabricated. Challenged, the agent named the document and the two
pages: the name came from the prior cycle's appraisal, where that person was the supervisor of
record for the prior cycle's midpoint and closeout. It had been carried into the current cycle's
supervisor list. A wrong-cycle attribution rather than an invention, and it cited its source when
asked, which is the behavior wanted. Recorded as a lesser finding: facts read from a prior-cycle
document must carry that cycle with them.

## Diagnostic result
The four dropped corrections were resent with no attachment, in the same conversation at the same
length, and all four landed, with an audit of the other entries volunteered alongside. So finding 14
is instructions losing to document processing within a turn, not instruction decay over conversation
length. The fix is a single rule in `orchestrator.md`: answer or refuse every instruction in a
message, naming each one, before processing an attachment.

## What the run has proved about the deterministic layer
Every defect above is one a well-formed document passes cleanly: a stale certification statement, a
wrong broadband level, an invented date, a role verb the calendar does not support. None of them can
be caught by a character counter or a repeat detector. They are caught by asking the employee, which
is why the question rounds are the product and the checker is only the last gate.

## Method note
The employee answers deep-dive questions from memory rather than from the finished annual. Feeding
the answer key back in would measure nothing about what the pipeline recovers on its own.
