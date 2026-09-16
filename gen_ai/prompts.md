# Copy-Paste Prompts

For someone who has a chat box and nothing else. No agent builder, no saved instructions, no
subagents, no uploads beyond what the chat window itself accepts.

Every prompt below is meant to be copied whole into the chat, edited where it says to, and sent.
Work the stages in order. At certain points the assistant shows you two blocks holding everything it
has recorded. Read them when they appear. A number that came out wrong costs one sentence to fix
there and a redraft of a whole factor if it survives into the text.

## What you lose without the agent builder

Say it plainly, because it changes how much you have to do yourself.

- **No subagents.** One model does the reading, the ledger keeping, the drafting, the evidence
  audit, and the panel read. The two passes that lose the most are the audit and the panel read,
  and they lose it for the same reason: on the full build they are done by a reader who did not
  write the text and cannot remember you mentioning something. Here the same conversation checks
  its own work, and it will be gentler on itself than a stranger would be. Stage 8 works around
  this as far as a single chat can, by making you start a brand new conversation.
- **No Knowledge files.** The descriptors for your career path, the question bank, and the worked
  examples are not attached to anything. Stage 0 has you paste in the descriptors for your target
  level, which is the one reference the drafting genuinely cannot do without.
- **No instructions that persist.** A long chat drifts. The rules that must never slip are repeated
  at the top of several stages on purpose. Do not trim them because you already said them.
- **Context runs out.** A long appraisal export plus a year of questions will fill a chat window.
  When replies get slow, vague, or start forgetting entries, ask for both blocks, open a fresh chat,
  paste Stage 0 and both blocks into it, and carry on. The same pair also carries a cycle into the
  Claude Code version of this toolkit, which reads the identical format.

Everything else survives: the question sequence, the recall sweeps, the drill-down ladder, the
estimate protocol, the ledger format, and the offline checker, which is a separate file and does
not care what produced the text.

## Before you start

Pull these if you can. Any of them can arrive later and none of them blocks the start.

1. Your last completed cycle's **Salary Appraisal** from CAS2Net, exported with **Check All**.
2. This cycle's **Midpoint Assessment** and **Contribution Plan**. If you are writing the midpoint
   now, ask for the plan instead; there is no earlier midpoint and the plan is the jump-off point.
3. Your **Outlook calendar** for the rating period, saved as a text file. Calendar, View tab, Change
   View, List; sort or filter to the period; select the first meeting, Shift-click the last, Ctrl+C,
   paste into Notepad, save as .txt. Never from a classified system.

Also get `acqdemo-checker.html` and, if you want it, `brain-dump-worksheet.md`, from whoever gave
you this pack. You need the checker at Stage 7.

Nothing classified goes into any of this. Not a document, not a calendar title, not a sentence you
type. If a program name is sensitive, call it Program A and describe what you did instead.

---

## Stage 0: the standing instructions

Paste this first, in every new chat, before anything else. It is the whole ruleset in one block.

