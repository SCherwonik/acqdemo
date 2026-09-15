# Phase 2: Draft Checker Script (Tasks 8-11)

Back to [plan index](../2026-09-15-acqdemo-wave1.md).

`skills/acqdemo-review/scripts/check.py` enforces every countable writing rule. The review skill (Task 16) runs it; the annual skill runs it before finalizing. It is standard-library Python and importable for tests.

Each task adds code to the same two files:
- `skills/acqdemo-review/scripts/check.py`
- `skills/acqdemo-review/scripts/tests/test_check.py`

---

### Task 8: Constants, parsing, and character counting

**Files:**
- Create: `skills/acqdemo-review/scripts/check.py`
- Create: `skills/acqdemo-review/scripts/tests/test_check.py`

- [ ] **Step 1: Write the failing tests (with shared helpers)**

Create `skills/acqdemo-review/scripts/tests/test_check.py`:

```python
"""Tests for skills/acqdemo-review/scripts/check.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import check  # noqa: E402

ACQ = ("I am fully certified in BUS-CE (Advanced) as of 20 Aug 2024 and have completed "
       "80 Continuous Learning Points (CLPs) for the cycle ending 30 Sep 2026.")
FM = ("I am fully certified at DoD FM Level 2. I have met my requirement of 40 CETs "
      "for the current cycle ending 30 Sep 2026.")
SUP = ("I supervise 0 military, 3 civilians, and manage 2 contractors. I held monthly "
       "feedback sessions and completed all required personnel actions on time.")


def wri(topic, n):
    return (f"W: Built {topic} tool number {n} for the analysts.\n"
            f"R: Delivered {topic} release {n} on schedule.\n"
            f"I: Improved {topic} readiness across the agency {n}.\n")


def factor_text(topic, count=3, preamble=()):
    parts = list(preamble) + [wri(topic, i) for i in range(1, count + 1)]
    return "\n".join(p if p.endswith("\n") else p + "\n" for p in parts)


def write_dir(tmp_path, ja=None, ct=None, ms=None):
    folder = tmp_path / "final"
    folder.mkdir(exist_ok=True)
    texts = {"JA": ja if ja is not None else factor_text("alpha"),
             "CT": ct if ct is not None else factor_text("bravo"),
             "MS": ms if ms is not None else factor_text("charlie")}
    for key, name in check.FACTOR_FILES.items():
        (folder / name).write_text(texts[key], encoding="utf-8", newline="\n")
    return folder


def codes(findings, severity=None):
    return [f.code for f in findings if severity is None or f.severity == severity]


# ---------------------------------------------------------------- parsing

def test_parse_preamble_and_entries():
    text = f"{ACQ}\n\n{FM}\n\n{wri('alpha', 1)}\n{wri('alpha', 2)}"
    factor = check.parse_factor("MS", text)
    assert factor.preamble == [ACQ, FM]
    assert len(factor.entries) == 2
    assert all(e.complete for e in factor.entries)
    assert factor.entries[0].line == 5


def test_parse_joins_continuation_lines():
    text = "W: Led the effort\nacross three divisions.\nR: Finished early.\nI: Saved money.\n"
    entry = check.parse_factor("JA", text).entries[0]
    assert entry.W == "Led the effort across three divisions."


def test_parse_orphan_and_repeated_labels():
    text = "R: Result with no what.\nW: What.\nR: One.\nR: Two.\nI: Impact.\n"
    factor = check.parse_factor("JA", text)
    assert factor.orphans == [1, 4]


def test_char_count_counts_line_breaks_twice():
    assert check.char_count("ab\ncd\n") == 6
    assert check.char_count("ab\r\ncd") == 6
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest skills/acqdemo-review/scripts/tests/test_check.py`
Expected: collection ERROR with `ModuleNotFoundError: No module named 'check'`.

- [ ] **Step 3: Write the constants, data classes, and parser**

Create `skills/acqdemo-review/scripts/check.py`:

