"""The probe harness must never let a headless session reach a real workspace."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import run_probe  # noqa: E402


def make_repo(tmp_path):
    """A stand-in for the plugin repository: plugin folders plus a live workspace."""
    repo = tmp_path / "repo"
    (repo / ".claude-plugin").mkdir(parents=True)
    (repo / ".claude-plugin" / "plugin.json").write_text('{"name": "acqdemo"}', encoding="utf-8")
    (repo / "skills" / "start" / "templates").mkdir(parents=True)
    (repo / "skills" / "start" / "SKILL.md").write_text("# start", encoding="utf-8")
    (repo / "skills" / "start" / "templates" / "profile.md").write_text("# template", encoding="utf-8")
    (repo / "skills" / "start" / "__pycache__").mkdir()
    (repo / "skills" / "start" / "__pycache__" / "x.pyc").write_bytes(b"\x00")
    # The workspace that probes have written into twice.
    (repo / "profile.md").write_text("name: someone", encoding="utf-8")
    (repo / "FY26" / "rambles").mkdir(parents=True)
    (repo / "FY26" / "rambles" / "2026-09-15-dump.md").write_text("I worked on", encoding="utf-8")
    (repo / "FY26" / "ledger.md").write_text("# Ledger FY26", encoding="utf-8")
    return repo


def git(repo, *args, **kwargs):
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True, **kwargs)


def make_git_repo(tmp_path):
    """A repository with one commit behind it and the workspace files still untracked."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
    git(repo, "config", "user.name", "Probe Test")
    git(repo, "config", "user.email", "probe@example.invalid")
    git(repo, "config", "commit.gpgsign", "false")
    (repo / "README.md").write_text("# toolkit", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "first")
    (repo / "FY26").mkdir()
    (repo / "FY26" / "ledger.md").write_text("# Ledger FY26", encoding="utf-8")
    return repo


def write_stub(tmp_path, body):
    """A stand-in for the claude executable. Never probe with the real one from a test."""
    stub = tmp_path / "stub.py"
    stub.write_text(body, encoding="utf-8")
    return [sys.executable, str(stub)]


def assistant_skill_line(skill):
    return json.dumps({"type": "assistant", "message": {"content": [
        {"type": "tool_use", "name": "Skill", "input": {"skill": skill}}]}})


# ---------- sandbox ----------

def test_sandbox_takes_the_plugin_and_leaves_the_workspace(tmp_path):
    repo = make_repo(tmp_path)
    sandbox = run_probe.build_sandbox(repo, tmp_path / "sandbox")
    assert (sandbox / ".claude-plugin" / "plugin.json").exists()
    assert (sandbox / "skills" / "start" / "SKILL.md").exists()
    assert not (sandbox / "profile.md").exists()
    assert not (sandbox / "FY26").exists()


def test_sandbox_keeps_template_files_named_like_workspace_files(tmp_path):
    repo = make_repo(tmp_path)
    sandbox = run_probe.build_sandbox(repo, tmp_path / "sandbox")
    assert (sandbox / "skills" / "start" / "templates" / "profile.md").exists()


def test_sandbox_drops_caches(tmp_path):
    repo = make_repo(tmp_path)
    sandbox = run_probe.build_sandbox(repo, tmp_path / "sandbox")
    assert not (sandbox / "skills" / "start" / "__pycache__").exists()


def test_refuses_a_plugin_folder_that_is_also_a_workspace(tmp_path):
    """The original leak: --plugin-dir pointed at a folder holding profile.md."""
    folder = tmp_path / "plugin-and-workspace"
    folder.mkdir()
    (folder / "profile.md").write_text("name: someone", encoding="utf-8")
    with pytest.raises(SystemExit) as caught:
        run_probe.assert_no_workspace(folder)
    assert "refusing to run" in str(caught.value)
    assert "profile.md" in str(caught.value)


def test_a_clean_sandbox_passes_the_workspace_check(tmp_path):
    repo = make_repo(tmp_path)
    run_probe.assert_no_workspace(run_probe.build_sandbox(repo, tmp_path / "sandbox"))


def test_root_markers_ignore_nested_copies(tmp_path):
    folder = tmp_path / "plugin"
    (folder / "skills" / "start" / "templates").mkdir(parents=True)
    (folder / "skills" / "start" / "templates" / "profile.md").write_text("t", encoding="utf-8")
    assert run_probe.root_workspace_markers(folder) == []
    (folder / "roster.md").write_text("r", encoding="utf-8")
    assert run_probe.root_workspace_markers(folder) == ["roster.md"]


