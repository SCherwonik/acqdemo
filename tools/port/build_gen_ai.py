"""Generate gen_ai/knowledge/ from skills/start/references/.

Usage (from the private workspace root):
    python tools/port/build_gen_ai.py [--dry-run]

What gets generated:
  * The lookup references that belong in the agent builder's Knowledge panel. The step
    sequence, the ledger format, and the rules that must never be missed stay inline in the
    agent instructions instead; see docs/superpowers/specs/2026-09-16-gen-ai-gemini-port-design.md.
  * Nested source paths are flattened into single file names, because the panel takes a flat
    list of uploads: descriptors/nh.md becomes descriptors-nh.md.
  * Each worked example directory is composed into one file.
  * INDEX.md, which names every file, what it covers, and when to open it.

What gets rewritten, and why:
  The source files are written for a Claude Code plugin with a shell, a microphone, a
  workspace on disk, and git repositories to mine. They point at each other with paths like
  ../scripts/doc_text.py, name skills like acqdemo:extract, tell the reader to run scripts,
  assume dictated answers, and cite commit counts as evidence. In a flat upload bundle all of
  that is dead or wrong. Every such reference is replaced with the flattened file name, with
  the name of a file that ships in the pack where that is the right substitute, or with plain
  prose. The sources themselves are never edited: the Claude version really does have voice
  input and git mining, and the instructions are correct there.

Safety:
  * Every rewrite must match its source text, and every rewrite must belong to a file the
    bundle copies. A source that drifts away from a rewrite, or a rule that would never run,
    aborts the build rather than shipping a dead reference.
  * The whole bundle is verified for forbidden wording and for the platform's character limit
    BEFORE anything is written.
  * Output is deterministic. Running twice produces identical files.
"""
from __future__ import annotations

import argparse
import shlex
import sys
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
DEFAULT_SRC = REPO / "skills" / "start" / "references"
DEFAULT_DST = REPO / "gen_ai" / "knowledge"

# The agent builder caps instructions and descriptions at 500,000 characters. A knowledge file
# larger than that cannot be pasted anywhere useful either, so the build refuses to emit one.
CHAR_LIMIT = 500_000

# Two files that travel with the bundle. Named, never pathed: the reader holds a flat list of
# uploads and no file system, so a repository-relative path is as dead as a shell command.
CHECKER = "acqdemo-checker.html"
WORKSHEET = "brain-dump-worksheet.md"

# Wording that must not survive into a bundle read by an agent with no shell and no plugin.
FORBIDDEN = (
    "../",
    "acqdemo:",
    "--plugin-dir",
    ".claude-plugin",
    "claude",
    ".py",
    "descriptors/",
    "rules/",
    "scripts/",
    "templates/",
    "skills/",
    "gen_ai/",  # a file that ships in the pack, pointed at by a path the reader does not have
    # No microphone: every answer on this platform is typed.
    "by voice",
    "for voice",
    "transcription",
    "dictation",
    "speech-to-text",
    "spoken",
    "rambles/",
    # No shell and no repositories: nothing here can count commits or read a git config.
    "git counts",
    "git repository",
    "out of git",
    ".gitignore",
    "pii guard",
    "repositories to harvest",
    "—",  # em dash: the repository's writing rules ban it
)

# Wording the bundle MUST carry, checked per file. Half the rewrites exist to add something
# rather than to remove something, and what they add carries no forbidden token: a heading
# spelled `# Session State` instead of `# Session state` breaks the agent contract and would
# otherwise ship in silence. REQUIRED_LINES matches a whole line, because `# Roster` is a
# substring of `## Roster` and would pass a substring test without ever being emitted.
REQUIRED_LINES: tuple[tuple[str, str], ...] = (
    ("ledger-format.md", "# Profile"),
    ("ledger-format.md", "# Pay pool"),
    ("ledger-format.md", "# Roster"),
    ("ledger-format.md", "# Session state"),
)

REQUIRED_TEXT: tuple[tuple[str, str], ...] = (
    ("ledger-format.md", "```ledger"),
    ("ledger-format.md", "```workspace"),
    ("writing-style.md", CHECKER),
    ("INDEX.md", CHECKER),
)

FORBIDDEN_LINES: tuple[tuple[str, str], ...] = (
    ("ledger-format.md", "# Session State"),  # the capital S the Ledger Keeper does not know
)


class BuildError(Exception):
    """A source file drifted, or the bundle would ship something it must not."""


