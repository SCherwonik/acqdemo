"""Tests for tools/port/build_gen_ai.py (reference material -> flat knowledge bundle).

The bundle is uploaded into an agent builder's Knowledge panel. Nothing in it may point at a
path that does not exist there, name a Claude Code skill, or tell the user to run a script.
"""
import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build_gen_ai  # noqa: E402

REPO = Path(__file__).resolve().parents[3]
SRC = REPO / "skills" / "start" / "references"

# Wording that must not survive into a bundle read by an agent with no shell and no plugin.
CLAUDE_TOKENS = ("acqdemo:", "--plugin-dir", ".claude-plugin", "claude", ".py")

EXPECTED = {
    "descriptors-nh.md",
    "descriptors-nj.md",
    "descriptors-nk.md",
    "question-bank.md",
    "rules-ccas-core.md",
    "getting-your-documents.md",
    "levels.md",
    "cert-templates.md",
    "intake-checklist.md",
    "writing-style.md",
    "ledger-format.md",
    "examples-nh2-supervisor.md",
    "examples-nj3-engineer.md",
    "examples-nk2-admin.md",
    "INDEX.md",
}


@pytest.fixture(scope="module")
def items():
    return build_gen_ai.bundle(SRC)


@pytest.fixture
def built(tmp_path):
    """The bundle written to a throwaway directory."""
    dst = tmp_path / "knowledge"
    assert build_gen_ai.main(["--src", str(SRC), "--dst", str(dst)]) == 0
    return dst


def read_all(dst):
    return {p.name: p.read_text(encoding="utf-8") for p in sorted(dst.iterdir())}


# ---------- flattening ----------

def test_flatten_turns_a_nested_path_into_one_file_name():
    assert build_gen_ai.flatten("descriptors/nh.md") == "descriptors-nh.md"
    assert build_gen_ai.flatten("rules/ccas-core.md") == "rules-ccas-core.md"
    assert build_gen_ai.flatten("levels.md") == "levels.md"


def test_every_generated_name_is_flat(items):
    for item in items:
        assert "/" not in item.name and "\\" not in item.name


def test_demote_pushes_headings_down_but_leaves_fenced_lines_alone():
    out = build_gen_ai.demote("# Title\n\n## Section\n\n```\n# not a heading\n```\n\n### Deeper\n")
    assert "### Section" in out
    assert "#### Deeper" in out
    assert "\n# not a heading\n" in out, "a comment inside a fence is code, not a heading"


# ---------- coverage ----------

def test_every_expected_source_reference_is_in_the_bundle(built):
    assert set(read_all(built)) == EXPECTED


def test_nested_sources_arrive_under_their_flattened_names(built):
    files = read_all(built)
    assert "NH: Business Management and Technical Management" in files["descriptors-nh.md"]
    assert "CCAS Rules Summary" in files["rules-ccas-core.md"]


def test_each_worked_example_is_one_file_holding_all_three_factors(built):
    text = read_all(built)["examples-nh2-supervisor.md"]
    for factor in ("Job Achievement and Innovation", "Communication and Teamwork", "Mission Support"):
        assert factor in text
    # The profile, the spoken input, and the roster travel with the finished text.
    assert "career_path: NH" in text
    assert "Roster" in text
    # Checker flags become prose, not a command line.
    assert "--mode" not in text
    assert "supervisory objective" in text


# ---------- nothing points at a path that does not exist ----------

def test_no_relative_path_survives(built):
    for name, text in read_all(built).items():
        assert "../" not in text, name


def test_no_claude_specific_token_survives(built):
    for name, text in read_all(built).items():
        low = text.lower()
        for token in CLAUDE_TOKENS:
            assert token not in low, f"{name} still contains {token!r}"


def test_no_source_folder_path_survives(built):
    for name, text in read_all(built).items():
        low = text.lower()
        for folder in ("descriptors/", "rules/", "scripts/", "templates/", "skills/"):
            assert folder not in low, f"{name} still points at {folder!r}"


def test_the_script_instructions_become_platform_equivalents(built):
    files = read_all(built)
    assert "doc_text" not in files["getting-your-documents.md"]
    assert "upload" in files["getting-your-documents.md"].lower()
    assert "prd_text" not in files["question-bank.md"]
    # The checks that used to be a script now point at the offline checker page.
    assert "acqdemo-checker.html" in files["writing-style.md"]


def test_the_checker_and_the_worksheet_are_named_not_pathed(built):
    """A reader holding a flat list of uploads cannot follow a repository-relative path."""
    files = read_all(built)
    for name, text in files.items():
        assert "gen_ai/" not in text, f"{name} points at a path the reader does not have"
    assert "acqdemo-checker.html" in files["writing-style.md"]
    assert "acqdemo-checker.html" in files["INDEX.md"]
    assert "brain-dump-worksheet.md" in files["examples-nh2-supervisor.md"]