```python
"""Deterministic checks for AcqDemo self-assessment drafts.

Usage:
    python check.py --dir <folder> [--mode annual|midpoint] [--min-wri N]
                    [--acq-cert] [--fm-cert] [--supervisor]
                    [--prior FILE_OR_DIR ...] [--roster roster.md]
                    [--allow-phrases FILE] [--json]

The folder must contain the three factor files:
    Job Achievement and Innovation.txt
    Communication and Teamwork.txt
    Mission Support.txt

Exit code 1 if any CRITICAL finding, otherwise 0.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

FACTOR_FILES = {
    "JA": "Job Achievement and Innovation.txt",
    "CT": "Communication and Teamwork.txt",
    "MS": "Mission Support.txt",
}
HARD_LIMIT = 4000
SOFT_LIMIT = 3900
PRIOR_RUN = 6
CROSS_RUN = 8
WHAT_MAX_WORDS = 35
BANNED = ["seamlessly", "friction-free", "perfectly", "unbroken", "synergy", "cutting-edge", "world-class"]
ONCE_ONLY = {"robust": r"\brobust\b", "leverage": r"\bleverag\w*"}
SEVERITY_ORDER = {"CRITICAL": 0, "WARNING": 1, "INFO": 2}

LABEL_RE = re.compile(r"^\s*(W|R|I)\s*:\s?(.*)$")
LABEL_PREFIX_RE = re.compile(r"^\s*[WRI]\s*:\s?", re.M)
SUPERVISOR_RE = re.compile(
    r"I supervise \d+ military, \d+ civilians?,? and manage \d+ contractors?\.?", re.I
)
CERT_RE = re.compile(r"certif", re.I)
FM_RE = re.compile(r"\bDoD\s+FM\b|\bCETs?\b", re.I)
ACQ_RE = re.compile(r"\bBUS-[A-Z]{2}\b|\bCLPs?\b|\bacquisition\b|\bDAWIA\b", re.I)
EM_DASH_RE = re.compile("—")
SMART_QUOTES_RE = re.compile("[‘’“”]")
MARKDOWN_RE = re.compile(r"^\s*(#{1,6}\s|[-*+]\s)|\*\*|__|`", re.M)


@dataclass
class Entry:
    W: str = ""
    R: str = ""
    I: str = ""
    line: int = 0

    @property
    def complete(self) -> bool:
        return bool(self.W.strip() and self.R.strip() and self.I.strip())


@dataclass
class Factor:
    key: str
    text: str
    preamble: list[str] = field(default_factory=list)
    entries: list[Entry] = field(default_factory=list)
    orphans: list[int] = field(default_factory=list)


@dataclass
class Finding:
    severity: str
    code: str
    factor: str
    message: str


# ---------------------------------------------------------------- parsing

def parse_factor(key: str, text: str) -> Factor:
    text = text.replace("\r\n", "\n")
    factor = Factor(key=key, text=text)
    para: list[str] = []
    current: Entry | None = None
    last_field: str | None = None
    for number, raw in enumerate(text.split("\n"), 1):
        line = raw.rstrip()
        match = LABEL_RE.match(line)
        if match:
            label, body = match.group(1), match.group(2)
            if label == "W":
                if current is None and para:
                    factor.preamble.append(" ".join(para))
                    para = []
                current = Entry(W=body, line=number)
                factor.entries.append(current)
                last_field = "W"
            elif current is None or getattr(current, label):
                factor.orphans.append(number)
            else:
                setattr(current, label, body)
                last_field = label
            continue
        if not line.strip():
            if current is None and para:
                factor.preamble.append(" ".join(para))
                para = []
            continue
        if current is None:
            para.append(line.strip())
        elif last_field:
            joined = f"{getattr(current, last_field)} {line.strip()}".strip()
            setattr(current, last_field, joined)
    if current is None and para:
        factor.preamble.append(" ".join(para))
    return factor


def char_count(text: str) -> int:
    body = text.replace("\r\n", "\n").rstrip()
    return len(body) + body.count("\n")
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest skills/acqdemo-review/scripts/tests/test_check.py`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add skills/acqdemo-review/scripts
git commit -m "feat(review): parse factor files and count characters"
```

---

### Task 9: Structure, mandatory paragraphs, and length checks

