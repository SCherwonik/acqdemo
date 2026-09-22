# Setup: Building the AcqDemo Assistant in the Gemini Agent Builder

Click-by-click, using the builder's own field names. Allow about 30 minutes the first time. Everything you paste comes from files in this pack, so keep this folder open in a second window.

Nothing here needs a network connection beyond the builder itself. No file in this pack calls out to the internet.

## Before you start

Have these open:

- `gen_ai/gemini/orchestrator.md`, the primary agent's instructions.
- `gen_ai/gemini/starter-prompts.md`, the three Personalization prompts.
- `gen_ai/gemini/subagents/`, five files, one per subagent. Each file holds a Name, a Description, and an Instructions block ready to paste.
- `gen_ai/knowledge/`, the files that go in the Knowledge panel.

Two files in this pack are **not** uploaded anywhere, and both have to reach the employee some other way. `gen_ai/checker/acqdemo-checker.html` is opened directly in a browser when it is time to check a draft. `gen_ai/worksheets/brain-dump-worksheet.md` is filled in offline by the employee and uploaded into a chat, not into the agent.

**Plan how you will hand those two files to every employee who uses the agent.** They never see this repository and they never see this folder, so a path like `gen_ai/checker/acqdemo-checker.html` means nothing to them. Put both files on a shared drive, in a Teams or SharePoint folder, or attach them to the mail that tells people the agent exists, and say where they are in the same message. Part 5 has the wording. The agent refers to them by file name only, as things that came with the pack, and tells the employee to ask whoever set the agent up if they cannot find them, which is you.

## Part 1: Create the primary agent

1. Open the agent builder and create a new agent.

2. **Name.** Type:

   ```
   AcqDemo Assistant
   ```

   The field takes up to 128 characters. Keep it short: the name shows in the agent picker and in the flow canvas, and every subagent name has to be readable next to it.

3. **Description.** Paste:

   ```
   Writes AcqDemo contribution plans, midpoint assessments, closeouts, and annual self-assessments with a DoD employee: gathers their documents, runs the recall questions, builds an evidence ledger, drafts paste-ready C-R-I text for Job Achievement and Innovation, Communication and Teamwork, and Mission Support, and checks it before it goes into CAS2Net.
   ```

   The field allows up to 500,000 characters, so there is no reason to abbreviate. On the primary agent the description is for humans picking an agent. On subagents it is something else entirely, which Part 3 covers.

4. **Instructions.** Open `gen_ai/gemini/orchestrator.md`, select the entire file, copy, and paste it into the field. The whole file is the instructions text; there is no preamble to strip out and nothing to leave behind.

   The field is required and allows up to 500,000 characters. The orchestrator is a small fraction of that, so do not trim it to save room. Length is not the constraint here; completeness is. If you cut the rationale paragraphs, the agent starts skipping the steps they justify.

   After pasting, scroll the field to the bottom and confirm the last line is there. Long pastes into web fields silently truncate more often than you would think.

5. **Model.** Choose the strongest model offered, the Pro tier rather than the fast tier. The primary agent holds the conversation, the ledger, and the judgment calls about what is worth claiming, and that is exactly the work that degrades on a faster model.

6. **Connectors.** **Remove Enterprise Web Search.** It is attached by default and it has to come off.

   The reason is specific, not a general caution about the internet. AcqDemo rules differ by pay pool and by year: due dates, minimum entry counts, mandatory paragraph order, the character limit, promotion windows, and the local business rules all vary. Public web pages about AcqDemo are frequently out of date, or accurate for a different pay pool, and the agent cannot tell which. When web search is available the model will reach for it and will state another organization's rule as though it were this employee's rule, confidently and without a citation the employee can check. Every rule this agent states must come from an attached Knowledge file or from what the employee says about their own pay pool. Remove the connector and that failure cannot happen.

   Remove any other connector that is attached by default too. This agent needs none of them. Uploads arrive through the chat window.

7. **Knowledge.** Upload every file from `gen_ai/knowledge/`. These are the references the agent looks things up in rather than reciting: the factor descriptors for each career path, the question bank, the CCAS program rules, the certification statement templates, the CAS2Net document retrieval steps, and the worked examples.

   These are public reference material that ships with the toolkit. Do not upload the employee's own documents here. Their appraisal, midpoint, plan, and calendar export go into the chat as uploads, one conversation at a time, because they carry PII and often salary and they do not belong in an agent's permanent Knowledge panel.

8. **Personalization.** Fill the three starter prompt slots from `gen_ai/gemini/starter-prompts.md`, in order. Paste each one exactly; the wording routes the conversation.

9. Save the agent.

## Part 2: Add the five subagents on the Flow canvas

Open the Flow canvas for the AcqDemo Assistant. The primary agent is the root node. Each subagent is added as a child of it.

Add these five, in this order. The order does not change behavior, but it makes the canvas readable later.

