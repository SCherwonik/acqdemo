# Starter Prompts

The builder's Personalization panel takes three starter prompts. These are the three. Paste one per slot, exactly as written, on the primary agent only. Subagents do not use them.

The wording matters more than it looks. Each prompt lands the user on a specific branch of Step 4 of the orchestrator instructions, and each one makes the agent's first reply the document ask rather than a menu.

## Slot 1

```
Help me write my annual AcqDemo self-assessment. Tell me what documents to pull first.
```

Leads to the full annual path: the document ask, the Document Extractor on whatever is uploaded, the candidate list, the recall sweeps, deep-dives, allocation, drafting, and the three-layer check.

## Slot 2

```
Help me write my midpoint self-assessment for this cycle.
```

Leads to the same engine with the midpoint differences applied, starting with the document ask itself. A midpoint gets its own list: the last completed cycle's Salary Appraisal exported with Check All, this cycle's Contribution Plan, any closeout already written, and a calendar export covering cycle start to today. It does not ask for a midpoint assessment, because that is the document the user is sitting down to write. The plan is the jump-off point instead of a prior midpoint. After that: two strong entries per factor instead of four, no scores, no Very High language, and no supervisor crib sheet.

## Slot 3

```
I have a saved session from last time. Ask me for my blocks so we can pick up where we left off.
```

Leads to the resume path. The wording matters here more than in the other two slots, and it was changed after a review caught the failure. A clicked starter prompt sends its sentence and nothing else: no file, no pasted text. The earlier wording, "Here is my saved ledger block", promised an attachment that was never there, and the agent's resume branch is gated on a block actually being present, so the click landed on the full document ask and the user was asked to pull their appraisal again.

This wording asks the agent to ask. The agent requests both blocks by name, the `ledger` block and the `workspace` block holding Profile, Pay pool, Roster, and Session state, the user pastes them or uploads the document they kept them in, and only then does the agent read Session state, say in two lines what step it stopped on and what the ledger already holds, and continue from next_action without re-asking anything the blocks already answer.

The orchestrator handles the other order too: a user who pastes a block into their very first message skips straight past the ask. And a user who brings only the ledger is told plainly that the evidence is there but the profile is not, and gets one short round to rebuild the career path, levels, and pay pool rules before drafting.

This slot is mainly for work carried in from elsewhere: another chat, or the Claude Code version of the toolkit, which uses the same ledger format. Reopening a chat on this platform resumes it with its own history, so most people will never need it, and it costs nothing to keep.

## If a slot is ever freed up

Only three slots exist, and the resume prompt keeps one of them: it is the only route back into work that started somewhere else, in another chat or in the Claude Code toolkit, and without file writes there is no other handle on it. Everything else the agent does is reachable by typing. These two are the strongest candidates if the annual or midpoint slot is ever reassigned:

```
I want to write down one win while it is fresh.
```

Leads to the one-win capture: one candidate entry, at most six numbered questions, a ledger block, and done. No long path.

```
Review the self-assessment draft I already wrote.
```

Leads to the check. The agent says up front that a draft arriving with no evidence ledger behind it cannot go through the middle layer as it stands, and offers the choice: spend a round or two building a minimal ledger from the draft so every claim can be traced, or run the checker and the Panel Reader only and accept that nothing has been traced. Then the offline checker, the Evidence Auditor if there is a ledger, and the Panel Reader.