@dataclass(frozen=True)
class Rewrite:
    """One literal replacement in one source file. It must match, or the build aborts."""

    rel: str
    old: str
    new: str


@dataclass(frozen=True)
class SectionRewrite:
    """Replace a whole `##` section of one source file, heading included.

    For passages that are wrong here from top to bottom rather than wrong in a phrase. The
    heading must appear exactly once outside a fenced block, or the build aborts.
    """

    rel: str
    heading: str
    new: str


@dataclass
class Item:
    name: str
    text: str
    covers: str
    when: str


# --------------------------------------------------------------------------------------
# What goes in the bundle
# --------------------------------------------------------------------------------------

COPIES: list[tuple[str, str, str]] = [
    (
        "intake-checklist.md",
        "What to ask the user for and in what order, what each item buys, the five minute "
        "question set for a user with no documents, and the privacy rules to say out loud.",
        "At first contact, before asking for anything.",
    ),
    (
        "getting-your-documents.md",
        "Click by click steps for pulling contribution plans, midpoints, closeouts, annuals, "
        "and salary appraisals out of CAS2Net, which sections to tick, and what to do when "
        "CAS2Net is out of reach.",
        "The user cannot find a document, or does not know which export to pull.",
    ),
    (
        "question-bank.md",
        "Every question the intake asks: brain dump prompts, the drill down ladder, gate "
        "questions, discriminator questions per factor, the calendar, timeline, and people "
        "sweeps, the portfolio roll up, the estimate protocol, and the coverage stop rule.",
        "Before every question round, and whenever a ledger entry is missing a field.",
    ),
    (
        "ledger-format.md",
        "Ledger entry fields and allowed values, the status lifecycle, roster rings, the "
        "session state block, and the profile and pay pool fields.",
        "Whenever an entry is written or updated, so field names and values stay valid.",
    ),
    (
        "rules/ccas-core.md",
        "CCAS rules: cycle dates, contribution plans, midpoint, closeout, annual minimums, "
        "mandatory objectives, supervisor narratives, scoring and pay, and special situations, "
        "each tagged [common] or [pay pool].",
        "Before answering any rules question, and before deciding what a factor must contain.",
    ),
    (
        "levels.md",
        "Career paths, broadband levels, factor score ranges, Very High scores and their "
        "eligibility bands, categorical scores, and how descriptors are read.",
        "When setting the target level, or when the user asks what a score means.",
    ),
    (
        "descriptors/nh.md",
        "NH Business Management and Technical Management: factor descriptions, expected "
        "contribution criteria, discriminators, and the descriptors for levels I to IV.",
        "The user is NH. Open it to pick target level language and to check a draft against "
        "the level's descriptors.",
    ),
    (
        "descriptors/nj.md",
        "NJ Technical Management Support: factor descriptions, expected contribution criteria, "
        "discriminators, and the descriptors for levels I to IV.",
        "The user is NJ. Open it to pick target level language and to check a draft against "
        "the level's descriptors.",
    ),
    (
        "descriptors/nk.md",
        "NK Administrative Support: factor descriptions, expected contribution criteria, "
        "discriminators, and the descriptors for levels I to III.",
        "The user is NK. Open it to pick target level language and to check a draft against "
        "the level's descriptors.",
    ),
    (
        "writing-style.md",
        "Paste ready output format, the character budget, ordering, framing policy, role verbs, "
        "vocabulary, the impact ladder, one project across three factors, and the repeat rule, "
        "with weak and strong examples.",
        "Before drafting any C-R-I text, and before rewriting a weak entry.",
    ),
    (
        "cert-templates.md",
        "Certification self statement templates for acquisition coded and DoD FM coded "
        "positions, with the placeholders to fill from the profile.",
        "Mission Support needs a certification paragraph.",
    ),
]

EXAMPLES: list[tuple[str, str, str, str]] = [
    (
        "examples/nh2-supervisor",
        "NH II supervisor aiming at III",
        "Worked example, fictional: profile, brain dump, roster, and the three finished factor "
        "files for an NH II team lead, including the supervisory objective paragraph and a DoD "
        "FM certification statement.",
        "To show the expected depth of a finished factor, or when the user supervises anyone.",
    ),
    (
        "examples/nj3-engineer",
        "NJ III engineering technician aiming at IV",
        "Worked example, fictional: profile, brain dump, roster, and the three finished factor "
        "files for an NJ III technician, including an acquisition certification statement.",
        "To show the expected depth of a finished factor for a hands on technical position.",
    ),
    (
        "examples/nk2-admin",
        "NK II program support assistant aiming at III",
        "Worked example, fictional: profile, brain dump, roster, and the three finished factor "
        "files for an NK II assistant, with no certification statement and no supervisory "
        "objective.",
        "To show the expected depth of a finished factor for an administrative position.",
    ),
]

