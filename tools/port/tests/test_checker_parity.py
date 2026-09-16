"""The offline checker page and skills/review/scripts/check.py must agree.

The fixture corpus lives inside gen_ai/checker/acqdemo-checker.html between the
FIXTURES markers. The page runs it behind ?selftest=1 or #selftest; this module parses
the same block out of the HTML and runs every fixture through check.py.

Both directions are guarded. The corpus alone only proves check.py still says what the
fixtures claim, so the page's own engine is extracted from between the ENGINE markers and
run under node on the same fixtures, comparing whole findings: severity, factor, code and
message. Codes alone are too coarse. A count in a message drifting from "2 labels are
lowercase" to "3" is a real defect and changes no code, and that is the shape most of the
divergences found in review took. Without node the page comparison skips and the check.py
side still runs, so a machine without node still has a green, if weaker, suite.
"""
import functools
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
HTML = ROOT / "gen_ai" / "checker" / "acqdemo-checker.html"

sys.path.insert(0, str(ROOT / "skills" / "review" / "scripts"))
import check  # noqa: E402

START = "<!-- FIXTURES:START -->"
END = "<!-- FIXTURES:END -->"
ENGINE_START = "// ENGINE:START"
ENGINE_END = "// ENGINE:END"
NODE = shutil.which("node")

# Reads the engine and the cases from one JSON file so nothing has to be escaped into a
# command line, and returns every finding as [severity, factor, code, message].
RUNNER = """
var fs = require("fs");
var payload = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
var engine = new Function(payload.engine + "\\nreturn ACQ_ENGINE;")();
var out = payload.cases.map(function (one) {
  return engine.runChecks(one).findings.map(function (f) {
    return [f.severity, f.factor, f.code, f.message];
  });
});
process.stdout.write(JSON.stringify(out));
"""

# The two message differences that are by design. Each is normalized on the check.py side
# only, and only the part that differs, so real drift anywhere else in the message still
# fails. Anything added here is a decision that the two engines may differ; do not reach for
# it to make a failing test pass.
CLI_ONLY_ADVICE = " (set --what-label to match your pay pool)"
PRIOR_FILE_NAME = re.compile(r"run also in prior file '[^']*':")
PRIOR_MERGED = "run also in the prior or midpoint text:"
PRIOR_CANONICAL = "run also in prior material:"


def canonical(severity, factor, code, message):
    """One finding, with the accepted wording differences folded together."""
    # check.py names the prior file a run came from; the page has one prior box, merges what
    # is in it, and names no file. Documented in the design spec as the accepted difference.
    message = PRIOR_FILE_NAME.sub(PRIOR_CANONICAL, message)
    message = message.replace(PRIOR_MERGED, PRIOR_CANONICAL)
    # check.py tells you which command line flag to set; there is no command line in the page.
    if message.endswith(CLI_ONLY_ADVICE):
        message = message[: -len(CLI_ONLY_ADVICE)]
    return severity, factor, code, message

# Every code check.py can emit except MISSING_FILE, which needs a file system.
PORTED_CODES = {
    "ACQ_CERT", "BANNED_WORD", "CHAR_COUNT", "CHAR_LIMIT", "CHAR_SOFT_LIMIT",
    "CONTRIBUTION_TOO_LONG", "CROSS_FACTOR_REPEAT", "EM_DASH", "ENTRY_INCOMPLETE",
    "FM_CERT", "LABEL_CASE", "LABEL_STYLE", "MARKDOWN", "MIN_ENTRIES", "NAME_IN_TEXT",
    "ORPHAN_LABEL", "OVERUSED_WORD", "PREAMBLE_REPEAT", "PRIOR_REPEAT", "SMART_QUOTES",
    "SUPERVISOR_STATEMENT",
}
NETWORK = re.compile(r"https?://|\bfetch\s*\(|XMLHttpRequest|WebSocket|navigator\.sendBeacon|"
                     r"<script[^>]+\bsrc=|<link[^>]+\bhref=|<img[^>]+\bsrc=|@import")


def page_text():
    return HTML.read_text(encoding="utf-8")


def load_fixtures():
    text = page_text()
    start = text.index(START) + len(START)
    end = text.index(END)
    return json.loads(text[start:end])


FIXTURES = load_fixtures()


