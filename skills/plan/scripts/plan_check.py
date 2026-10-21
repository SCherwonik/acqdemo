"""Deterministic checks for an AcqDemo contribution plan.

Usage:
    python plan_check.py --file PATH [--min-objectives N] [--kpo-count N]
                         [--kpo-factor JA|CT|MS] [--char-limit N] [--json]

The plan file has one heading per factor, each followed by labeled
objectives (JA1, CT1, MS1, ...), each with a KPI: line and a PRD: line.
Labels are written either "JA1: text" or "(JA1) text":

    Job Achievement and/or Innovation
    JA1: <objective>
    KPI: <measure and target>
    PRD: <duty numbers>

    Communication and/or Teamwork
    CT1: ...

Key Performance Objectives (KPO1, KPO2, ...) are checked only when
--kpo-count is above 0. They are labeled like any objective and sit under
the --kpo-factor heading after that factor's regular objectives. KPO labels
never count toward --min-objectives.

Each factor's objective text (KPOs included, KPI: and PRD: lines excluded,
since those stay in the working file) must fit --char-limit characters,
3900 by default to leave room under CAS2Net's 4,000 per field. 0 turns it off.

Exit code 1 if any CRITICAL finding, otherwise 0.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

FACTOR_HEADINGS = {
    "Job Achievement and/or Innovation": "JA",
    "Communication and/or Teamwork": "CT",
    "Mission Support": "MS",
}
HEADING_BY_KEY = {key: heading for heading, key in FACTOR_HEADINGS.items()}


def normalize_heading(line: str) -> str:
    """Match headings with or without "/or", any case, and a trailing colon."""
    text = line.strip().rstrip(":").lower().replace("and/or", "and")
    return " ".join(text.split())


HEADING_KEYS = {normalize_heading(heading): key for heading, key in FACTOR_HEADINGS.items()}
FACTOR_ORDER = ["JA", "CT", "MS"]
DEFAULT_MIN_OBJECTIVES = 2
DEFAULT_CHAR_LIMIT = 3900

# Tolerates "JA 1:", "ja1:" and "(JA1) text"; only the factor and KPO prefixes count,
# so prose like "at 10:" is ignored.
OBJECTIVE_RE = re.compile(
    r"^\s*(?:\(\s*(JA|CT|MS|KPO)\s*(\d+)\s*\)\s*:?|(JA|CT|MS|KPO)\s*(\d+)\s*:)\s*(.*)$", re.I)
KPI_RE = re.compile(r"^\s*KPI\s*:\s*(.*)$", re.I)
PRD_RE = re.compile(r"^\s*PRD\s*:\s*(.*)$", re.I)
COUNT_WORD_RE = re.compile(r"\d|\b(number|count|percent|hours)\b", re.I)
EM_DASH_RE = re.compile("—")
SEVERITY_ORDER = {"CRITICAL": 0, "WARNING": 1}


@dataclass
class Objective:
    label: str
    prefix: str
    factor: str | None
    text: str
    line: int
    kpi: str | None = None
    kpi_line: int | None = None
    prd: str | None = None
    prd_line: int | None = None


@dataclass
class Finding:
    severity: str
    code: str
    factor: str
    message: str


# ---------------------------------------------------------------- parsing

def parse_plan(text: str) -> tuple[list[Objective], set[str]]:
    text = text.replace("\r\n", "\n")
    current_factor: str | None = None
    current_obj: Objective | None = None
    found_factors: set[str] = set()
    objectives: list[Objective] = []
    for number, raw in enumerate(text.split("\n"), 1):
        line = raw.rstrip()
        stripped = line.strip()
        if normalize_heading(stripped) in HEADING_KEYS:
            current_factor = HEADING_KEYS[normalize_heading(stripped)]
            found_factors.add(current_factor)
            current_obj = None
            continue
        match = OBJECTIVE_RE.match(line)
        if match:
            prefix = (match.group(1) or match.group(3)).upper()
            num = match.group(2) or match.group(4)
            body = match.group(5).strip()
            current_obj = Objective(label=f"{prefix}{num}", prefix=prefix, factor=current_factor,
                                    text=body, line=number)
            objectives.append(current_obj)
            continue
        kpi_match = KPI_RE.match(line)
        if kpi_match and current_obj is not None and current_obj.kpi is None:
            current_obj.kpi = kpi_match.group(1).strip()
            current_obj.kpi_line = number
            continue
        prd_match = PRD_RE.match(line)
        if prd_match and current_obj is not None and current_obj.prd is None:
            current_obj.prd = prd_match.group(1).strip()
            current_obj.prd_line = number
            continue
    return objectives, found_factors


# ---------------------------------------------------------------- checks

def check_missing_factor(found_factors: set[str]) -> list[Finding]:
    out = []
    for key in FACTOR_ORDER:
        if key not in found_factors:
            out.append(Finding("CRITICAL", "MISSING_FACTOR", key,
                               f"heading '{HEADING_BY_KEY[key]}' not found"))
    return out


def check_duplicate_labels(objectives: list[Objective]) -> list[Finding]:
    out = []
    seen: dict[str, int] = {}
    for obj in objectives:
        key = obj.label.upper()
        if key in seen:
            out.append(Finding("CRITICAL", "DUPLICATE_LABEL", obj.factor or obj.prefix,
                               f"{obj.label} at line {obj.line} duplicates the label first used "
                               f"at line {seen[key]}"))
        else:
            seen[key] = obj.line
    return out


def check_label_mismatch(objectives: list[Objective]) -> list[Finding]:
    out = []
    for obj in objectives:
        if obj.factor is None:
            out.append(Finding("CRITICAL", "LABEL_FACTOR_MISMATCH", obj.prefix,
                               f"{obj.label} at line {obj.line} appears before any factor heading"))
        elif obj.prefix != obj.factor and obj.prefix != "KPO":
            out.append(Finding("CRITICAL", "LABEL_FACTOR_MISMATCH", obj.factor,
                               f"{obj.label} at line {obj.line} is labeled {obj.prefix} but appears "
                               f"under the {HEADING_BY_KEY[obj.factor]} heading"))
    return out


def check_kpos(objectives: list[Objective], kpo_count: int, kpo_factor: str | None) -> list[Finding]:
    kpos = [o for o in objectives if o.prefix == "KPO"]
    out = []
    present = {o.label for o in kpos}
    home = kpo_factor or "KPO"
    for n in range(1, kpo_count + 1):
        if f"KPO{n}" not in present:
            out.append(Finding("CRITICAL", "MISSING_KPO", home, f"KPO{n} is required and was not found"))
    if len(present) > kpo_count:
        out.append(Finding("CRITICAL", "KPO_COUNT", home,
                           f"{len(present)} KPO labels found; the pay pool requires exactly {kpo_count}"))
    for obj in kpos:
        if kpo_factor and obj.factor is not None and obj.factor != kpo_factor:
            out.append(Finding("WARNING", "KPO_FACTOR", obj.factor,
                               f"{obj.label} at line {obj.line} sits under the {HEADING_BY_KEY[obj.factor]} "
                               f"heading; the pay pool places KPOs under {HEADING_BY_KEY[kpo_factor]}"))
        if obj.factor is not None:
            later_regular = [o for o in objectives
                             if o.prefix == obj.factor and o.factor == obj.factor and o.line > obj.line]
            if later_regular:
                out.append(Finding("WARNING", "KPO_ORDER", obj.factor,
                                   f"{obj.label} at line {obj.line} appears before the "
                                   f"{HEADING_BY_KEY[obj.factor]} regular objectives; write KPOs after them"))
    return out


def check_min_objectives(objectives: list[Objective], found_factors: set[str],
                         min_objectives: int) -> list[Finding]:
    out = []
    counts: dict[str, int] = {}
    for obj in objectives:
        if obj.factor is not None and obj.prefix == obj.factor:
            counts[obj.factor] = counts.get(obj.factor, 0) + 1
    for factor in found_factors:
        n = counts.get(factor, 0)
        if n < min_objectives:
            out.append(Finding("CRITICAL", "MIN_OBJECTIVES", factor,
                               f"{n} objective(s); minimum is {min_objectives}"))
    return out


def check_kpi(objectives: list[Objective]) -> list[Finding]:
    out = []
    for obj in objectives:
        if not obj.kpi or not obj.kpi.strip():
            out.append(Finding("WARNING", "NO_KPI", obj.factor or obj.prefix,
                               f"{obj.label} at line {obj.line} has no KPI: line"))
        elif not COUNT_WORD_RE.search(obj.kpi):
            out.append(Finding("WARNING", "KPI_NOT_MEASURABLE", obj.factor or obj.prefix,
                               f"{obj.label} KPI '{obj.kpi}' has no digit or count word "
                               f"(number, count, percent, hours)"))
    return out


def check_prd(objectives: list[Objective]) -> list[Finding]:
    out = []
    for obj in objectives:
        if not obj.prd or not obj.prd.strip():
            out.append(Finding("WARNING", "NO_PRD_TIEBACK", obj.factor or obj.prefix,
                               f"{obj.label} at line {obj.line} has no PRD: tie-back"))
    return out


# Square brackets never appear in finished plan text, so any bracketed span is an unfilled gap:
# "[N]", "[TBD]", "[CONFIRM: ...]". Angle brackets count only when they enclose words, the way
# the pay pool templates write their slots ("<Insert Program(s) Here>"), so "< 5 days" survives.
PLACEHOLDER_RE = re.compile(r"\[[^\]\n]*\]|<[^<>\n]*[A-Za-z][^<>\n]*>")


def check_placeholders(text: str) -> list[Finding]:
    """An unfilled placeholder must never reach CAS2Net.

    The plan skill leaves a labeled placeholder rather than invent a number, which is right,
    but a date elsewhere on the line supplies the digit KPI_NOT_MEASURABLE looks for, so
    "[N] pipelines by 30 Sep 2027" passed every other check. CRITICAL because the fix is
    always the same and always the user's: supply the value.
    """
    out: list[Finding] = []
    for number, line in enumerate(text.split("\n"), 1):
        for match in PLACEHOLDER_RE.finditer(line):
            out.append(Finding("CRITICAL", "PLACEHOLDER", "-",
                               f"line {number}: unfilled placeholder '{match.group(0)}'; "
                               "fill it before the plan goes into CAS2Net"))
    return out


def factor_texts(text: str) -> dict[str, str]:
    """The text each factor's CAS2Net field receives: every line under the heading except KPI: and PRD:."""
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for raw in text.split("\n"):
        stripped = raw.strip()
        if normalize_heading(stripped) in HEADING_KEYS:
            current = HEADING_KEYS[normalize_heading(stripped)]
            sections.setdefault(current, [])
            continue
        if current is None or not stripped or KPI_RE.match(raw) or PRD_RE.match(raw):
            continue
        sections[current].append(stripped)
    return {key: "\n".join(lines) for key, lines in sections.items()}


