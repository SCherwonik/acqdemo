# Phase 3: Harvest Scripts (Tasks 12-15)

Back to [plan index](../2026-09-15-acqdemo-wave1.md).

Two standard-library scripts turn raw evidence into Markdown that the harvest skill (Task 17) clusters into candidate ledger entries:
- `skills/harvest/scripts/git_harvest.py`: commits, months, authors, and tags from local repositories (`git log`) and GitHub repositories (`gh api`), merge commits skipped.
- `skills/harvest/scripts/calendar_harvest.py`: a calendar list export (Subject and Start, tab-separated; README Section 6.4) filtered to the rating period, with canceled meetings skipped, recurring series counted, and meetings listed by month.

Tests live in `skills/harvest/scripts/tests/`.

---

### Task 12: Git harvest parsing, filtering, and Markdown

**Files:**
- Create: `skills/harvest/scripts/git_harvest.py`
- Create: `skills/harvest/scripts/tests/test_git_harvest.py`

- [ ] **Step 1: Write the failing tests**

Create `skills/harvest/scripts/tests/test_git_harvest.py`:

```python
"""Tests for skills/harvest/scripts/git_harvest.py."""
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import git_harvest as gh  # noqa: E402

SEP = gh.SEP

def commit(sha, date, author="Dana", subject="work"):
    return gh.Commit(sha, date, author, subject)

def test_parse_git_log_skips_malformed_lines():
    output = f"abc{SEP}2026-01-05{SEP}Dana{SEP}feat: add thing\nnot a commit line\n{SEP}{SEP}{SEP}\n"
    assert gh.parse_git_log(output) == [commit("abc", "2026-01-05", subject="feat: add thing")]

def test_parse_github_items_skips_merges_and_keeps_first_line():
    items = [
        {"sha": "a1", "parents": [{}], "commit": {"author": {"name": "Dana", "date": "2026-02-01T10:00:00Z"},
                                                   "message": "fix: bug\n\nlong body"}},
        {"sha": "m1", "parents": [{}, {}], "commit": {"author": {"name": "Dana", "date": "2026-02-02T10:00:00Z"},
                                                       "message": "Merge branch"}},
    ]
    assert gh.parse_github_items(items) == [commit("a1", "2026-02-01", subject="fix: bug")]

def test_filter_commits_by_period_and_author_sorted():
    commits = [commit("b", "2026-03-01", "Dana Smith"), commit("a", "2025-09-30", "Dana Smith"),
               commit("c", "2026-01-01", "Robin Park"), commit("d", "2025-10-01", "dana smith")]
    kept = gh.filter_commits(commits, "2025-10-01", "2026-09-30", ["dana"])
    assert [c.sha for c in kept] == ["d", "b"]

def test_repo_summary_properties():
    s = gh.RepoSummary("tool", [commit("a", "2026-01-05"), commit("b", "2026-01-20", "Robin"), commit("c", "2026-03-02")])
    assert (s.first, s.last) == ("2026-01-05", "2026-03-02")
    assert s.by_month == {"2026-01": 2, "2026-03": 1}
    assert s.authors["Dana"] == 2

def test_render_markdown_totals_errors_and_order():
    ok = gh.RepoSummary("tool", [commit("a", "2026-01-05", subject="first"), commit("b", "2026-02-01", subject="second")],
                        tags=[("v1.0", "2026-02-01")])
    empty = gh.RepoSummary("quiet", [])
    broken = gh.RepoSummary("owner/missing", [], error="Not Found")
    md = gh.render_markdown([ok, empty, broken], "2025-10-01", "2026-09-30")
    assert md.startswith("# Git harvest: 2025-10-01 to 2026-09-30")
    assert "| tool | 2 | 2026-01-05 | 2026-02-01 | 2 | 1 |" in md
    assert "- No commits in this period." in md
    assert "- Error: Not Found" in md
    assert md.index("- 2026-01-05 first") < md.index("- 2026-02-01 second")
    assert "- Tags: v1.0 (2026-02-01)" in md
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest skills/harvest/scripts/tests/test_git_harvest.py`
Expected: collection ERROR with `ModuleNotFoundError: No module named 'git_harvest'`.

- [ ] **Step 3: Write the data classes, parsers, filter, and renderer**

Create `skills/harvest/scripts/git_harvest.py`:

