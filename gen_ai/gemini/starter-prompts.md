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
I already wrote my self-assessment and I want it checked. Here is the draft.
```

Leads to the shortcut path, and it is the only route to it. Someone who arrives here has already written the whole thing, this cycle's or a previous cycle's, because they did the thinking in their head rather than in a conversation. Their draft is their ledger. The Draft Intake subagent reads it back into entries, reports which mandatory paragraphs the text contains, flags grammar and sentence mechanics, and says how many characters each factor uses against the limit. Then the same three check layers run that the long path runs, so the shortcut loses none of the rigor.

The wording carries a lesson from the slot that used to sit here. A clicked starter prompt sends its sentence and nothing else: no file, no pasted text. An earlier prompt promised an attachment that was never there, the branch behind it was gated on that attachment, and the click fell through to the wrong path. So "Here is the draft" is an invitation, not a claim that something is attached, and the orchestrator asks for the draft and waits.

**This prompt is the gate.** Draft Intake is reachable from here and from a user who supplies complete factor text and asks for it read in, and from nowhere else. It is never called during a normal writing session, on a midpoint, on a closeout, or on an uploaded document, which is the Document Extractor's work. The two agents both read text and return candidate entries, so the only thing keeping them apart is which path reached them. The reason is the stance: the shortcut takes the user's words as settled, asserted work, and applying that to a half-formed sentence someone is still thinking through would turn a draft thought into a claim.

### What happened to the resume prompt

This slot used to hold "I have a saved session from last time." It was written when losing the chat meant losing the work, and the file argued it was load bearing for that reason. It is not any more: chats on this platform persist and carry their own history, so the ordinary way back into an unfinished session is to reopen it. The capability is unchanged and only the button is gone. A user who pastes a `ledger` block into their first message still skips straight to the resume branch, and a user who types the request still gets asked for both blocks by name. That matters most for work carried in from elsewhere, another chat or the Claude Code toolkit, which uses the same ledger format.

## If a slot is ever freed up

Only three slots exist, and slot 3 now keeps one of them for a reason the other two do not share: it is the only way to reach Draft Intake. The annual and midpoint paths are both reachable by typing, and so is resume. Reassigning slot 3 would not make the shortcut path harder to find, it would close it.

These are the strongest candidates if slot 1 or slot 2 is ever reassigned:

```
I want to write down one win while it is fresh.
```

Leads to the one-win capture: one candidate entry, at most six numbered questions, a ledger block, and done. No long path.

```
I have a saved session from last time. Ask me for my blocks so we can pick up where we left off.
```

The prompt that used to sit in slot 3. Worth restoring only for someone routinely carrying work in from another chat or from the Claude Code toolkit, since reopening a chat on this platform already resumes it.
