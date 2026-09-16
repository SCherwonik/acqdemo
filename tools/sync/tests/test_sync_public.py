"""Tests for tools/sync/sync_public.py (private workspace -> public mirror)."""
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sync_public  # noqa: E402

START = "<!-- PERSONAL" + ":START -->"
END = "<!-- PERSONAL" + ":END -->"


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def make_repo(path, files, track=True):
    path.mkdir(parents=True, exist_ok=True)
    git(path, "init", "-q")
    for rel, content in files.items():
        f = path / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            f.write_bytes(content)
        else:
            f.write_text(content, encoding="utf-8", newline="\n")
    if track:
        git(path, "add", "-A")
    return path


def base_files(**extra):
    files = {
        "tools/sync/personal-paths.txt": "# personal\npersonal/\n*.secret.md\n",
        "tools/sync/denylist.txt": "# names\nZebulon\n",
        "README.md": f"# Title\n\nGeneral text.\n\n{START}\nMy private status.\n{END}\n\nMore general text.\n",
        "general/guide.md": "Generic guide.\n",
        "personal/notes.md": "Private notes.\n",
        "draft.secret.md": "Private draft.\n",
    }
    files.update(extra)
    return files


# ---------- strip_personal ----------

def test_strip_personal_removes_marked_block_and_marker_lines():
    text = f"a\n{START}\nsecret\n{END}\nb\n"
    out, n = sync_public.strip_personal(text)
    assert out == "a\nb\n"
    assert n == 1


def test_strip_personal_supports_hash_markers():
    text = "x = 1\n# PERSONAL" + ":START\ny = 2\n# PERSONAL" + ":END\nz = 3\n"
    out, n = sync_public.strip_personal(text)
    assert out == "x = 1\nz = 3\n"
    assert n == 1


def test_strip_personal_collapses_extra_blank_lines_left_behind():
    text = f"a\n\n{START}\nsecret\n{END}\n\nb\n"
    out, _ = sync_public.strip_personal(text)
    assert out == "a\n\nb\n"


def test_strip_personal_ignores_inline_mentions_of_markers():
    text = "Wrap private text in PERSONAL" + ":START and PERSONAL" + ":END lines.\nnext\n"
    out, n = sync_public.strip_personal(text)
    assert out == text
    assert n == 0


def test_strip_personal_ignores_markers_inside_fenced_code_blocks():
    text = f"Example:\n```\n{START}\nPrivate status notes.\n{END}\n```\nafter\n"
    out, n = sync_public.strip_personal(text)
    assert out == text
    assert n == 0


def test_strip_personal_allows_code_fences_inside_a_personal_block():
    text = f"a\n{START}\n```\nsecret tree\n```\n{END}\nb\n"
    out, n = sync_public.strip_personal(text)
    assert out == "a\nb\n"
    assert n == 1


def test_strip_personal_unterminated_block_raises():
    with pytest.raises(ValueError, match="unterminated"):
        sync_public.strip_personal(f"a\n{START}\nsecret\n")


def test_strip_personal_end_without_start_raises():
    with pytest.raises(ValueError, match="without"):
        sync_public.strip_personal(f"a\n{END}\n")


ROOT_EXAMPLE = Path(__file__).resolve().parents[1] / "personal-paths.example.txt"


# ---------- is_excluded ----------

@pytest.mark.parametrize(
    "rel, expected",
    [
        ("personal/notes.md", True),
        ("personal/deep/x.txt", True),
        ("draft.secret.md", True),
        ("sub/other.secret.md", True),
        ("general/guide.md", False),
        ("personalities.md", False),
        ("tools/sync/denylist.txt", True),
        ("tools/sync/personal-paths.txt", True),
        ("FY26/ledger.md", True),
        ("FY27/final/Mission Support.txt", True),
        ("docs/FY26-notes.md", False),
        ("tests/backtest-fy25/draft.md", True),
        ("profile.md", True),
        ("skills/start/templates/profile.md", False),
    ],
)
def test_is_excluded(rel, expected):
    patterns = ["personal/", "*.secret.md", "FY*/", "tests/backtest-*/", "/profile.md"]
    assert sync_public.is_excluded(rel, patterns) is expected


