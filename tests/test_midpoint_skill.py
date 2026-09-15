"""Content checks for the acqdemo-midpoint SKILL.md.

Frontmatter and relative-path validity are covered generically for every
skill by tests/test_plugin_structure.py. This file checks the anchors and
exclusions specific to Task W2-2.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "acqdemo-midpoint" / "SKILL.md"

REQUIRED_ANCHORS = [
    "--mode midpoint",
    "--mode closeout",
    "min_entries_midpoint",
    "CROSS_FACTOR_REPEAT",
    "FY<yy>/midpoint/final/",
]

# Any line mentioning "crib sheet" must read as an exclusion, not an
# instruction to produce one.
EXCLUSION_MARKERS = ("no ", "not ", "never", "skip", "n't")


def _read_skill():
    assert SKILL.exists(), f"{SKILL} does not exist"
    return SKILL.read_text(encoding="utf-8")


def test_skill_exists():
    _read_skill()


def test_anchors_present():
    text = _read_skill()
    missing = [anchor for anchor in REQUIRED_ANCHORS if anchor not in text]
    assert not missing, f"SKILL.md is missing required anchors: {missing}"


def test_crib_sheet_mentioned_only_as_exclusion():
    text = _read_skill()
    lowered_lines = [line.lower() for line in text.splitlines() if "crib sheet" in line.lower()]
    assert lowered_lines, "expected the skill to explicitly exclude the crib sheet"
    for line in lowered_lines:
        assert any(marker in line for marker in EXCLUSION_MARKERS), (
            f"'crib sheet' must appear only as an exclusion, found: {line!r}"
        )


def test_references_annual_instead_of_copying():
    text = _read_skill()
    assert "../acqdemo-annual/SKILL.md" in text
    # It should not re-list the annual's own step bodies (e.g. the brain
    # dump prompt text); a light heuristic is that this file stays short.
    assert len(text.splitlines()) < 80


def test_no_scores_or_very_high_language():
    text = _read_skill()
    lowered_lines = [line.lower() for line in text.splitlines() if "very high" in line.lower()]
    assert lowered_lines, "expected the skill to explicitly exclude Very High language"
    for line in lowered_lines:
        assert any(marker in line for marker in EXCLUSION_MARKERS), (
            f"'very high' must appear only as an exclusion, found: {line!r}"
        )
