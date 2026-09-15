# Writing Style for Paste-Ready Text

Applies to the three factor files that go into CAS2Net. The working doc and crib sheet may use Markdown.

## Output format
Each factor file is plain text:

```
<mandatory paragraph 1, if any>

<mandatory paragraph 2, if any>

C: <what you did, one sentence>
R: <result>
I: <impact>

C: ...
R: ...
I: ...
```

- Labels are exactly `C: `, `R: `, `I: ` at the start of a line (Contribution, Result, Impact). If `paypool.md` sets `what_label: W`, use `W: ` instead of `C: `; the structure is the same.
- One blank line between paragraphs and between entries.
- Straight quotes only. No em dashes. No bullets, headers, bold, or other Markdown.
- Mandatory paragraphs (supervisory objective under JA; certification statements under MS) come first, in the order `paypool.md` specifies. See `rules/ccas-core.md` and `cert-templates.md`.

## Length budget
- At most **3,900 characters** per factor, counting each line break as two characters (CAS2Net allows about 4,000).
- The Contribution is one sentence of at most 35 words. Result and Impact are one or two sentences each and carry the detail.
- Usually three or four C-R-I per factor. Put spare entries on the bench in the working doc rather than squeezing a fifth.

## Order
Greatest impact first. Rank by scope, organizational level reached, and novelty.

## Framing policy
| Allowed and encouraged | Never |
|---|---|
| The strongest verb the ledger role supports | Invented events, audiences, awards, or recognition |
| Stacked scope: dollar value, portfolio, number of programs, organizational level | Ownership verbs for work someone else owned |
| Language from the target level's descriptors | People's names |
| Impact at the highest rung of the impact ladder the facts reach | Classified information |
| Estimated numbers at the top of a plausible range, rounded up, framed favorably, each with a basis recorded in the ledger (for an unknown input, its defensible low end, phrased "over N" or "about N") | Numbers with no basis |

## Role verbs
| Ledger role | Verbs |
|---|---|
| owned | led, directed, spearheaded, architected, established |
| co-owned | co-led, partnered with (role) to, jointly developed |
| owned-a-piece | drove, built, delivered (the piece) for |
| supported | describe the specific piece delivered, with a strong verb on that smaller noun |

Shrink the noun, keep the verb strong: "Directed the subsystem reconciliation for the program estimate" instead of "Supported the program estimate."

## Vocabulary
- Pull phrases from the target level's descriptors in `descriptors/<path>.md` (for example, "recognized as a technical authority within and outside the organization," "works with senior management to establish new methodologies," "resolves diverse viewpoints").
- Banned words: seamlessly, friction-free, perfectly, unbroken, synergy, cutting-edge, world-class.
- "Robust" and "leverage" at most once per factor.
- Adjective test: if a number or a noun can replace an adjective, replace it.
- Active voice, subject-verb-object, precise and objective (Tongue and Quill style). Result and Impact sentences may omit the subject ("Cut review time from five days to one.").

## Impact ladder
team > division or branch > agency or command > headquarters staff > military service or department > DoD or Congress

Tie each Impact to the level the work actually reaches (team, division, organization, mission) and name the mission tie (budget decisions, program readiness, acquisition strategy, workforce capability).
- Aim two rungs above where the Result happened when the facts support it. For field and support positions, a tie to the mission one or two levels up satisfies the ladder. Never claim a level the facts do not reach.
- Use a mission-statement phrase in at most one Impact per factor, and vary Impact wording from entry to entry.

## One project, three angles
When a project supports more than one factor, each factor gets a different angle and different wording:
- **JA:** what was built or solved and why it was hard or new.
- **CT:** who was briefed, trained, or aligned, and what they adopted.
- **MS:** the customer need met, resources saved, or schedule and budget effect.

The same project may appear in more than one factor this way, but each fact and number appears in only one factor. Assign each number to one factor (for example, the count in JA and the dollars in MS) and note the split in the ledger entry's `notes`.

## Raise or award framing
- **Sustained** contributions support a raise: "institutionalized," "now the standard method for every estimate," "adopted as the division's recurring process."
- **One-time "big rocks"** support an award: a single high-stakes delivery, a one-of-a-kind rescue.
Tag each allocated entry `sustained` or `one-time` in the working doc so the supervisor can argue both.

## Repeat rule
- The current cycle's midpoint is the starting point. Reuse its facts, expand them with later results, and upgrade the wording.
- Prior cycles are off limits: no run of six or more identical words, and no re-claiming an achievement already submitted. A continuing project claims only what is new this cycle.

## Special situations
- **Promotion inside a late-cycle window** (see `rules/ccas-core.md`): make continuity explicit. Show higher-level contributions before and after the effective date, emphasize sustained strategic work, and give the supervisor a substantial-justification paragraph in the crib sheet.
- **Split year (closeout):** cover both halves; the self-assessment should still stand on its own.
- **Supervisors:** the supervisory objective paragraph opens JA. First the exact counts sentence from `rules/ccas-core.md`. Then two or three sentences on the scope of supervision: what the team delivered as a whole, how staff were developed, hiring and training, and how workload was managed. Do not repeat facts or numbers from the JA C-R-I entries.

## Examples
All examples are fictional.

**Weak**
```
C: Worked on the cost model for the program and helped the team with data.
R: The model was improved and the team was happy with the results.
I: This helped the organization make better decisions.
```

**Strong (owned role, estimate recorded in ledger)**
```
C: Architected and delivered an automated regression tool that replaced manual spreadsheet testing for 40 cost estimating relationships across 6 programs.
R: Cut model development time from about three weeks to four days per estimate and surfaced two unit errors in the legacy workbook before a leadership review.
I: Established the division's standard method for relationship testing, giving headquarters decision-makers defensible estimates for over $2B in program funding decisions.
```

**Same project, CT angle**
```
C: Trained 14 analysts across 3 divisions to use the new regression tool through live demonstrations and a written user guide.
R: Analysts in all three divisions adopted the tool for their next estimates, and questions to the team dropped to near zero within two months.
I: Raised the agency's analytic baseline and freed senior analysts for higher-priority program reviews.
```