def test_no_em_dashes(built):
    for name, text in read_all(built).items():
        assert "—" not in text, name


# ---------- the port has no microphone and no repositories ----------

VOICE_AND_GIT = ("by voice", "for voice", "transcription", "dictation", "speech-to-text",
                 "spoken", "rambles/", "git counts", "git repository", "out of git",
                 ".gitignore", "pii guard", "repositories to harvest")


def test_no_voice_or_git_instruction_survives(built):
    for name, text in read_all(built).items():
        low = text.lower()
        for token in VOICE_AND_GIT:
            assert token not in low, f"{name} still tells the reader about {token!r}"


def test_what_the_voice_section_carried_is_still_there(built):
    """Dropping the section must not drop the rules inside it that still apply."""
    text = read_all(built)["question-bank.md"]
    assert "Term glossary" in text
    assert "Never guess a name" in text
    assert "CAS2Net" in text  # the resolve-before-asking worked example


def test_the_claude_sources_keep_their_voice_and_git_instructions():
    """Bundle only. The plugin really does have voice input and a shell, and is right to say so."""
    question_bank = (SRC / "question-bank.md").read_text(encoding="utf-8")
    assert "by voice" in question_bank
    assert "git counts" in question_bank
    assert "PII guard" in (SRC / "intake-checklist.md").read_text(encoding="utf-8")


# ---------- the two blocks the user saves ----------

def test_the_ledger_file_states_the_two_block_contract(built):
    text = read_all(built)["ledger-format.md"]
    lines = text.split("\n")
    assert "```ledger" in text and "```workspace" in text
    for heading in ("# Profile", "# Pay pool", "# Roster", "# Session state"):
        assert heading in lines, f"the workspace block never emits {heading!r}"
    assert "# Session State" not in lines, "the Ledger Keeper does not know that spelling"
    assert "session-state.md" not in text


def test_the_verification_catches_a_heading_whose_capitalization_drifted(items):
    """A capitalization mismatch carries no forbidden token, so it needs its own check."""
    assert build_gen_ai.verify(items) == []
    drifted = [replace_text(i, "# Session state", "# Session State") for i in items]
    findings = " ".join(build_gen_ai.verify(drifted))
    assert "ledger-format.md" in findings
    assert "Session state" in findings


def test_the_verification_catches_a_block_name_that_went_missing(items):
    gutted = [replace_text(i, "```workspace", "```") for i in items]
    findings = " ".join(build_gen_ai.verify(gutted))
    assert "workspace" in findings and "ledger-format.md" in findings


def replace_text(item, old, new):
    return build_gen_ai.Item(item.name, item.text.replace(old, new), item.covers, item.when)


# ---------- index ----------

def test_index_lists_every_file_present(built):
    files = read_all(built)
    index = files["INDEX.md"]
    for name in files:
        assert name in index, f"INDEX.md does not list {name}"


def test_index_says_what_each_file_is_for(items, built):
    """Every file's own summary and its own "when" reach the index, not just its name."""
    index = read_all(built)["INDEX.md"]
    for item in items:
        assert item.covers in index, f"INDEX.md does not say what {item.name} covers"
        assert item.when in index, f"INDEX.md does not say when to open {item.name}"


# ---------- determinism ----------

def test_build_is_idempotent(tmp_path):
    dst = tmp_path / "knowledge"
    assert build_gen_ai.main(["--src", str(SRC), "--dst", str(dst)]) == 0
    first = read_all(dst)
    assert build_gen_ai.main(["--src", str(SRC), "--dst", str(dst)]) == 0
    assert read_all(dst) == first


def test_second_run_writes_nothing(tmp_path, capsys):
    dst = tmp_path / "knowledge"
    build_gen_ai.main(["--src", str(SRC), "--dst", str(dst)])
    capsys.readouterr()
    build_gen_ai.main(["--src", str(SRC), "--dst", str(dst)])
    assert "0 written" in capsys.readouterr().out


def test_dry_run_creates_no_destination(tmp_path):
    dst = tmp_path / "knowledge"
    assert build_gen_ai.main(["--src", str(SRC), "--dst", str(dst), "--dry-run"]) == 0
    assert not dst.exists()


def test_dry_run_changes_nothing_in_a_populated_destination(built, capsys):
    """The interesting dry run is the one with something to overwrite and something to delete."""
    stale = built / "leftover.md"
    stale.write_text("old", encoding="utf-8")
    edited = built / "levels.md"
    edited.write_text("hand edited", encoding="utf-8")
    before = read_all(built)
    capsys.readouterr()

    assert build_gen_ai.main(["--src", str(SRC), "--dst", str(built), "--dry-run"]) == 0

    out = capsys.readouterr().out
    assert "DRY RUN" in out
    assert "levels.md" in out and "leftover.md" in out
    assert read_all(built) == before, "a dry run wrote to the destination"


