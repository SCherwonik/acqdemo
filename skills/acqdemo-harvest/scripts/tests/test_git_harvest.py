"""Tests for skills/acqdemo-harvest/scripts/git_harvest.py."""
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


def test_main_prints_text_a_windows_console_cannot_encode(tmp_path):
    repo = make_repo(tmp_path)
    (repo / "arrow.txt").write_text("a", encoding="utf-8")
    ident = ["-c", "user.name=Dana Smith", "-c", "user.email=dana@example.com", "-C", str(repo)]
    env = {**os.environ, "GIT_AUTHOR_DATE": "2026-04-01T12:00:00", "GIT_COMMITTER_DATE": "2026-04-01T12:00:00"}
    subprocess.run(["git", *ident, "add", "-A"], check=True, capture_output=True)
    subprocess.run(["git", *ident, "commit", "-q", "-m", "map inputs → outputs"], check=True, capture_output=True, env=env)
    env = {**os.environ, "PYTHONIOENCODING": "cp1252"}
    run = subprocess.run([sys.executable, gh.__file__, "--since", "2025-10-01", "--until", "2026-09-30",
                          "--local", str(repo)], capture_output=True, env=env)
    assert run.returncode == 0, run.stderr.decode("utf-8", "replace")
    assert "map inputs → outputs" in run.stdout.decode("utf-8")


def test_local_summary_keeps_in_period_commit_rewritten_after_period(tmp_path):
    repo = make_repo(tmp_path)
    (repo / "late.txt").write_text("x", encoding="utf-8")
    ident = ["-c", "user.name=Dana Smith", "-c", "user.email=dana@example.com", "-C", str(repo)]
    env = {**os.environ, "GIT_AUTHOR_DATE": "2026-09-20T12:00:00", "GIT_COMMITTER_DATE": "2026-11-01T12:00:00"}
    subprocess.run(["git", *ident, "add", "-A"], check=True, capture_output=True)
    subprocess.run(["git", *ident, "commit", "-q", "-m", "rebased late"], check=True, capture_output=True, env=env)
    s = gh.local_summary(repo, "2025-10-01", "2026-09-30", [])
    assert "rebased late" in [c.subject for c in s.commits]


def test_filter_commits_ignores_blank_author_values():
    commits = [gh.Commit("a", "2026-01-05", "Dana Smith", "one"), gh.Commit("b", "2026-01-06", "Lee Park", "two")]
    assert [c.subject for c in gh.filter_commits(commits, "2025-10-01", "2026-09-30", ["", "  ", "dana"])] == ["one"]


def test_filter_commits_dedupes_same_author_date_and_subject():
    # git log --all walks every branch, so a commit cherry-picked or ported between
    # branches (same author date, same subject, different sha) must count once.
    commits = [
        gh.Commit("aaa111", "2026-01-05", "Dana Smith", "fix: same underlying bug"),
        gh.Commit("bbb222", "2026-01-05", "Dana Smith", "fix: same underlying bug"),
        gh.Commit("ccc333", "2026-01-06", "Dana Smith", "feat: unrelated"),
    ]
    kept = gh.filter_commits(commits, "2025-10-01", "2026-09-30", [])
    assert [c.sha for c in kept] == ["aaa111", "ccc333"]


def test_local_summary_dedupes_commit_ported_to_two_branches(tmp_path):
    repo = make_repo(tmp_path)
    ident = ["-c", "user.name=Dana Smith", "-c", "user.email=dana@example.com", "-C", str(repo)]
    env = {**os.environ, "GIT_AUTHOR_DATE": "2026-04-05T12:00:00", "GIT_COMMITTER_DATE": "2026-04-05T12:00:00"}
    for branch, fname in [("branch-a", "fix-a.txt"), ("branch-b", "fix-b.txt")]:
        subprocess.run(["git", *ident, "checkout", "-q", "main"], check=True, capture_output=True)
        subprocess.run(["git", *ident, "checkout", "-q", "-b", branch], check=True, capture_output=True)
        (repo / fname).write_text(fname, encoding="utf-8")
        subprocess.run(["git", *ident, "add", "-A"], check=True, capture_output=True)
        subprocess.run(["git", *ident, "commit", "-q", "-m", "fix: same underlying bug"],
                        check=True, capture_output=True, env=env)
    s = gh.local_summary(repo, "2025-10-01", "2026-09-30", [])
    matching = [c for c in s.commits if c.subject == "fix: same underlying bug"]
    assert len(matching) == 1
