# Gen AI Pack

The AcqDemo toolkit, rebuilt for a browser-based agent builder instead of a command line.

The Claude Code plugin in `skills/` assumes a shell, a file system, and a plugin loader. Plenty of people who have to write an AcqDemo self-assessment have none of those. What they have is a government workstation, a browser, an approved gen AI agent builder, and the ability to upload a file. This pack is for them.

It ports the two things that carry the value: the question sequence that gets a year of work out of someone's head, and the deterministic checks that keep the result defensible. Everything else is scaffolding that did not survive the move.

## Who this is for

A Department of Defense AcqDemo employee, at any career path and broadband level, writing their own contribution plan, midpoint assessment, closeout, or annual self-assessment. No programming, no install, no command line. Someone has to build the agent once, following `gemini/setup.md`, and hand out two loose files with it: `checker/acqdemo-checker.html` and `worksheets/brain-dump-worksheet.md`. Employees never see this repository, so the agent names those two by file name and expects the builder to have distributed them. After that anyone with access to the agent can use it.

The target platform is the Gemini agent builder available on government networks. The pack is plain Markdown with a short header per agent, so it should adapt to other agent builders with similar fields, but nothing here has been verified against any platform other than Gemini.

## What is in here

```
gen_ai/
  README.md                          this file
  gemini/
    setup.md                         click-by-click build, using the builder's field names
    orchestrator.md                  paste into the primary agent's Instructions
    starter-prompts.md               the three Personalization prompts
    subagents/                       one file per subagent, ready to paste
  knowledge/                         files to upload into the Knowledge panel
  worksheets/brain-dump-worksheet.md typed substitute for the spoken ramble
  checker/acqdemo-checker.html       single file, offline, no network calls
  prompts.md                         fallback for a plain chat box with no agent builder
```

The architecture is one primary agent, five subagents, and one offline checker. The primary agent holds the conversation and the evidence ledger. Document Extractor reads uploaded documents. Ledger Keeper formats answers into ledger entries. Factor Drafter writes the paste-ready text. Evidence Auditor traces every claim back to evidence. Panel Reader reads the result the way a pay pool panel would.

The character cap, the C-R-I label rules, banned wording, repeat detection, and the check for names that leaked into the text are given to no agent at all. They are arithmetic and string matching, and they live in `checker/acqdemo-checker.html`, which runs in the browser with no network calls. Before sending anyone to that page the agent emits a setup block filling in every field the page needs, including the prior cycle's text and the roster's names, because the repeat check and the name check do not run on an empty box. The employee pastes that setup in along with their draft, runs it, and pastes the findings back into the chat.

`prompts.md` is the same flow for someone who has a chat box but no agent builder: copy-paste prompts, stage by stage, with no subagents. It loses the fresh-reader passes and the extractor's isolation, and it says so.

## What it cannot do, compared with the Claude Code plugin

Read this section before deciding which version to use. The differences are real and three of them cost quality.

**No voice input.** This is the big one. The Claude version assumes a long spoken ramble, often two thousand words or more, and most of the evidence in a finished assessment comes out of it. Typing produces a fraction of that. The port answers this three ways: documents go in first so the user corrects a list instead of generating one from nothing, questions are yes/no and pick-from-list wherever an open question would otherwise be used, and `worksheets/brain-dump-worksheet.md` lets the user write offline over several days and upload the result. Those help. They do not fully replace talking for forty minutes.

**No file writes, so nothing is checked on the way past.** The plugin saves a ledger, a profile, a pay pool overlay, a roster, and a session state file after every exchange, and runs `ledger_check.py` over the ledger each time, so a malformed entry surfaces in seconds. Here that state lives in two fenced blocks the agent holds: a `ledger` block carrying the evidence entries and nothing else, so it stays valid against that same `ledger_check.py`, and a `workspace` block carrying `# Profile`, `# Pay pool`, `# Roster`, and `# Session state`. The agent shows both in full at checkpoints, when an entry is finished, before the allocation, before drafting, at the end, and whenever asked, and between those it confirms in one line what it recorded. Reading those blocks is the employee's substitute for the checker: a wrong number caught at the ledger stage costs one sentence, and the same number caught at the evidence audit costs a redraft. Field names and allowed values are identical to the plugin's, so the pair also moves a cycle between this agent and the plugin in either direction.

**No shell, so no git mining.** `acqdemo:extract` mines repositories for commit-level evidence with dates and release milestones. That is not ported. The calendar export is uploaded as a text file instead, which recovers the meetings but not the code.

**No automated checking inside the conversation.** The plugin runs `ledger_check.py` after every ledger save and `check.py` on every draft, so a malformed entry or an over-length factor surfaces within seconds. Here the checker is a separate browser page and the user has to go run it. The same rules, checked at a slower cadence, and only when someone remembers.

**No contribution plan help from a PRD file.** The plan path works only if the user pastes their position duties as text, because there is no script here to read a .docx for them.

**No probe harness, no plugin packaging, no automatic updates.** When a file in this pack changes, someone re-pastes it into the builder by hand.

## What is the same

The question bank, the recall sweeps, the drill-down ladder, the estimate protocol, the ledger format, the descriptors, the writing rules, and the checker's rule corpus. The rule corpus in the HTML checker and the plugin's `skills/review/scripts/check.py` are tested against each other, so a draft that passes on one passes on the other.

The safety rules are the same and they are not negotiable on either platform: never invent events, audiences, awards, recognition, dates, or how a system behaves; numbers are proposed as estimates, confirmed by the user, and recorded with a basis; no people's names in factor text; the current cycle's midpoint is the starting point and prior cycles are off limits; stop the user if they begin to share classified information; at most 3900 characters per factor.

Three rules came out of a live run against a real employee's own documents and they are written into the orchestrator's instructions. A value that contradicts one already held is a question, never a merge: the field carries a marker naming both values with their sources and dates until the employee says which one governs, so nothing downstream can draft from a number nobody chose. Before the deep-dive questions begin, a special-situation pass asks five questions about the cycle itself, covering a broadband level that differs between documents, a supervisor change, any closeout found, an organization change, and a certification change, because each of those changes what the finished text has to say and none of them is ever inferred. And certification statements read out of a prior cycle's appraisal are marked unconfirmed and refreshed by asking, because a year-old certification statement is well formed, passes every rule the checker runs, and is wrong.

Two more came from the same run and both are about what the agent writes down rather than what it says. Nothing enters the `# Pay pool` section that was not read from a document or supplied by the employee, and every line in it names which, because an invented rule recorded there is read back by every later session as the employee's own pay pool policy, where an invented sentence in a reply would have been corrected on sight. And the bench test is stated once, applied to every candidate, and named in the allocation, so an employee can see which rule benched their work rather than inferring it from the outcomes.

## Privacy

An employee's own documents go into a chat conversation, never into the agent's Knowledge panel. A CAS2Net salary appraisal is normally marked CUI and often carries salary. The Knowledge panel holds only the public reference material that ships with this toolkit.

Nothing classified belongs in any of it: not in a document uploaded here, not in a calendar export, not in the conversation. The agent is instructed to stop the user if they begin, and the user should not rely on it catching them.

## Source of truth

`skills/` is the source. Everything here is derived from it. Fix a rule there first, then bring it across.
