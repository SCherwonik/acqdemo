"""Tests for skills/start/scripts/doc_text.py."""
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import doc_text  # noqa: E402

DOCX_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:t>Duty 1: Lead the cost estimating tool release process.</w:t></w:r></w:p>
    <w:p><w:r><w:t>Duty 2: Brief leadership on portfolio risk quarterly.</w:t></w:r></w:p>
  </w:body>
</w:document>
"""

SLIDE_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
       xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:sp>
        <p:txBody>
          <a:p><a:r><a:t>{text}</a:t></a:r></a:p>
        </p:txBody>
      </p:sp>
    </p:spTree>
  </p:cSld>
</p:sld>
"""


def build_docx(path):
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("word/document.xml", DOCX_XML)
    return path


def build_pptx(path, slide_texts):
    """slide_texts: dict of slide number -> text, e.g. {1: "...", 2: "...", 10: "..."}."""
    with zipfile.ZipFile(path, "w") as z:
        for num, text in slide_texts.items():
            z.writestr(f"ppt/slides/slide{num}.xml", SLIDE_XML.format(text=text))
    return path


# ---------------------------------------------------------------- docx

def test_extract_docx_reads_two_paragraphs(tmp_path):
    path = build_docx(tmp_path / "doc.docx")
    text = doc_text.extract_docx(path)
    assert text.splitlines() == [
        "Duty 1: Lead the cost estimating tool release process.",
        "Duty 2: Brief leadership on portfolio risk quarterly.",
    ]


def test_extract_docx_keeps_tabs_and_line_breaks(tmp_path):
    xml = DOCX_XML.replace(
        "<w:p><w:r><w:t>Duty 1: Lead the cost estimating tool release process.</w:t></w:r></w:p>",
        "<w:p><w:r><w:t>Duty 1</w:t></w:r><w:r><w:tab/></w:r><w:r><w:t>Train analysts</w:t></w:r>"
        "<w:r><w:br/></w:r><w:r><w:t>Second line</w:t></w:r></w:p>")
    path = tmp_path / "doc.docx"
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("word/document.xml", xml)
    lines = doc_text.extract_docx(path).splitlines()
    assert lines[0] == "Duty 1\tTrain analysts"
    assert lines[1] == "Second line"


def test_main_prints_docx_paragraphs(tmp_path, capsys):
    path = build_docx(tmp_path / "doc.docx")
    assert doc_text.main(["--file", str(path)]) == 0
    out = capsys.readouterr().out
    assert "Duty 1: Lead the cost estimating tool release process." in out
    assert "Duty 2: Brief leadership on portfolio risk quarterly." in out


def test_docx_bad_zip_reports_error(tmp_path, capsys):
    path = tmp_path / "doc.docx"
    path.write_bytes(b"not a zip")
    code = doc_text.main(["--file", str(path)])
    captured = capsys.readouterr()
    assert code == 2
    assert "docx" in (captured.out + captured.err).lower()


# ---------------------------------------------------------------- pptx

def test_extract_pptx_reads_slides_in_numeric_order(tmp_path):
    path = build_pptx(tmp_path / "deck.pptx", {1: "Slide one", 2: "Slide two", 10: "Slide ten"})
    text = doc_text.extract_pptx(path)
    assert text.splitlines() == ["Slide one", "Slide two", "Slide ten"]


def test_extract_pptx_keeps_tabs_and_line_breaks(tmp_path):
    xml = SLIDE_XML.replace(
        "<a:p><a:r><a:t>{text}</a:t></a:r></a:p>",
        "<a:p><a:r><a:t>Duty 1</a:t></a:r><a:r><a:tab/></a:r><a:r><a:t>Train analysts</a:t></a:r>"
        "<a:r><a:br/></a:r><a:r><a:t>Second line</a:t></a:r></a:p>",
    )
    path = tmp_path / "deck.pptx"
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("ppt/slides/slide1.xml", xml)
    lines = doc_text.extract_pptx(path).splitlines()
    assert lines[0] == "Duty 1\tTrain analysts"
    assert lines[1] == "Second line"


def test_main_prints_pptx_slide_text(tmp_path, capsys):
    path = build_pptx(tmp_path / "deck.pptx", {1: "Briefing point one", 2: "Briefing point two"})
    assert doc_text.main(["--file", str(path)]) == 0
    out = capsys.readouterr().out
    assert "Briefing point one" in out
    assert "Briefing point two" in out


def test_pptx_bad_zip_reports_error(tmp_path, capsys):
    path = tmp_path / "deck.pptx"
    path.write_bytes(b"not a zip")
    code = doc_text.main(["--file", str(path)])
    captured = capsys.readouterr()
    assert code == 2
    assert "pptx" in (captured.out + captured.err).lower()


# ---------------------------------------------------------------- txt / md passthrough

def test_txt_passthrough(tmp_path, capsys):
    path = tmp_path / "doc.txt"
    path.write_text("Duty 1: Do the thing.\nDuty 2: Do another thing.\n", encoding="utf-8")
    assert doc_text.main(["--file", str(path)]) == 0
    out = capsys.readouterr().out.replace("\r\n", "\n")
    assert out == "Duty 1: Do the thing.\nDuty 2: Do another thing.\n"


def test_md_passthrough(tmp_path, capsys):
    path = tmp_path / "doc.md"
    path.write_text("# Duties\nDuty 1: Something important.\n", encoding="utf-8")
    assert doc_text.main(["--file", str(path)]) == 0
    out = capsys.readouterr().out
    assert "Duty 1: Something important." in out