EXAMPLE_PARTS = ("profile.md", "ramble.md", "roster.md")
FACTORS = (
    "Job Achievement and Innovation",
    "Communication and Teamwork",
    "Mission Support",
)

# Checker flags recorded with each example, translated into prose. An unknown flag aborts.
FLAG_PHRASES = {
    "--acq-cert": "an acquisition certification statement is expected as the first Mission "
    "Support paragraph",
    "--fm-cert": "a DoD FM certification statement is expected as a Mission Support paragraph",
    "--supervisor": "a supervisory objective paragraph is expected as the first Job Achievement "
    "and Innovation paragraph",
}


# --------------------------------------------------------------------------------------
# Rewrites
# --------------------------------------------------------------------------------------

REWRITES: list[Rewrite] = [
    # A script the reader does not have. The platform equivalent is an upload.
    Rewrite(
        "getting-your-documents.md",
        "Read whatever comes down with `../scripts/doc_text.py`, which handles pdf, docx, pptx, "
        "txt, and md and takes page ranges for long exports.",
        "Upload whatever comes down (pdf, docx, pptx, txt, or md) in the chat. A long export is "
        "easier to work through a section at a time, so say which pages matter if asked.",
    ),
    Rewrite(
        "intake-checklist.md",
        "Read them with `../scripts/doc_text.py` (pdf, docx, pptx, txt, md). Long export PDFs "
        "read in page ranges.",
        "Upload the export in the chat (pdf, docx, pptx, txt, md). A long export PDF is easier "
        "to work through a section at a time.",
    ),
    # A git hook in a repository the reader does not have.
    Rewrite(
        "intake-checklist.md",
        "- Keep personnel forms (SF-50, SF-52) and resumes out of git entirely. If the workspace "
        "is a git repository, offer the PII guard hook.",
        "- Keep personnel forms (SF-50, SF-52) and resumes out of the conversation entirely. Do "
        "not upload them.",
    ),
    # A script, and a README section number that means nothing here.
    Rewrite(
        "question-bank.md",
        "1. Position duties: read them with `../../plan/scripts/prd_text.py --file "
        '"<profile prd_path>"` and ask about the two or three duties that carry the most weight.',
        "1. Position duties: ask the user to upload or paste their Position Requirements "
        "Document (PRD), then ask about the two or three duties that carry the most weight.",
    ),
    Rewrite(
        "question-bank.md",
        "If `FY<yy>/evidence/` has no calendar file, give the user these steps (classic desktop "
        "Outlook; README Section 6.4 has the full version):",
        "If the user has not uploaded a calendar export, give them these steps (classic desktop "
        "Outlook):",
    ),
    # A skill invocation name, and a save-to-disk step.
    Rewrite(
        "question-bank.md",
        "5. Paste into Notepad and save as `FY<yy>/evidence/calendar-<YYYY-MM-DD>.txt`.\n"
        "Then run the calendar harvest (see the `acqdemo:extract` skill).",
        "5. Paste into Notepad, save it as a plain .txt file, and upload it in the chat.\n"
        "Then ask for a calendar sweep of that file.",
    ),
    # A script that checks ledger entries. Nothing on this platform replaces it, so the check
    # becomes an instruction to the agent instead.
    Rewrite(
        "ledger-format.md",
        "`ledger_check.py` lists blank fields as `OPEN_FIELDS` (INFO) on every entry and warns "
        "(`READY_INCOMPLETE`) when a `ready` entry still has any, so nothing stays blank by "
        "accident.",
        "List the blank fields of every entry when the entry is shown, and say so when a `ready` "
        "entry still has any, so nothing stays blank by accident.",
    ),
    # Template files that are not part of this bundle.
    Rewrite(
        "ledger-format.md",
        "See `templates/profile.md`. Required for drafting:",
        "These are the fields of the `# Profile` section of the workspace block. Required for "
        "drafting:",
    ),
    Rewrite(
        "ledger-format.md",
        "See `templates/paypool.md`. Skills read due dates, minimums, mandatory paragraph order, "
        "the promotion window, the plan-days requirement, the character limit, and allow-phrases "
        "from here instead of assuming defaults.",
        "These are the fields of the `# Pay pool` section of the workspace block. Read due dates, "
        "minimums, mandatory paragraph order, the promotion window, the plan-days requirement, "
        "the character limit, and allow-phrases from it instead of assuming defaults.",
    ),
    # "This repo" means nothing to someone holding a folder of uploads.
    Rewrite(
        "rules/ccas-core.md",
        "(the examples in this repo)",
        "(the examples in this pack)",
    ),
    # The deterministic checks moved out of the agent and into the offline checker page.
    Rewrite(
        "writing-style.md",
        "- At most **3,900 characters** per factor, counting each line break as two characters "
        "(CAS2Net allows about 4,000).",
        "- At most **3,900 characters** per factor, counting each line break as two characters "
        "(CAS2Net allows about 4,000).\n"
        f"- Character counts, the `C: ` `R: ` `I: ` labels, banned wording, and repeats of "
        f"prior-cycle text are checked offline by `{CHECKER}`, the checker page that came with "
        f"this pack. Open it in a browser and paste each finished factor into it before the text "
        f"goes into CAS2Net.",
    ),
    Rewrite(
        "writing-style.md",
        "Pull phrases from the target level's descriptors in `descriptors/<path>.md`",
        "Pull phrases from the target level's descriptors in `descriptors-<path>.md`",
    ),
    # ----------------------------------------------------------------------------------
    # No microphone. The Claude version is driven by dictation; this one is typed.
    # ----------------------------------------------------------------------------------
    Rewrite(
        "question-bank.md",
        '- Number every question in a round (1, 2, 3...) so the user can answer by voice: '
        '"number four: ...".',
        '- Number every question in a round (1, 2, 3...) so the user can answer them one at a '
        'time: "number four: ...".',
    ),
    Rewrite(
        "question-bank.md",
        "- Rounds of 5-8 questions work well for voice; there is no cap on the number of rounds.",
        "- Rounds of 5-8 questions work well; there is no cap on the number of rounds.",
    ),
    # ----------------------------------------------------------------------------------
    # No shell and no repositories. Nothing here can count commits or read a git log.
    # ----------------------------------------------------------------------------------
    Rewrite(
        "question-bank.md",
        "- Confirm every number with its source: stated, git, or estimate (see Estimate "
        "protocol).",
        "- Confirm every number with its source: stated, documented, or estimate (see Estimate "
        "protocol).",
    ),
    Rewrite(
        "question-bank.md",
        "3. Harvest anchors, when a harvest exists: the biggest repositories, recurring meeting "
        "series, releases, and the midpoint or closeout claims.",
        "3. Anchors from what the user uploaded: the biggest projects, recurring meeting series, "
        "releases, and the midpoint or closeout claims.",
    ),
    Rewrite(
        "question-bank.md",
        "2. Seed each month with anchors already known: meetings from the calendar harvest "
        "(especially briefings, demos, working groups, and recurring series), git releases and "
        "tags, midpoint and closeout dates,",
        "2. Seed each month with anchors already known: meetings from the calendar export "
        "(especially briefings, demos, working groups, and recurring series), releases and "
        "version dates, midpoint and closeout dates,",
    ),
    Rewrite(
        "question-bank.md",
        "1. **Evidence:** git counts (commits, versions, tags, findings closed), file counts, "
        "attendance lists, calendar entries.",
        "1. **Evidence:** counts the user can point at in something they have (versions, tags, "
        "findings closed), file counts, attendance lists, calendar entries.",
    ),
    Rewrite(
        "intake-checklist.md",
        "| Repositories, notebooks, or shared folders they work in | `profile.md` Repositories "
        "to harvest | Commit-level evidence with dates and release milestones |",
        "| Projects, notebooks, or shared folders they work in | Named in the profile block | "
        "Product and release names to ask about by name |",
    ),
    Rewrite(
        "intake-checklist.md",
        "Keep the source PDF out of git (see Privacy).",
        "Keep the rest of the source PDF out of the conversation (see Privacy).",
    ),
    Rewrite(
        "intake-checklist.md",
        "- The workspace is private. Names, scores, salary, and draft text belong there and never "
        "in a public repository.",
        "- These notes are private. Names, scores, salary, and draft text belong in them and "
        "never anywhere public.",
    ),
    Rewrite(
        "intake-checklist.md",
        "- A CAS2Net appraisal export is usually marked PII or CUI, and often contains salary. "
        "Extract the text you need, then keep the source file out of any git repository: store "
        "it outside the workspace, or in a folder the workspace ignores.",
        "- A CAS2Net appraisal export is usually marked PII or CUI, and often contains salary. "
        "Take only the text you need out of it, and keep the rest of the export out of the "
        "conversation.",
    ),
    Rewrite(
        "getting-your-documents.md",
        "**Check All** is fine when the user would rather pull everything once, as long as they "
        "know the result then contains salary and stays out of git.",
        "**Check All** is fine when the user would rather pull everything once, as long as they "
        "know the result then contains salary and is not something to upload whole.",
    ),
    Rewrite(
        "getting-your-documents.md",
        "The rule for the source file: the downloaded PDF stays out of git. These exports are "
        "normally marked CUI, and any of them may carry salary if Compensation Detail was "
        "included. Keep the PDF outside the workspace, or in a folder the workspace's PII guard "
        "or `.gitignore` excludes, and commit only the extracted text that the drafting actually "
        "needs.",
        "The rule for the source file: these exports are normally marked CUI, and any of them may "
        "carry salary if Compensation Detail was included. Upload only the pages the drafting "
        "actually needs, and keep the rest of the export out of the conversation.",
    ),
    Rewrite(
        "ledger-format.md",
        "  - 52 commits, v1.0 to v2.3 | source: git | basis: harvest 2026-08-20",
        "  - 12 releases, v1.0 to v2.3 | source: document | basis: release notes, uploaded "
        "2026-08-20",
    ),
    Rewrite(
        "ledger-format.md",
        "- `numbers`: every number that may appear in text needs a line with `source:` "
        "(`stated`, `git`, `estimate`, `calendar`, or `document`) and `basis:`.",
        "- `numbers`: every number that may appear in text needs a line with `source:` "
        "(`stated`, `estimate`, `calendar`, or `document`) and `basis:`.",
    ),
]