```
You are helping me write my Department of Defense AcqDemo self-assessment. Follow these rules for
the rest of this conversation, including in any new chat where I paste this block again.

Never-miss rules, no exceptions, and tell me plainly if I ask you to set one aside:
1. Never invent events, audiences, awards, or recognition. If I did not say it happened and no
   document says it happened, it does not go in the draft.
2. Numbers are proposed as estimates, confirmed by me, and recorded with a basis showing how the
   number was arrived at.
3. No people's names in the finished factor text. Names are welcome in my notes and in the ledger's
   audience, evidence, and notes fields, because they help me remember and they produce counts.
4. This cycle's midpoint is the starting point. Prior cycles are off limits: never re-claim a
   previous cycle's achievement unless I can say what is new, larger, or different this cycle.
5. If I start describing anything classified, stop me immediately, do not repeat it back, and help
   me say the same contribution in unclassified terms: scope, audience, effect, difficulty.
6. At most 3,900 characters per factor. Do not count characters yourself; a separate offline
   checker does that.

How to work with me:
- Ask five to eight numbered questions per round, so I can answer "1 yes, 2 no, 3 about forty".
  "Skip" and "I don't know" are always acceptable answers from me.
- Prefer yes/no and pick-from-list questions. Propose an answer and ask me to correct it rather
  than asking me to produce one from a blank page. Keep open questions to one per round.
- End every round of questions with: "What else does that bring to mind?"
- Write my answers into the blocks before you ask the next thing, every round, never afterward.
  Nothing reaches a draft that was only said in conversation; the entries are the only evidence.
- Between checkpoints, do not print the blocks. End with one short line naming what you recorded,
  like "Recorded: L-004 numbers and basis, L-005 audience", then the questions.
- Print both blocks in full at exactly these points: when an entry is finished and set to ready;
  before you propose the allocation; before you draft any factor; whenever I ask to see them; and
  at the end. Ask me to read them over at each one. Never print a partial block or write "the rest
  is unchanged".

My two blocks. Keep both current after every round, and print them whole, in fenced blocks, at the
points listed above.

A block labeled ledger, holding ONLY entries whose headings are "## L-NNN Short title". No session
state, no profile, no roster in this block; it has to stay machine-checkable. Entry fields:
- status: candidate, ready, allocated, submitted, or rejected
- dates, project, what, role (owned, co-owned, owned-a-piece, supported)
- audience, decision_fed, obstacle, sustained (yes or one-time)
- numbers: one line each, ending "| source: X | basis: Y", source being stated, estimate, calendar,
  or document
- lenses (JA, CT, MS), descriptor_hits, prd_duty, plan_tag, evidence
- prior_cycle_overlap: none, or "continuing (cycle delta: ...)"
- allocated: JA, CT, MS, bench, or empty
- notes
Only status, dates, and what are required. Blank means not asked yet; write "none" when it was
asked and does not apply. Ids only increase and are never reused.

A block labeled workspace, holding exactly four headings in this order:
# Profile: career_path (NH, NJ, NK), level, target_level, series_and_title, organization,
first_cycle, rating_period, eocs (expected overall contribution score), value_of_position,
supervises (exact counts), supervisor, prior_supervisors, certifications with status, dates and
point counts, promotions, mission statements one and two levels up.
# Pay pool: pay_pool, business_rules_source, what_label (C or W), mandatory_paragraph_order,
min_entries_annual, min_entries_midpoint, midpoint_window, employee_due, supervisor_due,
promotion_window_days, char_limit, allow_phrases.
# Roster: a table of Ring, Name, Organization, Role, Worked on, Frequency, Ledger. Rings are
1 my own office, 2 other divisions, 3 government outside my organization, 4 contractors,
5 leadership.
# Session state: step, current_entry, round, pending_questions, next_action, open_questions, updated.

I read both blocks when you print them, which is how a wrong number gets caught while it is still
cheap to fix. I may also copy them out to carry this work into another chat or into the Claude Code
version of this toolkit.

Do not use the open web for AcqDemo rules. They vary by pay pool and by year and public pages are
frequently out of date or about someone else's pay pool. If you do not know a local rule, say so and
tell me to check my business rules or this year's guidance email.

Acknowledge in two lines, then wait.
```

Then paste the descriptors for your career path and target broadband level for all three factors,
from your organization's AcqDemo materials, with this line above them:

```
These are the descriptors for my career path and the level I am targeting. Use this language when
you draft and when you judge the draft later. Do not write from memory about descriptors.
```

## Stage 1: your documents

One document per message. Long ones go in pieces, and say which piece it is.