```python
"""Summarize git activity for an AcqDemo rating period as Markdown.

Usage:
    python git_harvest.py --since 2025-10-01 --until 2026-09-30
        [--local PATH ...] [--github OWNER/REPO ...] [--author NAME ...] [--out FILE]

Local repositories are read with `git log`; GitHub repositories with the GitHub CLI (`gh`).
Merge commits are skipped. Output lists totals, and per repository: months, authors, tags,
and commit subjects (oldest first).
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

SEP = "\x1f"

@dataclass
class Commit:
    sha: str
    date: str
    author: str
    subject: str

@dataclass
class RepoSummary:
    name: str
    commits: list[Commit]
    tags: list[tuple[str, str]] = field(default_factory=list)
    error: str = ""

    @property
    def first(self) -> str:
        return self.commits[0].date if self.commits else ""

    @property
    def last(self) -> str:
        return self.commits[-1].date if self.commits else ""

    @property
    def authors(self) -> Counter:
        return Counter(c.author for c in self.commits)

    @property
    def by_month(self) -> dict[str, int]:
        return dict(sorted(Counter(c.date[:7] for c in self.commits).items()))

def parse_git_log(output: str) -> list[Commit]:
    commits: list[Commit] = []
    for line in output.splitlines():
        parts = line.split(SEP)
        if len(parts) != 4 or not parts[0].strip():
            continue
        sha, date, author, subject = (p.strip() for p in parts)
        commits.append(Commit(sha, date[:10], author, subject))
    return commits

def parse_github_items(items: list[dict]) -> list[Commit]:
    commits: list[Commit] = []
    for item in items:
        if len(item.get("parents") or []) > 1:
            continue
        info = item.get("commit") or {}
        author = info.get("author") or {}
        message = info.get("message") or ""
        subject = message.splitlines()[0] if message else ""
        commits.append(Commit(item.get("sha", ""), (author.get("date") or "")[:10],
                              author.get("name") or "", subject))
    return commits

def filter_commits(commits: list[Commit], since: str, until: str, authors: list[str]) -> list[Commit]:
    wanted = [a.lower() for a in authors]
    kept = [c for c in commits
            if since <= c.date <= until and (not wanted or any(a in c.author.lower() for a in wanted))]
    return sorted(kept, key=lambda c: (c.date, c.sha))

def render_markdown(summaries: list[RepoSummary], since: str, until: str) -> str:
    lines = [f"# Git harvest: {since} to {until}", "",
             "| Repository | Commits | First | Last | Active months | Tags |",
             "|---|---|---|---|---|---|"]
    for s in summaries:
        lines.append(f"| {s.name} | {len(s.commits)} | {s.first or '-'} | {s.last or '-'} "
                     f"| {len(s.by_month)} | {len(s.tags)} |")
    for s in summaries:
        lines += ["", f"## {s.name}"]
        if s.error:
            lines.append(f"- Error: {s.error}")
            continue
        if not s.commits:
            lines.append("- No commits in this period.")
            continue
        lines.append(f"- Commits: {len(s.commits)} ({s.first} to {s.last})")
        lines.append("- Authors: " + ", ".join(f"{a} ({n})" for a, n in s.authors.most_common()))
        lines.append("- By month: " + ", ".join(f"{m}: {n}" for m, n in s.by_month.items()))
        if s.tags:
            lines.append("- Tags: " + ", ".join(f"{n} ({d})" for n, d in s.tags))
        lines += ["", "### Commit subjects (oldest first)"]
        lines += [f"- {c.date} {c.subject}" for c in s.commits]
    return "\n".join(lines) + "\n"
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest skills/harvest/scripts/tests/test_git_harvest.py`
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add skills/harvest/scripts
git commit -m "feat(harvest): parse, filter, and render git activity"
```

---

### Task 13: Git harvest readers and command line

**Files:**
- Modify: `skills/harvest/scripts/git_harvest.py` (append)
- Modify: `skills/harvest/scripts/tests/test_git_harvest.py` (append)

- [ ] **Step 1: Append the failing tests**

Append to `skills/harvest/scripts/tests/test_git_harvest.py`:

```python
def make_repo(tmp_path):
    repo = tmp_path / "demo-repo"
    repo.mkdir()

    def git(*args, date=None):
        env = dict(os.environ)
        if date:
            env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = f"{date}T12:00:00"
        subprocess.run(["git", "-c", "user.name=Dana Smith", "-c", "user.email=dana@example.com",
                        "-C", str(repo), *args], check=True, capture_output=True, env=env)

    git("init", "-q", "-b", "main")
    for day, name in [("2025-09-15", "before"), ("2025-11-05", "inside-1"), ("2026-02-10", "inside-2")]:
        (repo / f"{name}.txt").write_text(name, encoding="utf-8")
        git("add", "-A")
        git("commit", "-q", "-m", f"add {name}", date=day)
    git("checkout", "-q", "-b", "feature")
    (repo / "feature.txt").write_text("f", encoding="utf-8")
    git("add", "-A")
    git("commit", "-q", "-m", "add feature", date="2026-03-01")
    git("checkout", "-q", "main")
    git("merge", "-q", "--no-ff", "feature", "-m", "Merge feature", date="2026-03-02")
    git("tag", "-a", "v1.0", "-m", "release", date="2026-03-03")
    return repo