def check_char_limit(text: str, char_limit: int) -> list[Finding]:
    """Each factor is its own CAS2Net field with a hard cap, and Mission Support carries the KPOs too."""
    if char_limit <= 0:
        return []
    out = []
    for key, body in factor_texts(text).items():
        if len(body) > char_limit:
            out.append(Finding("CRITICAL", "FACTOR_TOO_LONG", key,
                               f"{len(body)} characters of objective text; the limit is {char_limit}. "
                               f"Tighten the wording before it goes into CAS2Net"))
    return out


def check_em_dash(text: str) -> list[Finding]:
    if EM_DASH_RE.search(text):
        return [Finding("WARNING", "EM_DASH", "-", "em dash found; use a comma, colon, or period")]
    return []


# ---------------------------------------------------------------- orchestration

def read_text(path: Path) -> str:
    data = path.read_bytes()
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return data.decode("cp1252", errors="replace")


def run_checks(text: str, min_objectives: int = DEFAULT_MIN_OBJECTIVES,
               kpo_count: int = 0, kpo_factor: str | None = None,
               char_limit: int = DEFAULT_CHAR_LIMIT) -> list[Finding]:
    text = text.replace("\r\n", "\n")
    objectives, found_factors = parse_plan(text)
    if kpo_count <= 0:
        objectives = [o for o in objectives if o.prefix != "KPO"]
    findings: list[Finding] = []
    findings += check_missing_factor(found_factors)
    findings += check_duplicate_labels(objectives)
    findings += check_label_mismatch(objectives)
    findings += check_kpos(objectives, kpo_count, kpo_factor)
    findings += check_min_objectives(objectives, found_factors, min_objectives)
    findings += check_kpi(objectives)
    findings += check_prd(objectives)
    findings += check_placeholders(text)
    findings += check_char_limit(text, char_limit)
    findings += check_em_dash(text)
    return sorted(findings, key=lambda f: (SEVERITY_ORDER[f.severity], f.factor, f.code))


