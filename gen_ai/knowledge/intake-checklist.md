# Intake Checklist

> Platform note. This copy is for an agent with no file system. Where the text below names a
> workspace file or folder such as `profile.md`, `paypool.md`, `roster.md`, `ledger.md`, or
> `FY<yy>/evidence/`, read it as a block of text kept in the conversation: the assistant
> re-emits those blocks at the end of every round and the user keeps them in a document of
> their own. Source documents are uploaded in the chat rather than saved into folders. Field
> names, allowed values, and every rule below are unchanged.

What to ask a user for when setting up an AcqDemo workspace, where each item goes, and what it buys. Walk it out loud, one item at a time: name the item, say in one sentence what it unlocks, ask whether they have it, and take it however it comes (a file path, a paste, a screenshot's text, or "skip").

The toolkit already ships the public reference material: factor descriptors for every career path, CCAS assessment guidance, and an example pay pool's business rules. Never ask the user for those. Ask only for the things about **them**.

Nothing is required to start. With only the profile the toolkit still works; every item added makes the draft more specific and easier to defend.

## Which situation is the user in
Ask this before asking for documents, because it decides what exists to ask for:

1. "Have you been through an AcqDemo cycle before, and did you submit a self-assessment last cycle?"
2. "Did you write a midpoint self-assessment this cycle?"
3. "Did you change position or supervisor during this cycle?"

| Situation | What to ask for | What changes |
|---|---|---|
| Returning: submitted last cycle, wrote a midpoint | Both priority documents below | The normal path |
| Returning, no midpoint (or it was skipped) | The prior-cycle export only | The annual covers the whole cycle from scratch; say so, and lean harder on the calendar export and the memory sweeps |
| New to AcqDemo this cycle (new hire, or converted from another system) | No prior assessment exists. Ask for the contribution plan, the PRD, the entry-on-duty or conversion date, and any probationary or onboarding milestones | The rating period starts at their entry date, not 1 October; prior-cycle repeat checks are skipped because `prior/` is empty; the plan and PRD carry the vocabulary the prior documents would have |
| Changed position or supervisor mid-cycle | Any closeout the losing supervisor wrote, plus both priority documents | Closeouts are evidence for the partial period and the gaining supervisor weighs them; note each supervisor and the dates in `profile.md` |
| Has nothing at hand right now | Nothing | Five minutes of position questions, then straight into the memory sweep. Say plainly that anything found later can be dropped in and folded back |

Record the answer in `profile.md` (`first_cycle`, entry date, supervisors and dates) so later steps stop asking for documents that do not exist.

## Ask for these two first
| Document | Why it matters most | Where it goes |
|---|---|---|
| **The CAS2Net export for the last completed cycle** (the full appraisal or assessment package; usually a PDF) | Holds the prior cycle's submitted assessments, the supervisor narrative, scores, EOCS, value of position, and often the prior contribution plan. It shows what this person does, how their pay pool words things, and what they must not repeat this year. | Text into `prior/FY<yy>/`; profile values (EOCS, value of position, scores) into `profile.md`. Keep the rest of the source PDF out of the conversation (see Privacy). |
| **This cycle's midpoint review** (PDF, docx, text, or markdown) | The starting point for the annual: work already claimed, in the user's own words, which the annual builds on with a delta rather than repeating. | `FY<yy>/midpoint/final/`, one file per factor when it splits cleanly |

If the user does not have either one saved, both come out of CAS2Net; the click-by-click steps, and which sections to tick, are in `getting-your-documents.md`.

Pull the last completed cycle's salary appraisal with every section checked: one file holds that cycle's employee and supervisor assessments, its midpoint, its closeout, the plan it ran under, and the scores. Steps are in `getting-your-documents.md`. Upload the export in the chat (pdf, docx, pptx, txt, md). A long export PDF is easier to work through a section at a time. If a format will not open, ask the user to paste the text instead; never make them retype a document.

## Then these, if they exist
| Item | Where it goes | What it buys |
|---|---|---|
| Contribution plan for this cycle, and the prior cycle's plan | `FY<yy>/plan/`, prior plan text into `prior/FY<yy>/` | Objective labels (JA1, CT1, MS1) to tie contributions to, the 90-day eligibility check, and a clear picture of the kind of analyst or engineer this person is |
| Position Requirements Document (PRD) | anywhere in the workspace; path in `profile.md` `prd_path` | Duty numbers to tie each contribution to, and the vocabulary of the position |
| Calendar export for the rating period | `FY<yy>/evidence/` | The single best memory jog; drives the timeline walk and the people sweep (steps in the question bank) |
| Earlier cycles' assessments, if they want a longer no-repeat window | `prior/FY<yy>/`, one folder per cycle | Blocks repeating older wording, which pay pools penalize |
| Their pay pool's own business rules or this year's guidance email | values into `paypool.md` | Local due dates, minimum entries, mandatory paragraph order, label style. The shipped example is a fallback, not their rules. |
| Projects, notebooks, or shared folders they work in | Named in the profile block | Product and release names to ask about by name |
| Praise emails, award citations, time-off awards | `FY<yy>/evidence/` | Recognition facts that are safe to cite because they happened |
| Slide decks or papers they authored | titles are enough, into the ledger | Artifact prompts that recover forgotten work |

## Five minutes of questions, no documents needed
Career path (NH, NJ, NK) and broadband level; series and title; organization; rating period; supervisor of record and any earlier supervisors this cycle with dates; whether they supervise anyone and the counts; certifications held or in progress with dates; mission statements one and two levels up; the office map (sections and who sits in each). These drive descriptor selection, mandatory paragraphs, closeout reminders, impact wording, and the people sweep.

## Privacy rules to state once, out loud
- These notes are private. Names, scores, salary, and draft text belong in them and never anywhere public.
- A CAS2Net appraisal export is usually marked PII or CUI, and often contains salary. Take only the text you need out of it, and keep the rest of the export out of the conversation.
- Never put classified material in the workspace, in a calendar export, or in the conversation.
- Keep personnel forms (SF-50, SF-52) and resumes out of the conversation entirely. Do not upload them.

## What to say when the user has nothing
"We can start with five minutes of questions about your position and go straight into a memory sweep. Anything you find later, drop into the workspace and tell me, and I will fold it in."