**Files:**
- Modify: `skills/acqdemo-review/scripts/check.py` (append)
- Modify: `skills/acqdemo-review/scripts/tests/test_check.py` (append)

- [ ] **Step 1: Append the failing tests**

Append to `skills/acqdemo-review/scripts/tests/test_check.py`:

```python
# ---------------------------------------------------------------- structure and mandatory

def test_clean_draft_has_no_critical(tmp_path):
    findings = check.run_checks(write_dir(tmp_path), min_wri=3)
    assert codes(findings, "CRITICAL") == []


def test_incomplete_entry_and_minimum(tmp_path):
    ja = factor_text("alpha", count=2) + "W: Something without result.\n"
    findings = check.run_checks(write_dir(tmp_path, ja=ja), min_wri=3)
    assert "WRI_INCOMPLETE" in codes(findings, "CRITICAL")
    assert "MIN_WRI" in codes(findings, "CRITICAL")


def test_midpoint_minimum_is_one(tmp_path):
    folder = write_dir(tmp_path, ja=factor_text("alpha", 1), ct=factor_text("bravo", 1), ms=factor_text("charlie", 1))
    assert "MIN_WRI" not in codes(check.run_checks(folder, min_wri=1))
    assert "MIN_WRI" in codes(check.run_checks(folder, min_wri=3))


def test_supervisor_statement_required_first(tmp_path):
    folder = write_dir(tmp_path)
    assert "SUPERVISOR_STATEMENT" in codes(check.run_checks(folder, 3, supervisor=True))
    folder = write_dir(tmp_path, ja=factor_text("alpha", preamble=[SUP]))
    assert "SUPERVISOR_STATEMENT" not in codes(check.run_checks(folder, 3, supervisor=True))


def test_certification_statements_in_order(tmp_path):
    good = write_dir(tmp_path, ms=factor_text("charlie", preamble=[ACQ, FM]))
    assert codes(check.run_checks(good, 3, acq=True, fm=True), "CRITICAL") == []
    swapped = write_dir(tmp_path, ms=factor_text("charlie", preamble=[FM, ACQ]))
    found = codes(check.run_checks(swapped, 3, acq=True, fm=True), "CRITICAL")
    assert "ACQ_CERT" in found and "FM_CERT" in found


def test_fm_only_position_is_first(tmp_path):
    folder = write_dir(tmp_path, ms=factor_text("charlie", preamble=[FM]))
    assert codes(check.run_checks(folder, 3, fm=True), "CRITICAL") == []


def test_bus_fm_acquisition_statement_is_not_dod_fm(tmp_path):
    bus_fm = ("I am partially certified in BUS-FM (Practitioner) and on track to achieve full "
              "certification by 30 Jun 2027. I am current on my CLPs.")
    folder = write_dir(tmp_path, ms=factor_text("charlie", preamble=[bus_fm]))
    assert codes(check.run_checks(folder, 3, acq=True), "CRITICAL") == []


# ---------------------------------------------------------------- length

def padded_factor(target):
    """A valid 3-entry factor whose character count is exactly target."""
    base = factor_text("alpha", 2) + "W: What.\nR: Result.\nI: "
    pad = target - len(base) - base.count("\n")
    text = base + "y" * pad + "\n"
    assert check.char_count(text) == target
    return text


@pytest.mark.parametrize(
    "target, critical, warning",
    [(3900, False, False), (3901, False, True), (4000, False, True), (4001, True, False)],
)
def test_char_limits(tmp_path, target, critical, warning):
    found = check.run_checks(write_dir(tmp_path, ja=padded_factor(target)), 3)
    assert ("CHAR_LIMIT" in codes(found, "CRITICAL")) is critical
    assert ("CHAR_SOFT_LIMIT" in codes(found, "WARNING")) is warning
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest skills/acqdemo-review/scripts/tests/test_check.py`
Expected: the new tests FAIL with `AttributeError: module 'check' has no attribute 'run_checks'`; the 4 parsing tests still pass.

- [ ] **Step 3: Append the checks and a first `run_checks`**

Append to `skills/acqdemo-review/scripts/check.py`:

```python
# ---------------------------------------------------------------- structure

def check_structure(factor: Factor, min_wri: int) -> list[Finding]:
    out: list[Finding] = []
    for entry in factor.entries:
        if not entry.complete:
            missing = ", ".join(k for k in ("W", "R", "I") if not getattr(entry, k).strip())
            out.append(Finding("CRITICAL", "WRI_INCOMPLETE", factor.key,
                               f"entry starting line {entry.line} is missing {missing}"))
    for number in factor.orphans:
        out.append(Finding("CRITICAL", "WRI_ORPHAN_LABEL", factor.key,
                           f"line {number}: R or I label outside a W-R-I entry, or repeated"))
    complete = sum(1 for e in factor.entries if e.complete)
    if complete < min_wri:
        out.append(Finding("CRITICAL", "MIN_WRI", factor.key,
                           f"{complete} complete W-R-I; minimum is {min_wri}"))
    return out


def check_mandatory(factors: dict[str, Factor], acq: bool, fm: bool, supervisor: bool) -> list[Finding]:
    out: list[Finding] = []
    ja, ms = factors["JA"], factors["MS"]
    if supervisor and not (ja.preamble and SUPERVISOR_RE.search(ja.preamble[0])):
        out.append(Finding("CRITICAL", "SUPERVISOR_STATEMENT", "JA",
                           "first JA paragraph must state 'I supervise X military, Y civilians, "
                           "and manage Z contractors.' before any W-R-I"))
    expected = []
    if acq:
        expected.append(("ACQ_CERT", "acquisition certification statement",
                         lambda p: bool(CERT_RE.search(p) and ACQ_RE.search(p) and not FM_RE.search(p))))
    if fm:
        expected.append(("FM_CERT", "DoD FM certification statement",
                         lambda p: bool(CERT_RE.search(p) and FM_RE.search(p))))
    for position, (code, label, ok) in enumerate(expected):
        if len(ms.preamble) <= position or not ok(ms.preamble[position]):
            out.append(Finding("CRITICAL", code, "MS",
                               f"MS paragraph {position + 1} must be the {label}, before any W-R-I"))
    return out


def check_length(factor: Factor) -> list[Finding]:
    count = char_count(factor.text)
    out = [Finding("INFO", "CHAR_COUNT", factor.key, f"{count} characters (line breaks count as 2)")]
    if count > HARD_LIMIT:
        out.append(Finding("CRITICAL", "CHAR_LIMIT", factor.key, f"{count} characters exceeds {HARD_LIMIT}"))
    elif count > SOFT_LIMIT:
        out.append(Finding("WARNING", "CHAR_SOFT_LIMIT", factor.key, f"{count} characters exceeds {SOFT_LIMIT}"))
    return out


# ---------------------------------------------------------------- orchestration

def read_text(path: Path) -> str:
    data = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-16", "cp1252"):
        try:
            return data.decode(encoding)
        except UnicodeError:
            continue
    return data.decode("utf-8", "replace")


def run_checks(folder: Path, min_wri: int, acq: bool = False, fm: bool = False,
               supervisor: bool = False) -> list[Finding]:
    missing = [name for name in FACTOR_FILES.values() if not (folder / name).exists()]
    if missing:
        return [Finding("CRITICAL", "MISSING_FILE", "-", f"missing factor file '{m}'") for m in missing]
    factors = {key: parse_factor(key, read_text(folder / name)) for key, name in FACTOR_FILES.items()}
    findings: list[Finding] = []
    for factor in factors.values():
        findings += check_structure(factor, min_wri)
        findings += check_length(factor)
    findings += check_mandatory(factors, acq, fm, supervisor)
    return sorted(findings, key=lambda f: (SEVERITY_ORDER[f.severity], f.factor, f.code))
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest skills/acqdemo-review/scripts/tests/test_check.py`
Expected: 15 passed.

- [ ] **Step 5: Commit**

```bash
git add skills/acqdemo-review/scripts
git commit -m "feat(review): check W-R-I structure, mandatory paragraphs, and length"
```

---

### Task 10: Repeat, name, and style checks