def test_local_summary_reads_period_skips_merges_and_dates_tags(tmp_path):
    repo = make_repo(tmp_path)
    s = gh.local_summary(repo, "2025-10-01", "2026-09-30", [])
    assert [c.subject for c in s.commits] == ["add inside-1", "add inside-2", "add feature"]
    assert s.tags == [("v1.0", "2026-03-03")]
    assert s.error == ""

def test_local_summary_reports_error_for_non_repo(tmp_path):
    s = gh.local_summary(tmp_path, "2025-10-01", "2026-09-30", [])
    assert s.error

def test_github_summary_without_gh(monkeypatch):
    monkeypatch.setattr(gh.shutil, "which", lambda name: None)
    assert gh.github_summary("owner/repo", "2025-10-01", "2026-09-30", []).error == "GitHub CLI (gh) not found"

def test_github_summary_parses_gh_output(monkeypatch):
    item = {"sha": "a1", "parents": [{}], "commit": {"author": {"name": "Dana", "date": "2026-04-01T09:00:00Z"},
                                                      "message": "feat: new screen"}}
    monkeypatch.setattr(gh.shutil, "which", lambda name: "gh")

    def fake_run(cmd):
        return "v2.0\n" if "tags" in cmd[3] else json.dumps(item) + "\n"

    monkeypatch.setattr(gh, "run", fake_run)
    s = gh.github_summary("owner/repo", "2025-10-01", "2026-09-30", [])
    assert [c.subject for c in s.commits] == ["feat: new screen"]
    assert s.tags == [("v2.0", "undated")]

def test_main_writes_markdown_file(tmp_path, capsys):
    repo = make_repo(tmp_path)
    out = tmp_path / "harvest" / "git.md"
    code = gh.main(["--since", "2025-10-01", "--until", "2026-09-30", "--local", str(repo), "--out", str(out)])
    assert code == 0
    assert "3 commits across 1 repositories" in capsys.readouterr().out
    assert "## demo-repo" in out.read_text(encoding="utf-8")

def test_main_requires_a_source(capsys):
    assert gh.main(["--since", "2025-10-01", "--until", "2026-09-30"]) == 2
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest skills/harvest/scripts/tests/test_git_harvest.py`
Expected: 6 new tests FAIL with `AttributeError: module 'git_harvest' has no attribute 'local_summary'` (or `'github_summary'`, `'main'`); the first 5 still pass.

- [ ] **Step 3: Append the readers and `main`**

Append to `skills/harvest/scripts/git_harvest.py`:

```python
def run(cmd: list[str]) -> str:
    return subprocess.run(cmd, capture_output=True, check=True, text=True, encoding="utf-8").stdout

def local_summary(path: Path, since: str, until: str, authors: list[str]) -> RepoSummary:
    name = path.resolve().name
    try:
        log = run(["git", "-C", str(path), "log", "--all", "--no-merges", "--date=short",
                   f"--since={since} 00:00:00", f"--until={until} 23:59:59",
                   f"--pretty=format:%H{SEP}%ad{SEP}%an{SEP}%s"])
        tag_lines = run(["git", "-C", str(path), "for-each-ref", "refs/tags",
                         f"--format=%(refname:short){SEP}%(creatordate:short)"])
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        detail = getattr(exc, "stderr", "") or str(exc)
        return RepoSummary(name, [], error=detail.strip() or "git failed")
    tags = [tuple(t.split(SEP, 1)) for t in tag_lines.splitlines() if SEP in t]
    tags = sorted(((n, d) for n, d in tags if since <= d <= until), key=lambda t: t[1])
    return RepoSummary(name, filter_commits(parse_git_log(log), since, until, authors), tags)

