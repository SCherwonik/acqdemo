"""Tests for skills/acqdemo-plan/scripts/plan_check.py."""
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import plan_check  # noqa: E402

JA_GOOD = """Job Achievement and/or Innovation
JA1: Lead the regression tool rebuild for the estimating branch.
KPI: 40 analysts trained by Q2, measured by attendance log.
PRD: 3, 4

JA2: Mentor two junior analysts on cost model validation.
KPI: 2 analysts certified by cycle end.
PRD: 5
"""

CT_GOOD = """Communication and/or Teamwork
CT1: Brief senior leadership monthly on portfolio status.
KPI: 12 briefings delivered, 100 percent on schedule.
PRD: 6

CT2: Coordinate with the program office on data requirements.
KPI: 4 joint reviews completed.
PRD: 7
"""

MS_GOOD = """Mission Support
MS1: Maintain the cost estimating tool release pipeline.
KPI: 6 releases shipped with zero critical defects.
PRD: 8

MS2: Track budget execution for the branch portfolio.
KPI: Reports delivered within 5 business days each quarter.
PRD: 9
"""


def plan_text(ja=None, ct=None, ms=None):
    blocks = []
    for block in (JA_GOOD if ja is None else ja, CT_GOOD if ct is None else ct, MS_GOOD if ms is None else ms):
        if block:
            blocks.append(block.strip("\n"))
    return "\n\n".join(blocks) + "\n"


def write_plan(tmp_path, text, name="Contribution Plan.txt"):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def codes(findings, severity=None):
    return [f.code for f in findings if severity is None or f.severity == severity]


def run(text, **kwargs):
    return plan_check.run_checks(text, **kwargs)


# ---------------------------------------------------------------- clean plan

def test_clean_plan_has_no_findings():
    findings = run(plan_text())
    assert findings == []


# ---------------------------------------------------------------- CRITICAL codes

def test_min_objectives_flags_factor_with_too_few():
    ja_one = """Job Achievement and/or Innovation
JA1: Lead the regression tool rebuild for the estimating branch.
KPI: 40 analysts trained by Q2, measured by attendance log.
PRD: 3, 4
"""
    findings = run(plan_text(ja=ja_one))
    critical = [f for f in findings if f.code == "MIN_OBJECTIVES"]
    assert critical and critical[0].factor == "JA"


def test_duplicate_label_flagged():
    ja_dup = """Job Achievement and/or Innovation
JA1: Lead the regression tool rebuild for the estimating branch.
KPI: 40 analysts trained by Q2, measured by attendance log.
PRD: 3, 4

JA1: Rebuild the legacy cost model validation suite.
KPI: 3 validation runs completed each quarter.
PRD: 5
"""
    findings = run(plan_text(ja=ja_dup))
    assert "DUPLICATE_LABEL" in codes(findings, "CRITICAL")
    assert "MIN_OBJECTIVES" not in codes(findings, "CRITICAL")


def test_label_factor_mismatch_flagged():
    ja_mismatch = """Job Achievement and/or Innovation
JA1: Lead the regression tool rebuild for the estimating branch.
KPI: 40 analysts trained by Q2, measured by attendance log.
PRD: 3, 4

JA2: Mentor two junior analysts on cost model validation.
KPI: 2 analysts certified by cycle end.
PRD: 5

CT9: Misfiled objective that belongs under Communication and/or Teamwork.
KPI: 3 sessions held.
PRD: 6
"""
    findings = run(plan_text(ja=ja_mismatch))
    mismatch = [f for f in findings if f.code == "LABEL_FACTOR_MISMATCH"]
    assert mismatch and "CT9" in mismatch[0].message
    assert "MIN_OBJECTIVES" not in codes(findings, "CRITICAL")
    assert "DUPLICATE_LABEL" not in codes(findings, "CRITICAL")


def test_missing_factor_flagged_when_heading_absent():
    findings = run(plan_text(ms=""))
    missing = [f for f in findings if f.code == "MISSING_FACTOR"]
    assert missing and missing[0].factor == "MS"
    assert "MIN_OBJECTIVES" not in codes(findings, "CRITICAL")


# ---------------------------------------------------------------- WARNING codes

def test_no_kpi_flagged_when_kpi_line_missing():
    ct_no_kpi = """Communication and/or Teamwork
CT1: Brief senior leadership monthly on portfolio status.
PRD: 6

CT2: Coordinate with the program office on data requirements.
KPI: 4 joint reviews completed.
PRD: 7
"""
    findings = run(plan_text(ct=ct_no_kpi))
    no_kpi = [f for f in findings if f.code == "NO_KPI"]
    assert no_kpi and "CT1" in no_kpi[0].message
    assert "NO_PRD_TIEBACK" not in codes(findings, "WARNING")


