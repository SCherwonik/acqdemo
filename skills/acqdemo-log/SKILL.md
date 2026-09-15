---
name: acqdemo-log
description: Use when the user says "log a win" or wants to capture an accomplishment, praise email, briefing, release, or slide title as AcqDemo self-assessment evidence - appends one entry to the evidence ledger in their private AcqDemo workspace (FY<yy>/ledger.md). Use this instead of saving a general memory for work accomplishments.
---

# AcqDemo Log

Capture one accomplishment from a ramble into a ledger entry. Fast, any time, no drafting.

## Step 0: Load
1. Find the workspace: the current directory if it holds `profile.md`, otherwise ask. If there is no profile, run the `acqdemo` skill's first-time setup first.
2. Find the current `FY<yy>/` the same way `acqdemo` does. Create `FY<yy>/ledger.md` (starting with `# Ledger FY<yy>`) and `FY<yy>/rambles/` if missing.

## Step 1: Take the ramble
Accept whatever the user gives: voice dictation, a pasted praise email, a release note, a slide title. Save it unedited to `FY<yy>/rambles/<YYYY-MM-DD>-<slug>.md` (slug from the topic, lowercase, hyphens).

## Step 2: Extract facts
Read `../acqdemo/references/ledger-format.md` for the entry format. Draft the entry from the ramble, then ask at most six targeted questions, only for fields still missing, in this order:
1. Numbers, each with a basis (estimates need one line explaining how it was worked out).
2. Audience: highest rank or title present, and headcount.
3. Role: `owned`, `co-owned`, `owned-a-piece`, or `supported`.
4. What decision this fed.
5. The obstacle overcome.
6. The contribution plan objective tag it maps to (if the plan has labels).

Estimates are allowed with a one-line basis. Never invent events, audiences, or awards.

## Step 3: Names
Put any person's name in `roster.md` only (add a row if new). The ledger entry itself uses roles and organizations, not names, except in `audience`, `notes`, and `evidence` per `ledger-format.md`.

## Step 4: Write the entry
1. Get the next id: `python scripts/ledger_check.py --file "<workspace>/FY<yy>/ledger.md" --next-id`.
2. Append a `##` section with that id to the ledger, `status: candidate` if fields are still open, or `status: ready` once every field in Step 2 is filled.
3. Validate: `python scripts/ledger_check.py --file "<workspace>/FY<yy>/ledger.md"`. Fix every CRITICAL finding before moving on; WARNINGs (for example `READY_INCOMPLETE`) can wait if the user wants to finish later.

## Step 5: Confirm
Reply in two lines: the entry id and title, and the single most useful missing fact to capture later (or "nothing missing" if the entry is `ready`).

## Rules
- Never invent numbers, audiences, events, or awards.
- Names never go into factor files; they live in `roster.md` and the ledger only.
- If the ramble appears to contain classified information, stop and tell the user to remove it before continuing.
