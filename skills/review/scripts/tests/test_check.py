"""Tests for skills/review/scripts/check.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import check  # noqa: E402

ACQ = ("I am fully certified in BUS-CE (Advanced) as of 20 Aug 2024 and have completed "
       "80 Continuous Learning Points (CLPs) for the cycle ending 30 Sep 2026.")
FM = ("I am fully certified at DoD FM Level 2. I have met my requirement of 40 CETs "
      "for the current cycle ending 30 Sep 2026.")
SUP = ("I supervise 0 military, 3 civilians, and manage 2 contractors. I held monthly "
       "feedback sessions and completed all required personnel actions on time.")


def cri(topic, n):
    return (f"C: Built {topic} tool number {n} for the analysts.\n"
            f"R: Delivered {topic} release {n} on schedule.\n"
            f"I: Improved {topic} readiness across the agency {n}.\n")


def factor_text(topic, count=3, preamble=()):
    parts = list(preamble) + [cri(topic, i) for i in range(1, count + 1)]
    return "\n".join(p if p.endswith("\n") else p + "\n" for p in parts)


def write_dir(tmp_path, ja=None, ct=None, ms=None):
    folder = tmp_path / "final"
    folder.mkdir(exist_ok=True)
    texts = {"JA": ja if ja is not None else factor_text("alpha"),
             "CT": ct if ct is not None else factor_text("bravo"),
             "MS": ms if ms is not None else factor_text("charlie")}
    for key, name in check.FACTOR_FILES.items():
        (folder / name).write_text(texts[key], encoding="utf-8", newline="\n")
    return folder


def codes(findings, severity=None):
    return [f.code for f in findings if severity is None or f.severity == severity]


# ---------------------------------------------------------------- parsing

def test_parse_preamble_and_entries():
    text = f"{ACQ}\n\n{FM}\n\n{cri('alpha', 1)}\n{cri('alpha', 2)}"
    factor = check.parse_factor("MS", text)
    assert factor.preamble == [ACQ, FM]
    assert len(factor.entries) == 2
    assert all(e.complete for e in factor.entries)
    assert factor.entries[0].line == 5


def test_parse_joins_continuation_lines():
    text = "C: Led the effort\nacross three divisions.\nR: Finished early.\nI: Saved money.\n"
    entry = check.parse_factor("JA", text).entries[0]
    assert entry.C == "Led the effort across three divisions."


def test_parse_orphan_and_repeated_labels():
    text = "R: Result with no what.\nC: What.\nR: One.\nR: Two.\nI: Impact.\n"
    factor = check.parse_factor("JA", text)
    assert factor.orphans == [1, 4]


def test_parse_accepts_older_w_label_as_contribution():
    entry = check.parse_factor("JA", "W: Built it.\nR: Shipped.\nI: Saved.\n").entries[0]
    assert entry.complete and entry.C == "Built it."


def test_char_count_counts_line_breaks_twice():
    assert check.char_count("ab\ncd\n") == 6
    assert check.char_count("ab\r\ncd") == 6


# ---------------------------------------------------------------- structure and mandatory

def test_clean_draft_has_no_critical(tmp_path):
    findings = check.run_checks(write_dir(tmp_path), min_entries=3)
    assert codes(findings, "CRITICAL") == []


def test_incomplete_entry_and_minimum(tmp_path):
    ja = factor_text("alpha", count=2) + "C: Something without result.\n"
    findings = check.run_checks(write_dir(tmp_path, ja=ja), min_entries=3)
    assert "ENTRY_INCOMPLETE" in codes(findings, "CRITICAL")
    assert "MIN_ENTRIES" in codes(findings, "CRITICAL")


def test_w_labels_count_as_entries_with_style_warning(tmp_path):
    ja = factor_text("alpha").replace("C: ", "W: ")
    found = check.run_checks(write_dir(tmp_path, ja=ja), min_entries=3)
    assert codes(found, "CRITICAL") == []
    style = [f for f in found if f.code == "LABEL_STYLE"]
    assert [f.factor for f in style] == ["JA"] and style[0].severity == "WARNING"
    assert "3 entries" in style[0].message
    found_w = check.run_checks(write_dir(tmp_path, ja=ja), min_entries=3, what_label="W")
    assert sorted(f.factor for f in found_w if f.code == "LABEL_STYLE") == ["CT", "MS"]


def test_midpoint_minimum_is_one(tmp_path):
    folder = write_dir(tmp_path, ja=factor_text("alpha", 1), ct=factor_text("bravo", 1), ms=factor_text("charlie", 1))
    assert "MIN_ENTRIES" not in codes(check.run_checks(folder, min_entries=1))
    assert "MIN_ENTRIES" in codes(check.run_checks(folder, min_entries=3))


def test_supervisor_statement_required_first(tmp_path):
    folder = write_dir(tmp_path)
    assert "SUPERVISOR_STATEMENT" in codes(check.run_checks(folder, 3, supervisor=True))
    folder = write_dir(tmp_path, ja=factor_text("alpha", preamble=[SUP]))
    assert "SUPERVISOR_STATEMENT" not in codes(check.run_checks(folder, 3, supervisor=True))


def test_certification_statements_in_order(tmp_path):
    good = write_dir(tmp_path, ms=factor_text("charlie", preamble=[ACQ, FM]))
    assert codes(check.run_checks(good, 3, acq=True, fm=True), "CRITICAL") == []
    swapped = write_dir(tmp_path, ms=factor_text("charlie", preamble=[FM, ACQ]))
    found = codes(check.run_checks(swapped, 3, acq=True, fm=True), "CRITICAL")
    assert "ACQ_CERT" in found and "FM_CERT" in found


def test_fm_only_position_is_first(tmp_path):
    folder = write_dir(tmp_path, ms=factor_text("charlie", preamble=[FM]))
    assert codes(check.run_checks(folder, 3, fm=True), "CRITICAL") == []


def test_bus_fm_acquisition_statement_is_not_dod_fm(tmp_path):
    bus_fm = ("I am partially certified in BUS-FM (Practitioner) and on track to achieve full "
              "certification by 30 Jun 2027. I am current on my CLPs.")
    folder = write_dir(tmp_path, ms=factor_text("charlie", preamble=[bus_fm]))
    assert codes(check.run_checks(folder, 3, acq=True), "CRITICAL") == []


# ---------------------------------------------------------------- length

def padded_factor(target):
    """A valid 3-entry factor whose character count is exactly target."""
    base = factor_text("alpha", 2) + "C: What.\nR: Result.\nI: "
    pad = target - len(base) - base.count("\n")
    text = base + "y" * pad + "\n"
    assert check.char_count(text) == target
    return text


@pytest.mark.parametrize(
    "target, critical, warning",
    [(3900, False, False), (3901, False, True), (4000, False, True), (4001, True, False)],
)
def test_char_limits(tmp_path, target, critical, warning):
    found = check.run_checks(write_dir(tmp_path, ja=padded_factor(target)), 3)
    assert ("CHAR_LIMIT" in codes(found, "CRITICAL")) is critical
    assert ("CHAR_SOFT_LIMIT" in codes(found, "WARNING")) is warning


# ---------------------------------------------------------------- repeats

PRIOR_SENTENCE = "Reconciled contractor cost reports with the program office every quarter."


def test_prior_repeat_flags_six_word_run(tmp_path):
    ja = factor_text("alpha", 2) + "C: Reconciled contractor cost reports with the program office twice.\nR: Done.\nI: Better data.\n"
    folder = write_dir(tmp_path, ja=ja)
    findings = check.run_checks(folder, 3, prior={"fy25.txt": PRIOR_SENTENCE})
    messages = [f.message for f in findings if f.code == "PRIOR_REPEAT"]
    assert messages and "reconciled contractor cost reports with the program office" in messages[0]


def test_prior_repeat_ignores_allowed_phrase(tmp_path):
    org = "Office of the Regional Cost Estimating Directorate"
    ja = factor_text("alpha", 2) + f"C: Briefed the {org} leadership.\nR: Done.\nI: Better data.\n"
    folder = write_dir(tmp_path, ja=ja)
    prior = {"fy25.txt": f"Supported the {org} staff."}
    assert "PRIOR_REPEAT" in codes(check.run_checks(folder, 3, prior=prior))
    assert "PRIOR_REPEAT" not in codes(check.run_checks(folder, 3, prior=prior, allow=[org]))


def test_cross_factor_repeat_flags_eight_word_run(tmp_path):
    shared = "Automated the quarterly data pull for every program estimate in the branch."
    ja = factor_text("alpha", 2) + f"C: {shared}\nR: Done.\nI: Faster.\n"
    ct = factor_text("bravo", 2) + f"C: {shared}\nR: Trained staff.\nI: Adoption.\n"
    findings = check.run_checks(write_dir(tmp_path, ja=ja, ct=ct), 3)
    assert "CROSS_FACTOR_REPEAT" in codes(findings, "CRITICAL")


# ---------------------------------------------------------------- names

ROSTER = """# Roster

