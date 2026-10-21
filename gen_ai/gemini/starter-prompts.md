# Starter Prompts

The builder's Personalization panel takes three starter prompts. These are the three. Paste one per slot, exactly as written, on the primary agent only. Subagents do not use them.

The wording matters more than it looks. Each prompt lands the user on a specific branch of Step 4 of the orchestrator instructions, and each one makes the agent's first reply the document ask rather than a menu. The three document asks differ: the annual list, the midpoint list, and the plan list.

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
Help me start this year's contribution plan, including any Key Performance Objectives my pay pool requires. Ask me for my position requirements document and last year's plan.
```

Leads to the plan path, branch 1 of Step 4. A clicked starter sends its sentence and nothing else, so this is worded as an invitation that makes the agent ask for the documents, never as a claim that something is attached. Step 1 reads the opening message, sees a plan, and answers with the plan's document list: the Position Requirements Document and last cycle's plan. It does not ask for the Salary Appraisal export, the midpoint, or a calendar, which is the annual's list and would be wrong for a plan.

After the documents the agent settles the pay pool's plan rules (how many objectives per factor, whether KPOs are required, how many, how they are labeled, under which factor, and the label style), proposes candidate objectives from the PRD duties for the user to correct, drafts them, and runs a written self-check. The plan is not handed over as paste-ready while any placeholder remains.

## If a slot is ever freed up

Only three slots exist. Resume held slot 3 until the plan prompt took it, for this reason: chats on this platform persist and carry their own history, so reopening a chat resumes it with nothing to paste, and a resume prompt is the least needed of the candidates. Typing "I have a saved block from another chat" still works, because Step 1 handles a pasted block or a mention of one without any starter. Swap candidates, if a slot is ever reassigned:

The old resume prompt, kept in case work from another chat or from the Claude Code toolkit, which uses the same ledger format, turns out to be common:

```
I have a saved session from last time. Ask me for my blocks so we can pick up where we left off.
```

Its wording matters, and it was changed after a review caught a failure. A clicked starter sends its sentence and nothing else, so the earlier wording, "Here is my saved ledger block", promised an attachment that was never there. The resume branch is gated on a block actually being present, so the click landed on the full document ask and the user was asked to pull their appraisal again. This wording asks the agent to ask: it requests both blocks by name, the `ledger` block and the `workspace` block, then reads Session state, says in two lines where the session stopped, and continues from next_action. A user who brings only the ledger is told the evidence is there but the profile is not, and gets one short round to rebuild it.

```
I want to write down one win while it is fresh.
```

Leads to the one-win capture: one candidate entry, at most six numbered questions, a ledger block, and done. No long path.

```
Review the self-assessment draft I already wrote.
```

Leads to the check. The agent says up front that a draft arriving with no evidence ledger behind it cannot go through the middle layer as it stands, and offers the choice: spend a round or two building a minimal ledger from the draft so every claim can be traced, or run the checker and the Panel Reader only and accept that nothing has been traced. Then the offline checker, the Evidence Auditor if there is a ledger, and the Panel Reader.