def test_example_personal_paths_keep_skill_templates_public():
    patterns = sync_public.load_list(ROOT_EXAMPLE)
    for name in ("profile.md", "paypool.md", "roster.md"):
        assert not sync_public.is_excluded(f"skills/start/templates/{name}", patterns), name
        assert sync_public.is_excluded(name, patterns), name


# ---------- build ----------

def test_build_uses_tracked_files_only_and_applies_exclusions(tmp_path):
    src = make_repo(tmp_path / "src", base_files())
    (src / "untracked.txt").write_text("not added\n", encoding="utf-8")
    items = sync_public.build(src)
    rels = {i.rel for i in items}
    assert rels == {"README.md", "general/guide.md"}
    readme = next(i for i in items if i.rel == "README.md")
    assert b"My private status" not in readme.data
    assert readme.stripped_blocks == 1


# ---------- scan ----------

def test_scan_flags_denylist_term_whole_word_case_insensitive(tmp_path):
    src = make_repo(tmp_path / "src", base_files(**{"general/guide.md": "Written by zebulon.\n"}))
    items = sync_public.build(src)
    findings = sync_public.scan(items, ["Zebulon"])
    assert any("general/guide.md" in f and "Zebulon" in f for f in findings)


def test_scan_allows_term_inside_larger_word(tmp_path):
    src = make_repo(tmp_path / "src", base_files(**{"general/guide.md": "See github.com/XZebulon/repo\n"}))
    items = sync_public.build(src)
    assert sync_public.scan(items, ["Zebulon"]) == []


def test_scan_flags_pii_pattern(tmp_path):
    fake_ssn = "123" + "-45-" + "6789"
    src = make_repo(tmp_path / "src", base_files(**{"general/guide.md": f"id {fake_ssn}\n"}))
    items = sync_public.build(src)
    findings = sync_public.scan(items, [])
    assert any("SSN" in f for f in findings)


# ---------- main (end to end) ----------

def test_main_mirrors_strips_and_deletes_stale(tmp_path):
    src = make_repo(tmp_path / "src", base_files())
    dst = make_repo(tmp_path / "dst", {"stale.md": "old\n", "general/guide.md": "outdated\n"})
    code = sync_public.main(["--src", str(src), "--dst", str(dst)])
    assert code == 0
    assert not (dst / "stale.md").exists()
    assert (dst / "general/guide.md").read_text(encoding="utf-8") == "Generic guide.\n"
    readme = (dst / "README.md").read_text(encoding="utf-8")
    assert "General text." in readme and "My private status" not in readme
    assert not (dst / "personal").exists()
    assert not (dst / "tools/sync/denylist.txt").exists()


def test_main_aborts_on_denylist_hit_without_writing(tmp_path):
    src = make_repo(tmp_path / "src", base_files(**{"general/guide.md": "Zebulon was here.\n"}))
    dst = make_repo(tmp_path / "dst", {"keep.md": "untouched\n"})
    code = sync_public.main(["--src", str(src), "--dst", str(dst)])
    assert code == 1
    assert (dst / "keep.md").read_text(encoding="utf-8") == "untouched\n"
    assert not (dst / "README.md").exists()


def test_main_dry_run_writes_nothing(tmp_path):
    src = make_repo(tmp_path / "src", base_files())
    dst = make_repo(tmp_path / "dst", {"stale.md": "old\n"})
    code = sync_public.main(["--src", str(src), "--dst", str(dst), "--dry-run"])
    assert code == 0
    assert (dst / "stale.md").exists()
    assert not (dst / "README.md").exists()


def test_main_refuses_same_src_and_dst(tmp_path):
    src = make_repo(tmp_path / "src", base_files())
    assert sync_public.main(["--src", str(src), "--dst", str(src)]) == 2