**Files:**
- Modify: `skills/acqdemo-review/scripts/check.py` (insert new sections, replace `run_checks`)
- Modify: `skills/acqdemo-review/scripts/tests/test_check.py` (append)

- [ ] **Step 1: Append the failing tests**

Append to `skills/acqdemo-review/scripts/tests/test_check.py`:

```python
# ---------------------------------------------------------------- repeats

PRIOR_SENTENCE = "Reconciled contractor cost reports with the program office every quarter."


def test_prior_repeat_flags_six_word_run(tmp_path):
    ja = factor_text("alpha", 2) + "W: Reconciled contractor cost reports with the program office twice.\nR: Done.\nI: Better data.\n"
    folder = write_dir(tmp_path, ja=ja)
    findings = check.run_checks(folder, 3, prior={"fy25.txt": PRIOR_SENTENCE})
    messages = [f.message for f in findings if f.code == "PRIOR_REPEAT"]
    assert messages and "reconciled contractor cost reports with the program office" in messages[0]


def test_prior_repeat_ignores_allowed_phrase(tmp_path):
    org = "Office of the Regional Cost Estimating Directorate"
    ja = factor_text("alpha", 2) + f"W: Briefed the {org} leadership.\nR: Done.\nI: Better data.\n"
    folder = write_dir(tmp_path, ja=ja)
    prior = {"fy25.txt": f"Supported the {org} staff."}
    assert "PRIOR_REPEAT" in codes(check.run_checks(folder, 3, prior=prior))
    assert "PRIOR_REPEAT" not in codes(check.run_checks(folder, 3, prior=prior, allow=[org]))


def test_cross_factor_repeat_flags_eight_word_run(tmp_path):
    shared = "Automated the quarterly data pull for every program estimate in the branch."
    ja = factor_text("alpha", 2) + f"W: {shared}\nR: Done.\nI: Faster.\n"
    ct = factor_text("bravo", 2) + f"W: {shared}\nR: Trained staff.\nI: Adoption.\n"
    findings = check.run_checks(write_dir(tmp_path, ja=ja, ct=ct), 3)
    assert "CROSS_FACTOR_REPEAT" in codes(findings, "CRITICAL")


# ---------------------------------------------------------------- names

ROSTER = """# Roster

| Ring | Name | Organization | Role | Worked on | Frequency | Ledger |
|---|---|---|---|---|---|---|
| own office: estimating | Jordan Quill | Estimating branch | analyst | tool training | 4 | L-001 |
| contractor: Example Corp | Avery Lee | Example Corp | engineer | data pipeline | weekly | L-004 |
"""


def test_roster_names_parsed():
    assert check.roster_names(ROSTER) == ["Jordan Quill", "Avery Lee"]


def test_names_in_text_flagged_full_and_last(tmp_path):
    ja = factor_text("alpha", 2) + "W: Mentored Quill on regression.\nR: Done.\nI: Growth.\n"
    ct = factor_text("bravo", 2) + "W: Worked with Avery Lee daily.\nR: Done.\nI: Growth.\n"
    findings = check.run_checks(write_dir(tmp_path, ja=ja, ct=ct), 3, names=check.roster_names(ROSTER))
    messages = " ".join(f.message for f in findings if f.code == "NAME_IN_TEXT")
    assert "'Quill'" in messages and "'Avery Lee'" in messages


def test_short_last_names_are_not_matched_alone(tmp_path):
    ja = factor_text("alpha", 2) + "W: Worked with the lee side team.\nR: Done.\nI: Growth.\n"
    findings = check.run_checks(write_dir(tmp_path, ja=ja), 3, names=check.roster_names(ROSTER))
    assert "NAME_IN_TEXT" not in codes(findings)


# ---------------------------------------------------------------- style

def test_style_warnings(tmp_path):
    ja = factor_text("alpha", 2) + (
        "W: Seamlessly built a robust and robust tool — fast.\n"
        "R: Called it “great”.\nI: **Big** win.\n"
    )
    found = codes(check.run_checks(write_dir(tmp_path, ja=ja), 3), "WARNING")
    for code in ("BANNED_WORD", "OVERUSED_WORD", "EM_DASH", "SMART_QUOTES", "MARKDOWN"):
        assert code in found


def test_what_too_long(tmp_path):
    long_what = "W: " + " ".join(["word"] * 36) + "\nR: Done.\nI: Impact.\n"
    found = codes(check.run_checks(write_dir(tmp_path, ja=factor_text("alpha", 2) + long_what), 3), "WARNING")
    assert "WHAT_TOO_LONG" in found
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest skills/acqdemo-review/scripts/tests/test_check.py`
Expected: new tests FAIL with `TypeError: run_checks() got an unexpected keyword argument 'prior'` (or `'names'`), `AttributeError: ... 'roster_names'`, and missing style warnings; earlier 15 still pass.

