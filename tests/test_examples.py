"""Committed persona outputs keep passing the draft checker."""
import shlex
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "skills" / "acqdemo" / "references" / "examples"
CHECK = ROOT / "skills" / "acqdemo-review" / "scripts" / "check.py"
PERSONAS = sorted(p for p in EXAMPLES.iterdir() if (p / "final").is_dir()) if EXAMPLES.exists() else []


def test_three_personas_exist():
    assert {p.name for p in PERSONAS} == {"nj3-engineer", "nk2-admin", "nh2-supervisor"}


@pytest.mark.parametrize("persona", PERSONAS, ids=lambda p: p.name)
def test_example_passes_checker(persona):
    flags = shlex.split((persona / "flags.txt").read_text(encoding="utf-8").strip())
    res = subprocess.run([sys.executable, str(CHECK), "--dir", str(persona / "final"), *flags,
                          "--roster", str(persona / "roster.md")],
                         capture_output=True, text=True)
    assert res.returncode == 0, res.stdout
