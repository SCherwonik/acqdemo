"""Content checks for the annual SKILL.md.

The annual skill must tell a user which documents to gather before it starts
asking questions, because a returning user never sees the router's first-time
setup.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "annual" / "SKILL.md"
MIDPOINT = ROOT / "skills" / "midpoint" / "SKILL.md"


def read(path):
    return path.read_text(encoding="utf-8")


def test_documents_step_comes_before_the_gate():
    text = read(SKILL)
    assert "## Step 0b: Documents to gather, said first" in text
    assert text.index("Step 0b") < text.index("## Step 1: Gate")


def test_annual_names_the_documents_and_the_reason():
    text = read(SKILL)
    for anchor in ["Salary Appraisal", "Check All", "Midpoint Assessment", "Contribution Plan",
                   "Closeout Assessment", "Outlook calendar", "getting-your-documents.md",
                   "first_cycle: yes"]:
        assert anchor in text, anchor


def test_midpoint_asks_for_its_own_combination():
    text = read(MIDPOINT)
    assert "Documents to gather" in text
    assert "Salary Appraisal" in text and "Check All" in text
    assert "Contribution Plan" in text
    assert "getting-your-documents.md" in text
