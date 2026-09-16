"""Extract plain text from a user document: Word, PowerPoint, PDF, or plain text/Markdown.

Shared by every skill in this plugin that needs to read a PRD, an appraisal
export, a briefing deck, or any other reference document a user points at.

Usage:
    python doc_text.py --file PATH [--pages N-M] [--out PATH]

Supported formats:
    .docx       reads word/document.xml directly via zipfile (no python-docx
                dependency); one paragraph (w:p) per output line.
    .pptx       reads ppt/slides/slideN.xml in slide order; one paragraph
                (a:p, a "text run group") per output line, in document order
                within each slide.
    .txt/.md    read and printed as-is.
    .pdf        via pdftotext, when available (see find_pdftotext()). Prints
                a clear error and exits 2 if pdftotext cannot be found.
                --pages N-M extracts only that page range (passed to
                pdftotext as -f N -l M), for long appraisal exports.

Prints plain text to stdout, or to --out PATH if given.
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
A_NS = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
GIT_FOR_WINDOWS_PDFTOTEXT = r"C:\Program Files\Git\mingw64\bin\pdftotext.exe"

SUPPORTED_EXTENSIONS = (".docx", ".pptx", ".txt", ".md", ".pdf")


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
        # Headers and footers carry real content in many templates, so read them too.
        names = z.namelist()
        parts = ([n for n in sorted(names) if n.startswith("word/header")]
                 + ["word/document.xml"]
                 + [n for n in sorted(names) if n.startswith("word/footer")])
        blobs = [z.read(name) for name in parts if name in names]
    paragraphs = []
    for xml_bytes in blobs:
        root = ET.fromstring(xml_bytes)
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


def _slide_number(name: str) -> int:
    """'ppt/slides/slide12.xml' -> 12, so slides sort in presentation order (not lexicographic)."""
    stem = Path(name).stem
    digits = "".join(ch for ch in stem if ch.isdigit())
    return int(digits) if digits else 0


def extract_pptx(path: Path) -> str:
    with zipfile.ZipFile(path) as z:
        slide_names = sorted(
            (n for n in z.namelist() if n.startswith("ppt/slides/slide") and n.endswith(".xml")),
            key=_slide_number,
        )
        paragraphs = []
        for name in slide_names:
            root = ET.fromstring(z.read(name))
            for p in root.iter(f"{A_NS}p"):  # one "text run group" per line, in document order
                parts = []
                for el in p.iter():
                    if el.tag == f"{A_NS}t":
                        parts.append(el.text or "")
                    elif el.tag == f"{A_NS}tab":
                        parts.append("\t")
                    elif el.tag == f"{A_NS}br":
                        parts.append("\n")
                paragraphs.append("".join(parts))
    return "\n".join(paragraphs)


def extract_pdf(path: Path, pages: tuple[int, int] | None = None, pdftotext: str | None = None) -> str | None:
    exe = pdftotext if pdftotext is not None else find_pdftotext()
    if not exe:
        return None
    cmd = [exe]
    if pages:
        start, end = pages
        cmd += ["-f", str(start), "-l", str(end)]
    cmd += [str(path), "-"]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:  # encrypted, corrupt, or page range past the end
        detail = result.stderr.decode("utf-8", "replace").strip().splitlines()
        raise RuntimeError(detail[0] if detail else f"pdftotext exited {result.returncode}")
    return result.stdout.decode("utf-8", "replace")


def parse_pages(value: str) -> tuple[int, int]:
    """Parse a '--pages N-M' value into (start, end). Raises ValueError with a clear message."""
    parts = value.split("-")
    if len(parts) == 2 and all(p.strip().isdigit() for p in parts):
        start, end = int(parts[0]), int(parts[1])
        if start >= 1 and end >= start:
            return start, end
    raise ValueError(f"--pages must look like N-M, for example 2-5 (got '{value}')")


def extract(path: Path, pages: tuple[int, int] | None = None) -> str:
    """Extract text for any supported extension. Raises ValueError with a clear, one-line message."""
    suffix = path.suffix.lower()
    if suffix == ".docx":
        try:
            return extract_docx(path)
        except (KeyError, zipfile.BadZipFile, ET.ParseError) as exc:
            raise ValueError(f"could not read '{path}' as a .docx file: {exc}") from exc
    if suffix == ".pptx":
        try:
            return extract_pptx(path)
        except (KeyError, zipfile.BadZipFile, ET.ParseError) as exc:
            raise ValueError(f"could not read '{path}' as a .pptx file: {exc}") from exc
    if suffix in (".txt", ".md"):
        return read_text(path)
    if suffix == ".pdf":
        try:
            text = extract_pdf(path, pages=pages)
        except RuntimeError as exc:
            raise ValueError(
                f"pdftotext could not read '{path}': {exc}. If the file is encrypted or scanned, "
                "paste the text instead."
            ) from exc
        if text is None:
            raise ValueError(
                "pdftotext not found. Install poppler-utils, or use Git for Windows "
                f"(expected at {GIT_FOR_WINDOWS_PDFTOTEXT}), then try again."
            )
        return text
    raise ValueError(
        f"unsupported file type '{suffix or path.name}'; use .docx, .pptx, .txt, .md, or .pdf"
    )


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", type=Path, required=True)
    ap.add_argument("--pages", help="PDF page range, e.g. 2-5 (passed to pdftotext as -f/-l); .pdf only")
    ap.add_argument("--out", type=Path, help="write extracted text here instead of stdout")
    args = ap.parse_args(argv)

    path = args.file
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2

    pages = None
    if args.pages is not None:
        if path.suffix.lower() != ".pdf":
            print("error: --pages only applies to .pdf files", file=sys.stderr)
            return 2
        try:
            pages = parse_pages(args.pages)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

    try:
        text = extract(path, pages=pages)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not text.endswith("\n"):
        text += "\n"

    if args.out:
        args.out.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