# Whole sections that are wrong here from top to bottom rather than wrong in a phrase.
SECTIONS: list[SectionRewrite] = [
    # The Claude version assumes dictation. Typed answers garble differently, and the file the
    # glossary was written into does not exist here.
    SectionRewrite(
        "question-bank.md",
        "## Voice and transcription",
        """## Terms, names, and numbers
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
""",
    ),
    # A folder tree for a reader with no folders.
    SectionRewrite(
        "ledger-format.md",
        "## Workspace layout",
        """## What the conversation holds
There is no file system here. Everything the toolkit keeps in files lives in the conversation as
text, and the user keeps their own copy of it:

- The **ledger block** and the **workspace block**, described below and re-emitted at the end of
  every round. Together they are the workspace.
- Brain dumps: what the user said when asked what they did this cycle, one block per session.
  Each one ends with its own `## Term glossary` section (wrote -> meant); see
  `question-bank.md`, Terms, names, and numbers.
- Uploads: the calendar export, prior-cycle assessments, the contribution plan, the position
  requirements document. These arrive in the chat rather than in folders.
- Finished factor text: one plain text block per factor, ready to paste into CAS2Net.

Nothing is written to disk by anyone but the user, so anything that is not re-emitted in a block
is lost when the conversation ends.
""",
    ),
    # The Claude version keeps four files on disk. Here they are two fenced blocks in the
    # conversation, and the split matters: session state inside the ledger block parses as an
    # entry and the ledger check stalls on BAD_ID for something that cannot be deleted.
    SectionRewrite(
        "ledger-format.md",
        "## Session state",
        """## The two blocks the user saves
The workspace is two fenced blocks in the conversation. Show both in full at each checkpoint,
so the user can read what was recorded and keep a copy to paste back. There is no third block,
and nothing else is saved.

**1. The ledger block.** It may open with its `# Ledger FY<yy>` title line, and after that it
holds `## L-NNN` entries in the format below and nothing else. Session state, profile, pay pool,
and roster material never appears inside it: anything else starting with `##` is read as an
entry, and an entry with an id that is not `L-NNN` is a CRITICAL error on every round after it.

```ledger
# Ledger FY26
## L-001 Automated regression tool
- status: ready
```

**2. The workspace block.** Exactly four sections, in this order, spelled and capitalized
exactly as shown. `# Session state` has a lowercase "state".

```workspace
# Profile
- career_path, level, target_level, rating_period, supervisor counts, certifications and their
  dates, EOCS, and the projects the user works in (fields below)

# Pay pool
- due dates, minimum entries, mandatory paragraph order, the `C:` or `W:` label, the promotion
  window, the character limit, allow-phrases (fields below)

# Roster
- one table row per person, by ring (format above)

# Session state
- step: 4 deep-dives
- current_entry: L-007
- round: 3
- pending_questions: 2
- next_action: deep-dive on L-007, then coverage grid
- open_questions:
  - EOCS after the promotion
- updated: 2026-09-03
```

The workspace block is what makes resume work. Without it a saved ledger loses the career path
and the target level, and drafting stops until they are asked for again.
""",
    ),
]

