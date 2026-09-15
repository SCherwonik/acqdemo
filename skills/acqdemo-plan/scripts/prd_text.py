"""Extract plain text from a Position Requirements Document (PRD).

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
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
GIT_FOR_WINDOWS_PDFTOTEXT = r"C:\Program Files\Git\mingw64\bin\pdftotext.exe"


def find_pdftotext() -> str | None:
    """pdftotext ships with Git for Windows but is only on PATH inside Git Bash."""
    exe = shutil.which("pdftotext")
    if exe:
        return exe
    if os.path.exists(GIT_FOR_WINDOWS_PDFTOTEXT):
        return GIT_FOR_WINDOWS_PDFTOTEXT
    return None


def read_text(path: Path) -> str:
    data = path.read_bytes()
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return data.decode("cp1252", errors="replace")


def extract_docx(path: Path) -> str:
    with zipfile.ZipFile(path) as z:
        xml_bytes = z.read("word/document.xml")
    root = ET.fromstring(xml_bytes)
    paragraphs = []
    for p in root.iter(f"{W_NS}p"):
        parts = []
        for el in p.iter():  # document order, so tabs and breaks land between the right runs
            if el.tag == f"{W_NS}t":
                parts.append(el.text or "")
            elif el.tag == f"{W_NS}tab":
                parts.append("\t")
            elif el.tag in (f"{W_NS}br", f"{W_NS}cr"):
                parts.append("\n")
        paragraphs.append("".join(parts))
    return "\n".join(paragraphs)


def extract_pdf(path: Path) -> str | None:
    exe = find_pdftotext()
    if not exe:
        return None
    result = subprocess.run([exe, str(path), "-"], capture_output=True)
    return result.stdout.decode("utf-8", "replace")


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
