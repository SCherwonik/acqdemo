# Gen AI Port: Gemini Agent Builder

Date: 2026-09-16. Target: the Gemini agent builder on a government network. Source of truth stays
`skills/`; everything under `gen_ai/` is generated or derived from it.

## Why this exists
The Claude Code plugin assumes a shell, a file system, and a plugin loader. Many users have none of
those. They have a browser, an agent builder, and file upload. This port keeps the two things that
carry the value: the question sequence and the deterministic checks.

## Platform facts (observed in the builder, 2026-09-16)
| Field | Limit or behavior |
|---|---|
| Agent name | 128 characters |
| Agent description | 500,000 characters |
| Agent instructions | 500,000 characters, required |
| Model | Per agent, chosen from a dropdown. Both a Flash tier and a Pro tier are available; subagents default to Flash |
| Connectors | Per agent; Enterprise Web Search is attached by default |
| Knowledge | File uploads on the primary agent, "files your agent can reference" |
| Personalization | Three starter prompts |
| Subagents | Unlimited, added as children of the primary on a flow canvas |

Consequences:
- The whole corpus is about 147,000 characters, so nothing needs condensing to fit.
- **Remove Enterprise Web Search from every agent.** Rules must come from the attached references,
  not from the open web. Web results about AcqDemo are frequently out of date or from another pay pool.
- Subagent descriptions are routing keys. The rule learned on Claude applies unchanged: never name
  another agent's subject matter in a description, even to exclude it, because it attracts those requests.
- Pro is available, so instructions are a faithful port of the skill files rather than stripped
  checklists. Richness is where the Claude version's quality comes from. Use Pro for the primary agent
  and for the three judgment subagents; Flash is fine for the two mechanical ones, and those two are
  what to downgrade first if Pro is rate limited on the tenant.
- Explicit stop points stay, for a different reason than model capability. The agent must wait for the
  user to answer, and the chat equivalent of "save before you ask" is to emit the updated ledger block
  BEFORE asking the next round, never after. An early Claude version asked eight questions and saved
  nothing, so a closed window restarted from the beginning.

## What the user cannot do here
1. **No voice input.** The Claude version assumes a 2,500-word spoken ramble. Typed input yields a
   fraction of that, and everything downstream depends on intake volume. The port answers this three ways:
   - Recognition over recall: documents go in first, the extractor proposes a candidate list, and the
     user corrects and adds rather than generating from a blank prompt.
   - A worksheet the user fills in offline, over several days, and uploads.
   - Yes/no and pick-from-list questions wherever an open question would otherwise be used.
2. **No file writes.** The ledger becomes a fenced block the orchestrator re-emits at the end of every
   round. The user keeps it in a document and pastes or uploads it to resume. This replaces `session-state.md`.
3. **No shell.** Git mining is not ported. The calendar export is uploaded as a text file instead.

## Architecture
One primary agent, five subagents, one offline checker.

| Agent | Role | Model | Why it is separate |
|---|---|---|---|
| AcqDemo Assistant (primary) | Intake, cycle stage, question rounds, holds the ledger, routes | Strongest available | Continuity. The question thread and the ledger cannot be handed off |
| Document Extractor | Reads uploaded appraisal, midpoint, plan, and calendar files; returns structured candidate entries | Fast | Keeps hundreds of pages out of the primary's context |
| Ledger Keeper | Turns a round of answers into correctly formatted ledger entries; reports missing fields | Fast | Format discipline is mechanical and does not belong in the conversation |
| Factor Drafter | Ledger entries in, paste-ready C-R-I factor text out | Strongest available | The style ruleset is large and only needed at drafting time |
| Evidence Auditor | Every claim traced to something the user said or a document; flags anything unsupported | Strongest available | Fresh context is the point. On the real FY26 run this caught eight unsupported claims precisely because it had not sat through the drafting |
| Panel Reader | Reads as a pay pool panel would, names the fixes | Strongest available | Same argument: a reader who did not write the text |

The character cap, C-R-I labels, banned wording, and repeat detection are **not** given to any agent.
They go to `gen_ai/checker/acqdemo-checker.html`, which is arithmetic and string matching.

## Ledger in chat
The orchestrator ends every round with a fenced block the user saves:

    ```ledger
    ## L-007
    - status: ready
    - what: ...
    ```

Field names and allowed values are unchanged from `skills/start/references/ledger-format.md`, so a
ledger written on either platform is valid on the other. Resuming means uploading or pasting the block back.

### Two blocks, not one
A review caught session state being emitted as a `## SESSION STATE` heading inside the ledger block.
Run through the real `ledger_check.py` that produces `BAD_ID` and `MISSING_FIELD`, both CRITICAL, every
round, which the Ledger Keeper is told to flag and the orchestrator is told to fix before asking
anything else. A permanent stall on an error that cannot be fixed without deleting the session state.

The user therefore saves **two** fenced blocks, and nothing else:

1. A ```ledger block holding only `## L-NNN` entries. It must pass `ledger_check.py` unchanged.
2. A ```workspace block holding four sections that mirror the four Claude-side files:
   `# Profile` (career path, current level, target level, rating period, supervisor counts,
   certifications and dates, EOCS, repositories), `# Pay pool` (mandatory paragraph order, the `C:` or
   `W:` label, due dates, promotion window), `# Roster` (the five rings), and `# Session state`
   (`step`, `current_entry`, `round`, `pending_questions`, `next_action`, `open_questions`, `updated`).