```
Here is my [last completed cycle's Salary Appraisal / this cycle's midpoint / contribution plan /
calendar export]. Read it and give me, in this order:

1. An inventory: what this document is and what period it covers.
2. Profile facts: career path, broadband level, series and title, organization, rating period,
   supervisor and dates, whether I supervise anyone and the counts, certifications with status and
   dates, expected overall contribution score, value of position.
3. PRIOR CYCLE TEXT: if this is a completed cycle, my submitted factor text, copied out verbatim,
   one part per factor. Keep it; I need it twice later.
4. Plan objectives with their labels, and position duties numbered, if this is a plan.
5. From a calendar: recurring meeting series with how many occurrences and the month range; one-off
   events that look like briefings, reviews, training, or trips; every organization or person
   appearing more than once; and any months with no meetings at all.
6. Candidate entries in my ledger format, all at status candidate, numbering on from the highest
   entry id already in my ledger. Leave every field blank that this document does not answer.

Rules for this: never create a candidate from a completed cycle, since that is the thing I must not
repeat. Every midpoint statement from THIS cycle does become a candidate, with
prior_cycle_overlap: continuing (cycle delta: unknown). Do not create candidates from a plan; a plan
says what was supposed to happen. Copy numbers exactly as written, never rounded or totalled. Never
infer a role, an audience size, or an impact from a meeting title.

Then print both blocks so I can check what you recorded, and stop.
```

If you are using the worksheet, upload or paste it here with the same prompt and treat it as a
document. If you have no documents at all, skip to Stage 2 and say so.

## Stage 2: situation and profile

```
Three questions first, then fill my profile.

1. Have I been through an AcqDemo cycle before and submitted a self-assessment?
2. Did I write a midpoint self-assessment this cycle?
3. Did my position or my supervisor change during this cycle?

After I answer, ask me five to eight numbered questions for whatever is still blank in my Profile
and Pay pool sections. Ask career path, current level, and target level first; nothing later works
without them. Do not ask me for descriptors or general AcqDemo rules. Do ask whether I have my pay
pool's business rules or this year's guidance email, because the due dates, the minimum entries per
factor, the mandatory paragraph order, the C or W label, and the character limit come from there.

Park anything I do not know in open_questions and move on. Confirm in one line what you recorded, then ask.
```

If your position or supervisor changed, say the date out loud: a closeout is due within 30 calendar
days of the change.

## Stage 3: the candidate list

```
Show me every candidate entry as a numbered inventory, with your read on the evidence (strong,
some, or thin) and which factors each one might serve. Then ask me to correct anything wrong,
delete anything that is not mine or not this cycle, and add what is missing.

To help me add, give me eight to ten numbered prompts, and build the first few from my own material
by naming the actual duty, objective, project, or meeting series. Fill the rest from these openers:
products somebody else used; recurring duties and what was different this time; customers and what
they did with what I gave them; firsts for me, my office, or my organization; things that were
broken, slow, manual, wrong, or risky that I fixed; people I taught, trained, mentored, reviewed,
onboarded, or unblocked; rooms I spoke in and who was in them.

Confirm in one line what you recorded, then ask.
```

## Stage 4: the recall sweeps

One sweep per message. This is where the year you actually had turns up, so do not skip ahead.

```
Sweep 1, the timeline. Build a month list for my rating period and seed each month with what you
already have: meetings from my calendar, releases, the midpoint date, promotions or moves, budget
and program milestones. Walk it three months at a time and ask me what else was going on in those
months: briefings, deadlines, fires, trips, training. If I gave you no calendar, do not ask me open
month questions. Walk the budget and program milestones instead and ask what I delivered for each.
```

```
Sweep 2, the people. First ask me to describe my office map, the sections or teams and who sits in
each. Then go ring by ring, one ring per round, asking for names: ring 1 my own office section by
section, ring 2 other divisions or directorates, ring 3 government outside my organization such as
program offices and headquarters staff, ring 4 contractors by company, ring 5 leadership I briefed
or advised. Put every person in the Roster table with their ring, organization, role, what was
done, how often, and the entry it belongs to. Counts from that table become numbers in my text. The
names stay in the workspace block and never reach the finished text.
```

```
Sweep 3, the artifacts. Ask me to go and look rather than remember: read meeting titles out of my
calendar for a given month; search my sent mail for "attached", "brief", "slides", and "thanks" and
read the subjects back; name the slide decks and documents I created or updated this year; name the
busiest chat threads; name the shared folders I touched most. Titles alone are enough to make an
entry.
```

## Stage 5: the deep-dives

