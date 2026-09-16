# Question Bank

> Platform note. This copy is for an agent with no file system. Where the text below names a
> workspace file or folder such as `profile.md`, `paypool.md`, `roster.md`, `ledger.md`, or
> `FY<yy>/evidence/`, read it as a block of text kept in the conversation: the assistant
> shows those blocks at each checkpoint and the user keeps them in a document of
> their own. Source documents are uploaded in the chat rather than saved into folders. Field
> names, allowed values, and every rule below are unchanged.

Recall is the bottleneck. Ask more, not less.

## How to ask
- Number every question in a round (1, 2, 3...) so the user can answer them one at a time: "number four: ...".
- Group questions under a short heading (the project, sweep, or factor being explored).
- Rounds of 5-8 questions work well; there is no cap on the number of rounds.
- Rambling is welcome. Extract facts from long answers; do not ask the user to restructure them.
- Say names back when the user gives them ("So you trained Pat, Lee, and Morgan from the estimating branch."). Names stay in private notes only.
- Confirm every number with its source: stated, documented, or estimate (see Estimate protocol).
- End every round with: "What else does that bring to mind?"
- "I don't know" and "skip" are always acceptable. Move on without pressure.
- Never ask about topics the user has not raised unless the question comes from a recall sweep or the gate list.

## Brain dump prompts
Open the dump with 8 to 10 numbered prompts, never a single "tell me everything". Build the list in this order and stop at ten.

**First, from the user's own material** (one prompt each, naming the actual duty, objective, project, or meeting series, because a named prompt recalls far more than a general one):
1. Position duties: ask the user to upload or paste their Position Requirements Document (PRD), then ask about the two or three duties that carry the most weight. "Your PRD duty 3 is <duty>. What did you do against that this cycle?"
2. Plan objectives: for each labeled objective (JA1, CT1, MS1) in `FY<yy>/plan/`, "What did you deliver toward <objective>?"
3. Anchors from what the user uploaded: the biggest projects, recurring meeting series, releases, and the midpoint or closeout claims. "You have <n> meetings on <series> between <month> and <month>. What was your part?"

**Then fill the rest from these openers.** They work for any series, career path, and organization, and for someone whose work leaves no git or calendar trace:
- **Products:** What did you produce this cycle that somebody else used? Estimates, models, tools, datasets, analyses, briefings, papers, policies, decisions.
- **Recurring duties:** What does your position require every cycle that you did again this year, and what was different this time?
- **Customers:** Who asked you for something, and what did they do with what you gave them?
- **Firsts:** What did you do this cycle that you, your office, or your organization had never done before?
- **Fixes:** What was broken, slow, manual, wrong, or risky that you improved? What would have happened if you had not?
- **People:** Who did you teach, train, mentor, review, onboard, or unblock?
- **Rooms:** Which meetings, reviews, working groups, or forums did you speak in, and who was in the room?
- **Scope changes:** New position, new duties, new supervisor, promotion, or extra duties. What got bigger or harder?
- **Problems:** What went wrong this cycle (shutdown, missing data, staffing, schedule, a failed tool) and what did you do about it?
- **Volume:** Roughly how many of the main thing you do did you handle: estimates, reviews, models, requests, audits, tickets, cases?

Close the round with "What else does that bring to mind?" Rambling, jumping around, and "skip" are all fine. Never suggest an accomplishment the user has not mentioned; ask about their work, do not supply it.

## Drill-down ladder
Apply to every accomplishment until it has enough for a strong C-R-I:
1. **What** exactly did you do? What was your role: owned, co-owned, owned a piece, or supported?
2. **So what?** What came out of it (product, decision, fix, capability)?
3. **Who used it?** Which people, teams, organizations, leaders? How many?
4. **What changed?** Before vs. after in time, cost, quality, risk, speed, or capability.
5. **Will it keep happening?** Is this now how things are done (sustained), or was it a one-time event?