def engine_source():
    text = page_text()
    return text[text.index(ENGINE_START):text.index(ENGINE_END)]


def page_case(case):
    """One case in the shape ACQ_ENGINE.runChecks expects."""
    return {"mode": case["mode"],
            "factors": case["factors"],
            "prior": case.get("prior", ""),
            "names": case.get("names", []),
            "allow": case.get("allow", []),
            "acq": case.get("acq", False),
            "fm": case.get("fm", False),
            "supervisor": case.get("supervisor", False),
            "whatLabel": case.get("whatLabel", "C")}


def run_in_page(cases):
    """Run cases through the engine the page itself ships, under node."""
    cases = [page_case(case) for case in cases]
    with tempfile.TemporaryDirectory() as folder:
        runner = Path(folder) / "runner.js"
        runner.write_text(RUNNER, encoding="utf-8")
        payload = Path(folder) / "payload.json"
        payload.write_text(json.dumps({"engine": engine_source(), "cases": cases}), encoding="utf-8")
        done = subprocess.run([NODE, str(runner), str(payload)],
                              capture_output=True, text=True, encoding="utf-8", timeout=180)
    assert done.returncode == 0, f"the page's engine would not run under node:\n{done.stderr}"
    return [[tuple(row) for row in case] for case in json.loads(done.stdout)]


@functools.lru_cache(maxsize=1)
def page_findings():
    """Every fixture run through the page's engine, in fixture order. Node starts once."""
    return run_in_page(FIXTURES)


def needs_node():
    if NODE is None:
        pytest.skip("node is not on PATH, so the page's engine can only be checked in a browser")


def run_fixture(fixture, folder):
    for key, name in check.FACTOR_FILES.items():
        (folder / name).write_text(fixture["factors"][key], encoding="utf-8", newline="\n")
    prior = {"prior": fixture["prior"]} if fixture.get("prior", "").strip() else {}
    min_entries = 3 if fixture["mode"] == "annual" else 1
    return check.run_checks(folder, min_entries,
                            acq=fixture.get("acq", False),
                            fm=fixture.get("fm", False),
                            supervisor=fixture.get("supervisor", False),
                            prior=prior,
                            names=fixture.get("names", []),
                            allow=fixture.get("allow", []),
                            what_label=fixture.get("whatLabel", "C"))


def test_page_exists_and_carries_the_markers():
    text = page_text()
    assert text.count(START) == 1 and text.count(END) == 1
    assert '<script type="application/json" id="fixtures">' in text
    assert text.index('<script type="application/json" id="fixtures">') < text.index(START)


def test_page_is_plain_text_with_no_control_bytes():
    # Sentinels are written as JS escapes, never as raw control bytes, so the file
    # survives email, SharePoint, and an editor that normalizes encodings.
    raw = HTML.read_bytes()
    stray = sorted({byte for byte in raw if byte < 0x20 and byte not in (0x09, 0x0A, 0x0D)} | {b for b in raw if b == 0x7F})
    assert stray == [], f"control bytes in the page: {[hex(b) for b in stray]}"
    assert '<meta charset="utf-8">' in page_text()
    # Pure ASCII for the same reason. The em dash and smart quote rules are the only characters
    # that would ever need escaping, and re-encoding the file would mojibake them and silently
    # stop both rules firing, which is worse than a wrong answer.
    high = sorted({hex(byte) for byte in raw if byte > 0x7F})
    assert high == [], f"write non-ASCII as \\uXXXX escapes, found bytes {high}"


def test_page_makes_no_network_calls():
    hits = sorted({m.group(0) for m in NETWORK.finditer(page_text())})
    assert hits == [], f"the checker must work offline from file://, found {hits}"


def test_corpus_is_large_enough():
    assert len(FIXTURES) >= 15
    names = [f["name"] for f in FIXTURES]
    assert len(set(names)) == len(names), "fixture names must be unique"


def test_every_fixture_is_well_formed():
    for fixture in FIXTURES:
        assert set(fixture["factors"]) == set(check.FACTOR_FILES)
        assert fixture["mode"] in ("annual", "midpoint", "closeout")
        assert isinstance(fixture["prior"], str)
        assert fixture["expect"] == sorted(set(fixture["expect"]))
        assert set(fixture["expect"]) <= PORTED_CODES