# Inserted after the first heading of any copied file that talks about a workspace on disk.
WORKSPACE_TOKENS = (
    "profile.md",
    "paypool.md",
    "roster.md",
    "ledger.md",
    "session-state.md",
    "FY<yy>",
    "prior/",
)

PLATFORM_NOTE = """> Platform note. This copy is for an agent with no file system. Where the text below names a
> workspace file or folder such as `profile.md`, `paypool.md`, `roster.md`, `ledger.md`, or
> `FY<yy>/evidence/`, read it as a block of text kept in the conversation: the assistant
> shows those blocks at each checkpoint and the user keeps them in a document of
> their own. Source documents are uploaded in the chat rather than saved into folders. Field
> names, allowed values, and every rule below are unchanged.
"""


# --------------------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------------------


def flatten(rel: str) -> str:
    """descriptors/nh.md -> descriptors-nh.md. The Knowledge panel takes a flat list."""
    return rel.replace("/", "-")


def read(src: Path, rel: str) -> str:
    path = src / rel
    if not path.is_file():
        raise BuildError(f"missing source file: {rel}")
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def outside_fences(lines: list[str]):
    """Yield (index, line) for every line that is not inside a ``` fenced block.

    Fence markers themselves are never yielded: a fence is not a heading and never needs
    demoting, and a `## ` line inside one is sample text, not a section of the document.
    """
    fenced = False
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if not fenced:
            yield i, line