## Confirm before dropping
When the user cannot expand on a claim from the midpoint, a closeout, or the plan, do not drop it after an open question. Switch to short yes/no questions built from the entities the claim or the workspace names (organizations in `roster.md`, meetings, budget rounds, audiences):
- "The midpoint says you organized key meetings. Were any with <organization>? Did you run them, or attend?"
- "Was that work aligned to <budget position>? More than one round?"
- "Was <group> in the room? More than <n> people?"
Keep the parts the user confirms; drop the claim only when the user cannot confirm any part or says it did not happen. If answers conflict with each other or with the document, the later answer wins; record the conflict and the correction in the entry's `notes`.

## Portfolio roll-up
Run once after the deep-dives, before allocation. Single entries hide the size of the year; totals across entries are often the strongest scope numbers.
1. Count across all `ready` entries and `roster.md`, each item once:
   - Distinct programs, estimates, systems, or teams supported.
   - Distinct organizations engaged, and how many of those groups or meetings the user led.
   - Senior-leader briefings: how many, highest rank or grade, total headcount.
   - People trained or mentored.
   - Forums, conferences, or communities briefed: how many, and the size of each audience.
   - Dollars influenced: program or portfolio value, budget constraints, or trade space.
2. Read each total back: "I count <n> <items>: <list>. Is that right? Did I miss any?"
3. Turn confirmed totals into stacked phrasing, for example "across 5 programs and 3 organizations" or "briefed 2 senior-leader forums totaling about 60 people". Record each total in the `numbers` of the entry that will carry it, with the counted ledger ids as the basis.

## Question types
| Type | Templates |
|---|---|
| Scope | What was the dollar value of the program or portfolio? How many programs, systems, datasets, or estimates did it touch? How many users or analysts? |
| Audience | Who was in the room? What was the highest rank or grade (SES, SL, O-6, GS-15 equivalent)? How many attended? Were they inside or outside your organization? |
| Role | Who asked you to do it? Did you own it, share it, own a piece, or support someone else? Who worked with you, and who worked for you? |
| Before and after | How was this done before? How long did it take then and now? What broke or went wrong before? |
| Obstacle | What almost stopped it: deadline, shutdown, missing data, a broken legacy product, competing priorities, a disagreement? |
| Decision | What decision did it feed: budget, program, acquisition strategy, schedule, policy? Who made the decision? |
| Significance | Was this a first for the organization? One of a kind? Interagency? On a short deadline? Done alongside competing priorities? |
| Sustained | Is this now standard practice or recurring each cycle? Who else depends on it going forward? |
| Recognition | Did anyone thank you, cite it, request more of it, or give an award or time off for it? |
| Evidence | Where would proof live: repository, file, slide title, email subject, meeting title? |

## Gate questions
Ask once per cycle, before drafting. Unknown answers are recorded as gaps, never guessed.
1. What is your career path and broadband level as of the last day of the cycle?
2. What is your EOCS for this cycle? If it changed during the year, what was it before and after?
3. What are the exact rating period dates?
4. Can you paste your contribution plan objectives (and any revised plan)?
5. What is your certification status: certification name and level, date, continuous learning points or CETs earned, due dates?
6. Who were your supervisors this cycle, with dates? Were closeouts done?
7. Were you promoted, reassigned, or given new duties this cycle? Effective dates?
8. Do you supervise anyone or manage contractors? Exact counts of military, civilians, and contractors.
9. Did you receive any awards or time off awards this cycle? For what?

## Discriminator questions
Pick the questions that fill gaps in the current ledger entry. Adapt wording to the project; never read them as a script.

### Job Achievement and/or Innovation

#### Leadership Role
- Did you lead this, or lead part of it? How many people or teams did you coordinate?
- Did anyone take direction from you, formally or informally?
- Did you set the approach others followed?

#### Mentoring/Employee Development
- Who did you teach, train, or mentor? Names, roles, and how many sessions?
- Did anyone you helped go on to do something on their own because of it?
- Did you create training material or documentation others still use?

#### Accountability
- What were you personally on the hook for? What deadline or deliverable carried your name?
- What would have happened if you had not delivered?

#### Complexity/Difficulty
- What made this hard: data quality, technical depth, many stakeholders, ambiguity, scale?
- Did you find and fix errors or defects in existing products, models, or processes?

