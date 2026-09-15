---
name: acqdemo-review
description: Use when checking an AcqDemo self-assessment draft (annual, midpoint, or closeout C-R-I statements) before it goes into CAS2Net, or when the user asks to review, audit, or fix a draft.
---

# AcqDemo Review

Checks the three paste-ready factor files against the program rules and a pay pool panel's eye, then offers fixes. Never adds facts.

## Inputs
- A draft folder containing exactly `Job Achievement and Innovation.txt`, `Communication and Teamwork.txt`, and `Mission Support.txt` (usually `FY<yy>/drafts/v<N>/` or `FY<yy>/final/` in the user's private workspace). If the user pasted text instead, save it into those three files in a new `FY<yy>/drafts/v<N>/` folder first. Ask where the workspace is if unknown.
- From the workspace when present: `profile.md`, `paypool.md`, `roster.md`, `FY<yy>/ledger.md`, `prior/`, and the current cycle's midpoint text.
- Rules: `../acqdemo/references/writing-style.md`, `../acqdemo/references/rules/ccas-core.md`, `../acqdemo/references/levels.md`, and the user's career path file in `../acqdemo/references/descriptors/`.

## Step 1: Run the deterministic checker
Build flags from the workspace:

| Source | Flag |
|---|---|
| Annual, midpoint, or closeout | `--mode annual`, `--mode midpoint`, or `--mode closeout` (closeouts have no rule-set minimum; the checker uses 1) |
| `paypool.md` `min_entries_annual` / `min_entries_midpoint` | `--min-entries N` |
| `profile.md` certification of type `acquisition` | `--acq-cert` |
| `profile.md` certification of type `dod-fm` | `--fm-cert` |
| `profile.md` `supervises` with any count above 0 | `--supervisor` |
| `prior/` (previous cycles only; never the current midpoint) | `--prior "<workspace>/prior"` |
| `roster.md` | `--roster "<workspace>/roster.md"` |
| `paypool.md` `allow_phrases` (write them one per line to `FY<yy>/drafts/allow-phrases.txt`) | `--allow-phrases <that file>` |
| `paypool.md` `what_label` (`C` unless the pay pool uses `W`) | `--what-label C` or `--what-label W` |

Run the checker at `scripts/check.py` in this skill's folder:

```
python "<this skill folder>/scripts/check.py" --dir "<draft folder>" <flags>
```

The checker expects acquisition before DoD FM when both apply. If `paypool.md` orders them differently, report `ACQ_CERT`/`FM_CERT` ordering findings as INFO instead of CRITICAL.

## Step 2: Judgment checks
Match each C-R-I to its ledger entry by content.

| Severity | Check | How to decide |
|---|---|---|
| CRITICAL | Same achievement as a prior cycle with no current-cycle delta | Compare against `prior/` meaningfully, not just wording, and against the entry's `prior_cycle_overlap` |
| WARNING | Number without a basis | Every number in the text must appear in the entry's `numbers` with a `basis` |
| WARNING | Verb stronger than the recorded role | Role verbs table in `writing-style.md` |
| WARNING | Impact climbs fewer than two rungs or lacks a mission tie | Impact ladder in `writing-style.md`; mission statements in `profile.md` |
| WARNING | Reads below the target level | Compare with the target level's descriptors; no recognizable descriptor language or scope |
| WARNING | Not ordered by impact | Scope x organizational level x novelty |
| INFO | Passive voice; uncovered discriminators per factor; raise vs. award balance; missing plan tags | |

With no ledger, turn the number-basis and role checks into questions for the user.

## Step 3: Report
Number every finding so the user can answer by voice ("fix 1 and 3, skip 2"):

```
Review: <n> CRITICAL, <n> WARNING, <n> INFO
Character counts: JA <n> | CT <n> | MS <n>

CRITICAL
1. [JA] PRIOR_REPEAT: "<run>" also in FY25. Fix: reword from ledger L-004 using the FY26 delta.
WARNING
2. [CT] Number "over 200 attendees" has no basis in the ledger. Fix: confirm the count or remove.
INFO
3. [MS] No coverage of Planning/Budgeting.
```

## Step 4: Fix loop
1. Ask: "Fix all, or which numbers?"
2. Write fixes to a new version folder `FY<yy>/drafts/v<N+1>/`; never overwrite the reviewed version.
3. Fix rules: keep every fact and number; cut adjectives before facts; reword repeats with fresh wording from the ledger; replace names with title, organization, or a count from the roster; change verbs to match the role; never invent a number (ask instead).
4. Show changed sentences as before and after, per factor.
5. Rerun Step 1 on the new folder. Repeat until 0 CRITICAL, then ask about remaining WARNINGs.

## Rules
- Never add accomplishments, numbers, audiences, or awards that are not in the ledger or stated by the user.
- Names never go into factor files.
- If a draft appears to contain classified information, stop and tell the user to remove it before continuing.