def test_corpus_covers_every_ported_rule():
    covered = {code for fixture in FIXTURES for code in fixture["expect"]}
    assert PORTED_CODES - covered == set()


def test_corpus_has_a_clean_fixture(tmp_path):
    clean = [f for f in FIXTURES if not set(f["expect"]) - {"CHAR_COUNT"}]
    assert clean, "at least one fixture must be a clean draft"
    for fixture in clean:
        folder = tmp_path / re.sub(r"\W+", "-", fixture["name"])
        folder.mkdir()
        findings = run_fixture(fixture, folder)
        assert [f.code for f in findings if f.severity == "CRITICAL"] == []


@pytest.mark.parametrize("fixture", FIXTURES, ids=[f["name"] for f in FIXTURES])
def test_fixture_codes_match_check_py(fixture, tmp_path):
    findings = run_fixture(fixture, tmp_path)
    got = sorted({f.code for f in findings})
    assert got == sorted(set(fixture["expect"])), (
        f"{fixture['name']}: check.py produced {got}, the fixture expects {sorted(set(fixture['expect']))}"
    )


@pytest.mark.parametrize("fixture", FIXTURES, ids=[f["name"] for f in FIXTURES])
def test_fixture_severities_are_stable(fixture, tmp_path):
    findings = run_fixture(fixture, tmp_path)
    for found in findings:
        assert found.severity in ("CRITICAL", "WARNING", "INFO")
        assert found.code in PORTED_CODES


def test_the_page_carries_an_extractable_engine():
    text = page_text()
    assert text.count(ENGINE_START) == 1 and text.count(ENGINE_END) == 1
    assert text.index(ENGINE_START) < text.index(ENGINE_END)
    assert "var ACQ_ENGINE = (function" in engine_source()


@pytest.mark.parametrize("index, fixture", list(enumerate(FIXTURES)),
                         ids=[f["name"] for f in FIXTURES])
def test_the_page_and_check_py_produce_the_same_findings(index, fixture, tmp_path):
    """The drift guard that matters: whole findings, both engines, same fixture."""
    needs_node()
    from_page = sorted(canonical(*row) for row in page_findings()[index])
    from_cli = sorted(canonical(f.severity, f.factor, f.code, f.message)
                      for f in run_fixture(fixture, tmp_path))
    only_page = [f for f in from_page if f not in from_cli]
    only_cli = [f for f in from_cli if f not in from_page]
    assert not only_page and not only_cli, (
        f"{fixture['name']}: the two engines disagree.\n"
        f"  only the page: {only_page}\n"
        f"  only check.py: {only_cli}"
    )


@pytest.mark.parametrize("index, fixture", list(enumerate(FIXTURES)),
                         ids=[f["name"] for f in FIXTURES])
def test_the_page_orders_findings_the_way_check_py_does(index, fixture, tmp_path):
    """Both sort by severity, then factor, then code, and both must be stable about it.

    Messages are left out here on purpose: check.py builds its roster name terms from a set,
    so two NAME_IN_TEXT findings that share a factor can come back either way round. The sort
    key itself is deterministic in both, so comparing the key sequence still catches a sort
    that has drifted without being hostage to that.
    """
    needs_node()
    from_page = [(row[0], row[1], row[2]) for row in page_findings()[index]]
    from_cli = [(f.severity, f.factor, f.code) for f in run_fixture(fixture, tmp_path)]
    assert from_page == from_cli, f"{fixture['name']}: findings come out in a different order"


def crowded_draft():
    """A draft that puts several codes inside one severity and factor.

    No fixture does: every fixture's findings are one code per severity and factor, so the
    code tiebreak in the sort is never reached and an ordering change there passes unnoticed.
    Built here rather than added to the corpus, which stays as the page ships it.
    """
    em_dash = chr(0x2014)
    return {
        "mode": "annual",
        "factors": {
            # MARKDOWN, then one complete entry carrying BANNED_WORD and EM_DASH, then a
            # repeated R for ORPHAN_LABEL and a bare C for ENTRY_INCOMPLETE. Under three
            # complete entries, so MIN_ENTRIES as well.
            "JA": ("- a bullet line\n"
                   "\n"
                   "C: seamlessly delivered the cost model\n"
                   "R: the result came in early " + em_dash + " by a week\n"
                   "I: the office decided sooner\n"
                   "R: a repeated R label\n"
                   "C: a second entry with nothing under it\n"),
            "CT": "",
            "MS": "",
        },
        "prior": "",
    }