def check_rewrites_are_reachable() -> None:
    """Every rule must belong to a file the bundle actually copies.

    apply_rewrites is only ever called for the rels in COPIES, so a rule whose rel is
    misspelled, or scoped to a worked example, is never looked at and never raises. Several
    rewrites leave behind text that carries no forbidden token, so a rule that never runs
    would ship a dead reference in silence.
    """
    copied = {rel for rel, _covers, _when in COPIES}
    for label, rels in (("REWRITES", {r.rel for r in REWRITES}),
                        ("SECTIONS", {s.rel for s in SECTIONS})):
        stray = sorted(rels - copied)
        if stray:
            raise BuildError(
                f"{label} names files the bundle never copies, so those rules would never run: "
                f"{', '.join(stray)}. Fix the rel, or add the file to COPIES."
            )


def apply_sections(rel: str, text: str) -> str:
    for rule in SECTIONS:
        if rule.rel != rel:
            continue
        lines = text.split("\n")
        starts = [i for i, line in outside_fences(lines) if line.rstrip() == rule.heading]
        if len(starts) != 1:
            raise BuildError(
                f"{rel}: expected exactly one {rule.heading!r} section to replace, found "
                f"{len(starts)}. Update SECTIONS in tools/port/build_gen_ai.py."
            )
        start = starts[0]
        end = next((i for i, line in outside_fences(lines)
                    if i > start and line.startswith("## ")), len(lines))
        body = rule.new.strip("\n").split("\n")
        tail = lines[end:]
        if tail and tail[0].strip():  # the blank line before the next heading went with the section
            body.append("")
        text = "\n".join(lines[:start] + body + tail)
    return text


def apply_rewrites(rel: str, text: str) -> str:
    for rule in REWRITES:
        if rule.rel != rel:
            continue
        if rule.old not in text:
            raise BuildError(
                f"{rel}: a rewrite no longer matches its source. Update REWRITES in "
                f"tools/port/build_gen_ai.py. Looking for:\n{rule.old}"
            )
        text = text.replace(rule.old, rule.new)
    return text


def relink(text: str) -> str:
    """Point cross-references at the flattened name the file actually has in the bundle."""
    for rel, _covers, _when in COPIES:
        if "/" in rel:
            text = text.replace(f"`{rel}`", f"`{flatten(rel)}`")
    return text


