"""Summarize a calendar list export for an AcqDemo rating period as Markdown.

Export the Subject and Start columns from a calendar list view (README Section 6.4),
paste into a text file, then run:
    python calendar_harvest.py --file calendar.txt --since 2025-10-01 --until 2026-09-30 [--out FILE]

Lines are tab-separated. A header row naming Subject and Start is used when present;
otherwise the first column is the subject and the second is the start.
Canceled meetings and meetings outside the period are skipped and counted.
Output: totals, recurring series (2 or more occurrences), and meetings by month.
"""
from __future__ import annotations

import argparse
import codecs
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

DATE_FORMATS = [
    "%a %m/%d/%Y %I:%M %p",
    "%m/%d/%Y %I:%M %p",
    "%a %m/%d/%Y %H:%M",
    "%m/%d/%Y %H:%M",
    "%Y-%m-%d %H:%M",
    "%a %m/%d/%Y",
    "%m/%d/%Y",
    "%Y-%m-%d",
]
CANCELED_RE = re.compile(r"^\s*(canceled|cancelled)\s*:", re.I)
PREFIX_RE = re.compile(r"^\s*((re|fw|fwd|updated|accepted|tentative|copy)\s*:\s*)+", re.I)


@dataclass
class Meeting:
    subject: str
    start: datetime


@dataclass
class Harvest:
    meetings: list[Meeting] = field(default_factory=list)
    canceled: int = 0
    outside: int = 0
    unparsed: list[str] = field(default_factory=list)


def read_text(path: Path) -> str:
    data = path.read_bytes()
    if data.startswith((codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)):
        return data.decode("utf-16")
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return data.decode("cp1252", errors="replace")


def parse_start(value: str) -> datetime | None:
    cleaned = " ".join(value.split())
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    return None


def rows(text: str) -> list[tuple[str, str, str]]:
    """Return (subject, start, raw_line) for every data line."""
    lines = [ln for ln in text.replace("\r\n", "\n").split("\n") if ln.strip()]
    if not lines:
        return []
    header = [c.strip().lower() for c in lines[0].split("\t")]
    if "subject" in header and "start" in header:
        subject_idx, start_idx, data = header.index("subject"), header.index("start"), lines[1:]
    else:
        subject_idx, start_idx, data = 0, 1, lines
    out: list[tuple[str, str, str]] = []
    for line in data:
        cells = line.split("\t")
        subject = cells[subject_idx].strip() if subject_idx < len(cells) else ""
        start = cells[start_idx].strip() if start_idx < len(cells) else ""
        out.append((subject, start, line))
    return out


def harvest(text: str, since: date, until: date) -> Harvest:
    result = Harvest()
    for subject, start, raw in rows(text):
        if CANCELED_RE.match(subject):
            result.canceled += 1
            continue
        when = parse_start(start)
        if when is None:
            result.unparsed.append(raw)
            continue
        if not since <= when.date() <= until:
            result.outside += 1
            continue
        result.meetings.append(Meeting(subject, when))
    result.meetings.sort(key=lambda m: (m.start, m.subject))
    return result


def series_key(subject: str) -> str:
    return " ".join(PREFIX_RE.sub("", subject).lower().split())


def recurring(meetings: list[Meeting]) -> list[tuple[str, int, date, date]]:
    groups: dict[str, list[Meeting]] = defaultdict(list)
    for m in meetings:
        groups[series_key(m.subject)].append(m)
    out = []
    for group in groups.values():
        if len(group) < 2:
            continue
        display = Counter(PREFIX_RE.sub("", m.subject).strip() for m in group).most_common(1)[0][0]
        out.append((display, len(group), group[0].start.date(), group[-1].start.date()))
    return sorted(out, key=lambda r: (-r[1], r[0].lower()))


def render_markdown(result: Harvest, since: date, until: date) -> str:
    lines = [f"# Calendar harvest: {since} to {until}", "",
             f"- Meetings in period: {len(result.meetings)}",
             f"- Canceled (skipped): {result.canceled}",
             f"- Outside period (skipped): {result.outside}",
             f"- Unreadable lines: {len(result.unparsed)}"]
    lines += [f"  - {raw.strip()}" for raw in result.unparsed[:5]]
    lines += ["", "## Recurring series (2 or more)"]
    series = recurring(result.meetings)
    if series:
        lines += ["", "| Series | Occurrences | First | Last |", "|---|---|---|---|"]
        lines += [f"| {name} | {count} | {first} | {last} |" for name, count, first, last in series]
    else:
        lines.append("- None.")
    lines += ["", "## Meetings by month"]
    by_month: dict[str, list[Meeting]] = defaultdict(list)
    for m in result.meetings:
        by_month[m.start.strftime("%Y-%m")].append(m)
    for month, items in by_month.items():
        lines += ["", f"### {month} ({len(items)})"]
        lines += [f"- {m.start:%Y-%m-%d %H:%M} {m.subject}" for m in items]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", type=Path, required=True)
    ap.add_argument("--since", type=date.fromisoformat, required=True, help="YYYY-MM-DD")
    ap.add_argument("--until", type=date.fromisoformat, required=True, help="YYYY-MM-DD")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args(argv)

    if not args.file.exists():
        print(f"calendar_harvest: file not found: {args.file}")
        return 2
    result = harvest(read_text(args.file), args.since, args.until)
    markdown = render_markdown(result, args.since, args.until)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(markdown, encoding="utf-8")
        print(f"calendar_harvest: {len(result.meetings)} meetings in period, "
              f"{len(recurring(result.meetings))} recurring series -> {args.out}")
    else:
        print(markdown)
    return 0


if __name__ == "__main__":
    sys.exit(main())