#### Creativity
- Was your approach new for your organization? Did you invent a method, tool, or technique?
- What did you try that others had not?

#### Scope/Impact
- How far did it reach: your team, division, agency, headquarters staff, service, DoD, Congress?
- What dollar values, program counts, or user counts are attached?

### Communication and/or Teamwork

#### Oral
- What briefings, demonstrations, or presentations did you give? To whom, how many, highest rank?
- Did any briefing seek a decision or consensus? What was decided?
- Was any session part of a larger forum, conference, or community (organization-wide, service-wide, DoD-wide)? How many were invited or attended across all sessions, and who made up the audience (grades, organizations, career fields)?

#### Written
- What did you write or co-write: reports, memos, documentation, user guides, specifications?
- Who read it and what did they do with it?

#### Contribution to Team
- Which teams or working groups did you participate in or lead? Across which organizations?
- Did you resolve a disagreement or align different approaches? Between whom?

#### Effectiveness
- Did your communication change anything: adoption, fewer questions, faster turnaround, fewer revisions?
- Did another organization, or an office above yours, start using what you briefed or wrote?
- Were you sought out for help? By whom and how often?

### Mission Support

#### Independence
- How much guidance did you need? Did you define the problem yourself?
- Did you anticipate a problem before it hit?

#### Customer Needs
- Who were your customers (program offices, leadership, other divisions, analysts)?
- Did a customer ask for something specific that you delivered? Did you translate their need into a product?
- Did an office above yours (headquarters staff, a service secretariat, OSD) or another organization adopt your product for a decision or for funding? Which decision?