- [ ] **Step 3: Insert repeat, name, and style checks above the orchestration section**

In `skills/acqdemo-review/scripts/check.py`, insert this block immediately before the line `# ---------------------------------------------------------------- orchestration`:

```python
# ---------------------------------------------------------------- repeats

def segments(text: str, allow: list[str]) -> list[list[str]]:
    body = LABEL_PREFIX_RE.sub("", text.replace("\r\n", "\n"))
    for phrase in allow:
        if phrase.strip():
            body = re.sub(re.escape(phrase.strip()), "\x00", body, flags=re.I)
    return [re.findall(r"[a-z0-9]+", part.lower()) for part in body.split("\x00")]


def shingles(segs: list[list[str]], n: int) -> set[tuple[str, ...]]:
    out: set[tuple[str, ...]] = set()
    for toks in segs:
        for i in range(len(toks) - n + 1):
            out.add(tuple(toks[i:i + n]))
    return out


def shared_runs(segs: list[list[str]], other: set[tuple[str, ...]], n: int) -> list[str]:
    runs: list[str] = []
    for toks in segs:
        start = end = None
        for i in range(len(toks) - n + 1):
            if tuple(toks[i:i + n]) in other:
                if start is None or i > end:
                    if start is not None:
                        runs.append(" ".join(toks[start:end]))
                    start = i
                end = i + n
        if start is not None:
            runs.append(" ".join(toks[start:end]))
    return runs


def check_prior(factors: dict[str, Factor], prior: dict[str, str], allow: list[str]) -> list[Finding]:
    out: list[Finding] = []
    prior_sets = {name: shingles(segments(text, allow), PRIOR_RUN) for name, text in prior.items()}
    for factor in factors.values():
        segs = segments(factor.text, allow)
        for name, other in prior_sets.items():
            for run in shared_runs(segs, other, PRIOR_RUN):
                out.append(Finding("CRITICAL", "PRIOR_REPEAT", factor.key,
                                   f"{len(run.split())}-word run also in prior file '{name}': \"{run}\""))
    return out


def check_cross(factors: dict[str, Factor], allow: list[str]) -> list[Finding]:
    out: list[Finding] = []
    keys = list(factors)
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            other = shingles(segments(factors[b].text, allow), CROSS_RUN)
            for run in shared_runs(segments(factors[a].text, allow), other, CROSS_RUN):
                out.append(Finding("CRITICAL", "CROSS_FACTOR_REPEAT", a,
                                   f"{len(run.split())}-word run also in {b}: \"{run}\""))
    return out


# ---------------------------------------------------------------- names

def roster_names(text: str) -> list[str]:
    names: list[str] = []
    name_col = None
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if name_col is None:
            lowered = [c.lower() for c in cells]
            if "name" in lowered:
                name_col = lowered.index("name")
            continue
        if set("".join(cells)) <= set("-: "):
            continue
        if name_col < len(cells) and cells[name_col]:
            names.append(cells[name_col])
    return names


def name_patterns(names: list[str]) -> list[tuple[str, re.Pattern]]:
    terms: list[str] = []
    for full in names:
        terms.append(full)
        last = full.split()[-1]
        if len(last) >= 4 and last != full:
            terms.append(last)
    unique = sorted(set(terms), key=len, reverse=True)
    return [(t, re.compile(r"(?<![A-Za-z])" + re.escape(t) + r"(?![A-Za-z])")) for t in unique]


def check_names(factors: dict[str, Factor], names: list[str]) -> list[Finding]:
    out: list[Finding] = []
    patterns = name_patterns(names)
    for factor in factors.values():
        for term, rx in patterns:
            if rx.search(factor.text):
                out.append(Finding("CRITICAL", "NAME_IN_TEXT", factor.key,
                                   f"roster name '{term}' appears; use title, organization, or a count"))
    return out


# ---------------------------------------------------------------- style

def check_style(factor: Factor) -> list[Finding]:
    out: list[Finding] = []
    text = factor.text
    for word in BANNED:
        if re.search(r"\b" + re.escape(word) + r"\b", text, re.I):
            out.append(Finding("WARNING", "BANNED_WORD", factor.key, f"banned word '{word}'"))
    for word, pattern in ONCE_ONLY.items():
        count = len(re.findall(pattern, text, re.I))
        if count > 1:
            out.append(Finding("WARNING", "OVERUSED_WORD", factor.key, f"'{word}' used {count} times (max 1)"))
    if EM_DASH_RE.search(text):
        out.append(Finding("WARNING", "EM_DASH", factor.key, "em dash found; use a comma, colon, or period"))
    if SMART_QUOTES_RE.search(text):
        out.append(Finding("WARNING", "SMART_QUOTES", factor.key, "smart quotes found; use straight quotes"))
    if MARKDOWN_RE.search(text):
        out.append(Finding("WARNING", "MARKDOWN", factor.key, "Markdown characters found; CAS2Net is plain text"))
    for entry in factor.entries:
        words = len(entry.W.split())
        if words > WHAT_MAX_WORDS:
            out.append(Finding("WARNING", "WHAT_TOO_LONG", factor.key,
                               f"What at line {entry.line} has {words} words (max {WHAT_MAX_WORDS})"))
    return out


```

