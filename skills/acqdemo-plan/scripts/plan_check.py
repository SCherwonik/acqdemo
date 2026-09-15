"""Deterministic checks for an AcqDemo contribution plan.

Usage:
    python plan_check.py --file PATH [--min-objectives N] [--json]

The plan file has one heading per factor, each followed by labeled
objectives (JA1, CT1, MS1, ...), each with a KPI: line and a PRD: line:

    Job Achievement and/or Innovation
    JA1: <objective>
    KPI: <measure and target>
    PRD: <duty numbers>

    Communication and/or Teamwork
    CT1: ...

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

# Tolerates "JA 1:" and "ja1:"; only the three factor prefixes count, so prose like "at 10:" is ignored.
OBJECTIVE_RE = re.compile(r"^\s*(JA|CT|MS)\s*(\d+)\s*:\s*(.*)$", re.I)
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
            prefix, num, body = match.group(1).upper(), match.group(2), match.group(3).strip()
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
        elif obj.prefix != obj.factor:
            out.append(Finding("CRITICAL", "LABEL_FACTOR_MISMATCH", obj.factor,
                               f"{obj.label} at line {obj.line} is labeled {obj.prefix} but appears "
                               f"under the {HEADING_BY_KEY[obj.factor]} heading"))
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


def run_checks(text: str, min_objectives: int = DEFAULT_MIN_OBJECTIVES) -> list[Finding]:
    text = text.replace("\r\n", "\n")
    objectives, found_factors = parse_plan(text)
    findings: list[Finding] = []
    findings += check_missing_factor(found_factors)
    findings += check_duplicate_labels(objectives)
    findings += check_label_mismatch(objectives)
    findings += check_min_objectives(objectives, found_factors, min_objectives)
    findings += check_kpi(objectives)
    findings += check_prd(objectives)
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
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    text = read_text(args.file)
    findings = run_checks(text, args.min_objectives)
    if args.json:
        print(json.dumps([asdict(f) for f in findings], indent=2))
    else:
        print(format_report(findings))
    return 1 if any(f.severity == "CRITICAL" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