#### Planning/Budgeting
- Did your work influence cost, schedule, or resource decisions? How much money or time was involved?
- Did you plan resources across more than one project?
- Did the work align programs or estimates to a budget position (for example the President's Budget, POM, or FYDP)? Through how many rounds, and against what dollar value, constraint, or trade space?

#### Execution/Efficiency
- What got faster, cheaper, or more accurate? By how much?
- What manual work did you eliminate or automate?

## Recall sweeps

### Calendar export
Ask for this before the timeline walk. If the user has not uploaded a calendar export, give them these steps (classic desktop Outlook):
1. Calendar > **View** tab > **Change View** > **List**.
2. Sort by the **Start** column, or **View Settings > Filter** to the rating period.
3. Optional: right-click column headers > **Remove This Column**; keep **Subject** and **Start**.
4. Click the first meeting, **Shift**+click the last, **Ctrl + C**.
5. Paste into Notepad, save it as a plain .txt file, and upload it in the chat.
Then ask for a calendar sweep of that file. Remind the user never to export from a classified system and to delete sensitive titles.

### Timeline walk
1. Build a month list from the first to the last month of the rating period.
2. Seed each month with anchors already known: meetings from the calendar export (especially briefings, demos, working groups, and recurring series), releases and version dates, midpoint and closeout dates, promotions or moves, awards, shutdowns, budget or program milestones the user mentioned.
3. Walk month by month: "In <month>, I have <anchors>. What else was going on that month? Any briefings, deadlines, fires, trips, trainings?"
   With no calendar export, do not ask open month-by-month questions. Walk the budget and program milestones instead (budget build and submission, budget release, program reviews and decision points, fiscal year end, shutdowns): "What did you deliver for <milestone>?"
4. Every new item becomes a candidate ledger entry.

### People rings
First time only: ask the user to describe their office map (sections or teams and the people in each). Save it to `profile.md`.
Then sweep ring by ring. Ask for names explicitly.
1. **Own office, section by section:** "Did you help anyone in <section>? Name them. What did you do with or for each?"
2. **Other divisions or directorates:** "Which other divisions did you work with? Who there, and on what?"
3. **Government outside your organization:** program offices, commands, headquarters staff, other agencies. "Who, what organization, what did you do together?"
4. **Contractors:** "Which contractor companies did you work with? Who in each company? Did you direct, review, or support their work?"
5. **Leadership:** "Which senior leaders did you brief, advise, or answer questions for? What about?"
Record each person in `roster.md` with ring, organization, role, what was done, frequency, and linked ledger entries. Counts from the roster become numbers in statements (people trained, organizations supported).

### Artifact prompts
- "Open your calendar for <month> and read me meeting titles that were yours or where you presented."
- "Search sent mail for 'attached', 'brief', 'slides', 'thanks' and read me subjects."
- "Which chat channels or threads were busiest for you?"
- "Which slide decks or documents did you create or update this year? Titles are enough."
- "Which shared drive folders or repositories did you touch most?"

## Estimate protocol
When the user does not know a number, climb this ladder and stop at the first rung that works:
1. **Evidence:** counts the user can point at in something they have (versions, tags, findings closed), file counts, attendance lists, calendar entries.
2. **Proxy count:** versions released, users onboarded, sessions held, programs supported, datasets processed.
3. **Estimate with a basis the user approves:**
   - Time saved = users x runs per period x hours saved per run.
   - Reach = attendees per session x sessions.
   - Dollar scope = value of the programs or portfolio the work supported.
   - Error reduction = defects found x consequence (for example, a unit error of 1,000x).
   Propose the top of the plausible range, rounded up, phrased "over" or "approximately". When an input is unknown (crew size, runs per month), use its defensible low end, phrase the result "over N" or "about N", and put the assumption in the basis. Ask: "Does <estimate> sound defensible to you?" Record the basis line in the ledger.
4. **No number:** lean on scope, audience, and organizational level instead.
Never estimate events, audiences, awards, or recognition. A vague count the user states stays as stated ("about 40" stays "about 40") unless an Evidence rung supports more. Never add counts that may overlap (the same people in two sessions, the same program in two entries).

## Terms, names, and numbers
Answers arrive typed. Hurried typing still garbles acronyms, program names, tool names, and
people's names, and it does not garble the same word the same way twice.

### Resolve before asking
Before asking the user to repeat or spell a word that does not land, check it against material
that already exists:
- The documents the user uploaded: prior assessments, the midpoint, the contribution plan, the
  position requirements document.
- The profile and roster sections of the workspace block.
- Calendar subjects from the calendar export.
A word that comes out close to a term that appears in any of these is almost certainly that term.

### Match on sound, not spelling
Compare by how the word sounds, not how it is spelled:
- Split or joined words ("re gres sion tool" for "Regression Tool").
- Missing or added plurals ("estimate" for "estimates").
- Homophones ("plan" for "planned", "sight" for "site").
- Letter-by-letter acronyms read as a word ("cas net" for "CAS2Net").

### Correct silently, confirm once
Apply the match silently in the ledger and in notes; do not make the user watch the correction
happen. Say the corrected term back once, in the next message, so the user can object: "I have
this as CAS2Net, the system named in your profile." Move on unless the user corrects it.

### Never guess a name
A person's name never gets the silent-correction treatment. Confirm it against the roster
section, or ask the user to spell it. Names go into private notes and the ledger only, and a
wrong name there is worse than one left unresolved.

### Never drop a term you cannot place
If a garbled word cannot be matched against anything the user has given you, do not drop it and
move on silently. Quote it back exactly as it arrived and ask what it was: "I have '<word>' and
could not match it to anything you have told me. What was that?"

### Numbers written as words
Numbers written out ("a hundred and twenty", "fifteen hundred") are confirmed as digits before
they enter the ledger: "I have that as 120, correct?"

Corrections are kept with the brain dump in a `## Term glossary` section, wrote -> meant, one
line per correction:
```
## Term glossary
- wrote: "re gres sion tool" -> meant: Regression Tool
- wrote: "cas net" -> meant: CAS2Net
```
Later rounds read this glossary first, so the same word is never resolved from scratch twice.

## Coverage grid and stop rule
After each deep-dive, show the grid:

| Factor | Ready entries (primary) | Weakest discriminators |
|---|---|---|
| JA | n | ... |
| CT | n | ... |
| MS | n | ... |

Count each `ready` entry once, under its primary factor (its strongest lens); a second-factor angle does not count. Continue deep-dives until every factor has at least four (three plus a spare), the sweeps and targeted questions turn up nothing new, or the user says "enough." Aim the next questions at the weakest factor and its uncovered discriminators.
