"""Descriptor transcriptions are complete and faithful to the source PDF."""
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DESC = ROOT / "skills" / "acqdemo" / "references" / "descriptors"
PDF = ROOT / "AcqDemo Factor Descriptors and Discriminators.pdf"
sys.path.insert(0, str(ROOT / "tools" / "hooks"))
import scan_pii  # noqa: E402  (reuses find_pdftotext)

FACTORS = [
    ("Factor 1: Job Achievement and/or Innovation", "JA"),
    ("Factor 2: Communication and/or Teamwork", "CT"),
    ("Factor 3: Mission Support", "MS"),
]
CAREER_PATH_RE = re.compile(r"CAREER PATH:[^\n]*?\((NH|NJ|NK)\)")
DISCRIMINATORS = {
    "JA": "Leadership Role; Mentoring/Employee Development; Accountability; Complexity/Difficulty; Creativity; Scope/Impact",
    "CT": "Oral; Written; Contribution to Team; Effectiveness",
    "MS": "Independence; Customer Needs; Planning/Budgeting; Execution/Efficiency",
}
EXPECTED = {
    "nh": {
        "title": "# NH: Business Management and Technical Management",
        "levels": [("I", "0-29"), ("II", "22-66"), ("III", "61-83"), ("IV", "79-100")],
        "very_high": "105, 110, 115",
        "bullets": {"JA": [6, 6, 6, 6], "CT": [4, 4, 4, 4], "MS": [4, 4, 4, 4]},
        "vh_bullets": 3,
    },
    "nj": {
        "title": "# NJ: Technical Management Support",
        "levels": [("I", "0-29"), ("II", "22-51"), ("III", "43-66"), ("IV", "61-83")],
        "very_high": "87, 91, 95",
        "bullets": {"JA": [6, 6, 6, 6], "CT": [4, 4, 4, 4], "MS": [4, 4, 4, 4]},
        "vh_bullets": 4,
    },
    "nk": {
        "title": "# NK: Administrative Support",
        "levels": [("I", "0-29"), ("II", "22-46"), ("III", "38-61")],
        "very_high": "64, 67, 70",
        "bullets": {"JA": [6, 6, 6], "CT": [4, 4, 4], "MS": [4, 4, 4]},
        "vh_bullets": 4,
    },
}


def split_sections(text, heading_prefix):
    parts = re.split(rf"^{re.escape(heading_prefix)} ", text, flags=re.M)
    return {p.splitlines()[0].strip(): p for p in parts[1:]}


def bullets(section):
    return [ln[2:].strip() for ln in section.splitlines() if ln.startswith("- ")]


def tokens(text):
    return re.findall(r"[a-z0-9]+", text.lower())


@pytest.fixture(scope="module")
def pdf_sections():
    exe = scan_pii.find_pdftotext()
    if exe is None:
        pytest.skip("pdftotext not installed")
    out = subprocess.run([exe, "-raw", str(PDF), "-"], capture_output=True, check=True)
    text = out.stdout.decode("utf-8", "replace")
    matches = list(CAREER_PATH_RE.finditer(text))
    sections = {}
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        key = m.group(1).lower()
        sections[key] = sections.get(key, "") + text[start:end]
    assert set(sections) == {"nh", "nj", "nk"}
    return {key: tokens(section_text) for key, section_text in sections.items()}


def appears_in_order(haystack, needle, slack=3):
    """True if needle's tokens appear in order in haystack within a bounded window."""
    if not needle:
        return True
    window = len(needle) * slack + 10
    starts = [i for i, tok in enumerate(haystack) if tok == needle[0]]
    for start in starts:
        pos, matched = start, 1
        limit = start + window
        for tok in needle[1:]:
            try:
                pos = haystack.index(tok, pos + 1, limit)
            except ValueError:
                break
            matched += 1
        if matched == len(needle):
            return True
    return False


@pytest.mark.parametrize("path", sorted(EXPECTED))
def test_structure(path):
    spec = EXPECTED[path]
    text = (DESC / f"{path}.md").read_text(encoding="utf-8")
    assert text.startswith(spec["title"])
    factors = split_sections(text, "##")
    for heading, key in FACTORS:
        assert heading in factors, f"{path}: missing '{heading}'"
        body = factors[heading]
        assert "**Factor description:**" in body
        assert "**Expected contribution criteria:**" in body
        assert f"**Discriminators:** {DISCRIMINATORS[key]}" in body
        levels = split_sections(body, "###")
        for (level, rng), count in zip(spec["levels"], spec["bullets"][key]):
            name = f"Level {level} ({rng})"
            assert name in levels, f"{path} {key}: missing '{name}'"
            assert len(bullets(levels[name])) == count, f"{path} {key} {name}: bullet count"
        vh = f"Very High ({spec['very_high']})"
        assert vh in levels, f"{path} {key}: missing '{vh}'"
        assert len(bullets(levels[vh])) == spec["vh_bullets"]


@pytest.mark.parametrize("path", sorted(EXPECTED))
def test_bullets_faithful_to_pdf(path, pdf_sections):
    text = (DESC / f"{path}.md").read_text(encoding="utf-8")
    unfaithful = [b for b in bullets(text) if not appears_in_order(pdf_sections[path], tokens(b))]
    assert not unfaithful, f"{path}: bullets not found in PDF: {unfaithful[:3]}"
