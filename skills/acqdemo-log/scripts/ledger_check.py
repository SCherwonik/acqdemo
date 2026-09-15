"""Deterministic checks for an AcqDemo evidence ledger (FY<yy>/ledger.md).

Usage:
    python ledger_check.py --file <ledger.md> [--json]
    python ledger_check.py --file <ledger.md> --next-id

Parses '## L-<digits> <title>' sections and '- key: value' fields, with
indented sub-items under 'numbers' and 'lenses'. See
../../acqdemo/references/ledger-format.md for the entry format.

Exit code 1 if any CRITICAL finding, otherwise 0. '--next-id' always exits 0.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

HEADING_RE = re.compile(r"^## (.*)$")
ID_RE = re.compile(r"^(L-\d+)(?:\s+(.*))?$")
FIELD_RE = re.compile(r"^- ([A-Za-z_][A-Za-z0-9_]*):\s?(.*)$")
SUBITEM_RE = re.compile(r"^\s+- (.*)$")

REQUIRED_FIELDS = ["status", "dates", "what", "role"]
STATUS_VALUES = {"candidate", "ready", "allocated", "submitted", "rejected"}
ROLE_VALUES = {"owned", "co-owned", "owned-a-piece", "supported"}
SUSTAINED_VALUES = {"yes", "one-time"}
LIST_FIELDS = {"numbers", "lenses"}
SEVERITY_ORDER = {"CRITICAL": 0, "WARNING": 1}


@dataclass
class Finding:
    severity: str
    code: str
    entry: str
    message: str


@dataclass
class LedgerEntry:
    raw_heading: str
    id_token: str
    title: str
    line: int
    fields: dict[str, str] = field(default_factory=dict)
    numbers: list[dict[str, str | None]] = field(default_factory=list)
    lenses: list[str] = field(default_factory=list)

    @property
    def display(self) -> str:
        return self.raw_heading


# ---------------------------------------------------------------- parsing

def parse_number_item(text: str) -> dict[str, str | None]:
    parts = [p.strip() for p in text.split("|")]
    item: dict[str, str | None] = {"text": parts[0] if parts else "", "source": None, "basis": None}
    for part in parts[1:]:
        if ":" in part:
            key, value = part.split(":", 1)
            key = key.strip().lower()
            if key in ("source", "basis"):
                item[key] = value.strip()
    return item


def parse_ledger(text: str) -> list[LedgerEntry]:
    text = text.replace("\r\n", "\n")
    current: LedgerEntry | None = None
    current_list: str | None = None
    entries: list[LedgerEntry] = []
    for number, raw in enumerate(text.split("\n"), 1):
        heading = HEADING_RE.match(raw)
        if heading:
            rest = heading.group(1).strip()
            match = ID_RE.match(rest)
            if match:
                id_token, title = match.group(1), (match.group(2) or "").strip()
            else:
                id_token, title = rest, ""
            current = LedgerEntry(raw_heading=rest, id_token=id_token, title=title, line=number)
            entries.append(current)
            current_list = None
            continue
        if current is None:
            continue  # preamble such as "# Ledger FY26"
        field_match = FIELD_RE.match(raw)
        if field_match:
            key, value = field_match.group(1), field_match.group(2).strip()
            if key in LIST_FIELDS:
                current_list = key
            else:
                current.fields[key] = value
                current_list = None
            continue
        sub_match = SUBITEM_RE.match(raw)
        if sub_match and current_list:
            item_text = sub_match.group(1).strip()
            if current_list == "numbers":
                current.numbers.append(parse_number_item(item_text))
            elif current_list == "lenses":
                current.lenses.append(item_text)
    return entries


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    data = path.read_bytes()
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return data.decode("cp1252", errors="replace")


# ---------------------------------------------------------------- checks

def check_entry(entry: LedgerEntry) -> list[Finding]:
    out: list[Finding] = []
    if not re.fullmatch(r"L-\d+", entry.id_token):
        out.append(Finding("CRITICAL", "BAD_ID", entry.display,
                           f"heading '{entry.raw_heading}' id is not 'L-' plus digits"))

    missing = [f for f in REQUIRED_FIELDS if not entry.fields.get(f, "").strip()]
    if missing:
        out.append(Finding("CRITICAL", "MISSING_FIELD", entry.display,
                           f"missing required field(s): {', '.join(missing)}"))

    status = entry.fields.get("status", "").strip()
    if status and status not in STATUS_VALUES:
        out.append(Finding("CRITICAL", "BAD_VALUE", entry.display,
                           f"status '{status}' is not one of {sorted(STATUS_VALUES)}"))
    role = entry.fields.get("role", "").strip()
    if role and role not in ROLE_VALUES:
        out.append(Finding("CRITICAL", "BAD_VALUE", entry.display,
                           f"role '{role}' is not one of {sorted(ROLE_VALUES)}"))
    sustained = entry.fields.get("sustained", "").strip()
    if sustained and sustained not in SUSTAINED_VALUES:
        out.append(Finding("CRITICAL", "BAD_VALUE", entry.display,
                           f"sustained '{sustained}' is not one of {sorted(SUSTAINED_VALUES)}"))

    for item in entry.numbers:
        if not item.get("source"):
            out.append(Finding("CRITICAL", "NUMBER_NO_SOURCE", entry.display,
                               f"number '{item['text']}' has no source"))
        elif (item["source"] or "").strip().lower() == "estimate" and not item.get("basis"):
            out.append(Finding("CRITICAL", "ESTIMATE_NO_BASIS", entry.display,
                               f"number '{item['text']}' is an estimate with no basis"))

    if status == "ready":
        audience = entry.fields.get("audience", "").strip()
        missing_bits = []
        if not audience:
            missing_bits.append("audience")
        if not entry.numbers:
            missing_bits.append("numbers")
        if not entry.lenses:
            missing_bits.append("lenses")
        if missing_bits:
            out.append(Finding("WARNING", "READY_INCOMPLETE", entry.display,
                               f"status ready but missing {', '.join(missing_bits)}"))

    overlap = entry.fields.get("prior_cycle_overlap", "").strip()
    if overlap.lower().startswith("continuing") and "delta" not in overlap.lower():
        out.append(Finding("WARNING", "OVERLAP_NO_DELTA", entry.display,
                           "prior_cycle_overlap is continuing with no delta noted"))
    return out


def check_duplicates(entries: list[LedgerEntry]) -> list[Finding]:
    out: list[Finding] = []
    seen: dict[int, str] = {}
    for entry in entries:
        match = re.fullmatch(r"L-(\d+)", entry.id_token)
        if not match:
            continue
        num = int(match.group(1))
        if num in seen:
            out.append(Finding("CRITICAL", "DUPLICATE_ID", entry.display,
                               f"id number {num} duplicates entry '{seen[num]}'"))
        else:
            seen[num] = entry.display
    return out


def run_checks(entries: list[LedgerEntry]) -> list[Finding]:
    findings: list[Finding] = []
    for entry in entries:
        findings += check_entry(entry)
    findings += check_duplicates(entries)
    return sorted(findings, key=lambda f: (SEVERITY_ORDER[f.severity], f.entry, f.code))


def next_id(entries: list[LedgerEntry]) -> str:
    nums = []
    for entry in entries:
        match = re.fullmatch(r"L-(\d+)", entry.id_token)
        if match:
            nums.append(int(match.group(1)))
    number = (max(nums) + 1) if nums else 1
    return f"L-{number:03d}"


# ---------------------------------------------------------------- report / CLI

def format_report(findings: list[Finding]) -> str:
    counts = {s: sum(1 for f in findings if f.severity == s) for s in SEVERITY_ORDER}
    lines = [f"ledger_check: {counts['CRITICAL']} CRITICAL, {counts['WARNING']} WARNING"]
    for f in findings:
        lines.append(f"[{f.severity}] {f.entry} {f.code}: {f.message}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", type=Path, required=True)
    ap.add_argument("--next-id", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    entries = parse_ledger(read_text(args.file))

    if args.next_id:
        print(next_id(entries))
        return 0

    findings = run_checks(entries)
    if args.json:
        print(json.dumps([asdict(f) for f in findings], indent=2))
    else:
        print(format_report(findings))
    return 1 if any(f.severity == "CRITICAL" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
