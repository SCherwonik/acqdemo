"""The probe harness must never let a headless session reach a real workspace."""
import json
import sys
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


def test_tripwire_ignores_git_and_caches(tmp_path):
    repo = make_repo(tmp_path)
    before = run_probe.snapshot(repo)
    (repo / ".git").mkdir()
    (repo / ".git" / "index").write_bytes(b"whatever")
    (repo / "skills" / "start" / "__pycache__").mkdir(exist_ok=True)
    (repo / "skills" / "start" / "__pycache__" / "y.pyc").write_bytes(b"\x01")
    changes = run_probe.diff_snapshots(before, run_probe.snapshot(repo))
    assert not any(changes.values())


def test_tripwire_reports_without_deleting(tmp_path, capsys):
    repo = make_repo(tmp_path)
    stray = repo / "FY26" / "harvest.md"
    stray.parent.mkdir(exist_ok=True)
    stray.write_text("snapshot", encoding="utf-8")
    code = run_probe.report_tripwire({"added": ["FY26/harvest.md"], "changed": [], "removed": []}, repo)
    assert code == 2
    assert stray.exists(), "the tripwire reports; the user decides what to remove"
    assert "TRIPWIRE" in capsys.readouterr().out


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


def test_command_disables_the_installed_release(tmp_path):
    command = run_probe.claude_command(tmp_path / "sandbox")
    settings = json.loads(command[command.index("--settings") + 1])
    assert settings["enabledPlugins"]["acqdemo@acqdemo"] is False


def test_command_runs_headless_without_saving_a_session(tmp_path):
    command = run_probe.claude_command(tmp_path / "sandbox")
    assert "-p" in command and "--no-session-persistence" in command
    assert command[command.index("--plugin-dir") + 1] == str(tmp_path / "sandbox")
    assert command[command.index("--allowedTools") + 1] == "Skill"
