"""Deterministic checks for AcqDemo self-assessment drafts.

Usage:
    python check.py --dir <folder> [--mode annual|midpoint|closeout] [--min-entries N]
                    [--acq-cert] [--fm-cert] [--supervisor]
                    [--prior FILE_OR_DIR ...] [--roster roster.md]
                    [--allow-phrases FILE] [--what-label C|W] [--json]

The folder must contain the three factor files:
    Job Achievement and Innovation.txt
    Communication and Teamwork.txt
    Mission Support.txt

Exit code 1 if any CRITICAL finding, otherwise 0.
"""
from __future__ import annotations

import argparse
import codecs
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
# Deliberately the longest of the three. This one compares two pieces of text inside the same
# factor, where the mandatory opening paragraphs are short, formulaic and impossible to delete,
# so overlap is expected rather than suspicious. The longest boilerplate run those paragraphs
# actually carry is "for the current cycle ending 30 Sep 2026", eight words; the threshold sits
# above it so the rule fires on restated substance, not on the scaffolding.
PREAMBLE_RUN = 10
CONTRIBUTION_MAX_WORDS = 35
BANNED = ["seamlessly", "friction-free", "perfectly", "unbroken", "synergy", "cutting-edge", "world-class"]
ONCE_ONLY = {"robust": r"\brobust\b", "leverage": r"\bleverag\w*"}
SEVERITY_ORDER = {"CRITICAL": 0, "WARNING": 1, "INFO": 2}

LABEL_RE = re.compile(r"^\s*(W|C|R|I)\s*:\s?(.*)$", re.I)
LABEL_PREFIX_RE = re.compile(r"^\s*[WCRI]\s*:\s?", re.M | re.I)
LOWER_LABEL_RE = re.compile(r"^\s*[wcri]\s*:", re.M)
# "C:" (Contribution) is the current label; older guidance used "W:" (What). Both start an entry.
LABEL_STYLE_RE = {"W": re.compile(r"^\s*W\s*:", re.M | re.I), "C": re.compile(r"^\s*C\s*:", re.M | re.I)}
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
    C: str = ""
    R: str = ""
    I: str = ""
    line: int = 0

    @property
    def complete(self) -> bool:
        return bool(self.C.strip() and self.R.strip() and self.I.strip())


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
            label, body = match.group(1).upper(), match.group(2)
            if label in ("W", "C"):
                if current is None and para:
                    factor.preamble.append(" ".join(para))
                    para = []
                current = Entry(C=body, line=number)
                factor.entries.append(current)
                last_field = "C"
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


# ---------------------------------------------------------------- structure

def check_structure(factor: Factor, min_entries: int, what_label: str = "C") -> list[Finding]:
    out: list[Finding] = []
    other = "W" if what_label == "C" else "C"
    mismatched = len(LABEL_STYLE_RE[other].findall(factor.text))
    if mismatched:
        out.append(Finding("WARNING", "LABEL_STYLE", factor.key,
                           f"{mismatched} entries start with '{other}:'; this pay pool's Contribution label is "
                           f"'{what_label}:' (set --what-label to match your pay pool)"))
    lowercase = len(LOWER_LABEL_RE.findall(factor.text))
    if lowercase:
        out.append(Finding("WARNING", "LABEL_CASE", factor.key,
                           f"{lowercase} labels are lowercase; write them as C:, R:, I:"))
    for entry in factor.entries:
        if not entry.complete:
            missing = ", ".join(k for k in ("C", "R", "I") if not getattr(entry, k).strip())
            out.append(Finding("CRITICAL", "ENTRY_INCOMPLETE", factor.key,
                               f"entry starting line {entry.line} is missing {missing}"))
    for number in factor.orphans:
        out.append(Finding("CRITICAL", "ORPHAN_LABEL", factor.key,
                           f"line {number}: R or I label outside a C-R-I entry, or repeated"))
    complete = sum(1 for e in factor.entries if e.complete)
    if complete < min_entries:
        out.append(Finding("CRITICAL", "MIN_ENTRIES", factor.key,
                           f"{complete} complete C-R-I; minimum is {min_entries}"))
    return out


def check_mandatory(factors: dict[str, Factor], acq: bool, fm: bool, supervisor: bool) -> list[Finding]:
    out: list[Finding] = []
    ja, ms = factors["JA"], factors["MS"]
    if supervisor and not (ja.preamble and SUPERVISOR_RE.search(ja.preamble[0])):
        out.append(Finding("CRITICAL", "SUPERVISOR_STATEMENT", "JA",
                           "first JA paragraph must state 'I supervise X military, Y civilians, "
                           "and manage Z contractors.' before any C-R-I"))
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
                               f"MS paragraph {position + 1} must be the {label}, before any C-R-I"))
    return out


def check_length(factor: Factor) -> list[Finding]:
    count = char_count(factor.text)
    out = [Finding("INFO", "CHAR_COUNT", factor.key, f"{count} characters (line breaks count as 2)")]
    if count > HARD_LIMIT:
        out.append(Finding("CRITICAL", "CHAR_LIMIT", factor.key, f"{count} characters exceeds {HARD_LIMIT}"))
    elif count > SOFT_LIMIT:
        out.append(Finding("WARNING", "CHAR_SOFT_LIMIT", factor.key, f"{count} characters exceeds {SOFT_LIMIT}"))
    return out


# ---------------------------------------------------------------- repeats