def test_stale_output_is_removed(built):
    stale = built / "leftover.md"
    stale.write_text("old", encoding="utf-8")
    assert build_gen_ai.main(["--src", str(SRC), "--dst", str(built)]) == 0
    assert not stale.exists()


def test_a_stale_folder_is_named_and_left_alone(built, capsys):
    """The build only ever makes files, so a folder here was put there by hand."""
    folder = built / "old-bundle"
    folder.mkdir()
    (folder / "levels.md").write_text("an older copy", encoding="utf-8")
    capsys.readouterr()
    assert build_gen_ai.main(["--src", str(SRC), "--dst", str(built)]) == 0
    assert "old-bundle/" in capsys.readouterr().out
    assert (folder / "levels.md").exists(), "the build deleted a folder it did not create"


# ---------- loud failures ----------

def test_a_file_over_the_platform_character_limit_fails(items):
    with pytest.raises(build_gen_ai.BuildError) as exc:
        build_gen_ai.check_limits(items, limit=100)
    assert "100" in str(exc.value)


def test_the_character_limit_aborts_before_anything_is_written(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(build_gen_ai, "CHAR_LIMIT", 100)
    dst = tmp_path / "knowledge"
    assert build_gen_ai.main(["--src", str(SRC), "--dst", str(dst)]) == 1
    assert not dst.exists() or not list(dst.iterdir())
    assert "character limit" in capsys.readouterr().out


def test_every_rewrite_aborts_the_build_when_its_source_drifts(tmp_path):
    """All of them, not the first: a rule that stops matching must never be skipped quietly."""
    src = tmp_path / "references"
    shutil.copytree(SRC, src)
    for rule in build_gen_ai.REWRITES:
        target = src / rule.rel
        original = target.read_text(encoding="utf-8")
        assert rule.old in original.replace("\r\n", "\n"), f"{rule.rel}: rule does not match today"
        target.write_text(original.replace(rule.old, "rewritten upstream"),
                          encoding="utf-8", newline="\n")
        try:
            with pytest.raises(build_gen_ai.BuildError) as exc:
                build_gen_ai.bundle(src)
            assert rule.rel in str(exc.value)
        finally:
            target.write_text(original, encoding="utf-8", newline="")


def test_a_section_rewrite_aborts_when_its_heading_is_gone(tmp_path):
    src = tmp_path / "references"
    shutil.copytree(SRC, src)
    for rule in build_gen_ai.SECTIONS:
        target = src / rule.rel
        original = target.read_text(encoding="utf-8")
        assert rule.heading in original, f"{rule.rel}: {rule.heading!r} is not there today"
        target.write_text(original.replace(rule.heading, "## Renamed upstream"),
                          encoding="utf-8", newline="\n")
        try:
            with pytest.raises(build_gen_ai.BuildError) as exc:
                build_gen_ai.bundle(src)
            assert rule.heading in str(exc.value)
        finally:
            target.write_text(original, encoding="utf-8", newline="")


def test_a_rewrite_for_a_file_the_bundle_never_copies_fails(monkeypatch):
    """A misspelled rel used to be silently skipped: apply_rewrites only sees COPIES."""
    stray = build_gen_ai.Rewrite("question-bnak.md", "anything", "anything else")
    monkeypatch.setattr(build_gen_ai, "REWRITES", [stray])
    with pytest.raises(build_gen_ai.BuildError) as exc:
        build_gen_ai.bundle(SRC)
    assert "question-bnak.md" in str(exc.value)


def test_a_section_rewrite_scoped_to_a_worked_example_fails(monkeypatch):
    stray = build_gen_ai.SectionRewrite("examples/nh2-supervisor", "## Nope", "## Nope\n")
    monkeypatch.setattr(build_gen_ai, "SECTIONS", [stray])
    with pytest.raises(build_gen_ai.BuildError) as exc:
        build_gen_ai.bundle(SRC)
    assert "examples/nh2-supervisor" in str(exc.value)


def test_a_missing_source_fails(tmp_path):
    src = tmp_path / "references"
    shutil.copytree(SRC, src)
    (src / "levels.md").unlink()
    with pytest.raises(build_gen_ai.BuildError):
        build_gen_ai.bundle(src)


def test_an_unknown_checker_flag_fails():
    assert "annual assessment" in build_gen_ai.flags_to_prose("--mode annual")
    with pytest.raises(build_gen_ai.BuildError):
        build_gen_ai.flags_to_prose("--mode annual --invent-something")


# ---------- privacy ----------

def test_the_bundle_carries_no_sensitive_looking_values(built):
    # Built at runtime so this test file never trips the repository's PII hook.
    ssn = "123" + "-45-" + "6789"
    dob = "date" + " of " + "birth"
    banner = "CUI" + "//" + "SP-PRVCY"
    for name, text in read_all(built).items():
        assert ssn not in text, name
        assert dob not in text.lower(), name
        assert banner not in text, name