```
Order my candidates by likely impact, meaning scope times organizational level times novelty, tell
me the order, and let me reorder it. Then take them one at a time.

For each entry, run rounds of five to eight numbered questions until it carries facts, numbers, and
an audience, using this ladder:
1. What exactly did I do, and was my role owned, co-owned, owned a piece, or supported?
2. So what? What came out of it: a product, a decision, a fix, a capability?
3. Who used it? Which people, teams, organizations, leaders, and how many?
4. What changed, before versus after, in time, cost, quality, risk, speed, or capability?
5. Will it keep happening, or was it one-time?

When I cannot expand on something that came out of my own midpoint or plan, do not drop it after
one question. Switch to short yes/no questions built from the entities that document names. Keep
the parts I confirm. Drop the claim only if I cannot confirm any part of it.

When I do not know a number, climb this ladder and stop at the first rung that works: a count I can
look up; a proxy count such as versions released or sessions held; an estimate with a basis I
approve, proposed as the top of the plausible range, rounded, phrased "over N" or "about N", with
any unknown input taken at its defensible low end and written into the basis; or no number at all,
in which case lean on scope, audience, and organizational level. Never estimate an event, an
audience, an award, or recognition. Ask me "does that sound defensible to you?" before recording it.

Ask about every field that is blank on the entry you are working. Set an entry to ready only when
nothing is left blank. Every few entries, show me a coverage grid: how many ready entries per
factor, counting each entry once under its strongest factor, and the weakest discriminators in
each. Aim the next deep-dive at the weakest factor. Keep going until every factor has at least four
ready entries, or two for a midpoint, or the sweeps turn up nothing new, or I say enough.

Confirm in one line what you recorded before each round. When an entry reaches ready, print both
blocks in full and ask me to read the finished entry over before you start the next one.
```

When the deep-dives are done:

```
Run the portfolio roll-up once. Count across every ready entry, each item counted once: distinct
programs, estimates, systems, or teams supported; distinct organizations engaged and how many of
those groups I led; senior-leader briefings with the highest rank and the total headcount; people
trained or mentored; forums or conferences briefed and the audience size of each; dollars
influenced, meaning program or portfolio value or trade space. Read each total back and ask me if
it is right and what is missing. Never add counts that might overlap, like the same people in two
sessions or the same program in two entries. Confirmed totals become numbers on the entry that will
carry them, with the counted entry ids as the basis.
```

## Stage 6: allocate, then draft

```
Print both blocks in full first, so I can read what you recorded, then propose an allocation and
wait for my approval before drafting anything. A numbered list per factor, greatest impact first,
each line giving the entry id, the angle, why it belongs in that factor, and a raise or award tag
taken from the entry's sustained value: sustained work argues for a raise, a one-time high-stakes
delivery argues for an award.

Three or four entries per factor for an annual, two for a midpoint. Each entry is primary in exactly
one factor. A project may appear in a second factor only from a genuinely different angle with
different wording, and no fact and no number appears in more than one factor. Never allocate an
entry whose prior-cycle overlap has no delta. Everything else ready goes to the bench. If a factor
cannot be filled, tell me plainly that it is thin rather than padding it with a reused project.
```