def segments(text: str, allow: list[str]) -> list[list[str]]:
    # Break runs at every label and blank line so a repeat never bridges two fields or entries.
    body = LABEL_PREFIX_RE.sub("\x00", text.replace("\r\n", "\n"))
    body = re.sub(r"\n[ \t]*\n", "\x00", body)
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


def check_preamble(factors: dict[str, Factor], allow: list[str]) -> list[Finding]:
    """Flag a C-R-I that restates the mandatory opening paragraphs of its own factor.

    CROSS_FACTOR_REPEAT compares factors against each other and PRIOR_REPEAT compares a factor
    against a completed cycle, so neither one sees an entry echoing the certification or
    supervisory statement sitting four lines above it in the same file. Runs are reported from
    the entries, never from the preamble: the preamble is required text the employee cannot
    remove, so the entry is the only side of the overlap they can rewrite. A factor with no
    opening paragraphs has nothing to compare and produces nothing here, and entry-against-entry
    is out of scope on purpose.
    """
    out: list[Finding] = []
    for factor in factors.values():
        if not factor.preamble or not factor.entries:
            continue
        opening = shingles(segments("\n\n".join(factor.preamble), allow), PREAMBLE_RUN)
        # Blank line between every field so a run can never bridge two fields or two entries,
        # which is the same contract segments() gives the other two repeat checks.
        body = "\n\n".join(field for e in factor.entries for field in (e.C, e.R, e.I))
        for run in shared_runs(segments(body, allow), opening, PREAMBLE_RUN):
            out.append(Finding("WARNING", "PREAMBLE_REPEAT", factor.key,
                               f"{len(run.split())}-word run also in this factor's "
                               f"opening paragraphs: \"{run}\""))
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
    # Full names match in any case; a last name alone must be capitalized so common words ("young") pass.
    return [(t, re.compile(r"(?<![A-Za-z])" + re.escape(t) + r"(?![A-Za-z])", re.I if t in names else 0))
            for t in unique]


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
        words = len(entry.C.split())
        if words > CONTRIBUTION_MAX_WORDS:
            out.append(Finding("WARNING", "CONTRIBUTION_TOO_LONG", factor.key,
                               f"Contribution at line {entry.line} has {words} words (max {CONTRIBUTION_MAX_WORDS})"))
    return out


# ---------------------------------------------------------------- orchestration

def read_text(path: Path) -> str:
    data = path.read_bytes()
    if data.startswith((codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)):
        return data.decode("utf-16")
    # UTF-16 saved without a BOM: an even length, and NUL bytes, at least a quarter of the file.
    # Every part matters. Without the NUL floor a 2-byte ASCII file decodes to one wrong character
    # and without the even-length test a 3-byte file raises "truncated data".
    if len(data) >= 2 and len(data) % 2 == 0 and data.count(0) >= max(1, len(data) // 4):
        try:
            return data.decode("utf-16-le" if data[1::2].count(0) >= data[0::2].count(0) else "utf-16-be")
        except UnicodeDecodeError:
            pass  # NUL bytes in something that is not UTF-16; fall through rather than crash
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return data.decode("cp1252", errors="replace")


def run_checks(folder: Path, min_entries: int, acq: bool = False, fm: bool = False, supervisor: bool = False,
               prior: dict[str, str] | None = None, names: list[str] | None = None,
               allow: list[str] | None = None, what_label: str = "C") -> list[Finding]:
    missing = [name for name in FACTOR_FILES.values() if not (folder / name).exists()]
    if missing:
        return [Finding("CRITICAL", "MISSING_FILE", "-", f"missing factor file '{m}'") for m in missing]
    factors = {key: parse_factor(key, read_text(folder / name)) for key, name in FACTOR_FILES.items()}
    allow = allow or []
    findings: list[Finding] = []
    for factor in factors.values():
        findings += check_structure(factor, min_entries, what_label)
        findings += check_length(factor)
        findings += check_style(factor)
    findings += check_mandatory(factors, acq, fm, supervisor)
    findings += check_prior(factors, prior or {}, allow)
    findings += check_cross(factors, allow)
    findings += check_preamble(factors, allow)
    findings += check_names(factors, names or [])
    return sorted(findings, key=lambda f: (SEVERITY_ORDER[f.severity], f.factor, f.code))


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
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", type=Path, required=True)
    ap.add_argument("--mode", choices=["annual", "midpoint", "closeout"], default="annual")
    ap.add_argument("--min-entries", type=int)
    ap.add_argument("--acq-cert", action="store_true")
    ap.add_argument("--fm-cert", action="store_true")
    ap.add_argument("--supervisor", action="store_true")
    ap.add_argument("--prior", type=Path, nargs="*", default=[])
    ap.add_argument("--roster", type=Path)
    ap.add_argument("--allow-phrases", type=Path)
    ap.add_argument("--what-label", choices=["C", "W"], default="C")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    min_entries = args.min_entries if args.min_entries is not None else (3 if args.mode == "annual" else 1)
    names = roster_names(read_text(args.roster)) if args.roster else []
    findings = run_checks(args.dir, min_entries, args.acq_cert, args.fm_cert, args.supervisor,
                          load_prior(args.prior), names, load_list(args.allow_phrases),
                          what_label=args.what_label)
    if args.json:
        print(json.dumps([asdict(f) for f in findings], indent=2))
    else:
        print(format_report(findings))
    return 1 if any(f.severity == "CRITICAL" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