| Node | Paste from | Model |
|---|---|---|
| Document Extractor | `subagents/document-extractor.md` | Fast tier |
| Ledger Keeper | `subagents/ledger-keeper.md` | Fast tier |
| Factor Drafter | `subagents/factor-drafter.md` | Strongest available |
| Evidence Auditor | `subagents/evidence-auditor.md` | Strongest available |
| Panel Reader | `subagents/panel-reader.md` | Strongest available |

For each one:

1. Add a subagent node as a child of AcqDemo Assistant.
2. **Name.** Type the name from the Node column of the table above, exactly as it appears there: `Document Extractor`, `Ledger Keeper`, `Factor Drafter`, `Evidence Auditor`, `Panel Reader`. These five names are the canonical ones. They match the Name line in each subagent file and they match the names the orchestrator instructions call out to. Do not add a prefix, do not add "AcqDemo", and do not make them more descriptive. A renamed subagent is a subagent that never gets called, and the failure is silent: the primary agent simply does the work badly by itself.
3. **Description.** Copy the Description block from the file, exactly, and do not improve it.

   Subagent descriptions are routing keys, not summaries. The primary agent chooses which child to hand work to by reading these. Two rules follow from that, and both were learned the expensive way. Never name another subagent's subject matter in a description, even to exclude it: writing "does not draft factor text" in the Document Extractor's description reliably attracts drafting requests to the Document Extractor, because the match is on the words, not on the negation. And never write a description that describes the agent's quality rather than its trigger; "carefully reviews text" matches nothing in particular, while "called when a draft needs every claim traced back to evidence" matches exactly one situation.

4. **Instructions.** Paste the Instructions block from the file.
5. **Model.** Set it per the table above. The builder defaults subagents to a faster model than the primary, which is right for the Document Extractor and the Ledger Keeper and wrong for the other three. The Document Extractor reads long documents and extracts structure, and the Ledger Keeper moves text into labeled fields; both are mechanical and benefit from being fast and cheap. The Factor Drafter, the Evidence Auditor, and the Panel Reader all exercise judgment about what a claim is worth, and each one is the last line of defense on something the employee will have to defend in person. Put them on the strongest model available.
6. **Connectors.** **Remove Enterprise Web Search from this subagent too.** It is attached by default to every agent, including children, and it has to come off every one of them for the same reason it came off the primary. A subagent that reaches the open web while summarizing a document will quietly blend a web page's version of an AcqDemo rule into its output, and the primary agent has no way to tell that happened.
7. Save the node.

Repeat for all five. Then look at the canvas: AcqDemo Assistant at the root, five children, no other nodes.

## Part 3: Verify before you use it

Walk this list. It takes two minutes and catches the failures that are hard to diagnose later.

1. Open each of the six agents and confirm the Connectors list is empty. This is the one to double-check, because the default reattaches on some builds when an agent is duplicated.
2. Confirm all five subagent names match the names used in the orchestrator instructions: Document Extractor, Ledger Keeper, Factor Drafter, Evidence Auditor, Panel Reader.
3. Confirm the primary agent's Instructions field ends with the same line the orchestrator file ends with.
4. Confirm the Knowledge panel lists every file from `gen_ai/knowledge/` and none of the employee's own documents.
5. Confirm the three starter prompts are in place.

## Part 4: Smoke test

Start a new conversation with the primary agent and click the first starter prompt.

What should happen: the agent's first message is the document ask, in plain paragraphs. It asks for the prior cycle's CAS2Net Salary Appraisal exported with every section selected, this cycle's midpoint and contribution plan, and an Outlook calendar export saved as a text file, and it says in one or two sentences what each one unlocks. Then it stops and waits.

What should not happen: a greeting with a menu of options, a lecture about what AcqDemo is, a list of questions about the employee's career path, or a web citation. Any of those means something did not paste correctly. Reopen the Instructions field and check the beginning and the end of the text.

Second test: type "what is the character limit for my pay pool's factor text?" A correct answer says the toolkit's cap is 3,900 characters, notes that CAS2Net allows about 4,000, and says the limit varies by pay pool and asks the employee to confirm theirs. An answer that cites a website means a connector is still attached somewhere.

Third test: answer one question. The reply should end with a short line naming what was recorded, something like "Recorded: L-002 audience and role", and then the next questions. It should not dump the blocks after every round; that cadence was deliberately dropped. Then type "show me the ledger". Now you should get **two** fenced blocks: one labeled `ledger` holding only `## L-` entries, and one labeled `workspace` holding four headings, `# Profile`, `# Pay pool`, `# Roster`, `# Session state`. If asking for the ledger produces one block with session state inside it, or produces nothing, the RECORD EVERY ROUND, SHOW THE BLOCKS AT CHECKPOINTS section did not paste.

Read the workspace block's Session state while it is in front of you. `pending_questions` should hold the questions themselves, worded the way they were asked, and never a number of them. `current_entry` should hold one entry id such as `L-002`, or nothing at all, and never a step name or a title. `supervises` should read as counts by category, such as `0 military, 4 civilians, 2 contractors`, and never as yes or no. Each of those three is a field a later step reads and stops on, and each was found holding the wrong kind of value on a live run.

