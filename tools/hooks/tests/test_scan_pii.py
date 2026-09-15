"""Tests for tools/hooks/scan_pii.py (pre-commit PII guard).

All sensitive-looking values are assembled at runtime so this file itself
never matches the scanner's patterns.
"""
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

HOOKS = Path(__file__).resolve().parents[1]
SCANNER = HOOKS / "scan_pii.py"
sys.path.insert(0, str(HOOKS))
import scan_pii  # noqa: E402

FAKE_SSN = "123" + "-45-" + "6789"
FAKE_DOB = "Date of " + "Birth:\n 01/02/1990"
FAKE_BANNER = "PII - DO NOT " + "DISTRIBUTE"


def make_pdf(text: str) -> bytes:
    stream = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode()
    objs = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = b"%PDF-1.4\n"
    offsets = []
    for i, obj in enumerate(objs, 1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode() + obj + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode()
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode()
    out += f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    return out


def make_docx(text: str) -> bytes:
    import io

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("word/document.xml", f"<w:document><w:t>{text}</w:t></w:document>")
    return buf.getvalue()


def run_scanner(repo: Path, files: dict) -> subprocess.CompletedProcess:
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    for rel, content in files.items():
        f = repo / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    return subprocess.run(
        [sys.executable, str(SCANNER)], cwd=repo, capture_output=True, text=True
    )


def test_clean_text_passes(tmp_path):
    res = run_scanner(tmp_path, {"notes.txt": "hello world\n"})
    assert res.returncode == 0, res.stdout


@pytest.mark.parametrize(
    "files, expect",
    [
        ({"a.txt": f"id {FAKE_SSN}\n"}, "SSN"),
        ({"b.txt": FAKE_DOB}, "Date of birth"),
        ({"c.md": f"header {FAKE_BANNER}\n"}, "banner"),
        ({"d.docx": make_docx(f"number {FAKE_SSN}")}, "SSN"),
        ({"2026 SF-50 notes.txt": "harmless\n"}, "blocked file name"),
        ({"Important, Current Documents/x.txt": "harmless\n"}, "blocked file name"),
        ({"my_resume.txt": "harmless\n"}, "blocked file name"),
    ],
)
def test_sensitive_content_or_names_block(tmp_path, files, expect):
    res = run_scanner(tmp_path, files)
    assert res.returncode == 1
    assert expect.lower() in res.stdout.lower()


@pytest.mark.skipif(scan_pii.find_pdftotext() is None, reason="pdftotext not installed")
def test_pdf_with_ssn_blocks(tmp_path):
    res = run_scanner(tmp_path, {"doc.pdf": make_pdf(f"ID {FAKE_SSN}")})
    assert res.returncode == 1
    assert "SSN" in res.stdout


@pytest.mark.skipif(scan_pii.find_pdftotext() is None, reason="pdftotext not installed")
def test_clean_pdf_passes(tmp_path):
    res = run_scanner(tmp_path, {"doc.pdf": make_pdf("Factor descriptors")})
    assert res.returncode == 0, res.stdout


def test_scanner_source_does_not_match_itself():
    text = SCANNER.read_text(encoding="utf-8")
    for label, rx in scan_pii.CONTENT_PATTERNS.items():
        assert not rx.search(text), f"scan_pii.py matches its own pattern: {label}"