def format_report(findings: list[Finding]) -> str:
    counts = {s: sum(1 for f in findings if f.severity == s) for s in SEVERITY_ORDER}
    lines = [f"plan_check: {counts['CRITICAL']} CRITICAL, {counts['WARNING']} WARNING"]
    for f in findings:
        lines.append(f"[{f.severity}] {f.factor} {f.code}: {f.message}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", type=Path, required=True)
    ap.add_argument("--min-objectives", type=int, default=DEFAULT_MIN_OBJECTIVES)
    ap.add_argument("--kpo-count", type=int, default=0,
                    help="exact number of KPOs the plan carries; 0 turns KPO checks off")
    ap.add_argument("--kpo-factor", choices=FACTOR_ORDER, type=str.upper, default=None,
                    help="factor the KPOs are written under")
    ap.add_argument("--char-limit", type=int, default=DEFAULT_CHAR_LIMIT,
                    help="most characters of objective text per factor; 0 turns the check off")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    text = read_text(args.file)
    findings = run_checks(text, args.min_objectives, args.kpo_count, args.kpo_factor, args.char_limit)
    if args.json:
        print(json.dumps([asdict(f) for f in findings], indent=2))
    else:
        print(format_report(findings))
    return 1 if any(f.severity == "CRITICAL" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