```
Print both blocks in full one more time so I can check the entries you are about to draft from, then
draft one factor. Write [Job Achievement and/or Innovation].

Use my career path, my current broadband level, my target level, and my pay pool's [C:] label from
my workspace block, and the descriptors I pasted at the start. Draft only from recorded entries;
if something we discussed is not in an entry, say so and ask me rather than writing it in.

Mandatory paragraphs first, in my pay pool's order, and they are paragraphs, not C-R-I statements:
if I supervise anyone, the supervisory paragraph opens Job Achievement with the exact sentence
"I supervise X military, Y civilians, and manage Z contractors." followed by the scope of
supervision. Certification statements open Mission Support, filled from the template, and ask me for
any value you do not have rather than guessing a date or a point count.

Then the statements, greatest impact first, each one three labeled lines:
C: what I did, one sentence, at most 35 words
R: the result, carrying the entry's numbers, saying what came out of it
I: the impact, who is better off and at what organizational level, tied to the mission

The verb in C must match my recorded role: owned gets led, directed, spearheaded, architected,
established; co-owned gets co-led, partnered with, jointly developed; owned-a-piece gets drove,
built, delivered the piece; supported gets a strong verb on the smaller specific thing I delivered.
When my role was small, shrink the noun and keep the verb strong.

Aim each Impact about two rungs above where the Result happened, when the facts support it, on this
ladder: team, division or branch, agency or command, headquarters staff, service or department, DoD
or Congress. Never claim a level the facts do not reach. Vary the wording of every Impact.

Plain text only. No bullets, no headers, no bold, no Markdown, no em dashes, straight quotes. One
blank line between statements. Banned words: seamlessly, friction-free, perfectly, unbroken,
synergy, cutting-edge, world-class. "Robust" and "leverage" at most once each. If a number or a
specific noun can replace an adjective, replace it. Numbers exactly as my entries record them.

After the text, list which entry fed each statement, and list anything you left out because the
entry had no basis for it.
```

Repeat for Communication and/or Teamwork and for Mission Support. If a factor comes back under about
3,000 characters, go back to the ledger for numbers, audience, scope, and roll-up totals, or promote
a bench entry, and redraft. Never pad with adjectives.

For a midpoint or closeout there are no scores, no Very High language, and no crib sheet.

## Stage 7: the offline checker

Open `acqdemo-checker.html` in your browser. It runs entirely on your machine and sends nothing
anywhere. Fill the Setup panel and both Context boxes before you run it:

- **Cycle stage**: annual, midpoint, or closeout.
- **Career path**: NH, NJ, or NK.
- **Contribution label**: C or W, whichever your pay pool uses.
- **The three checkboxes**: whether you supervise people, hold an acquisition certification, hold a
  DoD FM certification.
- **Prior cycle and midpoint text**: paste in the PRIOR CYCLE TEXT the assistant pulled out at
  Stage 1, and this cycle's midpoint text. **This box is the only thing that makes the repeat check
  run.** Empty, the page reports no repeats because it looked for none.
- **Names to keep out of the text**: paste your Roster, or the names one per line. **This box is the
  only thing that makes the name check run.**
- **Allowed repeated phrases**: office, program, and system names that are allowed to repeat.

Paste each factor into its box, run it, then paste the findings back into the chat:

```
Here are the checker's findings on my draft. Fix every CRITICAL. For each WARNING, tell me what it
would cost to fix and what it would cost to leave, and let me decide. Then give me the corrected
factor text in full, and I will run the checker again.
```

## Stage 8: the two fresh readings

Start a **new chat** for each of these. A fresh window is the only way to get a reader who did not
write the text, and on the full build these two passes are separate agents for exactly that reason.
Do not run them in the conversation that produced the draft; it will defend its own sentences.

New chat, the evidence audit:

```
You are auditing finished text against the evidence behind it. You did not write this text and you
were not present for the conversation that produced it, so you cannot remember me mentioning
anything. Assume nothing you cannot see in the material below. A claim that is probably true but
whose support is not in front of you is unsupported, and you say so. A well written sentence is not
evidence.

[paste the ledger block]

[paste the three factors]

Pull out every claim separately, even several in one sentence: every action and the verb describing
my part in it, every number, every audience and every statement that someone used, adopted,
attended or received something, every count of people, teams, organizations, programs or systems,
every before-and-after comparison, every claim that something became standard or institutionalized,
every scope and dollar statement, every claim about the organizational level reached, every award or
recognition, and every named event.

Number the claims. For each, quote the supporting words from the ledger with the entry id, and give
a verdict: SUPPORTED, PARTIAL with the exact difference named, or UNSUPPORTED. Check every number
against the entry's recorded numbers, its source, and its basis, and flag any restated or rounded
number as a different number. Check every verb against the recorded role. Check every claimed
organizational level against what the entries show.

Open with a count line, then the table, then numbered fixes with the unsupported claims first. Each
fix gives me three options and nothing else: confirm it and record the basis, weaken it to exactly
what the source shows with the replacement wording written out for me, or remove it.
```

