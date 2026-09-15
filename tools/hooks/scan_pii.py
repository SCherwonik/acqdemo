"""Pre-commit guard: block PII/CUI from entering git history.

Checks every staged file:
  1. Blocked paths/names (SF-50/52, appraisals, resumes, 'Important, Current Documents').
  2. Content patterns (SSN, date-of-birth labels with dates, PII/CUI banners),
     extracted from text, .pdf (via pdftotext), and .docx/.pptx/.xlsx (zip XML).
Exit 1 with findings if anything matches. Never prints the matched value itself.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

BLOCKED_PATH_PATTERNS = [
    r"important, current documents/",
    r"actual appraisal/",
    r"sf[-_ ]?50",
    r"sf[-_ ]?52",
    r"resume",
    r"salaryappraisal",
]

CONTENT_PATTERNS = {
    "SSN (###-##-####)": re.compile(r"(?<![\d-])\d{3}-\d{2}-\d{4}(?![\d-])"),
    "SSN label with digits": re.compile(r"social\s+security(\s+number)?\D{0,40}\d{9}", re.I),
    "Date of birth with date": re.compile(
        r"(date\s+of\s+birth|\bDOB\b)\D{0,60}\d{1,2}[/-]\d{1,2}[/-]\d{2,4}", re.I | re.S
    ),
    # Literals split so this file does not match its own patterns.
    "PII/CUI banner": re.compile(r"PII\s*-\s*DO NOT " + "DISTRIBUTE|CONTROLLED" + r"\s+UNCLASSIFIED", re.I),
}


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, check=True).stdout


def staged_files():
    out = git("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z")
    return [p for p in out.decode("utf-8", "replace").split("\0") if p]


GIT_FOR_WINDOWS_PDFTOTEXT = r"C:\Program Files\Git\mingw64\bin\pdftotext.exe"


def find_pdftotext():
    """pdftotext ships with Git for Windows but is only on PATH inside Git Bash."""
    exe = shutil.which("pdftotext")
    if exe:
        return exe
    if os.path.exists(GIT_FOR_WINDOWS_PDFTOTEXT):
        return GIT_FOR_WINDOWS_PDFTOTEXT
    return None


def extract_text(path, blob):
    lower = path.lower()
    if lower.endswith(".pdf"):
        exe = find_pdftotext()
        if not exe:
            return None  # cannot inspect -> caller blocks
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, "in.pdf")
            with open(src, "wb") as f:
                f.write(blob)
            res = subprocess.run([exe, src, "-"], capture_output=True)
            return res.stdout.decode("utf-8", "replace")
    if lower.endswith((".docx", ".pptx", ".xlsx")):
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, "in.zip")
            with open(src, "wb") as f:
                f.write(blob)
            try:
                with zipfile.ZipFile(src) as z:
                    parts = [n for n in z.namelist() if n.endswith(".xml")]
                    xml = " ".join(z.read(n).decode("utf-8", "replace") for n in parts)
            except zipfile.BadZipFile:
                return None
            return re.sub(r"<[^>]+>", " ", xml)
    return blob.decode("utf-8", "replace")


def main():
    findings = []
    for path in staged_files():
        norm = path.replace("\\", "/").lower()
        for pat in BLOCKED_PATH_PATTERNS:
            if re.search(pat, norm):
                findings.append(f"{path}: blocked file name/location ({pat})")
        blob = git("show", f":{path}")
        text = extract_text(path, blob)
        if text is None:
            findings.append(f"{path}: could not inspect contents (install pdftotext or remove file)")
            continue
        for label, rx in CONTENT_PATTERNS.items():
            if rx.search(text):
                findings.append(f"{path}: contains {label}")
    if findings:
        print("PII GUARD: commit blocked. Remove these files from the commit:")
        for f in findings:
            print("  - " + f)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