def github_summary(repo: str, since: str, until: str, authors: list[str]) -> RepoSummary:
    gh = shutil.which("gh")
    if not gh:
        return RepoSummary(repo, [], error="GitHub CLI (gh) not found")
    try:
        out = run([gh, "api", "--paginate",
                   f"repos/{repo}/commits?since={since}T00:00:00Z&until={until}T23:59:59Z&per_page=100",
                   "--jq", ".[]"])
        tag_out = run([gh, "api", "--paginate", f"repos/{repo}/tags?per_page=100", "--jq", ".[].name"])
    except subprocess.CalledProcessError as exc:
        return RepoSummary(repo, [], error=(exc.stderr or "gh api failed").strip())
    items = [json.loads(line) for line in out.splitlines() if line.strip()]
    tags = [(t.strip(), "undated") for t in tag_out.splitlines() if t.strip()]
    return RepoSummary(repo, filter_commits(parse_github_items(items), since, until, authors), tags)

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--since", required=True, help="YYYY-MM-DD")
    ap.add_argument("--until", required=True, help="YYYY-MM-DD")
    ap.add_argument("--local", type=Path, nargs="*", default=[])
    ap.add_argument("--github", nargs="*", default=[])
    ap.add_argument("--author", nargs="*", default=[])
    ap.add_argument("--out", type=Path)
    args = ap.parse_args(argv)

    if not args.local and not args.github:
        print("git_harvest: give at least one --local PATH or --github OWNER/REPO")
        return 2
    summaries = [local_summary(p, args.since, args.until, args.author) for p in args.local]
    summaries += [github_summary(r, args.since, args.until, args.author) for r in args.github]
    markdown = render_markdown(summaries, args.since, args.until)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(markdown, encoding="utf-8")
        total = sum(len(s.commits) for s in summaries)
        print(f"git_harvest: {total} commits across {len(summaries)} repositories -> {args.out}")
    else:
        print(markdown)
    return 1 if all(s.error for s in summaries) else 0

if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest skills/harvest/scripts/tests/test_git_harvest.py`
Expected: 11 passed.

- [ ] **Step 5: Smoke-test against a real repository**

Run: `python skills/harvest/scripts/git_harvest.py --since 2025-10-01 --until 2026-09-30 --local .`
Expected: Markdown starting `# Git harvest: 2025-10-01 to 2026-09-30` with a row for this repository and its commit subjects. (GitHub form, if `gh` is authenticated: `--github <owner>/<repo>`.)

- [ ] **Step 6: Commit**

```bash
git add skills/harvest/scripts
git commit -m "feat(harvest): read local and GitHub repositories from the command line"
```

---

### Task 14: Calendar export parsing and recurring series

**Files:**
- Create: `skills/harvest/scripts/calendar_harvest.py`
- Create: `skills/harvest/scripts/tests/test_calendar_harvest.py`

- [ ] **Step 1: Write the failing tests**

Create `skills/harvest/scripts/tests/test_calendar_harvest.py`. The export below uses real tab characters between columns (`\t`):

```python
"""Tests for skills/harvest/scripts/calendar_harvest.py."""
import codecs
import sys
from datetime import date, datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import calendar_harvest as ch  # noqa: E402

SINCE, UNTIL = date(2025, 10, 1), date(2026, 9, 30)

EXPORT = (
    "Subject\tStart\t\n"
    "Estimating working group\tTue 10/14/2025 10:00 AM\t\n"
    "Canceled: Branch staff meeting\tMon 12/8/2025 11:00 AM\t\n"
    "Updated: Estimating Working Group\tTue 11/11/2025 10:00 AM\t\n"
    "Regression tool demo for program office\tThu 3/12/2026 1:30 PM\t\n"
    "Old kickoff\tTue 3/19/2024 2:00 PM\t\n"
    "Broken line with no date\t\t\n"
    "estimating working group\tTue 12/9/2025 10:00 AM\t\n"
)

@pytest.mark.parametrize(
    "value, expected",
    [
        ("Tue 3/19/2024 2:00 PM", datetime(2024, 3, 19, 14, 0)),
        ("3/19/2024 2:00 PM", datetime(2024, 3, 19, 14, 0)),
        ("Tue 3/19/2024 14:00", datetime(2024, 3, 19, 14, 0)),
        ("2024-03-19 14:00", datetime(2024, 3, 19, 14, 0)),
        ("3/19/2024", datetime(2024, 3, 19)),
        ("  Tue   3/19/2024   2:00 PM ", datetime(2024, 3, 19, 14, 0)),
        ("next Tuesday", None),
    ],
)
def test_parse_start_formats(value, expected):
    assert ch.parse_start(value) == expected

def test_harvest_filters_canceled_outside_and_unparsed():
    result = ch.harvest(EXPORT, SINCE, UNTIL)
    assert len(result.meetings) == 4
    assert result.canceled == 1
    assert result.outside == 1
    assert len(result.unparsed) == 1
    assert [m.start.date() for m in result.meetings] == sorted(m.start.date() for m in result.meetings)

def test_header_with_extra_columns_in_any_order():
    text = "Location\tStart\tSubject\nRoom 1\t10/20/2025 9:00 AM\tDesign review\n"
    result = ch.harvest(text, SINCE, UNTIL)
    assert [(m.subject, m.start) for m in result.meetings] == [("Design review", datetime(2025, 10, 20, 9, 0))]

def test_no_header_assumes_subject_then_start():
    text = "Design review\t10/20/2025 9:00 AM\n"
    assert ch.harvest(text, SINCE, UNTIL).meetings[0].subject == "Design review"

def test_recurring_groups_prefixes_and_case():
    series = ch.recurring(ch.harvest(EXPORT, SINCE, UNTIL).meetings)
    assert len(series) == 1
    name, count, first, last = series[0]
    assert count == 3
    assert name.lower() == "estimating working group"
    assert (first, last) == (date(2025, 10, 14), date(2025, 12, 9))

def test_read_text_handles_utf16_and_cp1252(tmp_path):
    utf16 = tmp_path / "u16.txt"
    utf16.write_bytes(codecs.BOM_UTF16_LE + "Subject\tStart\n".encode("utf-16-le"))
    assert ch.read_text(utf16).startswith("Subject")
    cp = tmp_path / "cp.txt"
    cp.write_bytes("Director’s sync\t10/20/2025 9:00 AM\n".encode("cp1252"))
    assert "Director’s sync" in ch.read_text(cp)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest skills/harvest/scripts/tests/test_calendar_harvest.py`