def test_sandbox_needs_a_plugin_repository(tmp_path):
    (tmp_path / "empty").mkdir()
    with pytest.raises(SystemExit) as caught:
        run_probe.build_sandbox(tmp_path / "empty", tmp_path / "sandbox")
    assert "is missing" in str(caught.value)


# ---------- tripwire: the worktree ----------

def test_tripwire_sees_a_new_file(tmp_path):
    repo = make_repo(tmp_path)
    before = run_probe.snapshot(repo)
    (repo / "FY26" / "rambles" / "2026-09-16-briefed-new-tool.md").write_text("fake", encoding="utf-8")
    changes = run_probe.diff_snapshots(before, run_probe.snapshot(repo))
    assert changes["added"] == ["FY26/rambles/2026-09-16-briefed-new-tool.md"]
    assert changes["changed"] == [] and changes["removed"] == []


def test_tripwire_sees_an_overwritten_ledger(tmp_path):
    repo = make_repo(tmp_path)
    before = run_probe.snapshot(repo)
    (repo / "FY26" / "ledger.md").write_text("", encoding="utf-8")
    changes = run_probe.diff_snapshots(before, run_probe.snapshot(repo))
    assert changes["changed"] == ["FY26/ledger.md"]


def test_tripwire_sees_a_deletion(tmp_path):
    repo = make_repo(tmp_path)
    before = run_probe.snapshot(repo)
    (repo / "FY26" / "rambles" / "2026-09-15-dump.md").unlink()
    changes = run_probe.diff_snapshots(before, run_probe.snapshot(repo))
    assert changes["removed"] == ["FY26/rambles/2026-09-15-dump.md"]


def test_tripwire_is_quiet_when_nothing_happens(tmp_path):
    repo = make_repo(tmp_path)
    before = run_probe.snapshot(repo)
    changes = run_probe.diff_snapshots(before, run_probe.snapshot(repo))
    assert not any(changes.values())


def test_tripwire_sees_an_edit_to_a_large_file_that_keeps_its_size_and_mtime(tmp_path):
    """The size-and-mtime shortcut for large files was a hole: os.utime closed it."""
    repo = make_repo(tmp_path)
    big = repo / "FY26" / "evidence.txt"
    big.write_bytes(b"a" * (4 << 20))
    stat = big.stat()
    before = run_probe.snapshot(repo)
    with big.open("r+b") as handle:
        handle.write(b"LEAK")
    os.utime(big, ns=(stat.st_atime_ns, stat.st_mtime_ns))
    assert big.stat().st_size == stat.st_size
    changes = run_probe.diff_snapshots(before, run_probe.snapshot(repo))
    assert changes["changed"] == ["FY26/evidence.txt"]


def test_tripwire_sees_a_permission_change_on_a_tracked_file(tmp_path):
    repo = make_repo(tmp_path)
    target = repo / "FY26" / "ledger.md"
    before = run_probe.snapshot(repo)
    original = target.stat().st_mode
    os.chmod(target, 0o444)
    try:
        changes = run_probe.diff_snapshots(before, run_probe.snapshot(repo))
    finally:
        os.chmod(target, original)
    assert changes["changed"] == ["FY26/ledger.md"]


def test_tripwire_sees_a_folder_created_and_left_empty(tmp_path):
    """os.walk reports files only, so an empty folder was invisible."""
    repo = make_repo(tmp_path)
    before = run_probe.snapshot(repo)
    (repo / "FY26" / "evidence").mkdir()
    changes = run_probe.diff_snapshots(before, run_probe.snapshot(repo))
    assert changes["added"] == ["FY26/evidence/"]


def test_tripwire_sees_a_new_worktree_without_hashing_its_contents(tmp_path):
    repo = make_repo(tmp_path)
    (repo / ".worktrees").mkdir()
    before = run_probe.snapshot(repo)
    checkout = repo / ".worktrees" / "probe-branch"
    (checkout / "skills").mkdir(parents=True)
    (checkout / "skills" / "SKILL.md").write_text("copy", encoding="utf-8")
    changes = run_probe.diff_snapshots(before, run_probe.snapshot(repo))
    assert changes["added"] == [".worktrees/probe-branch"]


def test_tripwire_ignores_caches(tmp_path):
    repo = make_repo(tmp_path)
    before = run_probe.snapshot(repo)
    (repo / "skills" / "start" / "__pycache__" / "y.pyc").write_bytes(b"\x01")
    (repo / ".pytest_cache").mkdir()
    (repo / ".pytest_cache" / "lastfailed").write_text("{}", encoding="utf-8")
    changes = run_probe.diff_snapshots(before, run_probe.snapshot(repo))
    assert not any(changes.values())


