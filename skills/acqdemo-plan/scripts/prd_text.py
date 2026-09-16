"""Extract plain text from a Position Requirements Document (PRD).

Thin wrapper around the shared document reader at
``../acqdemo/scripts/doc_text.py`` (loaded by file path, since these are
plain scripts, not an importable package) so there is one implementation of
docx/pptx/pdf/text extraction shared across skills. This module keeps its
own CLI and error messages for backward compatibility.

Usage:
    python prd_text.py --file PATH

Supported formats:
    .docx       reads word/document.xml directly via zipfile (no python-docx
                dependency); one paragraph (w:p) per output line.
    .txt/.md    read and printed as-is.
    .pdf        via pdftotext, when available (see find_pdftotext()). Prints
                a clear error and exits 2 if pdftotext cannot be found.

Prints plain text, one paragraph per line.
"""
from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

_DOC_TEXT_PATH = Path(__file__).resolve().parents[2] / "acqdemo" / "scripts" / "doc_text.py"
_spec = importlib.util.spec_from_file_location("acqdemo_doc_text", _DOC_TEXT_PATH)
_doc_text = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_doc_text)

GIT_FOR_WINDOWS_PDFTOTEXT = _doc_text.GIT_FOR_WINDOWS_PDFTOTEXT
find_pdftotext = _doc_text.find_pdftotext
read_text = _doc_text.read_text
extract_docx = _doc_text.extract_docx


def extract_pdf(path: Path) -> str | None:
    # Resolved through this module's own find_pdftotext (a module-level name,
    # not a hardcoded reference), so tests can monkeypatch prd_text.find_pdftotext.
    exe = find_pdftotext()
    if not exe:
        return None
    return _doc_text.extract_pdf(path, pdftotext=exe)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", type=Path, required=True)
    args = ap.parse_args(argv)

    path = args.file
    if not path.exists():
        print(f"error: PRD file not found: {path}", file=sys.stderr)
        return 2

    suffix = path.suffix.lower()
    if suffix == ".docx":
        try:
            text = extract_docx(path)
        except (KeyError, zipfile.BadZipFile, ET.ParseError) as exc:
            print(f"error: could not read '{path}' as a .docx file: {exc}", file=sys.stderr)
            return 2
        print(text)
    elif suffix in (".txt", ".md"):
        text = read_text(path)
        print(text, end="" if text.endswith("\n") else "\n")
    elif suffix == ".pdf":
        text = extract_pdf(path)
        if text is None:
            print(
                "error: pdftotext not found. Install poppler-utils, or use Git for Windows "
                f"(expected at {GIT_FOR_WINDOWS_PDFTOTEXT}), then try again.",
                file=sys.stderr,
            )
            return 2
        print(text, end="" if text.endswith("\n") else "\n")
    else:
        print(f"error: unsupported PRD file type '{suffix or path.name}'; use .docx, .txt, .md, or .pdf",
              file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