Expected: collection ERROR with `ModuleNotFoundError: No module named 'calendar_harvest'`.

- [ ] **Step 3: Write the reader, parser, filter, and series grouping**

Create `skills/harvest/scripts/calendar_harvest.py`:

```python
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
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest skills/harvest/scripts/tests/test_calendar_harvest.py`
Expected: 12 passed.

- [ ] **Step 5: Commit**

```bash
git add skills/harvest/scripts
git commit -m "feat(harvest): parse calendar exports and group recurring meetings"
```

---

### Task 15: Calendar Markdown and command line

**Files:**
- Modify: `skills/harvest/scripts/calendar_harvest.py` (append)
- Modify: `skills/harvest/scripts/tests/test_calendar_harvest.py` (append)

- [ ] **Step 1: Append the failing tests**

Append to `skills/harvest/scripts/tests/test_calendar_harvest.py`:

```python
def test_render_markdown_sections():
    result = ch.harvest(EXPORT, SINCE, UNTIL)
    md = ch.render_markdown(result, SINCE, UNTIL)
    assert md.startswith("# Calendar harvest: 2025-10-01 to 2026-09-30")
    assert "- Meetings in period: 4" in md
    assert "- Canceled (skipped): 1" in md
    assert "| Occurrences |" in md
    assert "### 2025-10 (1)" in md and "### 2026-03 (1)" in md
    assert "- 2026-03-12 13:30 Regression tool demo for program office" in md
    assert md.index("### 2025-10") < md.index("### 2026-03")

def test_render_markdown_without_series():
    result = ch.harvest("Subject\tStart\nOne-off\t10/20/2025 9:00 AM\n", SINCE, UNTIL)
    assert "## Recurring series (2 or more)\n- None." in ch.render_markdown(result, SINCE, UNTIL)

def test_main_writes_file_and_missing_file(tmp_path, capsys):
    source = tmp_path / "calendar.txt"
    source.write_text(EXPORT, encoding="utf-8")
    out = tmp_path / "harvest" / "calendar.md"
    assert ch.main(["--file", str(source), "--since", "2025-10-01", "--until", "2026-09-30", "--out", str(out)]) == 0
    assert "4 meetings in period, 1 recurring series" in capsys.readouterr().out
    assert out.exists()
    assert ch.main(["--file", str(tmp_path / "nope.txt"), "--since", "2025-10-01", "--until", "2026-09-30"]) == 2
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest skills/harvest/scripts/tests/test_calendar_harvest.py`
Expected: 3 new tests FAIL with `AttributeError: module 'calendar_harvest' has no attribute 'render_markdown'` (or `'main'`); the first 12 still pass.

- [ ] **Step 3: Append the renderer and `main`**

Append to `skills/harvest/scripts/calendar_harvest.py`:

```python
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
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest skills/harvest/scripts/tests/test_calendar_harvest.py`
Expected: 15 passed.

- [ ] **Step 5: Run the full suite and commit**

Run: `python -m pytest`
Expected: all pass.

```bash
git add skills/harvest/scripts
git commit -m "feat(harvest): render calendar harvest and add command line"
```

- [ ] **Step 7: Phase-end sync** (see plan index, "Phase-end sync")