# ---------- tripwire: git ----------

def test_tripwire_ignores_git_churn_that_says_nothing_about_a_leak(tmp_path):
    repo = make_repo(tmp_path)
    (repo / ".git" / "objects" / "ab").mkdir(parents=True)
    (repo / ".git" / "logs").mkdir(parents=True)
    before = run_probe.snapshot(repo)
    (repo / ".git" / "objects" / "ab" / "cdef").write_bytes(b"\x02")
    (repo / ".git" / "logs" / "HEAD").write_text("reflog", encoding="utf-8")
    (repo / ".git" / "FETCH_HEAD").write_text("fetched", encoding="utf-8")
    (repo / ".git" / "COMMIT_EDITMSG").write_text("message", encoding="utf-8")
    changes = run_probe.diff_snapshots(before, run_probe.snapshot(repo))
    assert not any(changes.values())


def test_tripwire_sees_the_index_the_head_file_and_the_refs(tmp_path):
    repo = make_repo(tmp_path)
    (repo / ".git" / "refs" / "heads").mkdir(parents=True)
    (repo / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (repo / ".git" / "index").write_bytes(b"DIRC")
    before = run_probe.snapshot(repo)
    (repo / ".git" / "index").write_bytes(b"DIRC-changed")
    (repo / ".git" / "refs" / "heads" / "main").write_text("0" * 40, encoding="utf-8")
    changes = run_probe.diff_snapshots(before, run_probe.snapshot(repo))
    assert changes["changed"] == [".git/index"]
    assert changes["added"] == [".git/refs/heads/main"]


def test_tripwire_sees_a_commit_that_leaves_the_worktree_byte_identical(tmp_path):
    """The realistic leak: a probe that runs `git add -A && git commit` changes no file."""
    repo = make_git_repo(tmp_path)
    before = run_probe.snapshot(repo)
    worktree_before = {k: v for k, v in before.items()
                       if not k.startswith(".git") and not k.startswith("git:")}
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "the probe committed the workspace")
    after = run_probe.snapshot(repo)
    worktree_after = {k: v for k, v in after.items()
                      if not k.startswith(".git") and not k.startswith("git:")}
    assert worktree_after == worktree_before, "the commit must not have touched the worktree"
    changes = run_probe.diff_snapshots(before, after)
    assert ".git/index" in changes["changed"]
    assert "git:HEAD" in changes["changed"]
    assert any(k.startswith(".git/refs/heads/")
               for k in changes["changed"] + changes["added"])


def test_tripwire_reports_without_deleting(tmp_path, capsys):
    repo = make_repo(tmp_path)
    stray = repo / "FY26" / "harvest.md"
    stray.parent.mkdir(exist_ok=True)
    stray.write_text("snapshot", encoding="utf-8")
    code = run_probe.report_tripwire({"added": ["FY26/harvest.md"], "changed": [], "removed": []}, repo)
    assert code == 2
    assert stray.exists(), "the tripwire reports; the user decides what to remove"
    assert "TRIPWIRE" in capsys.readouterr().out


# ---------- isolation ----------

def test_isolation_rejects_a_sandbox_inside_the_repo(tmp_path):
    repo = make_repo(tmp_path)
    with pytest.raises(SystemExit) as caught:
        run_probe.check_isolation(repo, repo, tmp_path / "scratch")
    assert "--plugin-dir" in str(caught.value)


def test_isolation_rejects_a_working_directory_inside_the_repo(tmp_path):
    repo = make_repo(tmp_path)
    with pytest.raises(SystemExit) as caught:
        run_probe.check_isolation(repo, tmp_path / "sandbox", repo / "FY26")
    assert "working directory" in str(caught.value)


def test_isolation_allows_temp_folders(tmp_path):
    repo = make_repo(tmp_path)
    run_probe.check_isolation(repo, tmp_path / "sandbox", tmp_path / "scratch")


def test_the_cli_can_point_the_sandbox_at_the_repo_and_is_refused_first(tmp_path):
    """The guard must fire before a plugin copy is written, or it blames the probe for it."""
    repo = make_repo(tmp_path)
    inside = repo / "under-test"
    with pytest.raises(SystemExit) as caught:
        run_probe.main(["hello", "--repo", str(repo), "--sandbox", str(inside),
                        "--cwd", str(tmp_path / "scratch")])
    assert "--plugin-dir" in str(caught.value)
    assert not inside.exists(), "the sandbox was built before the guard ran"


