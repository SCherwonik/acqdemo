"""Shared references and templates contain the anchors skills depend on."""
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "skills" / "acqdemo" / "references"
TPL = ROOT / "skills" / "acqdemo" / "templates"


def read(path):
    return path.read_text(encoding="utf-8")


def assert_contains(path, anchors):
    text = read(path)
    missing = [a for a in anchors if a not in text]
    assert not missing, f"{path.name} missing: {missing}"


def test_levels():
    assert_contains(
        REF / "levels.md",
        [
            "| NH | I | 0-29 |", "| NH | II | 22-66 |", "| NH | III | 61-83 |", "| NH | IV | 79-100 |",
            "| NJ | I | 0-29 |", "| NJ | II | 22-51 |", "| NJ | III | 43-66 |", "| NJ | IV | 61-83 |",
            "| NK | I | 0-29 |", "| NK | II | 22-46 |", "| NK | III | 38-61 |",
            "| NH | IV | 105, 110, 115 | 96-100 |",
            "| NJ | IV | 87, 91, 95 | 79-83 |",
            "| NK | III | 64, 67, 70 | 57-61 |",
            "## Target level",
        ],
    )


def test_ccas_core_rules():
    assert_contains(
        REF / "rules" / "ccas-core.md",
        [
            "[common]", "[pay pool]",
            "## Contribution plans", "## Midpoint", "## Closeout", "## Annual self-assessment",
            "## Mandatory objectives", "## Supervisor narratives", "## Scoring and pay",
            "## Special situations",
            "Meeting expected contributions", "Exceeding expected contributions",
            "Partially meeting expected contributions", "Not meeting expected contributions",
            "I supervise X military, Y civilians, and manage Z contractors.",
        ],
    )


def test_cert_templates():
    assert_contains(
        REF / "cert-templates.md",
        [
            "## Acquisition-coded positions", "## DoD FM certification-coded positions",
            "### Met or current", "### In progress", "### Waiver", "### Active cycle",
            "{certification}", "{points_earned}", "{cycle_end}",
        ],
    )


def test_question_bank():
    assert_contains(
        REF / "question-bank.md",
        [
            "## How to ask", "## Drill-down ladder", "## Confirm before dropping", "## Portfolio roll-up",
            "## Question types",
            "## Gate questions", "## Discriminator questions",
            "### Job Achievement and/or Innovation", "### Communication and/or Teamwork", "### Mission Support",
            "#### Leadership Role", "#### Mentoring/Employee Development", "#### Accountability",
            "#### Complexity/Difficulty", "#### Creativity", "#### Scope/Impact",
            "#### Oral", "#### Written", "#### Contribution to Team", "#### Effectiveness",
            "#### Independence", "#### Customer Needs", "#### Planning/Budgeting", "#### Execution/Efficiency",
            "## Recall sweeps", "### Calendar export", "### Timeline walk", "### People rings",
            "### Artifact prompts",
            "## Estimate protocol", "## Coverage grid and stop rule",
            "What else does that bring to mind?",
        ],
    )


def test_writing_style():
    assert_contains(
        REF / "writing-style.md",
        [
            "## Output format", "## Length budget", "## Order", "## Framing policy",
            "## Role verbs", "## Vocabulary", "## Impact ladder", "## One project, three angles",
            "## Raise or award framing", "## Repeat rule", "## Special situations", "## Examples",
            "seamlessly", "3,900", "C: ", "R: ", "I: ",
        ],
    )


LEDGER_FIELDS = [
    "status:", "dates:", "project:", "what:", "role:", "audience:", "numbers:",
    "decision_fed:", "obstacle:", "sustained:", "lenses:", "descriptor_hits:",
    "prd_duty:", "plan_tag:", "evidence:", "prior_cycle_overlap:",
]


def test_ledger_format():
    assert_contains(
        REF / "ledger-format.md",
        ["## Workspace layout", "## Ledger entry", "## Status lifecycle", "## Roster",
         "## Session state", "## Profile fields", "## Pay pool overlay fields"] + LEDGER_FIELDS,
    )


@pytest.mark.parametrize(
    "name, anchors",
    [
        ("profile.md", ["career_path:", "level:", "target_level:", "eocs:", "value_of_position:",
                        "rating_period:", "prd_path:", "supervisor:", "certifications:",
                        "## Office map", "## Repositories to harvest", "## Mission statements",
                        "## Promotions and position changes"]),
        ("paypool.md", ["employee_due:", "supervisor_due:", "min_entries_annual:", "min_entries_midpoint:", "what_label:",
                        "mandatory_paragraph_order:", "promotion_window_days:", "plan_days_required:",
                        "char_limit:", "allow_phrases:"]),
        ("roster.md", ["| Ring | Name | Organization | Role | Worked on | Frequency | Ledger |"]),
        ("session-state.md", ["step:", "current_entry:", "round:", "pending_questions:", "next_action:", "open_questions:", "updated:"]),
        ("working-doc.md", ["## 1. Status and gaps", "## 2. Final text", "## 3. Evidence table",
                            "## 4. Bench", "## 5. Descriptor map", "## 6. Supervisor and panel crib sheet",
                            "## 7. Next-cycle seeds", "### Big rocks", "### Substantial justification"]),
    ],
)
def test_templates(name, anchors):
    assert_contains(TPL / name, anchors)