New chat, the panel read:

```
Read this the way a pay pool panel reads it: quickly, against the descriptors for my target level,
with a stack of other packages still to get through, and with no memory of how it was written.

My career path is [NH]. My current broadband level is [III]. My target level is [IV]. My expected
overall contribution score is [82]. Here are the descriptors for that career path and level:

[paste the descriptors]

[paste the three factors]

1. Read each factor straight through once at speed and write down at most three bullets of what you
   retained, before analyzing anything. Keep that in your report. If the strongest thing in the
   factor is not in those bullets, that is the finding.
2. For each statement, name the descriptor line at my target level it lands on, quoting a few words,
   or say none.
3. Name the discriminators this factor does not touch. Job Achievement: leadership role, mentoring
   and employee development, accountability, complexity and difficulty, creativity, scope and
   impact. Communication and Teamwork: oral, written, contribution to team, effectiveness. Mission
   Support: independence, customer needs, planning and budgeting, execution and efficiency.
4. Give one verdict per factor: reads below expected contribution, reads at expected contribution,
   reads as exceeding expected contribution, or reads at the next level up. Then one sentence of
   why in descriptor language, naming the statement that carries it, and one sentence on what is
   holding it back. Be honest rather than encouraging; telling me this exceeds when it does not
   costs me money.
5. Apply the panel tests: does the first statement carry the largest contribution; is the reach
   stated rather than left to be inferred; does each statement say what changed rather than only
   what was done; is the scope stacked where the facts allow; is there at least one sustained
   contribution and at least one one-time high-stakes delivery; does any Impact repeat another's
   wording; is any verb doing work the sentence does not support.
6. Give me fixes numbered by how much score they move, each naming the factor, the statement, the
   change, and the descriptor it would then land on. Propose only fixes my existing facts support.
   Where a fix needs a fact that is not there, write it as a question for me instead.

Do not rewrite the draft and do not count characters.
```

Take both sets of findings back to your working chat, fix, and run the checker again. You are done
when the checker shows zero CRITICAL, every audit flag is resolved, every panel fix is made or
consciously accepted, and you think the text is right.

## Stage 9: the handoff

```
Give me these, each plainly labeled so I can copy them one at a time:

1. Status and gaps: where this package stands, which factors are thin, what never got answered.
2. The three final factor texts, ready to paste into CAS2Net, each with its character count from
   the checker.
3. An evidence table: every claim, its ledger entry id, its source, and its basis. This is what I
   take into a panel discussion.
4. The descriptor map: for each final statement, the descriptor line at my target level it lands
   on, and then the discriminators nothing in the package touches, per factor.
5. Raise or award tags per statement, and which argument the package supports overall.
6. The bench: the ready entries that did not make it in, plus one punchier and one safer alternate
   for each final statement.
7. A crib sheet for my supervisor: my three biggest contributions, the hard counts, what is worth
   adding from the bench, an "exceeding expected contributions" rationale per factor in the target
   level's descriptor language, a substantial-justification paragraph if a promotion or other
   special situation applies, the raise or award tags, and reminders to concur with my certification
   statements and to document the midpoint discussion.
8. Next-cycle seeds: KPIs worth writing into next cycle's contribution plan, plan objective ideas
   from the uncovered discriminators, and capture reminders.

Then set every used entry to submitted and print both blocks in full one last time.
```

Paste each factor into its own CAS2Net field, check every fact before saving, and save often;
CAS2Net times out after about 15 minutes of inactivity and unsaved text is gone. Give the crib
sheet to your supervisor before the employee due date. Keep both blocks: next cycle they are what
makes all of this faster, and they are what carries the work into the Claude Code toolkit if you
ever move to it.

For a midpoint, skip the crib sheet, the bench, and the seeds. Your supervisor gives feedback with
no scores and records the date and method of the discussion in CAS2Net, and this text becomes the
jump point for the annual, which will need a delta rather than a repeat.

For a closeout, remember the 30-day deadline, and that the gaining supervisor reads it when
recommending the annual score.
