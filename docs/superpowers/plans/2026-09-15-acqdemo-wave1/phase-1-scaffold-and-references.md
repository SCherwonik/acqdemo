# Phase 1: Scaffold and Shared References (Tasks 1-7)

Back to [plan index](../2026-09-15-acqdemo-wave1.md).

---

### Task 1: Plugin manifests and structure tests

**Files:**
- Create: `.claude-plugin/plugin.json`
- Create: `.claude-plugin/marketplace.json`
- Create: `tests/test_plugin_structure.py`
- Modify: `pytest.ini`

- [ ] **Step 1: Point pytest at all test folders**

Replace the contents of `pytest.ini` with:

```ini
[pytest]
testpaths = tools skills tests
addopts = -q
```

- [ ] **Step 2: Write the failing structure tests**

Create `tests/test_plugin_structure.py`:

```python
"""Plugin manifests and skill files are well formed."""
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
# Backticked relative paths a SKILL.md tells Claude to open or run.
REL_PATH = re.compile(r"`((?:\.\./|\./|scripts/|references/|templates/)[^`\s]+)`")


def load_json(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def skill_files():
    return sorted(SKILLS.glob("*/SKILL.md"))


def frontmatter(path):
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    match = FRONTMATTER.match(text)
    assert match, f"{path} is missing YAML frontmatter"
    fields = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip().strip('"')
    return fields, text


def test_plugin_manifest():
    data = load_json(".claude-plugin/plugin.json")
    assert data["name"] == "acqdemo"
    assert re.fullmatch(r"\d+\.\d+\.\d+", data["version"])
    assert data["description"]


def test_marketplace_matches_plugin():
    plugin = load_json(".claude-plugin/plugin.json")
    market = load_json(".claude-plugin/marketplace.json")
    assert market["name"] == "acqdemo"
    assert len(market["plugins"]) == 1
    entry = market["plugins"][0]
    assert entry["name"] == plugin["name"]
    assert entry["version"] == plugin["version"]
    assert entry["source"] == "./"


@pytest.mark.parametrize("skill", skill_files(), ids=lambda p: p.parent.name)
def test_skill_frontmatter(skill):
    fields, _ = frontmatter(skill)
    assert fields.get("name") == skill.parent.name
    description = fields.get("description", "")
    assert description.startswith("Use when"), "descriptions start with 'Use when'"
    assert len(description) <= 1024


@pytest.mark.parametrize("skill", skill_files(), ids=lambda p: p.parent.name)
def test_skill_relative_paths_exist(skill):
    _, text = frontmatter(skill)
    missing = [rel for rel in REL_PATH.findall(text) if not (skill.parent / rel).exists()]
    assert not missing, f"{skill} references missing paths: {missing}"
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `python -m pytest tests/test_plugin_structure.py`
Expected: FAIL in `test_plugin_manifest` and `test_marketplace_matches_plugin` with `FileNotFoundError` for `.claude-plugin/plugin.json`. The two parametrized tests report an empty parameter set (skipped) because no skills exist yet.

- [ ] **Step 4: Create the manifests**

Create `.claude-plugin/plugin.json`:

```json
{
  "name": "acqdemo",
  "description": "AcqDemo evaluation toolkit: recall-first intake, evidence ledger, C-R-I drafting, and compliance review for contribution plans, midpoint and annual self-assessments.",
  "version": "0.1.0",
  "author": {
    "name": "SCherwonik"
  },
  "homepage": "https://github.com/SCherwonik/acqdemo",
  "repository": "https://github.com/SCherwonik/acqdemo",
  "keywords": ["acqdemo", "ccas", "self-assessment", "c-r-i", "performance"]
}
```

Create `.claude-plugin/marketplace.json`:

```json
{
  "name": "acqdemo",
  "description": "Marketplace for the AcqDemo evaluation toolkit",
  "owner": {
    "name": "SCherwonik"
  },
  "plugins": [
    {
      "name": "acqdemo",
      "description": "AcqDemo evaluation toolkit: recall-first intake, evidence ledger, C-R-I drafting, and compliance review for contribution plans, midpoint and annual self-assessments.",
      "version": "0.1.0",
      "source": "./",
      "author": {
        "name": "SCherwonik"
      }
    }
  ]
}
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `python -m pytest tests/test_plugin_structure.py`
Expected: 2 passed, 2 skipped.

- [ ] **Step 6: Commit**

```bash
git add pytest.ini .claude-plugin tests/test_plugin_structure.py
git commit -m "feat: add plugin manifests and structure tests"
```

---

### Task 2: Career path levels reference

**Files:**
- Create: `skills/start/references/levels.md`
- Create: `tests/test_references.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_references.py`:

```python
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
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m pytest tests/test_references.py::test_levels`
Expected: FAIL with `FileNotFoundError` for `levels.md`.

- [ ] **Step 3: Create the reference**

Create `skills/start/references/levels.md`:

```markdown
# Career Paths, Broadband Levels, and Score Ranges

Sources: `AcqDemo Factor Descriptors and Discriminators.pdf` (score ranges, Very High scores) and example pay pool business rules (Very High eligibility for NH). NJ and NK eligibility bands follow the same pattern (the top five points of the top level); confirm with your pay pool.

## Factor score ranges

| Career path | Level | Score range |
|---|---|---|
| NH | I | 0-29 |
| NH | II | 22-66 |
| NH | III | 61-83 |
| NH | IV | 79-100 |
| NJ | I | 0-29 |
| NJ | II | 22-51 |
| NJ | III | 43-66 |
| NJ | IV | 61-83 |
| NK | I | 0-29 |
| NK | II | 22-46 |
| NK | III | 38-61 |

Career path names: **NH** Business Management and Technical Management; **NJ** Technical Management Support; **NK** Administrative Support.

## Very High scores

Available only to employees in the top broadband level of their career path, and only when the employee's Expected Overall Contribution Score (EOCS) falls in the eligibility band. A Very High score must be justified in writing by showing how the employee exceeds the top level's descriptors.

| Career path | Top level | Very High scores | EOCS eligibility band |
|---|---|---|---|
| NH | IV | 105, 110, 115 | 96-100 |
| NJ | IV | 87, 91, 95 | 79-83 |
| NK | III | 64, 67, 70 | 57-61 |

Note: only the NH eligibility band (96-100) is stated in the source documents. The NJ (79-83) and NK (57-61) bands are inferred from the same pattern; verify them with your pay pool before relying on them.

## Categorical scores

Each factor also receives a categorical score made of the level number and a position within the level: L (low), M (mid), or H (high). Examples: 3H, 4M. Categorical scores stay consistent with the employee's broadband level.

## How descriptors are read

- Descriptors are written to the **high end** of each level.
- A level's descriptors are taken **as a group**. Contributions relate to them; they do not need to match every line.
- Ranges overlap between levels on purpose.
- One activity can support more than one factor, but each factor needs its own statement written in that factor's language.

## Target level

The profile field `target_level` controls calibration:
- **At or below expected:** write to the employee's current level descriptors.
- **Aiming above expected (the usual goal):** borrow language from the high end of the current level and, when the employee is not in the top level, from the next level up.
- **Top level:** borrow Very High language only when the EOCS is inside the eligibility band.
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `python -m pytest tests/test_references.py::test_levels`
Expected: 1 passed.

- [ ] **Step 5: Commit**

```bash
git add skills/start/references/levels.md tests/test_references.py
git commit -m "feat: add career path levels reference"
```

---

### Task 3: Factor descriptors for NH, NJ, NK

**Files:**
- Create: `skills/start/references/descriptors/nh.md`
- Create: `skills/start/references/descriptors/nj.md`
- Create: `skills/start/references/descriptors/nk.md`
- Create: `tests/test_descriptors.py`

The descriptor files are a faithful transcription of `AcqDemo Factor Descriptors and Discriminators.pdf`. The test enforces structure (factors, levels, ranges, bullet counts) and fidelity (every bullet's words appear in the PDF in order).

- [ ] **Step 1: Write the failing test**

Create `tests/test_descriptors.py`:

```python
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
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m pytest tests/test_descriptors.py`
Expected: FAIL with `FileNotFoundError` for `nh.md`, `nj.md`, `nk.md`.

- [ ] **Step 3: Extract the source text**

Run: `pdftotext -raw "AcqDemo Factor Descriptors and Discriminators.pdf" descriptors-raw.txt`
(On Windows without Git Bash on PATH, use `"C:\Program Files\Git\mingw64\bin\pdftotext.exe"`.)
Expected: `descriptors-raw.txt` contains the three career paths in order: NH, NJ, NK, each with three factors. Delete this file after Step 5; do not commit it.

- [ ] **Step 4: Transcribe all three files using this exact schema**

Rules:
- Copy wording and punctuation verbatim. Fix only line-wrap hyphenation and whitespace. Replace bullet glyphs with `- `. Write score ranges with a plain hyphen (`0-29`).
- One file per career path; three `##` factor sections in order; inside each, `###` level sections in ascending order, then `### Very High (...)`.
- Level bullets are the "Classification Level and Appraisal Descriptors" bullets only. Discriminator names go on the `**Discriminators:**` line, never as bullets.
- The Job Achievement factor includes the "For Supervisors (as appropriate)" text as a `**Supervisors (as appropriate):**` paragraph.
- In Very High sections, the lead-in sentence ("In addition to fully meeting the expected contribution criteria:") is a plain paragraph; each criterion is a bullet.

Complete NH Factor 1 as the model for every other section (write `nh.md` starting exactly like this, then continue with Factors 2 and 3 in the same shape, then `nj.md` and `nk.md`):

```markdown
# NH: Business Management and Technical Management

## Factor 1: Job Achievement and/or Innovation

**Factor description:** This factor captures qualifications, critical thinking, calculated risks, problem solving, leadership, supervision, and personal accountability aspects appropriate for the positions classified to the broadband levels of the NH career path.

**Expected contribution criteria:** Produces desired results, in the needed timeframe, with the appropriate level of supervision through the use of appropriate knowledge, skills, abilities and understanding of the technical requirements of the job. Achieves, demonstrates and maintains the appropriate qualifications necessary to assume and execute key acquisition and/or support requirements. Demonstrates skilled critical thinking in identifying, analyzing and solving complex issues, as appropriate. Takes and displays personal accountability in leading, overseeing, guiding, and/or managing programs and projects within assigned areas of responsibility. Work is timely, efficient and of acceptable quality. Completed work meets project/program objectives. Leadership and/or supervision effectively promotes commitment to organization goals. Flexibility, adaptability, and decisiveness are exercised appropriately.

**Supervisors (as appropriate):** Recruits, develops, motivates, and retains quality team members in accordance with EEO/AA and Merit System Principles. Takes timely/appropriate personnel actions, communicates mission and organizational goals; by example, creates a positive, safe, and challenging work environment; distributes work and empowers team members.

**Discriminators:** Leadership Role; Mentoring/Employee Development; Accountability; Complexity/Difficulty; Creativity; Scope/Impact

### Level I (0-29)
- Proactively seeks opportunities to contribute to assigned tasks.
- Seeks and takes advantage of development opportunities. Takes initiative to pursue completion of qualification requirements.
- Effectively accepts feedback on assigned and accomplished work, and incorporates it to create a better end product.
- Resolves routine problems within established guidelines. Seeks assistance as required.
- Takes initiative in determining and implementing appropriate procedures.
- Conducts activities on a collective task; assists supervisor, or other appropriate personnel, as needed.

### Level II (22-66)
- Actively contributes as a team member/leader; provides insight and recommends changes or solutions to problems.
- Identifies and pursues individual/team development opportunities. Achieves and maintains qualification and certification requirements.
- Proactively guides, coordinates, and consults with others to accomplish projects, assuming ownership of personal processes and products.
- Identifies, analyzes, and resolves complex/difficult problems.
- Adapts existing plans and techniques to accomplish complex projects/programs. Recommends improvements to the design or operation of systems, equipment, or processes.
- Plans and conducts functional technical activities for projects/programs.

### Level III (61-83)
- Considered a functional/technical expert by others in the organization; is regularly sought out by others for advice and assistance.
- Pursues or creates certification, qualification, and/or developmental programs and opportunities for self and others.
- Guides, motivates, and oversees the activities of individuals and teams with focus on project/program issues. Assumes ownership of processes and products, as appropriate.
- Develops, integrates, and implements solutions to diverse, highly complex problems across multiple areas and disciplines.
- Develops plans and techniques to fit new situations to improve overall program and policies. Establishes precedents in application of problem-solving techniques to enhance existing processes.
- Defines, directs, or leads highly challenging projects/programs.

### Level IV (79-100)
- Recognized as a technical/functional authority within and outside of the organization.
- Fosters the development of others by providing guidance or sharing expertise. Directs assignments to encourage employee development and cross-functional growth to meet organizational needs. Pursues professional self-development.
- Leads, defines, manages, and integrates efforts of several groups or teams. Assumes and assigns ownership of processes and products, as appropriate.
- Assesses and provides strategic direction for resolution of mission-critical problems, policies, and procedures.
- Works with senior management to establish new fundamental concepts and criteria and stimulate the development of new policies, methodologies, and techniques. Converts strategic goals into programs or policies.
- Defines, establishes, and directs organizational focus on challenging and highly complex projects/programs.

### Very High (105, 110, 115)
Three scores available: 105, 110, or 115. Select only one score. In addition to fully meeting the expected contribution criteria:
- Contributed results substantially beyond what was expected in the face of extremely difficult obstacles; contributions were exemplary in quality, quantity, and/or impact to the stated expectations for the goals/objectives described in the contribution plan.
- Created novel and innovative business methods and processes that contributed substantially beyond expectations to accomplishment of current work and the mission of the organization.
- Demonstrated the highest standards of professionalism establishing the model for others to follow. Accomplishments and outcomes were of such magnitude that they contributed to the extraordinary success of the organization in exceeding its mission goals and objectives for the year.
```

Titles for the other files: `# NJ: Technical Management Support` and `# NK: Administrative Support`. NK has Levels I-III only.

- [ ] **Step 5: Run the test to verify it passes**

Run: `python -m pytest tests/test_descriptors.py`
Expected: 6 passed. If `test_bullets_faithful_to_pdf` lists a bullet, compare it word for word with `descriptors-raw.txt` and fix the transcription. If `test_structure` reports a bullet count, a bullet was split, merged, or a discriminator was written as a bullet.

- [ ] **Step 6: Delete the scratch extraction and commit**

```bash
rm descriptors-raw.txt
git add skills/start/references/descriptors tests/test_descriptors.py
git commit -m "feat: add NH, NJ, NK factor descriptors with fidelity tests"
```

---

### Task 4: Program rules summary and certification templates

**Files:**
- Create: `skills/start/references/rules/ccas-core.md`
- Create: `skills/start/references/cert-templates.md`
- Modify: `tests/test_references.py` (append tests)

- [ ] **Step 1: Append the failing tests**

Append to `tests/test_references.py`:

```python
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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_references.py -k "ccas_core or cert_templates"`
Expected: 2 failed with `FileNotFoundError`.

- [ ] **Step 3: Create the rules summary**

Create `skills/start/references/rules/ccas-core.md`:

```markdown
# CCAS Rules Summary

Tags: **[common]** applies across AcqDemo per the program's Federal Register notice and Operating Guide as reflected in pay pool guidance. **[pay pool]** comes from one pay pool's business rules or guidance (the examples in this repo) and may differ in yours. The user's `paypool.md` overrides anything tagged [pay pool]. When a rule matters to a decision, tell the user to confirm it against their pay pool's current business rules.

## Cycle
- [common] The appraisal cycle runs 1 October to 30 September.
- [pay pool] Employee self-assessment and supervisor narrative due dates are set locally (example: employee 15 Sep, supervisor 30 Sep). Read them from `paypool.md`.

## Contribution plans
- [common] Plans are based on the Position Requirements Document (PRD) and approved in CAS2Net within 30 calendar days of the start of the cycle, a change in position, or an appointment.
- [pay pool] Plans may be modified during the cycle but not in the last 90 calendar days.
- [pay pool] To be eligible for a payout, the employee must be on an approved plan for 90 consecutive calendar days immediately preceding the end of the cycle.
- [pay pool] Minimum objectives per factor are set locally (example: 2). Labeled objectives (JA1, CT1, MS1) with tiebacks in assessments are announced as coming in 2027 in the example guidance.

## Midpoint
- [common] Held about midway through the cycle (March/April).
- [common] The employee writes a midpoint self-assessment in C-R-I format; at least one C-R-I per factor.
- [common] The supervisor writes an assessment without scores, meets with the employee, and documents the date and method of communication in CAS2Net.
- [pay pool] Not required for employees who entered AcqDemo after 1 May.

## Closeout
- [common] Required when the supervisor or the employee's position changes, within 30 calendar days of the event. Documents contributions for the partial period; no scores.
- [common] The gaining supervisor considers closeouts when recommending annual scores.

## Annual self-assessment
- [common] C-R-I format (Contribution, Result, Impact) for every entry. Older guidance and business rules call the same structure W-R-I (What, Result, Impact); the labels differ, not the content. Read the preferred label from `paypool.md` `what_label`.
- [common] Minimum of three distinct C-R-I statements per factor (nine total).
- [common] Do not duplicate self-assessments from year to year, and do not use the same C-R-I for more than one factor. Duplication may affect factor scores.
- [common] Failing to provide the minimum statements or to address mandatory objectives may affect factor scores.
- [common] CAS2Net holds about 4,000 characters per factor and times out after about 15 minutes without saving.

## Mandatory objectives
These paragraphs are not C-R-I and do not count toward the minimum.
- **Supervisory objective** [common]: first statement under Job Achievement and/or Innovation, in paragraph form, stating counts in this exact format: "I supervise X military, Y civilians, and manage Z contractors." Then describe how the supervisory objective was met.
- **Acquisition-coded positions** [common]: a self-certification statement as the first statement under Mission Support (certification level, date, continuous learning points, cycle end). See `cert-templates.md`.
- **DoD FM certification-coded positions** [pay pool]: a self-certification and CET maintenance statement as the second statement under Mission Support in the example business rules (the example guidance allows first or second).

## Supervisor narratives
- [common] Not required in C-R-I format.
- [common] Each factor begins with exactly one lead-in:
  - "Meeting expected contributions." (scored at the EOCS)
  - "Exceeding expected contributions." (scored above the EOCS; explain with clear, precise specifics and add significant contributions the employee omitted)
  - "Partially meeting expected contributions." or "Not meeting expected contributions." (scored below the EOCS; requires documented feedback during the cycle; no surprises)
- [pay pool] Very High exception: when coding a Very High score requires one or two factors below the EOCS, the lead-in states the employee is meeting or exceeding expected contributions.
- [pay pool] Each factor includes a short PAQL statement beginning with "PAQL:" in bold, and the supervisor states concurrence or non-concurrence with the employee's certification statements.
- [common] Narratives address contributions and results only, never personality.

## Scoring and pay
- [common] Each factor receives a categorical score, a numerical score, and a PAQL. PAQLs average to the Rating of Record; a PAQL of 1 in any factor makes the rating Unacceptable.
- [common] The EOCS is the score implied by base salary. A positive delta (OCS above EOCS) must be documented in the narratives.
- [common] Pay pool components: General Pay Increase, Contribution Rating Increase (raise to base pay), Contribution Award (one-time). Time off may be requested in lieu of part of an award.
- [pay pool] Panels consider whether a contribution warrants a salary increase (the higher level will continue) or is a one-time "bonus event."
- [pay pool] OCS of 94 and above is generally attainable for technical advisors, branch chiefs, and division chiefs; NH-IV employees consistently providing strategic contributions are also eligible. Contributions at level IV "should show strategic contributions."
- [common] Very High scores: see `levels.md`.

## Special situations
- [pay pool] **Promotion late in the cycle:** employees who received a salary increase (promotion or new pay-setting) within 150 days of the end of the cycle receive their EOCS unless substantial justification is provided.
- [pay pool] **Promotion after the cycle ends but before payout:** rated against the position held before the promotion; any raise rolls into an award.
- [common] **Moves or supervisor changes:** closeouts from the losing supervisor; the supervisor of record on 30 September completes the annual.
- [common] **New employees** with fewer than 90 consecutive days in AcqDemo at cycle end are not rated.
- [pay pool] **Time off awards** are limited to 40 hours per award and 80 hours per leave year; panels review non-CCAS awards and time off awards paid during the cycle.
- [pay pool] **Reconsideration** requests are filed in CAS2Net during a window after results (example: late January to mid February).
```

- [ ] **Step 4: Create the certification templates**

Create `skills/start/references/cert-templates.md`:

```markdown
# Certification Self-Statement Templates

Use in Mission Support before any C-R-I. Not C-R-I format; not counted toward the minimum. Fill every `{placeholder}` from the profile; if a value is unknown, ask. Never guess dates or point counts. Order comes from `paypool.md` (example: acquisition first, DoD FM second).

## Acquisition-coded positions

### Met or current
I am fully certified in {certification} as of {cert_date} and have completed {points_earned} Continuous Learning Points (CLPs) for the cycle ending {cycle_end}.

### In progress
I am partially certified in {certification} and on track to achieve full certification by my due date of {due_date}. I am current on my CLPs, having earned {points_earned} points for the cycle ending {cycle_end}.

### Waiver
I am partially certified in {certification}. I have an approved waiver in place until my due date of {waiver_date}, and I am current on my CLP requirement with {points_earned} of {points_required} points for the cycle ending {cycle_end}.

## DoD FM certification-coded positions

### Met or current
I am fully certified at {certification}. I have met my requirement of {points_required} CETs for the current cycle ending {cycle_end}.

### In progress
I am partially certified at {certification} and am on track to complete my certification requirements by the due date of {due_date}. I am current on my annual requirement of {points_required} CETs for this cycle.

### Active cycle
I am fully certified at {certification}. I have completed {points_earned} of {points_required} required CETs and am on track to complete the remaining {points_remaining} CETs by my due date of {cycle_end}.

## Placeholders
| Placeholder | Example format |
|---|---|
| {certification} | BUS-CE (Advanced); BUS-FM (Practitioner); DoD FM Level 2 |
| {cert_date}, {due_date}, {waiver_date}, {cycle_end} | 20 Aug 2024; 30 Sep 2026 |
| {points_earned}, {points_required}, {points_remaining} | 80; 40; 15 |
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `python -m pytest tests/test_references.py`
Expected: 3 passed.

- [ ] **Step 6: Commit**

```bash
git add skills/start/references/rules skills/start/references/cert-templates.md tests/test_references.py
git commit -m "feat: add CCAS rules summary and certification templates"
```

---

### Task 5: Question bank

**Files:**
- Create: `skills/start/references/question-bank.md`
- Modify: `tests/test_references.py` (append test)

- [ ] **Step 1: Append the failing test**

Append to `tests/test_references.py`:

```python
def test_question_bank():
    assert_contains(
        REF / "question-bank.md",
        [
            "## How to ask", "## Drill-down ladder", "## Question types",
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
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m pytest tests/test_references.py::test_question_bank`
Expected: FAIL with `FileNotFoundError`.

- [ ] **Step 3: Create the question bank**

Create `skills/start/references/question-bank.md`:

```markdown
# Question Bank

Recall is the bottleneck. Ask more, not less.

## How to ask
- Number every question in a round (1, 2, 3...) so the user can answer by voice: "number four: ...".
- Group questions under a short heading (the project, sweep, or factor being explored).
- Rounds of 5-8 questions work well for voice; there is no cap on the number of rounds.
- Rambling is welcome. Extract facts from long answers; do not ask the user to restructure them.
- Say names back when the user gives them ("So you trained Pat, Lee, and Morgan from the estimating branch."). Names stay in private notes only.
- Confirm every number with its source: stated, git, or estimate (see Estimate protocol).
- End every round with: "What else does that bring to mind?"
- "I don't know" and "skip" are always acceptable. Move on without pressure.
- Never ask about topics the user has not raised unless the question comes from a recall sweep or the gate list.

## Drill-down ladder
Apply to every accomplishment until it has enough for a strong C-R-I:
1. **What** exactly did you do? What was your role: owned, co-owned, owned a piece, or supported?
2. **So what?** What came out of it (product, decision, fix, capability)?
3. **Who used it?** Which people, teams, organizations, leaders? How many?
4. **What changed?** Before vs. after in time, cost, quality, risk, speed, or capability.
5. **Will it keep happening?** Is this now how things are done (sustained), or was it a one-time event?

## Question types
| Type | Templates |
|---|---|
| Scope | What was the dollar value of the program or portfolio? How many programs, systems, datasets, or estimates did it touch? How many users or analysts? |
| Audience | Who was in the room? What was the highest rank or grade (SES, SL, O-6, GS-15 equivalent)? How many attended? Were they inside or outside your organization? |
| Role | Who asked you to do it? Did you own it, share it, own a piece, or support someone else? Who worked with you, and who worked for you? |
| Before and after | How was this done before? How long did it take then and now? What broke or went wrong before? |
| Obstacle | What almost stopped it: deadline, shutdown, missing data, a broken legacy product, competing priorities, a disagreement? |
| Decision | What decision did it feed: budget, program, acquisition strategy, schedule, policy? Who made the decision? |
| Significance | Was this a first for the organization? One of a kind? Interagency? On a short deadline? Done alongside competing priorities? |
| Sustained | Is this now standard practice or recurring each cycle? Who else depends on it going forward? |
| Recognition | Did anyone thank you, cite it, request more of it, or give an award or time off for it? |
| Evidence | Where would proof live: repository, file, slide title, email subject, meeting title? |

## Gate questions
Ask once per cycle, before drafting. Unknown answers are recorded as gaps, never guessed.
1. What is your career path and broadband level as of the last day of the cycle?
2. What is your EOCS for this cycle? If it changed during the year, what was it before and after?
3. What are the exact rating period dates?
4. Can you paste your contribution plan objectives (and any revised plan)?
5. What is your certification status: certification name and level, date, continuous learning points or CETs earned, due dates?
6. Who were your supervisors this cycle, with dates? Were closeouts done?
7. Were you promoted, reassigned, or given new duties this cycle? Effective dates?
8. Do you supervise anyone or manage contractors? Exact counts of military, civilians, and contractors.
9. Did you receive any awards or time off awards this cycle? For what?

## Discriminator questions
Pick the questions that fill gaps in the current ledger entry. Adapt wording to the project; never read them as a script.

### Job Achievement and/or Innovation

#### Leadership Role
- Did you lead this, or lead part of it? How many people or teams did you coordinate?
- Did anyone take direction from you, formally or informally?
- Did you set the approach others followed?

#### Mentoring/Employee Development
- Who did you teach, train, or mentor? Names, roles, and how many sessions?
- Did anyone you helped go on to do something on their own because of it?
- Did you create training material or documentation others still use?

#### Accountability
- What were you personally on the hook for? What deadline or deliverable carried your name?
- What would have happened if you had not delivered?

#### Complexity/Difficulty
- What made this hard: data quality, technical depth, many stakeholders, ambiguity, scale?
- Did you find and fix errors or defects in existing products, models, or processes?

#### Creativity
- Was your approach new for your organization? Did you invent a method, tool, or technique?
- What did you try that others had not?

#### Scope/Impact
- How far did it reach: your team, division, agency, headquarters staff, service, DoD, Congress?
- What dollar values, program counts, or user counts are attached?

### Communication and/or Teamwork

#### Oral
- What briefings, demonstrations, or presentations did you give? To whom, how many, highest rank?
- Did any briefing seek a decision or consensus? What was decided?

#### Written
- What did you write or co-write: reports, memos, documentation, user guides, specifications?
- Who read it and what did they do with it?

#### Contribution to Team
- Which teams or working groups did you participate in or lead? Across which organizations?
- Did you resolve a disagreement or align different approaches? Between whom?

#### Effectiveness
- Did your communication change anything: adoption, fewer questions, faster turnaround, fewer revisions?
- Were you sought out for help? By whom and how often?

### Mission Support

#### Independence
- How much guidance did you need? Did you define the problem yourself?
- Did you anticipate a problem before it hit?

#### Customer Needs
- Who were your customers (program offices, leadership, other divisions, analysts)?
- Did a customer ask for something specific that you delivered? Did you translate their need into a product?

#### Planning/Budgeting
- Did your work influence cost, schedule, or resource decisions? How much money or time was involved?
- Did you plan resources across more than one project?

#### Execution/Efficiency
- What got faster, cheaper, or more accurate? By how much?
- What manual work did you eliminate or automate?

## Recall sweeps

### Calendar export
Ask for this before the timeline walk. If `FY<yy>/evidence/` has no calendar file, give the user these steps (classic desktop Outlook; README Section 6.4 has the full version):
1. Calendar > **View** tab > **Change View** > **List**.
2. Sort by the **Start** column, or **View Settings > Filter** to the rating period.
3. Optional: right-click column headers > **Remove This Column**; keep **Subject** and **Start**.
4. Click the first meeting, **Shift**+click the last, **Ctrl + C**.
5. Paste into Notepad and save as `FY<yy>/evidence/calendar-<YYYY-MM-DD>.txt`.
Then run the calendar harvest (see the acqdemo-extract skill). Remind the user never to export from a classified system and to delete sensitive titles.

### Timeline walk
1. Build a month list from the first to the last month of the rating period.
2. Seed each month with anchors already known: meetings from the calendar harvest (especially briefings, demos, working groups, and recurring series), git releases and tags, midpoint and closeout dates, promotions or moves, awards, shutdowns, budget or program milestones the user mentioned.
3. Walk month by month: "In <month>, I have <anchors>. What else was going on that month? Any briefings, deadlines, fires, trips, trainings?"
4. Every new item becomes a candidate ledger entry.

### People rings
First time only: ask the user to describe their office map (sections or teams and the people in each). Save it to `profile.md`.
Then sweep ring by ring. Ask for names explicitly.
1. **Own office, section by section:** "Did you help anyone in <section>? Name them. What did you do with or for each?"
2. **Other divisions or directorates:** "Which other divisions did you work with? Who there, and on what?"
3. **Government outside your organization:** program offices, commands, headquarters staff, other agencies. "Who, what organization, what did you do together?"
4. **Contractors:** "Which contractor companies did you work with? Who in each company? Did you direct, review, or support their work?"
5. **Leadership:** "Which senior leaders did you brief, advise, or answer questions for? What about?"
Record each person in `roster.md` with ring, organization, role, what was done, frequency, and linked ledger entries. Counts from the roster become numbers in statements (people trained, organizations supported).

### Artifact prompts
- "Open your calendar for <month> and read me meeting titles that were yours or where you presented."
- "Search sent mail for 'attached', 'brief', 'slides', 'thanks' and read me subjects."
- "Which chat channels or threads were busiest for you?"
- "Which slide decks or documents did you create or update this year? Titles are enough."
- "Which shared drive folders or repositories did you touch most?"

## Estimate protocol
When the user does not know a number, climb this ladder and stop at the first rung that works:
1. **Evidence:** git counts (commits, versions, tags, findings closed), file counts, attendance lists, calendar entries.
2. **Proxy count:** versions released, users onboarded, sessions held, programs supported, datasets processed.
3. **Estimate with a basis the user approves:**
   - Time saved = users x runs per period x hours saved per run.
   - Reach = attendees per session x sessions.
   - Dollar scope = value of the programs or portfolio the work supported.
   - Error reduction = defects found x consequence (for example, a unit error of 1,000x).
   Propose the top of the plausible range, rounded up, phrased "over" or "approximately". Ask: "Does <estimate> sound defensible to you?" Record the basis line in the ledger.
4. **No number:** lean on scope, audience, and organizational level instead.
Never estimate events, audiences, awards, or recognition.

## Coverage grid and stop rule
After each deep-dive, show the grid:

| Factor | Ready entries | Weakest discriminators |
|---|---|---|
| JA | n | ... |
| CT | n | ... |
| MS | n | ... |

Continue deep-dives until every factor has at least four `ready` entries (three plus a spare) or the user says "enough." Aim the next questions at the weakest factor and its uncovered discriminators.
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `python -m pytest tests/test_references.py::test_question_bank`
Expected: 1 passed.

- [ ] **Step 5: Commit**

```bash
git add skills/start/references/question-bank.md tests/test_references.py
git commit -m "feat: add question bank with recall sweeps and estimate protocol"
```

---

### Task 6: Writing style reference

**Files:**
- Create: `skills/start/references/writing-style.md`
- Modify: `tests/test_references.py` (append test)

- [ ] **Step 1: Append the failing test**

Append to `tests/test_references.py`:

```python
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
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m pytest tests/test_references.py::test_writing_style`
Expected: FAIL with `FileNotFoundError`.

- [ ] **Step 3: Create the style reference**

Create `skills/start/references/writing-style.md`:

````markdown
# Writing Style for Paste-Ready Text

Applies to the three factor files that go into CAS2Net. The working doc and crib sheet may use Markdown.

## Output format
Each factor file is plain text:

```
<mandatory paragraph 1, if any>

<mandatory paragraph 2, if any>

C: <what you did, one sentence>
R: <result>
I: <impact>

C: ...
R: ...
I: ...
```

- Labels are exactly `C: `, `R: `, `I: ` at the start of a line (Contribution, Result, Impact). If `paypool.md` sets `what_label: W`, use `W: ` instead of `C: `; the structure is the same.
- One blank line between paragraphs and between entries.
- Straight quotes only. No em dashes. No bullets, headers, bold, or other Markdown.
- Mandatory paragraphs (supervisory objective under JA; certification statements under MS) come first, in the order `paypool.md` specifies. See `rules/ccas-core.md` and `cert-templates.md`.

## Length budget
- At most **3,900 characters** per factor, counting each line break as two characters (CAS2Net allows about 4,000).
- The Contribution is one sentence of at most 35 words. Result and Impact are one or two sentences each and carry the detail.
- Usually three or four C-R-I per factor. Put spare entries on the bench in the working doc rather than squeezing a fifth.

## Order
Greatest impact first. Rank by scope, organizational level reached, and novelty.

## Framing policy
| Allowed and encouraged | Never |
|---|---|
| The strongest verb the ledger role supports | Invented events, audiences, awards, or recognition |
| Stacked scope: dollar value, portfolio, number of programs, organizational level | Ownership verbs for work someone else owned |
| Language from the target level's descriptors | People's names |
| Impact that climbs at least two rungs of the impact ladder | Classified information |
| Estimated numbers at the top of a plausible range, rounded up, framed favorably, each with a basis recorded in the ledger | Numbers with no basis |

## Role verbs
| Ledger role | Verbs |
|---|---|
| owned | led, directed, spearheaded, architected, established |
| co-owned | co-led, partnered with (role) to, jointly developed |
| owned-a-piece | drove, built, delivered (the piece) for |
| supported | describe the specific piece delivered, with a strong verb on that smaller noun |

Shrink the noun, keep the verb strong: "Directed the subsystem reconciliation for the program estimate" instead of "Supported the program estimate."

## Vocabulary
- Pull phrases from the target level's descriptors in `descriptors/<path>.md` (for example, "recognized as a technical authority within and outside the organization," "works with senior management to establish new methodologies," "resolves diverse viewpoints").
- Banned words: seamlessly, friction-free, perfectly, unbroken, synergy, cutting-edge, world-class.
- "Robust" and "leverage" at most once per factor.
- Adjective test: if a number or a noun can replace an adjective, replace it.
- Active voice, subject-verb-object, precise and objective (Tongue and Quill style). Result and Impact sentences may omit the subject ("Cut review time from five days to one.").

## Impact ladder
team > division or branch > agency or command > headquarters staff > military service or department > DoD or Congress

Each Impact should sit at least two rungs above where the Result happened, and name the mission tie (budget decisions, program readiness, acquisition strategy, workforce capability).

## One project, three angles
When a project supports more than one factor, each factor gets a different angle and different wording:
- **JA:** what was built or solved and why it was hard or new.
- **CT:** who was briefed, trained, or aligned, and what they adopted.
- **MS:** the customer need met, resources saved, or schedule and budget effect.

## Raise or award framing
- **Sustained** contributions support a raise: "institutionalized," "now the standard method for every estimate," "adopted as the division's recurring process."
- **One-time "big rocks"** support an award: a single high-stakes delivery, a one-of-a-kind rescue.
Tag each allocated entry `sustained` or `one-time` in the working doc so the supervisor can argue both.

## Repeat rule
- The current cycle's midpoint is the starting point. Reuse its facts, expand them with later results, and upgrade the wording.
- Prior cycles are off limits: no run of six or more identical words, and no re-claiming an achievement already submitted. A continuing project claims only what is new this cycle.

## Special situations
- **Promotion inside a late-cycle window** (see `rules/ccas-core.md`): make continuity explicit. Show higher-level contributions before and after the effective date, emphasize sustained strategic work, and give the supervisor a substantial-justification paragraph in the crib sheet.
- **Split year (closeout):** cover both halves; the self-assessment should still stand on its own.
- **Supervisors:** the supervisory objective paragraph opens JA with exact counts.

## Examples
All examples are fictional.

**Weak**
```
C: Worked on the cost model for the program and helped the team with data.
R: The model was improved and the team was happy with the results.
I: This helped the organization make better decisions.
```

**Strong (owned role, estimate recorded in ledger)**
```
C: Architected and delivered an automated regression tool that replaced manual spreadsheet testing for 40 cost estimating relationships across 6 programs.
R: Cut model development time from about three weeks to four days per estimate and surfaced two unit errors in the legacy workbook before a leadership review.
I: Established the division's standard method for relationship testing, giving headquarters decision-makers defensible estimates for over $2B in program funding decisions.
```

**Same project, CT angle**
```
C: Trained 14 analysts across 3 divisions to use the new regression tool through live demonstrations and a written user guide.
R: Analysts in all three divisions adopted the tool for their next estimates, and questions to the team dropped to near zero within two months.
I: Raised the agency's analytic baseline and freed senior analysts for higher-priority program reviews.
```
````

- [ ] **Step 4: Run the test to verify it passes**

Run: `python -m pytest tests/test_references.py::test_writing_style`
Expected: 1 passed.

- [ ] **Step 5: Commit**

```bash
git add skills/start/references/writing-style.md tests/test_references.py
git commit -m "feat: add writing style reference"
```

---

### Task 7: Ledger format and templates

**Files:**
- Create: `skills/start/references/ledger-format.md`
- Create: `skills/start/templates/profile.md`
- Create: `skills/start/templates/paypool.md`
- Create: `skills/start/templates/roster.md`
- Create: `skills/start/templates/session-state.md`
- Create: `skills/start/templates/working-doc.md`
- Modify: `tests/test_references.py` (append tests)

- [ ] **Step 1: Append the failing tests**

Append to `tests/test_references.py`:

```python
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
        ("session-state.md", ["step:", "next_action:", "open_questions:", "updated:"]),
        ("working-doc.md", ["## 1. Status and gaps", "## 2. Final text", "## 3. Evidence table",
                            "## 4. Bench", "## 5. Descriptor map", "## 6. Supervisor and panel crib sheet",
                            "## 7. Next-cycle seeds", "### Big rocks", "### Substantial justification"]),
    ],
)
def test_templates(name, anchors):
    assert_contains(TPL / name, anchors)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_references.py -k "ledger or templates"`
Expected: 6 failed with `FileNotFoundError`.

- [ ] **Step 3: Create the ledger format reference**

Create `skills/start/references/ledger-format.md`:

````markdown
# Ledger, Roster, Session State, Profile, and Pay Pool Overlay

The ledger is the only interface between skills. Every skill that learns something writes it here; every skill that drafts reads from here.

## Workspace layout
The user's private workspace (never the public toolkit repo):

```
<workspace>/
  profile.md              who the user is (fields below)
  paypool.md              local rules and dates (fields below)
  roster.md               people, by ring (names allowed only here and in the ledger)
  prior/                  submitted text from previous cycles, one folder per cycle
  FY<yy>/
    ledger.md
    session-state.md
    rambles/              raw dictation, one file per session: YYYY-MM-DD-<topic>.md
    evidence/             raw evidence files: calendar-YYYY-MM-DD.txt (calendar export), others
    harvest/              harvest snapshots: YYYY-MM-DD-git.md, YYYY-MM-DD-calendar.md
    drafts/               v1/, v2/ ... each holding the three factor files
    final/                Job Achievement and Innovation.txt
                          Communication and Teamwork.txt
                          Mission Support.txt
                          FY<yy> working doc.md
```

## Ledger entry
`ledger.md` starts with `# Ledger FY<yy>` and holds one `##` section per entry. Ids increase and are never reused.

```markdown
## L-001 Automated regression tool
- status: ready
- dates: 2025-11 to 2026-06
- project: Regression tool
- what: Built a tool that tests every combination of cost drivers and ranks candidate relationships.
- role: owned
- audience: 14 analysts in 3 divisions; demo to division chief (GS-15 equivalent)
- numbers:
  - 40 relationships tested | source: stated | basis: user count from tool log
  - about 3 weeks to 4 days per estimate | source: estimate | basis: 2 analysts x 15 working days before vs 4 days after, user approved
  - 52 commits, v1.0 to v2.3 | source: git | basis: harvest 2026-08-20
- decision_fed: FY budget estimates for 6 programs
- obstacle: legacy workbook had two unit errors
- sustained: yes
- lenses:
  - JA: new automated method; found legacy errors
  - CT: trained 14 analysts; user guide
  - MS: cut estimate cycle time for program customers
- descriptor_hits: NH IV JA "works with senior management to establish new ... methodologies"; NH IV MS "promulgates innovative solutions and methodologies"
- prd_duty: 3
- plan_tag: JA1
- evidence: repo regression-tool@v2.3; slides "Regression Tool Demo" (Mar)
- prior_cycle_overlap: continuing (cycle delta: v2 interaction terms, adoption by 2 more divisions)
- allocated: JA
- notes:
```

Field rules:
- `role`: exactly one of `owned`, `co-owned`, `owned-a-piece`, `supported`.
- `numbers`: every number that may appear in text needs a line with `source:` (`stated`, `git`, or `estimate`) and `basis:`.
- `sustained`: `yes` or `one-time`.
- `prior_cycle_overlap`: `none`, or `continuing (cycle delta: ...)`. An entry that repeats a prior-cycle achievement with no delta is `rejected`.
- `allocated`: `JA`, `CT`, `MS`, `bench`, or empty.
- Names of people may appear in `audience`, `notes`, and `evidence`; they never pass into factor files.

## Status lifecycle
`candidate` (from harvest or a quick capture; not yet explored) > `ready` (drill-down complete; enough for a full C-R-I) > `allocated` (chosen for a factor or the bench) > `submitted` (in final text). Any status can move to `rejected` with a note.

## Roster
`roster.md`:

```markdown
# Roster

| Ring | Name | Organization | Role | Worked on | Frequency | Ledger |
|---|---|---|---|---|---|---|
| own office: estimating | Pat Example | Estimating branch | analyst | trained on regression tool | 4 sessions | L-001 |
```

Rings: `own office: <section>`, `other division`, `external government`, `contractor: <company>`, `leadership`.

## Session state
`FY<yy>/session-state.md`:

```markdown
# Session State
- step: 4 deep-dives
- next_action: deep-dive on L-007, then coverage grid
- open_questions:
  - EOCS after the promotion
- updated: 2026-09-03
```

## Profile fields
See `templates/profile.md`. Required for drafting: `career_path`, `level`, `target_level`, `rating_period`. Everything else improves quality and is asked for if missing.

## Pay pool overlay fields
See `templates/paypool.md`. Skills read due dates, minimums, mandatory paragraph order, the promotion window, the plan-days requirement, the character limit, and allow-phrases from here instead of assuming defaults.
````

- [ ] **Step 4: Create the templates**

Create `skills/start/templates/profile.md`:

```markdown
# Profile

- name_for_notes:
- career_path:            # NH, NJ, or NK
- level:                  # I, II, III, IV
- target_level:           # usually same as level; see references/levels.md
- series_and_title:
- organization:
- rating_period:          # 2025-10-01 to 2026-09-30
- eocs:                   # number; if it changed, "82 until 2026-06-13, 88 after"
- value_of_position:
- prd_path:               # path to the Position Requirements Document in this workspace
- supervisor:             # current supervisor of record and start date
- prior_supervisors:      # name, dates, closeout done yes/no
- supervises:             # "0 military, 0 civilians, 0 contractors" or "no"
- certifications:
  - type:                 # acquisition or dod-fm
    certification:
    status:               # met, in-progress, waiver, active-cycle
    cert_date:
    due_date:
    points_earned:
    points_required:
    points_remaining:
    cycle_end:

## Promotions and position changes
| Effective date | From | To | Notes |
|---|---|---|---|

## Mission statements
- one_level_up:
- two_levels_up:
- priorities:

## Office map
| Section or team | People |
|---|---|

## Repositories to harvest
| Kind | Location | Include authors |
|---|---|---|
| local | C:/path/to/repo | |
| github | owner/repo | |
```

Create `skills/start/templates/paypool.md`:

```markdown
# Pay Pool Overlay

Values below are the example pay pool's defaults. Replace them with your pay pool's current business rules and guidance.

- pay_pool:
- business_rules_source:          # file name and year
- cycle_start: 10-01
- cycle_end: 09-30
- plan_due_days: 30
- plan_days_required: 90           # consecutive days on an approved plan before cycle end
- plan_change_lock_days: 90
- midpoint_window: Mar-Apr
- employee_due: 09-15
- supervisor_due: 09-30
- panels: Oct-Nov
- reconsideration_window: late Jan to mid Feb
- min_entries_annual: 3
- min_entries_midpoint: 1
- what_label: C                    # C (Contribution, current) or W (What, older guidance)
- min_plan_objectives_per_factor: 2
- mandatory_paragraph_order:
  - JA: supervisory
  - MS: acquisition, dod-fm
- promotion_window_days: 150       # promotion within this many days of cycle end defaults to EOCS
- very_high_eocs_band: see references/levels.md
- char_limit: 3900
- supervisor_paql_prefix: "PAQL:"
- allow_phrases:                   # organization names allowed to repeat across factors and years
  -
- notes:
```

Create `skills/start/templates/roster.md`:

```markdown
# Roster

Names are private. They help recall and produce counts; they never appear in factor files.

| Ring | Name | Organization | Role | Worked on | Frequency | Ledger |
|---|---|---|---|---|---|---|
```

Create `skills/start/templates/session-state.md`:

```markdown
# Session State
- step:
- next_action:
- open_questions:
  -
- updated:
```

Create `skills/start/templates/working-doc.md`:

```markdown
# FY<yy> Working Doc

Private. Not pasted into CAS2Net.

## 1. Status and gaps
| Item | Value or gap |
|---|---|
| Career path and level | |
| EOCS | |
| Plan on file | |
| Certifications | |
| Supervisors and closeouts | |
| Special situations | |
| Review result | 0 CRITICAL / n WARNING |

## 2. Final text
### Job Achievement and/or Innovation (<n> characters)
### Communication and/or Teamwork (<n> characters)
### Mission Support (<n> characters)

## 3. Evidence table
| Factor | Entry | Claim | Ledger | Source | Basis |
|---|---|---|---|---|---|

## 4. Bench
### Unused entries
### Alternates (punchier / safer) per statement

## 5. Descriptor map
| Factor | Entry | Descriptor lines hit | Discriminators covered |
|---|---|---|---|
### Discriminators with no coverage

## 6. Supervisor and panel crib sheet
### Big rocks
1.
2.
3.
### Hard counts
### Contributions to add to the supervisor narrative
### Exceeding expected contributions rationale
- JA:
- CT:
- MS:
### Substantial justification
(Only when a special situation applies, such as a promotion inside the pay pool's late-cycle window.)
### Reminders
- State concurrence with the certification statements.
- Document the midpoint discussion date and method in CAS2Net.
### Raise or award tags
| Entry | sustained / one-time |
|---|---|

## 7. Next-cycle seeds
### KPIs to track
### Plan objective ideas
### Capture reminders
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `python -m pytest tests/test_references.py`
Expected: 11 passed.

- [ ] **Step 6: Run the whole suite and commit**

Run: `python -m pytest`
Expected: all pass (tools, structure, references, descriptors).

```bash
git add skills/start/references/ledger-format.md skills/start/templates tests/test_references.py
git commit -m "feat: add ledger format reference and workspace templates"
```

- [ ] **Step 7: Phase-end sync** (see plan index, "Phase-end sync")
