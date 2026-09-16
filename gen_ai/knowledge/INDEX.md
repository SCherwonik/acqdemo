# Knowledge Index

Every file in this folder is uploaded into the agent builder's Knowledge panel, which takes a flat list, so nested source folders were flattened into single names and every cross-reference was rewritten to match. This file, `INDEX.md`, is the map.

Generated from the toolkit's reference material by the port build tool. Do not edit these files by hand; change the source reference and run the build again.

| File | What it covers | When to open it |
|---|---|---|
| `intake-checklist.md` | What to ask the user for and in what order, what each item buys, the five minute question set for a user with no documents, and the privacy rules to say out loud. | At first contact, before asking for anything. |
| `getting-your-documents.md` | Click by click steps for pulling contribution plans, midpoints, closeouts, annuals, and salary appraisals out of CAS2Net, which sections to tick, and what to do when CAS2Net is out of reach. | The user cannot find a document, or does not know which export to pull. |
| `question-bank.md` | Every question the intake asks: brain dump prompts, the drill down ladder, gate questions, discriminator questions per factor, the calendar, timeline, and people sweeps, the portfolio roll up, the estimate protocol, and the coverage stop rule. | Before every question round, and whenever a ledger entry is missing a field. |
| `ledger-format.md` | Ledger entry fields and allowed values, the status lifecycle, roster rings, the session state block, and the profile and pay pool fields. | Whenever an entry is written or updated, so field names and values stay valid. |
| `rules-ccas-core.md` | CCAS rules: cycle dates, contribution plans, midpoint, closeout, annual minimums, mandatory objectives, supervisor narratives, scoring and pay, and special situations, each tagged [common] or [pay pool]. | Before answering any rules question, and before deciding what a factor must contain. |
| `levels.md` | Career paths, broadband levels, factor score ranges, Very High scores and their eligibility bands, categorical scores, and how descriptors are read. | When setting the target level, or when the user asks what a score means. |
| `descriptors-nh.md` | NH Business Management and Technical Management: factor descriptions, expected contribution criteria, discriminators, and the descriptors for levels I to IV. | The user is NH. Open it to pick target level language and to check a draft against the level's descriptors. |
| `descriptors-nj.md` | NJ Technical Management Support: factor descriptions, expected contribution criteria, discriminators, and the descriptors for levels I to IV. | The user is NJ. Open it to pick target level language and to check a draft against the level's descriptors. |
| `descriptors-nk.md` | NK Administrative Support: factor descriptions, expected contribution criteria, discriminators, and the descriptors for levels I to III. | The user is NK. Open it to pick target level language and to check a draft against the level's descriptors. |
| `writing-style.md` | Paste ready output format, the character budget, ordering, framing policy, role verbs, vocabulary, the impact ladder, one project across three factors, and the repeat rule, with weak and strong examples. | Before drafting any C-R-I text, and before rewriting a weak entry. |
| `cert-templates.md` | Certification self statement templates for acquisition coded and DoD FM coded positions, with the placeholders to fill from the profile. | Mission Support needs a certification paragraph. |
| `examples-nh2-supervisor.md` | Worked example, fictional: profile, brain dump, roster, and the three finished factor files for an NH II team lead, including the supervisory objective paragraph and a DoD FM certification statement. | To show the expected depth of a finished factor, or when the user supervises anyone. |
| `examples-nj3-engineer.md` | Worked example, fictional: profile, brain dump, roster, and the three finished factor files for an NJ III technician, including an acquisition certification statement. | To show the expected depth of a finished factor for a hands on technical position. |
| `examples-nk2-admin.md` | Worked example, fictional: profile, brain dump, roster, and the three finished factor files for an NK II assistant, with no certification statement and no supervisory objective. | To show the expected depth of a finished factor for an administrative position. |
| `INDEX.md` | The map of this folder: what every other file covers and when to open it. | First, before opening anything else. |

Two things are deliberately not in this folder:

- The step sequence, the ledger block, the estimate protocol, the character cap, the rule against names in factor text, and the rule against inventing events or awards live inline in the agent instructions, because they must never be missed.
- The arithmetic and string checks live in `acqdemo-checker.html`, the checker page that came with this pack. It runs in a browser, offline, with no network calls. No agent is asked to count characters or spot repeated wording.
