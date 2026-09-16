"""Content checks for the extract SKILL.md.

Frontmatter and relative-path validity are covered generically for every
skill by tests/test_plugin_structure.py. This file checks the anchors,
ordering, and exclusions specific to the new Documents input (CAS2Net
export and midpoint/closeout ingestion).
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "extract" / "SKILL.md"

REQUIRED_ANCHORS = [
    "## Step 1: Documents",
    "## Step 2: Git",
    "## Step 3: Calendar",
    "## Step 4: Confirm with the user",
    "../start/references/intake-checklist.md",
    "doc_text.py",
    "--pages",
    "--out",
    "prior/FY<yy>/",
    "FY<yy>/midpoint/final/",
    "FY<yy>/closeout-<date>/final/",
    "Job Achievement and Innovation.txt",
    "Communication and Teamwork.txt",
    "Mission Support.txt",
    "prior_cycle_overlap: continuing (cycle delta: unknown)",
    "paste the text",
]

def _read_skill():
    assert SKILL.exists(), f"{SKILL} does not exist"
    return SKILL.read_text(encoding="utf-8")


def test_skill_exists():
    _read_skill()


def test_anchors_present():
    text = _read_skill()
    missing = [anchor for anchor in REQUIRED_ANCHORS if anchor not in text]
    assert not missing, f"SKILL.md is missing required anchors: {missing}"


def test_documents_come_first():
    text = _read_skill()
    order = ["## Step 1: Documents", "## Step 2: Git", "## Step 3: Calendar",
             "## Step 4: Confirm with the user"]
    positions = [text.index(step) for step in order]
    assert positions == sorted(positions), (
        "Documents must be Step 1, ahead of Git and Calendar, since it shapes what "
        "the rest of the harvest looks for"
    )


def test_document_asks_are_gated_on_the_triage():
    """A first-cycle user has no prior assessment; harvest must not ask for one."""
    text = _read_skill()
    assert "first_cycle: yes" in text
    assert "skip 1.1" in text and "skip 1.2" in text
    assert "closeout the losing supervisor wrote" in text