- [ ] **Step 4: Replace `run_checks` with the full version**

Replace the entire `run_checks` function in `check.py` with:

```python
def run_checks(folder: Path, min_wri: int, acq: bool = False, fm: bool = False, supervisor: bool = False,
               prior: dict[str, str] | None = None, names: list[str] | None = None,
               allow: list[str] | None = None) -> list[Finding]:
    missing = [name for name in FACTOR_FILES.values() if not (folder / name).exists()]
    if missing:
        return [Finding("CRITICAL", "MISSING_FILE", "-", f"missing factor file '{m}'") for m in missing]
    factors = {key: parse_factor(key, read_text(folder / name)) for key, name in FACTOR_FILES.items()}
    allow = allow or []
    findings: list[Finding] = []
    for factor in factors.values():
        findings += check_structure(factor, min_wri)
        findings += check_length(factor)
        findings += check_style(factor)
    findings += check_mandatory(factors, acq, fm, supervisor)
    findings += check_prior(factors, prior or {}, allow)
    findings += check_cross(factors, allow)
    findings += check_names(factors, names or [])
    return sorted(findings, key=lambda f: (SEVERITY_ORDER[f.severity], f.factor, f.code))
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `python -m pytest skills/acqdemo-review/scripts/tests/test_check.py`
Expected: 23 passed.

- [ ] **Step 6: Commit**

```bash
git add skills/acqdemo-review/scripts
git commit -m "feat(review): check prior-cycle and cross-factor repeats, names, and style"
```

---

### Task 11: Command-line interface and report

**Files:**
- Modify: `skills/acqdemo-review/scripts/check.py` (append)
- Modify: `skills/acqdemo-review/scripts/tests/test_check.py` (append)

- [ ] **Step 1: Append the failing tests**

Append to `skills/acqdemo-review/scripts/tests/test_check.py`:

```python
# ---------------------------------------------------------------- CLI