# ---------------------------------------------------------------- pdf

def test_pdf_without_pdftotext_exits_two_with_clear_message(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(doc_text, "find_pdftotext", lambda: None)
    path = tmp_path / "doc.pdf"
    path.write_bytes(b"%PDF-1.4 fake")
    code = doc_text.main(["--file", str(path)])
    captured = capsys.readouterr()
    assert code == 2
    assert "pdftotext" in (captured.out + captured.err).lower()


def test_pdf_with_pdftotext_available(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(doc_text, "find_pdftotext", lambda: "pdftotext")

    class FakeResult:
        returncode = 0
        stdout = b"Duty 1: Extracted from PDF.\n"

    def fake_run(cmd, capture_output=True):
        return FakeResult()

    monkeypatch.setattr(doc_text.subprocess, "run", fake_run)
    path = tmp_path / "doc.pdf"
    path.write_bytes(b"%PDF-1.4 fake")
    assert doc_text.main(["--file", str(path)]) == 0
    out = capsys.readouterr().out
    assert "Duty 1: Extracted from PDF." in out


def test_pdf_pages_option_passes_f_and_l_to_pdftotext(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(doc_text, "find_pdftotext", lambda: "pdftotext")
    captured_cmd = {}

    class FakeResult:
        returncode = 0
        stdout = b"Page range text.\n"

    def fake_run(cmd, capture_output=True):
        captured_cmd["cmd"] = cmd
        return FakeResult()

    monkeypatch.setattr(doc_text.subprocess, "run", fake_run)
    path = tmp_path / "doc.pdf"
    path.write_bytes(b"%PDF-1.4 fake")
    assert doc_text.main(["--file", str(path), "--pages", "2-5"]) == 0
    cmd = captured_cmd["cmd"]
    assert "-f" in cmd and "2" in cmd
    assert "-l" in cmd and "5" in cmd
    assert cmd.index("-f") < cmd.index("2")
    assert cmd.index("-l") < cmd.index("5")


def test_pages_option_rejected_for_non_pdf(tmp_path, capsys):
    path = tmp_path / "doc.txt"
    path.write_text("hello\n", encoding="utf-8")
    code = doc_text.main(["--file", str(path), "--pages", "1-2"])
    captured = capsys.readouterr()
    assert code == 2
    assert "--pages" in (captured.out + captured.err)


def test_malformed_pages_option_reports_error(tmp_path, capsys):
    path = tmp_path / "doc.pdf"
    path.write_bytes(b"%PDF-1.4 fake")
    code = doc_text.main(["--file", str(path), "--pages", "banana"])
    captured = capsys.readouterr()
    assert code == 2
    assert "--pages" in (captured.out + captured.err)


# ---------------------------------------------------------------- --out

def test_out_option_writes_file_instead_of_stdout(tmp_path, capsys):
    src = tmp_path / "doc.txt"
    src.write_bytes(b"Duty 1: Do the thing.\n")  # exact bytes: avoid platform newline translation
    out_path = tmp_path / "out.txt"
    assert doc_text.main(["--file", str(src), "--out", str(out_path)]) == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    written = out_path.read_text(encoding="utf-8").replace("\r\n", "\n")
    assert written == "Duty 1: Do the thing.\n"


# ---------------------------------------------------------------- errors

def test_missing_file_reports_error_exit_two(tmp_path, capsys):
    path = tmp_path / "missing.txt"
    code = doc_text.main(["--file", str(path)])
    captured = capsys.readouterr()
    assert code == 2
    assert "not found" in (captured.out + captured.err).lower()


def test_unsupported_extension_reports_error_exit_two(tmp_path, capsys):
    path = tmp_path / "doc.xyz"
    path.write_text("data", encoding="utf-8")
    code = doc_text.main(["--file", str(path)])
    captured = capsys.readouterr()
    assert code == 2
    assert "unsupported" in (captured.out + captured.err).lower()


def test_pdf_failure_is_reported_not_silently_empty(tmp_path, monkeypatch, capsys):
    """An encrypted or corrupt export must raise, not look like a document with no text."""
    monkeypatch.setattr(doc_text, "find_pdftotext", lambda: "pdftotext")

    class FakeResult:
        returncode = 1
        stdout = b""
        stderr = b"Command Line Error: Incorrect password"

    monkeypatch.setattr(doc_text.subprocess, "run", lambda cmd, capture_output=True: FakeResult())
    path = tmp_path / "export.pdf"
    path.write_bytes(b"%PDF-1.4 fake")
    assert doc_text.main(["--file", str(path)]) == 2
    captured = capsys.readouterr()
    message = captured.out + captured.err
    assert "Incorrect password" in message and "paste" in message


def test_docx_reads_header_and_footer_text(tmp_path):
    doc = ('<?xml version="1.0"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
           "<w:body><w:p><w:r><w:t>Body duty line</w:t></w:r></w:p></w:body></w:document>")
    header = ('<?xml version="1.0"?><w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
              "<w:p><w:r><w:t>Position Requirements Document</w:t></w:r></w:p></w:hdr>")
    footer = ('<?xml version="1.0"?><w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
              "<w:p><w:r><w:t>Page footer note</w:t></w:r></w:p></w:ftr>")
    path = tmp_path / "prd.docx"
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("word/document.xml", doc)
        z.writestr("word/header1.xml", header)
        z.writestr("word/footer1.xml", footer)
    lines = doc_text.extract_docx(path).splitlines()
    assert lines == ["Position Requirements Document", "Body duty line", "Page footer note"]