The workspace block is what makes resume work. Without it a saved ledger loses the career path and
target level, and both the Factor Drafter and the Panel Reader are specified to stop when those are
missing. Every subagent that emits or consumes these blocks uses these two names and no others.

### Arming the checker
The page's Setup panel gates CRITICAL findings: cycle stage sets the minimum entry count, and the
prior-text and names boxes are what make `PRIOR_REPEAT` and `NAME_IN_TEXT` fire at all. Left empty they
pass silently, so two never-miss rules would go unchecked. The orchestrator holds this material, since
the Document Extractor returns the prior-cycle text and the roster carries the names. It therefore
emits a ready-to-paste checker setup block naming every field's value before sending the user to the page.

## Rules the live run forced
Sixteen findings from a real employee running the pack against his own documents
(`docs/superpowers/validation/gen-ai-live-run.md`). Most collapse into five rules, and each belongs
in one place so the agents cannot disagree about it.

1. **Conflict is a question, never a merge.** When a new value contradicts one already held, from a
   document or from the user, stop and ask which governs. Do not store both in separate fields, do
   not concatenate them, do not silently prefer the newer one. This one rule covers a missed
   promotion (a prior appraisal and a plan disagreed about broadband level), an unreconciled
   expected contribution score, and a supervisor carried in from the wrong cycle. It is the single
   highest-value fix in the list.
2. **Instructions are answered before attachments are read.** Every instruction in a message is
   applied, refused, or asked about, and named in the reply, before any uploaded file is processed.
   A turn that carried three corrections and an answer alongside an upload delivered the document
   work perfectly and dropped all four, including an answer to a question the same reply then asked
   again. Resending them without the attachment landed all four, which isolates the cause.
3. **Evidence names the true origin.** A fact the user supplied is `user stated in conversation
   <date>`, not the document the entry came from. A file is named exactly as supplied. A fact read
   from a prior-cycle document carries that cycle with it.
4. **Never invent extends past events.** It already covers events, audiences, awards and
   recognition. It also covers dates, including inferring one from a document's own date, and how a
   system behaves. Say what a record shows and what it appears to correspond to.
5. **A correction propagates.** Changing a value in the workspace block updates every ledger entry
   whose text restates it, or lists them for the user. Two blocks disagreeing is the failure the
   split was meant to avoid.

## Layout
```
gen_ai/
├── README.md                          what this is and which platform it targets
├── gemini/
│   ├── setup.md                       click-by-click, using the builder's own field names
│   ├── orchestrator.md                paste into the primary agent's Instructions
│   ├── starter-prompts.md             the three Personalization prompts
│   └── subagents/
│       ├── document-extractor.md      each file holds Name, Description, Instructions ready to paste
│       ├── ledger-keeper.md
│       ├── factor-drafter.md
│       ├── evidence-auditor.md
│       └── panel-reader.md
├── knowledge/                         files to upload into the Knowledge panel
├── worksheets/brain-dump-worksheet.md typed substitute for the spoken ramble
├── checker/acqdemo-checker.html       single file, offline, no network calls
└── prompts.md                         fallback for a plain chat box with no agent builder
```

## Inline versus Knowledge
- **Inline in instructions** (must never be missed): the step sequence, the ledger format, the estimate
  protocol, no names in factor text, the character cap, certification statement handling, the rule
  against inventing events or awards.
- **Knowledge files** (looked up): career path descriptors, the question bank, CCAS rules, document
  retrieval instructions, worked examples.

## Checker parity
The rule corpus lives inside the HTML as a JSON block between markers. The page runs it only when the
URL carries `?selftest=1` or `#selftest`, or when a maintainer calls `window.ACQ_SELFTEST()`; it is
invisible to an ordinary user, because a wall of green rows about built-in samples reads as a verdict
on the draft in the boxes. A Python test parses the same block out of the HTML and runs every fixture
through `skills/review/scripts/check.py`, asserting identical findings. One corpus, two engines, no
Node required. Drift fails `pytest`.

### The one accepted difference
`check.py` reads a set of prior files and reports a repeated run once per file it appears in. The page
has a single prior textarea, so it merges that material and reports the maximal run once. Verified
against a real FY26 annual, its drafts, and a midpoint: across five documents the page reported fewer
lines, and **every** run the Python reported and the page did not was contained inside a longer run the
page did report. Nothing goes undetected; the page is less repetitive about the same repeat.

## Build and test
`tools/port/build_gen_ai.py` generates `gen_ai/knowledge/` from `skills/start/references/` and verifies
that the generated pack contains no Claude-specific wording, no `../` reference paths, and no agent
instruction over the platform limit. Tests live in `tools/port/tests/`.

## Not ported
`acqdemo:extract` git mining, the probe harness, and plugin packaging. The plan skill works only if
the user pastes their position duties, since there is no `prd_text.py` to read the .docx for them.

## Open
Grok's skills and subagent format. The pack is plain markdown with a short header per agent, which
should adapt, but nothing here is verified against Grok.