| Ring | Name | Organization | Role | Worked on | Frequency | Ledger |
|---|---|---|---|---|---|---|
| own office: estimating | Jordan Quill | Estimating branch | analyst | tool training | 4 | L-001 |
| contractor: Example Corp | Avery Lee | Example Corp | engineer | data pipeline | weekly | L-004 |
"""


def test_roster_names_parsed():
    assert check.roster_names(ROSTER) == ["Jordan Quill", "Avery Lee"]


def test_names_in_text_flagged_full_and_last(tmp_path):
    ja = factor_text("alpha", 2) + "C: Mentored Quill on regression.\nR: Done.\nI: Growth.\n"
    ct = factor_text("bravo", 2) + "C: Worked with Avery Lee daily.\nR: Done.\nI: Growth.\n"
    findings = check.run_checks(write_dir(tmp_path, ja=ja, ct=ct), 3, names=check.roster_names(ROSTER))
    messages = " ".join(f.message for f in findings if f.code == "NAME_IN_TEXT")
    assert "'Quill'" in messages and "'Avery Lee'" in messages


def test_short_last_names_are_not_matched_alone(tmp_path):
    ja = factor_text("alpha", 2) + "C: Worked with the lee side team.\nR: Done.\nI: Growth.\n"
    findings = check.run_checks(write_dir(tmp_path, ja=ja), 3, names=check.roster_names(ROSTER))
    assert "NAME_IN_TEXT" not in codes(findings)


# ---------------------------------------------------------------- style

def test_style_warnings(tmp_path):
    ja = factor_text("alpha", 2) + (
        "C: Seamlessly built a robust and robust tool — fast.\n"
        "R: Called it “great”.\nI: **Big** win.\n"
    )
    found = codes(check.run_checks(write_dir(tmp_path, ja=ja), 3), "WARNING")
    for code in ("BANNED_WORD", "OVERUSED_WORD", "EM_DASH", "SMART_QUOTES", "MARKDOWN"):
        assert code in found


def test_what_too_long(tmp_path):
    long_what = "C: " + " ".join(["word"] * 36) + "\nR: Done.\nI: Impact.\n"
    found = codes(check.run_checks(write_dir(tmp_path, ja=factor_text("alpha", 2) + long_what), 3), "WARNING")
    assert "CONTRIBUTION_TOO_LONG" in found


# ---------------------------------------------------------------- CLI

def test_main_clean_exit_zero_and_json(tmp_path, capsys):
    folder = write_dir(tmp_path)
    assert check.main(["--dir", str(folder), "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert {d["code"] for d in data} == {"CHAR_COUNT"}


def test_main_critical_exit_one_with_prior_dir_and_roster(tmp_path, capsys):
    prior_dir = tmp_path / "prior"
    prior_dir.mkdir()
    (prior_dir / "fy25.txt").write_text(PRIOR_SENTENCE, encoding="utf-8")
    roster = tmp_path / "roster.md"
    roster.write_text(ROSTER, encoding="utf-8")
    ja = factor_text("alpha", 2) + "C: Reconciled contractor cost reports with the program office for Avery Lee.\nR: Done.\nI: Data.\n"
    folder = write_dir(tmp_path, ja=ja)
    code = check.main(["--dir", str(folder), "--prior", str(prior_dir), "--roster", str(roster)])
    out = capsys.readouterr().out
    assert code == 1
    assert "PRIOR_REPEAT" in out and "NAME_IN_TEXT" in out
    assert out.splitlines()[0].startswith("check: ")


def test_main_mode_midpoint_sets_minimum(tmp_path):
    folder = write_dir(tmp_path, ja=factor_text("alpha", 1), ct=factor_text("bravo", 1), ms=factor_text("charlie", 1))
    assert check.main(["--dir", str(folder), "--mode", "midpoint"]) == 0
    assert check.main(["--dir", str(folder)]) == 1


def test_missing_factor_file(tmp_path):
    folder = write_dir(tmp_path)
    (folder / "Mission Support.txt").unlink()
    assert check.main(["--dir", str(folder)]) == 1


def test_main_what_label_w_accepts_older_labels(tmp_path, capsys):
    folder = write_dir(tmp_path, ja=factor_text("alpha").replace("C: ", "W: "),
                       ct=factor_text("bravo").replace("C: ", "W: "), ms=factor_text("charlie").replace("C: ", "W: "))
    assert check.main(["--dir", str(folder), "--what-label", "W"]) == 0
    assert "LABEL_STYLE" not in capsys.readouterr().out


def test_read_text_handles_utf16_bom_and_cp1252(tmp_path):
    import codecs
    utf16 = tmp_path / "u16.txt"
    utf16.write_bytes(codecs.BOM_UTF16_LE + "C: Built it.\n".encode("utf-16-le"))
    assert check.read_text(utf16).startswith("C: Built it.")
    cp = tmp_path / "cp.txt"
    cp.write_bytes("C: Led the director’s review.\n".encode("cp1252"))
    assert "director’s" in check.read_text(cp)


def test_main_prints_text_a_windows_console_cannot_encode(tmp_path):
    import os
    import subprocess
    roster = tmp_path / "roster.md"
    roster.write_text(ROSTER + "| own office: estimating | Łucja Nowak | Estimating branch | analyst | reviews | 2 | L-002 |\n",
                      encoding="utf-8")
    ja = factor_text("alpha", 2) + "C: Paired with Łucja Nowak on estimates.\nR: Done.\nI: Growth.\n"
    folder = write_dir(tmp_path, ja=ja)
    env = {**os.environ, "PYTHONIOENCODING": "cp1252"}
    run = subprocess.run([sys.executable, check.__file__, "--dir", str(folder), "--roster", str(roster)],
                         capture_output=True, env=env)
    assert run.returncode in (0, 1), run.stderr.decode("utf-8", "replace")
    assert "Łucja Nowak" in run.stdout.decode("utf-8")


def test_lowercase_labels_parse_with_case_warning():
    factor = check.parse_factor("JA", "c: Built a tool.\nr: Saved time.\ni: Faster reviews.\n")
    assert len(factor.entries) == 1 and factor.entries[0].complete and not factor.preamble
    assert "LABEL_CASE" in codes(check.check_structure(factor, 1), "WARNING")


def test_read_text_detects_utf16_without_bom(tmp_path):
    for enc in ("utf-16-le", "utf-16-be"):
        path = tmp_path / f"{enc}.txt"
        path.write_bytes("C: Built a tool.\n".encode(enc))
        assert check.read_text(path) == "C: Built a tool.\n"


def test_full_names_match_in_any_case(tmp_path):
    ja = factor_text("alpha", 2) + "C: Worked with jordan quill daily.\nR: Done.\nI: Growth.\n"
    findings = check.run_checks(write_dir(tmp_path, ja=ja), 3, names=check.roster_names(ROSTER))
    assert "NAME_IN_TEXT" in codes(findings)


def test_last_name_alone_needs_capital_so_common_words_pass(tmp_path):
    roster = ROSTER + "| own office: estimating | Pat Young | Estimating branch | analyst | reviews | 2 | L-003 |\n"
    ja = factor_text("alpha", 2) + "C: Coached young analysts.\nR: Done.\nI: Growth.\n"
    ct = factor_text("bravo", 2) + "C: Briefed Young on results.\nR: Done.\nI: Growth.\n"
    findings = check.run_checks(write_dir(tmp_path, ja=ja, ct=ct), 3, names=check.roster_names(roster))
    assert [f.factor for f in findings if f.code == "NAME_IN_TEXT"] == ["CT"]


def test_segments_do_not_bridge_labels_or_blank_lines():
    segs = check.segments("C: one two three\nR: four five six\n\nI: seven eight\nnine ten\n", [])
    assert not any({"three", "four"} <= set(s) or {"six", "seven"} <= set(s) for s in segs)
    assert ["seven", "eight", "nine", "ten"] in segs


def test_main_mode_closeout_sets_minimum_one(tmp_path):
    folder = write_dir(tmp_path, ja=factor_text("alpha", 1), ct=factor_text("bravo", 1), ms=factor_text("charlie", 1))
    assert check.main(["--dir", str(folder), "--mode", "closeout"]) == 0