def test_main_clean_exit_zero_and_json(tmp_path, capsys):
    folder = write_dir(tmp_path)
    assert check.main(["--dir", str(folder), "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert {d["code"] for d in data} == {"CHAR_COUNT"}


def test_main_critical_exit_one_with_prior_dir_and_roster(tmp_path, capsys):
    prior_dir = tmp_path / "prior"
    prior_dir.mkdir()
    (prior_dir / "fy25.txt").write_text(PRIOR_SENTENCE, encoding="utf-8")
    roster = tmp_path / "roster.md"
    roster.write_text(ROSTER, encoding="utf-8")
    ja = factor_text("alpha", 2) + "W: Reconciled contractor cost reports with the program office for Avery Lee.\nR: Done.\nI: Data.\n"
    folder = write_dir(tmp_path, ja=ja)
    code = check.main(["--dir", str(folder), "--prior", str(prior_dir), "--roster", str(roster)])
    out = capsys.readouterr().out
    assert code == 1
    assert "PRIOR_REPEAT" in out and "NAME_IN_TEXT" in out
    assert out.splitlines()[0].startswith("check: ")


def test_main_mode_midpoint_sets_minimum(tmp_path):
    folder = write_dir(tmp_path, ja=factor_text("alpha", 1), ct=factor_text("bravo", 1), ms=factor_text("charlie", 1))
    assert check.main(["--dir", str(folder), "--mode", "midpoint"]) == 0
    assert check.main(["--dir", str(folder)]) == 1


def test_missing_factor_file(tmp_path):
    folder = write_dir(tmp_path)
    (folder / "Mission Support.txt").unlink()
    assert check.main(["--dir", str(folder)]) == 1
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest skills/acqdemo-review/scripts/tests/test_check.py`
Expected: 4 new tests FAIL with `AttributeError: module 'check' has no attribute 'main'`.

- [ ] **Step 3: Append loaders, report, and `main`**

Append to `skills/acqdemo-review/scripts/check.py`:

```python
def load_prior(paths: list[Path]) -> dict[str, str]:
    prior: dict[str, str] = {}
    for path in paths:
        files = sorted(path.rglob("*")) if path.is_dir() else [path]
        for f in files:
            if f.is_file() and f.suffix.lower() in (".txt", ".md"):
                prior[str(f)] = read_text(f)
    return prior


def load_list(path: Path | None) -> list[str]:
    if path is None:
        return []
    return [ln.strip() for ln in read_text(path).splitlines() if ln.strip() and not ln.startswith("#")]


def format_report(findings: list[Finding]) -> str:
    counts = {s: sum(1 for f in findings if f.severity == s) for s in SEVERITY_ORDER}
    lines = [f"check: {counts['CRITICAL']} CRITICAL, {counts['WARNING']} WARNING, {counts['INFO']} INFO"]
    for f in findings:
        lines.append(f"[{f.severity}] {f.factor} {f.code}: {f.message}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", type=Path, required=True)
    ap.add_argument("--mode", choices=["annual", "midpoint"], default="annual")
    ap.add_argument("--min-wri", type=int)
    ap.add_argument("--acq-cert", action="store_true")
    ap.add_argument("--fm-cert", action="store_true")
    ap.add_argument("--supervisor", action="store_true")
    ap.add_argument("--prior", type=Path, nargs="*", default=[])
    ap.add_argument("--roster", type=Path)
    ap.add_argument("--allow-phrases", type=Path)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    min_wri = args.min_wri if args.min_wri is not None else (3 if args.mode == "annual" else 1)
    names = roster_names(read_text(args.roster)) if args.roster else []
    findings = run_checks(args.dir, min_wri, args.acq_cert, args.fm_cert, args.supervisor,
                          load_prior(args.prior), names, load_list(args.allow_phrases))
    if args.json:
        print(json.dumps([asdict(f) for f in findings], indent=2))
    else:
        print(format_report(findings))
    return 1 if any(f.severity == "CRITICAL" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest skills/acqdemo-review/scripts/tests/test_check.py`
Expected: 27 passed.

- [ ] **Step 5: Smoke-test the CLI by hand**

Run: `python skills/acqdemo-review/scripts/check.py --help`
Expected: usage text beginning with the module docstring.

- [ ] **Step 6: Run the full suite and commit**

Run: `python -m pytest`
Expected: all pass.

```bash
git add skills/acqdemo-review/scripts
git commit -m "feat(review): add check.py command-line interface and report"
```

- [ ] **Step 7: Phase-end sync** (see plan index, "Phase-end sync")