def test_the_page_and_check_py_agree_on_a_draft_that_crowds_one_factor(tmp_path):
    needs_node()
    case = crowded_draft()
    from_page = [canonical(*row) for row in run_in_page([case])[0]]
    from_cli = [canonical(f.severity, f.factor, f.code, f.message)
                for f in run_fixture(case, tmp_path)]
    # Ordered, not sorted: this is the case that exercises the code tiebreak in both engines.
    assert from_page == from_cli
    crowded = [f for f in from_cli if f[0] == "CRITICAL" and f[1] == "JA"]
    assert len({f[2] for f in crowded}) >= 3, "this draft no longer crowds one severity and factor"


def fixtures_by_expectation(code, expected):
    return [(i, f) for i, f in enumerate(FIXTURES) if (code in f["expect"]) is expected]


def test_the_corpus_pairs_the_within_factor_repeat_with_an_allowed_phrase():
    """One firing fixture and the same draft with the phrase allowed.

    Without the pair, a corpus could cover PREAMBLE_REPEAT while proving nothing about the
    allow-phrases path, which is the only escape hatch an employee has for a mandatory
    paragraph they are required to quote.
    """
    groups = {}
    for fixture in FIXTURES:
        groups.setdefault(json.dumps(fixture["factors"], sort_keys=True), []).append(fixture)
    pairs = [group for group in groups.values()
             if len(group) == 2
             and {"PREAMBLE_REPEAT" in one["expect"] for one in group} == {True, False}
             and any(one.get("allow") for one in group)]
    assert pairs, "no fixture pair shows an allowed phrase suppressing PREAMBLE_REPEAT"


def test_both_engines_fire_the_within_factor_repeat(tmp_path):
    """The firing direction. Whole findings, so a drifted message or severity fails here."""
    needs_node()
    cases = fixtures_by_expectation("PREAMBLE_REPEAT", True)
    assert cases, "the corpus no longer exercises PREAMBLE_REPEAT"
    for index, fixture in cases:
        folder = tmp_path / f"fires-{index}"
        folder.mkdir()
        from_cli = sorted(canonical(f.severity, f.factor, f.code, f.message)
                          for f in run_fixture(fixture, folder) if f.code == "PREAMBLE_REPEAT")
        from_page = sorted(canonical(*row) for row in page_findings()[index]
                           if row[2] == "PREAMBLE_REPEAT")
        assert from_cli, f"{fixture['name']}: check.py did not fire PREAMBLE_REPEAT"
        assert from_page, f"{fixture['name']}: the page did not fire PREAMBLE_REPEAT"
        assert from_cli == from_page, f"{fixture['name']}: the two engines word it differently"
        # A WARNING, never a CRITICAL: the overlap is with text the employee must carry, and a
        # false CRITICAL there cannot be cleared by deleting the paragraph.
        assert {row[0] for row in from_cli} == {"WARNING"}


def test_neither_engine_invents_the_within_factor_repeat(tmp_path):
    """The quiet direction, over every other fixture, including the ones with no preamble."""
    needs_node()
    for index, fixture in fixtures_by_expectation("PREAMBLE_REPEAT", False):
        folder = tmp_path / f"quiet-{index}"
        folder.mkdir()
        assert [f.code for f in run_fixture(fixture, folder) if f.code == "PREAMBLE_REPEAT"] == [], \
            f"{fixture['name']}: check.py invented a PREAMBLE_REPEAT"
        assert [row for row in page_findings()[index] if row[2] == "PREAMBLE_REPEAT"] == [], \
            f"{fixture['name']}: the page invented a PREAMBLE_REPEAT"