def add_platform_note(text: str) -> str:
    if not any(token in text for token in WORKSPACE_TOKENS):
        return text
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("# "):
            rest = lines[i + 1 :]
            while rest and not rest[0].strip():
                rest = rest[1:]
            return "\n".join(lines[: i + 1] + ["", PLATFORM_NOTE.rstrip("\n"), ""] + rest)
    raise BuildError("file has no top-level heading to hang the platform note on")


def flags_to_prose(flags: str) -> str:
    """'--mode annual --fm-cert' -> 'annual assessment; a DoD FM certification statement ...'"""
    tokens = shlex.split(flags)
    phrases: list[str] = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token == "--mode":
            if i + 1 >= len(tokens):
                raise BuildError("checker flags: --mode has no value")
            phrases.append(f"{tokens[i + 1]} assessment")
            i += 2
            continue
        if token not in FLAG_PHRASES:
            raise BuildError(f"checker flags: no prose for {token!r}. Add it to FLAG_PHRASES.")
        phrases.append(FLAG_PHRASES[token])
        i += 1
    return "; ".join(phrases)


def demote(text: str) -> str:
    """Drop a part's own title and push its remaining headings one level down.

    Fenced blocks are left alone: a `# comment` inside one is code, not a heading.
    """
    lines = text.split("\n")
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
        while lines and not lines[0].strip():
            lines = lines[1:]
    out = list(lines)
    for i, line in outside_fences(lines):
        if line.startswith("#"):
            out[i] = "#" + line
    return "\n".join(out).strip("\n")


def compose_example(src: Path, rel: str, title: str) -> str:
    parts = {name: read(src, f"{rel}/{name}") for name in EXAMPLE_PARTS}
    flags = flags_to_prose(read(src, f"{rel}/flags.txt").strip())
    out = [
        f"# Worked example: {title}",
        "",
        "Fictional. The names, organizations, and numbers below were invented for this example. "
        "It shows what the intake collected and what the finished factor text looked like, so a "
        "draft can be measured against it.",
        "",
        f"Checker settings for this example: {flags}.",
        "",
        "## Profile",
        "",
        demote(parts["profile.md"]),
        "",
        "## Brain dump",
        "",
        "What the user said when asked what they did this cycle. A typed answer is thinner than "
        "what a long conversation draws out, so on this platform the same material is filled in "
        f"offline on `{WORKSHEET}`, the worksheet that came with this pack, and uploaded.",
        "",
        demote(parts["ramble.md"]),
        "",
        "## Roster",
        "",
        "Names live here and in private notes only. They never appear in the factor text below.",
        "",
        demote(parts["roster.md"]),
        "",
        "## Finished factor text",
        "",
        "Plain text, exactly as it was pasted into CAS2Net.",
        "",
    ]
    for factor in FACTORS:
        out += [
            f"### {factor}",
            "",
            "```",
            read(src, f"{rel}/final/{factor}.txt").strip("\n"),
            "```",
            "",
        ]
    return "\n".join(out).rstrip("\n") + "\n"


def render_index(items: list[Item]) -> str:
    rows = "\n".join(f"| `{i.name}` | {i.covers} | {i.when} |" for i in items)
    return (
        "# Knowledge Index\n"
        "\n"
        "Every file in this folder is uploaded into the agent builder's Knowledge panel, which "
        "takes a flat list, so nested source folders were flattened into single names and every "
        "cross-reference was rewritten to match. This file, `INDEX.md`, is the map.\n"
        "\n"
        "Generated from the toolkit's reference material by the port build tool. Do not edit "
        "these files by hand; change the source reference and run the build again.\n"
        "\n"
        "| File | What it covers | When to open it |\n"
        "|---|---|---|\n"
        f"{rows}\n"
        "\n"
        "Two things are deliberately not in this folder:\n"
        "\n"
        "- The step sequence, the ledger block, the estimate protocol, the character cap, the "
        "rule against names in factor text, and the rule against inventing events or awards live "
        "inline in the agent instructions, because they must never be missed.\n"
        f"- The arithmetic and string checks live in `{CHECKER}`, the checker page that came with "
        "this pack. It runs in a browser, offline, with no network calls. No agent is asked to "
        "count characters or spot repeated wording.\n"
    )


