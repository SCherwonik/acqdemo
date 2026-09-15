"""Tests for skills/acqdemo-harvest/scripts/calendar_harvest.py."""
import codecs
import sys
from datetime import date, datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import calendar_harvest as ch  # noqa: E402

SINCE, UNTIL = date(2025, 10, 1), date(2026, 9, 30)

EXPORT = (
    "Subject\tStart\t\n"
    "Estimating working group\tTue 10/14/2025 10:00 AM\t\n"
    "Canceled: Branch staff meeting\tMon 12/8/2025 11:00 AM\t\n"
    "Updated: Estimating Working Group\tTue 11/11/2025 10:00 AM\t\n"
    "Regression tool demo for program office\tThu 3/12/2026 1:30 PM\t\n"
    "Old kickoff\tTue 3/19/2024 2:00 PM\t\n"
    "Broken line with no date\t\t\n"
    "estimating working group\tTue 12/9/2025 10:00 AM\t\n"
)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("Tue 3/19/2024 2:00 PM", datetime(2024, 3, 19, 14, 0)),
        ("3/19/2024 2:00 PM", datetime(2024, 3, 19, 14, 0)),
        ("Tue 3/19/2024 14:00", datetime(2024, 3, 19, 14, 0)),
        ("2024-03-19 14:00", datetime(2024, 3, 19, 14, 0)),
        ("3/19/2024", datetime(2024, 3, 19)),
        ("  Tue   3/19/2024   2:00 PM ", datetime(2024, 3, 19, 14, 0)),
        ("next Tuesday", None),
    ],
)
def test_parse_start_formats(value, expected):
    assert ch.parse_start(value) == expected


def test_harvest_filters_canceled_outside_and_unparsed():
    result = ch.harvest(EXPORT, SINCE, UNTIL)
    assert len(result.meetings) == 4
    assert result.canceled == 1
    assert result.outside == 1
    assert len(result.unparsed) == 1
    assert [m.start.date() for m in result.meetings] == sorted(m.start.date() for m in result.meetings)


def test_header_with_extra_columns_in_any_order():
    text = "Location\tStart\tSubject\nRoom 1\t10/20/2025 9:00 AM\tDesign review\n"
    result = ch.harvest(text, SINCE, UNTIL)
    assert [(m.subject, m.start) for m in result.meetings] == [("Design review", datetime(2025, 10, 20, 9, 0))]


def test_no_header_assumes_subject_then_start():
    text = "Design review\t10/20/2025 9:00 AM\n"
    assert ch.harvest(text, SINCE, UNTIL).meetings[0].subject == "Design review"


def test_recurring_groups_prefixes_and_case():
    series = ch.recurring(ch.harvest(EXPORT, SINCE, UNTIL).meetings)
    assert len(series) == 1
    name, count, first, last = series[0]
    assert count == 3
    assert name.lower() == "estimating working group"
    assert (first, last) == (date(2025, 10, 14), date(2025, 12, 9))


def test_read_text_handles_utf16_and_cp1252(tmp_path):
    utf16 = tmp_path / "u16.txt"
    utf16.write_bytes(codecs.BOM_UTF16_LE + "Subject\tStart\n".encode("utf-16-le"))
    assert ch.read_text(utf16).startswith("Subject")
    cp = tmp_path / "cp.txt"
    cp.write_bytes("Director’s sync\t10/20/2025 9:00 AM\n".encode("cp1252"))
    assert "Director’s sync" in ch.read_text(cp)


def test_render_markdown_sections():
    result = ch.harvest(EXPORT, SINCE, UNTIL)
    md = ch.render_markdown(result, SINCE, UNTIL)
    assert md.startswith("# Calendar harvest: 2025-10-01 to 2026-09-30")
    assert "- Meetings in period: 4" in md
    assert "- Canceled (skipped): 1" in md
    assert "| Occurrences |" in md
    assert "### 2025-10 (1)" in md and "### 2026-03 (1)" in md
    assert "- 2026-03-12 13:30 Regression tool demo for program office" in md
    assert md.index("### 2025-10") < md.index("### 2026-03")


def test_render_markdown_without_series():
    result = ch.harvest("Subject\tStart\nOne-off\t10/20/2025 9:00 AM\n", SINCE, UNTIL)
    assert "## Recurring series (2 or more)\n- None." in ch.render_markdown(result, SINCE, UNTIL)


def test_main_writes_file_and_missing_file(tmp_path, capsys):
    source = tmp_path / "calendar.txt"
    source.write_text(EXPORT, encoding="utf-8")
    out = tmp_path / "harvest" / "calendar.md"
    assert ch.main(["--file", str(source), "--since", "2025-10-01", "--until", "2026-09-30", "--out", str(out)]) == 0
    assert "4 meetings in period, 1 recurring series" in capsys.readouterr().out
    assert out.exists()
    assert ch.main(["--file", str(tmp_path / "nope.txt"), "--since", "2025-10-01", "--until", "2026-09-30"]) == 2


def test_main_prints_text_a_windows_console_cannot_encode(tmp_path):
    import os
    import subprocess
    source = tmp_path / "export.txt"
    source.write_text("Subject\tStart\t\nSync → review\tTue 10/14/2025 10:00 AM\t\n", encoding="utf-8")
    env = {**os.environ, "PYTHONIOENCODING": "cp1252"}
    run = subprocess.run([sys.executable, ch.__file__, "--file", str(source),
                          "--since", "2025-10-01", "--until", "2026-09-30"], capture_output=True, env=env)
    assert run.returncode == 0, run.stderr.decode("utf-8", "replace")
    assert "Sync → review" in run.stdout.decode("utf-8")