def separator_drafts():
    """Drafts carrying the invisible characters the two regex dialects disagree about.

    Python's \\s covers U+001C-U+001F and U+0085 and JavaScript's does not; JavaScript's "."
    and "m" treat a carriage return, U+2028 and U+2029 as line ends and Python's do not; and
    check.py strips a byte order mark when it reads the file while a paste keeps one. Each
    shape below made the two engines disagree during review, one of them by voiding a whole
    C-R-I entry and reporting three critical findings against a clean draft.

    These live here, not in the corpus, so the block the page ships stays byte-identical and
    keeps matching what has already been run on a locked-down machine. Written with chr() so
    the separators cannot be flattened by an editor or lost in a diff.
    """
    ls, ps, nel, bom, cr = chr(0x2028), chr(0x2029), chr(0x85), chr(0xFEFF), chr(0x0D)
    entries = ("C: delivered the cost model\n"
               "R: it came in early\n"
               "I: the office decided sooner\n")
    return [
        ("line separator inside a label body",
         entries.replace("cost model", "cost" + ls + "model", 1)),
        ("paragraph separator inside a label body",
         entries.replace("cost model", "cost" + ps + "model", 1)),
        ("carriage return inside a label body",
         entries.replace("cost model", "cost" + cr + "model", 1)),
        ("next line before a label", nel + entries),
        ("file separator before a label", chr(0x1C) + entries),
        ("byte order mark before a label", bom + entries),
        ("line separator before a bullet", "intro" + ls + "- a bullet\n\n" + entries),
        ("line separator before a lowercase label", "intro" + ls + "c: lower\n\n" + entries),
        ("line separator before a W label", "intro" + ls + "W: what\n\n" + entries),
        ("carriage return before a bullet", "intro" + cr + "- a bullet\n\n" + entries),
    ]


@pytest.mark.parametrize("name, text", separator_drafts(),
                         ids=[name for name, _ in separator_drafts()])
def test_invisible_separators_do_not_split_the_two_engines(name, text, tmp_path):
    needs_node()
    case = {"mode": "annual", "factors": {"JA": text, "CT": "", "MS": ""}, "prior": ""}
    from_page = [canonical(*row) for row in run_in_page([case])[0]]
    from_cli = [canonical(f.severity, f.factor, f.code, f.message)
                for f in run_fixture(case, tmp_path)]
    assert from_page == from_cli, f"{name}: an invisible character reads differently in the page"


# Anything here is ES2015 or later. The page is ES5 on purpose: this repository is public and
# the checker is meant to open from a file on a machine whose browser nobody here controls, and
# the failure mode is not a wrong answer but a blank page with no console open to explain it.
# No behavioural test can catch this, because node has all of these, so it is checked as text.
POST_ES5 = [
    "Array.from", "Array.of", "Object.assign", "Object.entries", "Object.values",
    "String.fromCodePoint", "String.raw", "Number.isInteger", "Number.isNaN",
    "Math.trunc", "Math.sign", "Promise", "WeakMap", "Symbol", "globalThis",
    "new Map(", "new Set(", "Reflect.", "Proxy(",
    ".includes(", ".startsWith(", ".endsWith(", ".padStart(", ".padEnd(", ".repeat(",
    ".codePointAt(", ".normalize(", ".trimEnd(", ".trimStart(", ".matchAll(",
    ".replaceAll(", ".find(", ".findIndex(", ".flat(", ".flatMap(", ".fill(",
    "=>", "let ", "const ", "class ", "async ", "await ", "?.", "??",
]


def page_code():
    """The page's JavaScript, without the fixture JSON and without // comment lines.

    Comments are dropped because the engine explains in prose which modern APIs it avoids and
    why, and that prose should not read as a use of them.
    """
    text = page_text()
    text = text[:text.index(START)] + text[text.index(END):]
    return re.sub(r"^[ \t]*//.*$", "", text, flags=re.M)


def test_the_page_stays_on_es5():
    code = page_code()
    found = sorted({token for token in POST_ES5 if token in code})
    assert found == [], (
        f"these are ES2015 or later and the page must run on an older browser: {found}. "
        "If one is genuinely needed, decide that deliberately and say so here."
    )


def test_the_accepted_message_differences_are_exercised():
    """If the corpus stops covering them, the normalizations above are hiding nothing.

    They would then be dead code that a future fixture could hide real drift behind, so this
    fails loudly rather than letting them rot.
    """
    covered = {code for fixture in FIXTURES for code in fixture["expect"]}
    assert "PRIOR_REPEAT" in covered, "no fixture exercises the merged-prior wording difference"
    assert "LABEL_STYLE" in covered, "no fixture exercises the --what-label wording difference"