def test_the_cli_refuses_a_working_directory_inside_the_repo(tmp_path):
    repo = make_repo(tmp_path)
    with pytest.raises(SystemExit) as caught:
        run_probe.main(["hello", "--repo", str(repo), "--sandbox", str(tmp_path / "sandbox"),
                        "--cwd", str(repo / "scratch")])
    assert "working directory" in str(caught.value)


# ---------- a repository that is not there ----------

def test_check_only_fails_loudly_for_a_repository_that_does_not_exist(tmp_path, capsys):
    """A typo in --repo used to read as an all-clear: empty compares equal to empty."""
    with pytest.raises(SystemExit) as caught:
        run_probe.main(["--check-only", "--repo", str(tmp_path / "typo")])
    assert "does not exist" in str(caught.value)
    assert "tripwire clean" not in capsys.readouterr().out


def test_check_only_fails_loudly_for_an_empty_directory(tmp_path, capsys):
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(SystemExit) as caught:
        run_probe.main(["--check-only", "--repo", str(empty)])
    assert "no files to watch" in str(caught.value)
    assert "tripwire clean" not in capsys.readouterr().out


def test_check_only_reports_clean_on_a_real_repository(tmp_path, capsys):
    repo = make_repo(tmp_path)
    assert run_probe.main(["--check-only", "--repo", str(repo)]) == 0
    assert "tripwire clean" in capsys.readouterr().out


# ---------- the command line ----------

def test_command_disables_the_installed_release(tmp_path):
    command = run_probe.claude_command(tmp_path / "sandbox")
    settings = json.loads(command[command.index("--settings") + 1])
    assert settings["enabledPlugins"]["acqdemo@acqdemo"] is False


def test_command_runs_headless_without_saving_a_session(tmp_path):
    command = run_probe.claude_command(tmp_path / "sandbox")
    assert "-p" in command and "--no-session-persistence" in command
    assert command[command.index("--plugin-dir") + 1] == str(tmp_path / "sandbox")
    assert command[command.index("--allowedTools") + 1] == "Skill"


# ---------- run_prompt, driven by a stub process ----------

def test_run_prompt_reports_the_first_skill_and_stops_there(tmp_path):
    stub = write_stub(tmp_path, f"""
import sys, time
print("not json at all", flush=True)
print({assistant_skill_line("acqdemo:start")!r}, flush=True)
print({assistant_skill_line("acqdemo:review")!r}, flush=True)
time.sleep(60)
""")
    skill, seconds = run_prompt_here(tmp_path, stub, timeout=30)
    assert skill == "acqdemo:start"
    assert seconds < 20, "it kept reading after the first Skill call"


def test_run_prompt_stops_on_the_result_event(tmp_path):
    stub = write_stub(tmp_path, """
import json, sys, time
print(json.dumps({"type": "result", "subtype": "success"}), flush=True)
time.sleep(60)
""")
    skill, seconds = run_prompt_here(tmp_path, stub, timeout=30)
    assert skill == "none"
    assert seconds < 20


def test_the_timeout_fires_on_a_process_that_never_prints_anything(tmp_path):
    """`for line in proc.stdout` blocks, so a deadline inside that loop never fires."""
    stub = write_stub(tmp_path, """
import time
time.sleep(120)
""")
    skill, seconds = run_prompt_here(tmp_path, stub, timeout=1)
    assert skill == "none"
    assert seconds < 20, "the timeout did not fire on a silent process"


def test_the_timeout_kills_a_grandchild_too(tmp_path):
    """proc.kill() reaches the direct child only; with Bash allowed, a grandchild outlives it."""
    marker = tmp_path / "wrote-after-the-kill.txt"
    child = tmp_path / "grandchild.py"
    child.write_text(
        "import time\n"
        "time.sleep(3)\n"
        f"open({str(marker)!r}, 'w').write('leak')\n",
        encoding="utf-8")
    stub = write_stub(tmp_path, f"""
import subprocess, sys, time
subprocess.Popen([sys.executable, {str(child)!r}])
time.sleep(120)
""")
    skill, seconds = run_prompt_here(tmp_path, stub, timeout=1.5)
    assert skill == "none" and seconds < 20
    time.sleep(4)
    assert not marker.exists(), "a grandchild outlived the kill and kept writing"


def run_prompt_here(tmp_path, command, timeout):
    scratch = tmp_path / "scratch"
    scratch.mkdir(exist_ok=True)
    return run_probe.run_prompt("a prompt", tmp_path / "sandbox", scratch,
                                timeout=timeout, command=command)
