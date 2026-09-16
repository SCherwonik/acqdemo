"""Summarize git activity for an AcqDemo rating period as Markdown.

Usage:
    python git_harvest.py --since 2025-10-01 --until 2026-09-30
        [--local PATH ...] [--github OWNER/REPO ...] [--author NAME ...] [--out FILE]

Local repositories are read with `git log`; GitHub repositories with the GitHub CLI (`gh`).
Merge commits are skipped. A commit with the same author date and subject as one already
kept in the same repository is dropped (a fix cherry-picked or ported between branches
would otherwise be counted twice). Output lists totals, and per repository: months, authors,
tags, and commit subjects (oldest first).
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


def dedupe_commits(commits: list[Commit]) -> list[Commit]:
    """Drop commits that share an author date and subject within a repository, keeping the
    first. `git log --all` walks every branch, so a fix cherry-picked or ported between
    branches (different sha, same author date and message) would otherwise count twice."""
    seen: set[tuple[str, str]] = set()
    deduped: list[Commit] = []
    for c in commits:
        key = (c.date, c.subject)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(c)
    return deduped


def filter_commits(commits: list[Commit], since: str, until: str, authors: list[str]) -> list[Commit]:
    wanted = [a.strip().lower() for a in authors if a.strip()]
    kept = [c for c in commits
            if since <= c.date <= until and (not wanted or any(a in c.author.lower() for a in wanted))]
    kept = sorted(kept, key=lambda c: (c.date, c.sha))
    return dedupe_commits(kept)


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


def run(cmd: list[str]) -> str:
    return subprocess.run(cmd, capture_output=True, check=True, text=True, encoding="utf-8").stdout


def local_summary(path: Path, since: str, until: str, authors: list[str]) -> RepoSummary:
    name = path.resolve().name
    try:
        log = run(["git", "-C", str(path), "log", "--all", "--no-merges", "--date=short",
                   # No --until: git filters on committer date, so a commit written in the period but
                   # rebased later would vanish. filter_commits applies the window to the author date.
                   f"--since={since} 00:00:00",
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
                   f"repos/{repo}/commits?since={since}T00:00:00Z&per_page=100",
                   "--jq", ".[]"])
        tag_out = run([gh, "api", "--paginate", f"repos/{repo}/tags?per_page=100", "--jq", ".[].name"])
    except subprocess.CalledProcessError as exc:
        return RepoSummary(repo, [], error=(exc.stderr or "gh api failed").strip())
    items = [json.loads(line) for line in out.splitlines() if line.strip()]
    tags = [(t.strip(), "undated") for t in tag_out.splitlines() if t.strip()]
    return RepoSummary(repo, filter_commits(parse_github_items(items), since, until, authors), tags)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252
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