def bundle(src: Path) -> list[Item]:
    check_rewrites_are_reachable()
    items: list[Item] = []
    for rel, covers, when in COPIES:
        # Sections first: a rewrite aimed at text a section replacement deleted then fails
        # loudly instead of quietly doing nothing.
        text = add_platform_note(relink(apply_rewrites(rel, apply_sections(rel, read(src, rel)))))
        items.append(Item(flatten(rel), text.rstrip("\n") + "\n", covers, when))
    for rel, title, covers, when in EXAMPLES:
        items.append(Item(flatten(rel) + ".md", compose_example(src, rel, title), covers, when))
    # The index lists itself, so it is appended before it is rendered.
    index = Item(
        "INDEX.md",
        "",
        "The map of this folder: what every other file covers and when to open it.",
        "First, before opening anything else.",
    )
    items.append(index)
    index.text = render_index(items)
    return items


# --------------------------------------------------------------------------------------
# Verify, write
# --------------------------------------------------------------------------------------


def verify(items: list[Item]) -> list[str]:
    findings: list[str] = []
    by_name = {item.name: item for item in items}
    for item in items:
        low = item.text.lower()
        for token in FORBIDDEN:
            if token in low:
                findings.append(f"{item.name}: contains forbidden wording {token!r}")
    for name, line in FORBIDDEN_LINES:
        item = by_name.get(name)
        if item is not None and line in item.text.split("\n"):
            findings.append(f"{name}: has the line {line!r}, which is the wrong spelling")
    for label, wanted, present in (
        ("line", REQUIRED_LINES, lambda item, want: want in item.text.split("\n")),
        ("wording", REQUIRED_TEXT, lambda item, want: want in item.text),
    ):
        for name, want in wanted:
            item = by_name.get(name)
            if item is None:
                findings.append(f"{name}: is not in the bundle, so its required {label} "
                                f"{want!r} cannot be checked")
            elif not present(item, want):
                findings.append(f"{name}: is missing the required {label} {want!r}")
    return findings


def check_limits(items: list[Item], limit: int | None = None) -> None:
    limit = CHAR_LIMIT if limit is None else limit
    for item in items:
        if len(item.text) > limit:
            raise BuildError(
                f"{item.name}: {len(item.text)} characters is over the platform's "
                f"character limit of {limit}"
            )


def write(items: list[Item], dst: Path, dry_run: bool) -> tuple[list[str], list[str], list[str]]:
    """Write what changed, delete stale files, and report stale folders without touching them.

    The bundle is a flat list of files, so the build never creates a folder here. A folder in
    the destination was put there by hand, and deleting one recursively is a worse risk than
    the stale copy it holds, so it is named and left alone.
    """
    wanted = {i.name for i in items}
    changed: list[str] = []
    for item in items:
        target = dst / item.name
        data = item.text.encode("utf-8")
        if target.exists() and target.read_bytes() == data:
            continue
        changed.append(item.name)
        if not dry_run:
            dst.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    stale: list[str] = []
    folders: list[str] = []
    if dst.exists():
        for path in sorted(dst.iterdir()):
            if path.is_dir():
                folders.append(path.name + "/")
            elif path.name not in wanted:
                stale.append(path.name)
    if not dry_run:
        for name in stale:
            (dst / name).unlink()
    return changed, stale, folders


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--src", type=Path, default=DEFAULT_SRC, help="reference material root")
    ap.add_argument("--dst", type=Path, default=DEFAULT_DST, help="knowledge bundle output")
    ap.add_argument("--dry-run", action="store_true", help="report only, write nothing")
    args = ap.parse_args(argv)

    src, dst = args.src.resolve(), args.dst.resolve()
    if not src.is_dir():
        print(f"build: {src} is not a directory")
        return 2

    try:
        items = bundle(src)
        check_limits(items)
    except BuildError as exc:
        print(f"build: ABORTED, nothing written. {exc}")
        return 1

    findings = verify(items)
    if findings:
        print("build: ABORTED, nothing written. Fix these in the source or in REWRITES:")
        for f in findings:
            print(f"  - {f}")
        return 1

    changed, stale, folders = write(items, dst, args.dry_run)
    mode = "DRY RUN" if args.dry_run else "BUILT"
    total = sum(len(i.text) for i in items)
    print(
        f"build: {mode}: {len(items)} files in {dst}, {len(changed)} written, "
        f"{len(stale)} removed, {total} characters total"
    )
    for name in changed:
        print(f"  write  {name}")
    for name in stale:
        print(f"  remove {name}")
    for name in folders:
        print(f"  leave  {name} (a folder; the build makes none, so this one is not its to remove)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