def test_kpi_not_measurable_flagged_without_digit_or_count_word():
    ja_soft_kpi = """Job Achievement and/or Innovation
JA1: Lead the regression tool rebuild for the estimating branch.
KPI: Improve analyst confidence in the new tool.
PRD: 3, 4

JA2: Mentor two junior analysts on cost model validation.
KPI: 2 analysts certified by cycle end.
PRD: 5
"""
    findings = run(plan_text(ja=ja_soft_kpi))
    assert "KPI_NOT_MEASURABLE" in codes(findings, "WARNING")
    assert "NO_KPI" not in codes(findings, "WARNING")


def test_no_prd_tieback_flagged_when_prd_line_missing():
    ms_no_prd = """Mission Support
MS1: Maintain the cost estimating tool release pipeline.
KPI: 6 releases shipped with zero critical defects.

MS2: Track budget execution for the branch portfolio.
KPI: Reports delivered within 5 business days each quarter.
PRD: 9
"""
    findings = run(plan_text(ms=ms_no_prd))
    no_prd = [f for f in findings if f.code == "NO_PRD_TIEBACK"]
    assert no_prd and "MS1" in no_prd[0].message


def test_em_dash_flagged():
    ja_em_dash = """Job Achievement and/or Innovation
JA1: Lead the regression tool rebuild — replacing the legacy spreadsheet process.
KPI: 40 analysts trained by Q2, measured by attendance log.
PRD: 3, 4

JA2: Mentor two junior analysts on cost model validation.
KPI: 2 analysts certified by cycle end.
PRD: 5
"""
    findings = run(plan_text(ja=ja_em_dash))
    assert "EM_DASH" in codes(findings, "WARNING")


# ---------------------------------------------------------------- CLI

def test_main_clean_plan_exit_zero(tmp_path):
    path = write_plan(tmp_path, plan_text())
    assert plan_check.main(["--file", str(path)]) == 0


def test_main_json_shape_and_exit_one(tmp_path, capsys):
    ja_one = """Job Achievement and/or Innovation
JA1: Lead the regression tool rebuild for the estimating branch.
KPI: 40 analysts trained by Q2, measured by attendance log.
PRD: 3, 4
"""
    path = write_plan(tmp_path, plan_text(ja=ja_one))
    code = plan_check.main(["--file", str(path), "--json"])
    data = json.loads(capsys.readouterr().out)
    assert code == 1
    assert data and all({"severity", "code", "factor", "message"} == set(d) for d in data)
    assert "MIN_OBJECTIVES" in [d["code"] for d in data]


def test_main_report_first_line(tmp_path, capsys):
    path = write_plan(tmp_path, plan_text())
    plan_check.main(["--file", str(path)])
    out = capsys.readouterr().out
    assert out.splitlines()[0] == "plan_check: 0 CRITICAL, 0 WARNING"


def test_main_min_objectives_flag_overrides_default(tmp_path):
    ja_one = """Job Achievement and/or Innovation
JA1: Lead the regression tool rebuild for the estimating branch.
KPI: 40 analysts trained by Q2, measured by attendance log.
PRD: 3, 4
"""
    path = write_plan(tmp_path, plan_text(ja=ja_one))
    assert plan_check.main(["--file", str(path)]) == 1
    assert plan_check.main(["--file", str(path), "--min-objectives", "1"]) == 0


def test_main_prints_text_a_windows_console_cannot_encode(tmp_path):
    ja_arrow = """Job Achievement and/or Innovation
JA1: Lead the regression tool rebuild for the estimating branch.
KPI: Cut turnaround time → faster estimates for the branch.
PRD: 3, 4

JA2: Mentor two junior analysts on cost model validation.
KPI: 2 analysts certified by cycle end.
PRD: 5
"""
    path = write_plan(tmp_path, plan_text(ja=ja_arrow))
    env = {**os.environ, "PYTHONIOENCODING": "cp1252"}
    run_result = subprocess.run(
        [sys.executable, plan_check.__file__, "--file", str(path)], capture_output=True, env=env
    )
    assert run_result.returncode == 0, run_result.stderr.decode("utf-8", "replace")
    assert "→" in run_result.stdout.decode("utf-8")



# ---------------------------------------------------------------- tolerant parsing (review batch 2)

def test_blank_line_between_objective_and_kpi_keeps_kpi():
    ja = JA_GOOD.replace("the estimating branch.\n", "the estimating branch.\n\n")
    assert codes(run(plan_text(ja=ja))) == []


def test_spaced_and_lowercase_labels_are_recognized():
    ja = JA_GOOD.replace("JA1:", "JA 1:").replace("JA2:", "ja2:")
    assert codes(run(plan_text(ja=ja))) == []


def test_heading_variants_match():
    text = (plan_text()
            .replace("Job Achievement and/or Innovation", "Job Achievement and Innovation")
            .replace("Communication and/or Teamwork", "COMMUNICATION AND TEAMWORK:"))
    assert codes(run(text)) == []


def test_prose_line_with_time_is_not_an_objective():
    ja = JA_GOOD.replace("PRD: 3, 4\n", "PRD: 3, 4\nat 10: 30 each Monday the team syncs.\n")
    assert codes(run(plan_text(ja=ja)), "CRITICAL") == []
