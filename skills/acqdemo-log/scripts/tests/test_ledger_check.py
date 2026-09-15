"""Tests for skills/acqdemo-log/scripts/ledger_check.py."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ledger_check  # noqa: E402

DEFAULT_FIELDS = {
    "status": "ready",
    "dates": "2025-11 to 2026-06",
    "project": "Regression tool",
    "what": "Built a tool that tests every combination of cost drivers.",
    "role": "owned",
    "audience": "14 analysts in 3 divisions; demo to division chief",
    "decision_fed": "FY budget estimates for 6 programs",
    "obstacle": "legacy workbook had two unit errors",
    "sustained": "yes",
    "prd_duty": "3",
    "plan_tag": "JA1",
    "evidence": "repo regression-tool@v2.3",
    "prior_cycle_overlap": "none",
    "allocated": "JA",
}
DEFAULT_NUMBERS = [
    "40 relationships tested | source: stated | basis: user count from tool log",
    "about 3 weeks to 4 days per estimate | source: estimate | basis: 2 analysts x 15 days before vs 4 after",
]
DEFAULT_LENSES = [
    "JA: new automated method; found legacy errors",
    "CT: trained 14 analysts; user guide",
]


def make_entry(id_token="L-001", title="Automated regression tool", fields=None,
               numbers=DEFAULT_NUMBERS, lenses=DEFAULT_LENSES, omit=()):
    merged = {**DEFAULT_FIELDS, **(fields or {})}
    for key in omit:
        merged.pop(key, None)
    lines = [f"## {id_token} {title}"]
    for key, value in merged.items():
        lines.append(f"- {key}: {value}")
    if numbers is not None:
        lines.append("- numbers:")
        for item in numbers:
            lines.append(f"  - {item}")
    if lenses is not None:
        lines.append("- lenses:")
        for item in lenses:
            lines.append(f"  - {item}")
    return "\n".join(lines) + "\n"


def ledger_text(*entries):
    return "# Ledger FY26\n\n" + "\n".join(entries)


def write_ledger(tmp_path, *entries, name="ledger.md"):
    path = tmp_path / name
    path.write_text(ledger_text(*entries), encoding="utf-8")
    return path


def codes(findings, severity=None):
    return [f.code for f in findings if severity is None or f.severity == severity]


# ---------------------------------------------------------------- parsing / clean

def test_clean_ledger_has_no_findings(tmp_path):
    path = write_ledger(tmp_path, make_entry())
    findings = ledger_check.run_checks(ledger_check.parse_ledger(ledger_check.read_text(path)))
    assert findings == []


def test_allocated_comma_list_is_clean(tmp_path):
    path = write_ledger(tmp_path, make_entry(fields={"allocated": "JA, MS"}))
    findings = ledger_check.run_checks(ledger_check.parse_ledger(ledger_check.read_text(path)))
    assert findings == []


# ---------------------------------------------------------------- CRITICAL codes

def test_bad_id_heading_not_l_plus_digits(tmp_path):
    path = write_ledger(tmp_path, make_entry(id_token="L001"))
    findings = ledger_check.run_checks(ledger_check.parse_ledger(ledger_check.read_text(path)))
    assert "BAD_ID" in codes(findings, "CRITICAL")


def test_duplicate_id(tmp_path):
    first = make_entry(id_token="L-001", title="First win")
    second = make_entry(id_token="L-001", title="Second win")
    path = write_ledger(tmp_path, first, second)
    findings = ledger_check.run_checks(ledger_check.parse_ledger(ledger_check.read_text(path)))
    dupes = [f for f in findings if f.code == "DUPLICATE_ID"]
    assert len(dupes) == 1
    assert dupes[0].severity == "CRITICAL"
    assert "L-001 Second win" == dupes[0].entry


def test_missing_field(tmp_path):
    path = write_ledger(tmp_path, make_entry(omit=["dates", "role"]))
    findings = ledger_check.run_checks(ledger_check.parse_ledger(ledger_check.read_text(path)))
    missing = [f for f in findings if f.code == "MISSING_FIELD"]
    assert len(missing) == 1
    assert "dates" in missing[0].message and "role" in missing[0].message


def test_bad_value_status(tmp_path):
    path = write_ledger(tmp_path, make_entry(fields={"status": "in-progress"}))
    findings = ledger_check.run_checks(ledger_check.parse_ledger(ledger_check.read_text(path)))
    assert "BAD_VALUE" in codes(findings, "CRITICAL")


def test_bad_value_role(tmp_path):
    path = write_ledger(tmp_path, make_entry(fields={"role": "helped"}))
    findings = ledger_check.run_checks(ledger_check.parse_ledger(ledger_check.read_text(path)))
    assert "BAD_VALUE" in codes(findings, "CRITICAL")


def test_bad_value_sustained(tmp_path):
    path = write_ledger(tmp_path, make_entry(fields={"sustained": "maybe"}))
    findings = ledger_check.run_checks(ledger_check.parse_ledger(ledger_check.read_text(path)))
    assert "BAD_VALUE" in codes(findings, "CRITICAL")


def test_number_no_source(tmp_path):
    path = write_ledger(tmp_path, make_entry(numbers=["40 relationships tested"]))
    findings = ledger_check.run_checks(ledger_check.parse_ledger(ledger_check.read_text(path)))
    assert "NUMBER_NO_SOURCE" in codes(findings, "CRITICAL")


def test_estimate_no_basis(tmp_path):
    path = write_ledger(tmp_path, make_entry(numbers=["about 5 hours saved | source: estimate"]))
    findings = ledger_check.run_checks(ledger_check.parse_ledger(ledger_check.read_text(path)))
    assert "ESTIMATE_NO_BASIS" in codes(findings, "CRITICAL")
    assert "NUMBER_NO_SOURCE" not in codes(findings)


# ---------------------------------------------------------------- WARNING codes

def test_ready_incomplete_missing_audience(tmp_path):
    path = write_ledger(tmp_path, make_entry(omit=["audience"]))
    findings = ledger_check.run_checks(ledger_check.parse_ledger(ledger_check.read_text(path)))
    assert "READY_INCOMPLETE" in codes(findings, "WARNING")


def test_ready_incomplete_missing_numbers(tmp_path):
    path = write_ledger(tmp_path, make_entry(numbers=None))
    findings = ledger_check.run_checks(ledger_check.parse_ledger(ledger_check.read_text(path)))
    assert "READY_INCOMPLETE" in codes(findings, "WARNING")


def test_ready_incomplete_missing_lenses(tmp_path):
    path = write_ledger(tmp_path, make_entry(lenses=None))
    findings = ledger_check.run_checks(ledger_check.parse_ledger(ledger_check.read_text(path)))
    assert "READY_INCOMPLETE" in codes(findings, "WARNING")


def test_ready_incomplete_not_flagged_when_not_ready(tmp_path):
    path = write_ledger(tmp_path, make_entry(fields={"status": "candidate"}, omit=["audience"]))
    findings = ledger_check.run_checks(ledger_check.parse_ledger(ledger_check.read_text(path)))
    assert "READY_INCOMPLETE" not in codes(findings)


def test_overlap_no_delta(tmp_path):
    path = write_ledger(tmp_path, make_entry(fields={"prior_cycle_overlap": "continuing"}))
    findings = ledger_check.run_checks(ledger_check.parse_ledger(ledger_check.read_text(path)))
    assert "OVERLAP_NO_DELTA" in codes(findings, "WARNING")


def test_overlap_with_delta_is_clean(tmp_path):
    path = write_ledger(tmp_path, make_entry(
        fields={"prior_cycle_overlap": "continuing (cycle delta: v2 interaction terms)"}))
    findings = ledger_check.run_checks(ledger_check.parse_ledger(ledger_check.read_text(path)))
    assert "OVERLAP_NO_DELTA" not in codes(findings)


# ---------------------------------------------------------------- --next-id

def test_next_id_missing_ledger(tmp_path):
    missing = tmp_path / "ledger.md"
    assert ledger_check.main(["--file", str(missing), "--next-id"]) == 0


def test_next_id_missing_ledger_prints_l001(tmp_path, capsys):
    missing = tmp_path / "ledger.md"
    ledger_check.main(["--file", str(missing), "--next-id"])
    assert capsys.readouterr().out.strip() == "L-001"


def test_next_id_empty_ledger(tmp_path, capsys):
    path = tmp_path / "ledger.md"
    path.write_text("", encoding="utf-8")
    ledger_check.main(["--file", str(path), "--next-id"])
    assert capsys.readouterr().out.strip() == "L-001"


def test_next_id_non_empty_ledger(tmp_path, capsys):
    path = write_ledger(tmp_path, make_entry(id_token="L-001"), make_entry(id_token="L-002", title="Second"))
    ledger_check.main(["--file", str(path), "--next-id"])
    assert capsys.readouterr().out.strip() == "L-003"


def test_next_id_uses_max_not_count(tmp_path, capsys):
    path = write_ledger(tmp_path, make_entry(id_token="L-001"), make_entry(id_token="L-005", title="Fifth"))
    ledger_check.main(["--file", str(path), "--next-id"])
    assert capsys.readouterr().out.strip() == "L-006"


def test_next_id_does_not_truncate_wide_numbers(tmp_path, capsys):
    path = write_ledger(tmp_path, make_entry(id_token="L-999"))
    ledger_check.main(["--file", str(path), "--next-id"])
    assert capsys.readouterr().out.strip() == "L-1000"


# ---------------------------------------------------------------- --json / exit codes / report

def test_json_shape(tmp_path, capsys):
    path = write_ledger(tmp_path, make_entry(fields={"status": "bogus"}))
    code = ledger_check.main(["--file", str(path), "--json"])
    assert code == 1
    data = json.loads(capsys.readouterr().out)
    assert isinstance(data, list) and len(data) >= 1
    for item in data:
        assert set(item) == {"severity", "code", "entry", "message"}
    assert any(d["code"] == "BAD_VALUE" for d in data)


def test_main_exit_zero_on_clean_ledger(tmp_path):
    path = write_ledger(tmp_path, make_entry())
    assert ledger_check.main(["--file", str(path)]) == 0


def test_main_exit_one_on_critical(tmp_path):
    path = write_ledger(tmp_path, make_entry(id_token="L001"))
    assert ledger_check.main(["--file", str(path)]) == 1


def test_main_exit_zero_when_only_warning(tmp_path):
    path = write_ledger(tmp_path, make_entry(fields={"prior_cycle_overlap": "continuing"}))
    assert ledger_check.main(["--file", str(path)]) == 0


def test_report_first_line_format(tmp_path, capsys):
    path = write_ledger(tmp_path, make_entry(fields={"status": "bogus", "prior_cycle_overlap": "continuing"}))
    ledger_check.main(["--file", str(path)])
    first_line = capsys.readouterr().out.splitlines()[0]
    assert first_line == "ledger_check: 1 CRITICAL, 1 WARNING"


# ---------------------------------------------------------------- encoding

def test_read_text_handles_utf8_bom(tmp_path):
    path = tmp_path / "ledger.md"
    path.write_bytes(b"\xef\xbb\xbf" + ledger_text(make_entry()).encode("utf-8"))
    text = ledger_check.read_text(path)
    assert text.startswith("# Ledger FY26")


def test_main_prints_text_a_windows_console_cannot_encode(tmp_path):
    import os
    import subprocess

    entry = make_entry(title="Cost model v1 → v2", omit=["audience"])
    path = write_ledger(tmp_path, entry)
    env = {**os.environ, "PYTHONIOENCODING": "cp1252"}
    run = subprocess.run(
        [sys.executable, ledger_check.__file__, "--file", str(path)],
        capture_output=True, env=env,
    )
    assert run.returncode == 0, run.stderr.decode("utf-8", "replace")
    assert "→" in run.stdout.decode("utf-8")


def findings_for(path):
    return ledger_check.run_checks(ledger_check.parse_ledger(ledger_check.read_text(path)))


def test_crlf_and_extra_spaces_in_heading_parse_clean(tmp_path):
    text = ledger_text(make_entry(id_token="L-007", title="Spaced title"))
    text = text.replace("## L-007 Spaced title", "##  L-007   Spaced title  ")
    path = tmp_path / "ledger.md"
    path.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))
    assert codes(findings_for(path)) == []


def test_blank_lines_inside_sub_lists_keep_items(tmp_path):
    entry = make_entry().replace("- numbers:\n", "- numbers:\n\n").replace("- lenses:\n", "- lenses:\n\n")
    assert codes(findings_for(write_ledger(tmp_path, entry))) == []


def test_short_and_padded_ids_count_as_duplicates(tmp_path):
    path = write_ledger(tmp_path, make_entry(id_token="L-1", title="One"), make_entry(id_token="L-001", title="Two"))
    assert "DUPLICATE_ID" in codes(findings_for(path), "CRITICAL")
