"""Tests for skills/plan/scripts/prd_text.py."""
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import prd_text  # noqa: E402

DOCX_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:t>Duty 1: Lead the cost estimating tool release process.</w:t></w:r></w:p>
    <w:p><w:r><w:t>Duty 2: Brief leadership on portfolio risk quarterly.</w:t></w:r></w:p>
  </w:body>
</w:document>
"""


def build_docx(path):
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("word/document.xml", DOCX_XML)
    return path


# ---------------------------------------------------------------- docx

def test_extract_docx_reads_two_paragraphs(tmp_path):
    path = build_docx(tmp_path / "prd.docx")
    text = prd_text.extract_docx(path)
    assert text.splitlines() == [
        "Duty 1: Lead the cost estimating tool release process.",
        "Duty 2: Brief leadership on portfolio risk quarterly.",
    ]


def test_main_prints_docx_paragraphs(tmp_path, capsys):
    path = build_docx(tmp_path / "prd.docx")
    assert prd_text.main(["--file", str(path)]) == 0
    out = capsys.readouterr().out
    assert "Duty 1: Lead the cost estimating tool release process." in out
    assert "Duty 2: Brief leadership on portfolio risk quarterly." in out


# ---------------------------------------------------------------- txt / md passthrough

def test_txt_passthrough(tmp_path, capsys):
    path = tmp_path / "prd.txt"
    path.write_text("Duty 1: Do the thing.\nDuty 2: Do another thing.\n", encoding="utf-8")
    assert prd_text.main(["--file", str(path)]) == 0
    out = capsys.readouterr().out.replace("\r\n", "\n")
    assert out == "Duty 1: Do the thing.\nDuty 2: Do another thing.\n"


def test_md_passthrough(tmp_path, capsys):
    path = tmp_path / "prd.md"
    path.write_text("# Duties\nDuty 1: Something important.\n", encoding="utf-8")
    assert prd_text.main(["--file", str(path)]) == 0
    out = capsys.readouterr().out
    assert "Duty 1: Something important." in out


# ---------------------------------------------------------------- pdf

def test_pdf_without_pdftotext_exits_two_with_clear_message(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(prd_text, "find_pdftotext", lambda: None)
    path = tmp_path / "prd.pdf"
    path.write_bytes(b"%PDF-1.4 fake")
    code = prd_text.main(["--file", str(path)])
    captured = capsys.readouterr()
    assert code == 2
    assert "pdftotext" in (captured.out + captured.err).lower()


def test_pdf_with_pdftotext_available(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(prd_text, "find_pdftotext", lambda: "pdftotext")

    class FakeResult:
        returncode = 0
        stdout = b"Duty 1: Extracted from PDF.\n"

    def fake_run(cmd, capture_output=True):
        return FakeResult()

    monkeypatch.setattr(prd_text.subprocess, "run", fake_run)
    path = tmp_path / "prd.pdf"
    path.write_bytes(b"%PDF-1.4 fake")
    assert prd_text.main(["--file", str(path)]) == 0
    out = capsys.readouterr().out
    assert "Duty 1: Extracted from PDF." in out


# ---------------------------------------------------------------- errors

def test_missing_file_reports_error_exit_two(tmp_path, capsys):
    path = tmp_path / "missing.txt"
    code = prd_text.main(["--file", str(path)])
    captured = capsys.readouterr()
    assert code == 2
    assert "not found" in (captured.out + captured.err).lower()


def test_unsupported_extension_reports_error_exit_two(tmp_path, capsys):
    path = tmp_path / "prd.xyz"
    path.write_text("data", encoding="utf-8")
    code = prd_text.main(["--file", str(path)])
    captured = capsys.readouterr()
    assert code == 2
    assert "unsupported" in (captured.out + captured.err).lower()



def test_extract_docx_keeps_tabs_and_line_breaks(tmp_path):
    xml = DOCX_XML.replace(
        "<w:p><w:r><w:t>Duty 1: Lead the cost estimating tool release process.</w:t></w:r></w:p>",
        "<w:p><w:r><w:t>Duty 1</w:t></w:r><w:r><w:tab/></w:r><w:r><w:t>Train analysts</w:t></w:r>"
        "<w:r><w:br/></w:r><w:r><w:t>Second line</w:t></w:r></w:p>")
    path = tmp_path / "prd.docx"
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("word/document.xml", xml)
    lines = prd_text.extract_docx(path).splitlines()
    assert lines[0] == "Duty 1\tTrain analysts"
    assert lines[1] == "Second line"