Fourth test: if the agent ever puts a `## SESSION STATE` heading inside the `ledger` block, the two-block split did not paste. That single heading makes the ledger fail its own checker on an error that cannot be fixed without deleting the session state, and the conversation stalls there. Reopen the Instructions field and confirm both the THE TWO BLOCKS and THE WORKSPACE BLOCK sections are present.

Fifth test: give it two broadband levels in one sentence. Type "I am an NH-III and my contribution plan for this cycle says NH-IV." A correct reply does not quietly record `level: III` and `target_level: IV` and carry on. It says the two values disagree, marks the field itself with `[CONFLICT]` keeping both values and where each one came from, asks which level was held at the start of the rating period and which is held now and the effective date of any change, and puts a matching line in the Session state's `open_questions`. A reply that fills in a level and a target without asking is the exact failure that hid a mid-cycle promotion on a live run, and it means the CONFLICT IS A QUESTION, NEVER A MERGE section did not paste.

Sixth test: hand it a year-old certification. Type "last year's appraisal says I hold an acquisition practitioner certification, status met, 40 continuous learning points." That statement should land in Profile marked `confirmed: no` with the document and the cycle it came from, and a certification refresh line should appear in `open_questions`, rather than being recorded as this cycle's certification. Then answer whatever the agent asks until it has your position basics. Before it starts asking about individual pieces of work it should run the special-situation pass: five numbered questions covering broadband level, supervisor, any closeout document, an organization change, and a certification change. Certifications arriving as settled fact means CERTIFICATIONS ARE REFRESHED, NEVER CARRIED did not paste. The five questions never arriving means THE SPECIAL-SITUATION PASS did not paste, and that section is the one that catches a promotion, a supervisor change, or a move, every one of which changes what the finished text has to say.

Seventh test: say you supervise nobody. Type "I supervise no one, no military, no civilians, no contractors." Later, when the agent settles the mandatory paragraphs, there should be no supervisory paragraph at all, and nothing resembling a supervisory objective should appear in the workspace block's `# Pay pool` section. A supervisory paragraph written for an employee with zero counts is an invented requirement, and on a live run the same reply wrote that invention into the Pay pool section, where every later session reads it back as the employee's own pay pool policy. Every line in that section should name where it came from, either a document or the employee, or say it is an unconfirmed toolkit default.

## Part 5: Give the employee the two files, and five instructions

**Send them both loose files with the link to the agent.** `acqdemo-checker.html` and `brain-dump-worksheet.md`, attached to the mail or on a shared drive with the path written out. The agent names both files but cannot hand them over, and an employee who does not have the checker cannot finish: character counts, label structure, banned wording, repeated wording from a prior cycle, and names that leaked into the text are all checked there and nowhere else.

Then five things, said once:

- **Read the two blocks when they appear.** At certain points the agent shows a `ledger` block, which is the evidence it has recorded, and a `workspace` block, which is the career path, the broadband levels, the pay pool's rules, the roster, and where the work stands. Those points are: when a piece of work is finished being asked about, before the allocation, before drafting, at the end, and any time you ask to see the ledger. **Read them.** A number that came out wrong or a project credited to the wrong entry costs one sentence to fix there, and a redraft of a whole factor if it is not caught until the evidence audit. Copying both into a document of your own is worth doing too: that pair is what lets you carry the cycle into a new chat, or into the Claude Code version of this toolkit, which reads the same format.
- **Answer by number.** The agent numbers its questions. Answering "1 yes, 2 no, 3 about forty, 4 skip" is faster than prose and loses nothing. "Skip" and "I don't know" are always acceptable.
- **The checker is a separate file.** When the agent says a draft is ready to check, open `acqdemo-checker.html` in a browser, paste each factor in, run it, and paste the findings back into the chat. The page runs entirely in the browser and sends nothing anywhere. Before sending anyone there the agent gives them a setup block with every Setup and Context field filled in, including the prior cycle text and the list of names to keep out. **Paste those in too, not just the factor text.** The prior-text box and the names box are what make the repeat check and the name check run at all; leave them empty and the page reports a clean draft without having looked for either.
- **The five questions about your cycle are not admin.** Early on the agent asks whether your broadband level, your supervisor, or your organization changed this cycle, whether a closeout was written, and whether anything about your certifications changed. Answer them with dates. A promotion inside the rating period changes which descriptors your text is written against, changes the expected score the narrative has to clear, and requires a written justification that nobody raises if the promotion is never mentioned. The agent will also ask you to confirm any certification statement it read out of last year's appraisal, because a year-old one is well formed, passes every check, and is still wrong.
- **The worksheet is optional and it helps.** `brain-dump-worksheet.md` is filled in offline over several days and then uploaded into the chat. Typed answers are shorter than spoken ones, and this is the main way to make up the difference. Anyone who finds the question rounds slow going should be pointed at it early.

## Maintenance

When a file in this pack changes, the change has to be re-pasted into the builder by hand. There is no sync. The files in this folder are the source of truth for what the agents should say, so make the change here first, then paste it in, rather than editing an agent in the builder and trying to remember what you changed.
