"""Mirror this private workspace into the public repo, minus personal content.

Usage (from the private workspace root):
    python tools/sync/sync_public.py --dst "C:/path/to/public/clone" [--dry-run]

What gets mirrored:
  * Only files tracked by git in the source repo. Ignored files (SF-50s, appraisals,
    resumes) are never candidates.
  * Minus paths matched by tools/sync/personal-paths.txt (gitignore-like globs).
  * Text files have personal blocks removed, marker lines included. A block starts with a
    line that is only a START marker and ends with a line that is only an END marker, written
    as an HTML comment (Markdown) or a '#' comment (code/config). See README for syntax.

Safety:
  * Every output file is scanned for terms in tools/sync/denylist.txt (whole word,
    case-insensitive) and for PII patterns from tools/hooks/scan_pii.py.
    Any finding aborts BEFORE anything is written.
  * Files tracked in the destination that are not in the new set are deleted (true mirror).
  * The script never commits. Review and commit in the public clone yourself.
"""
from __future__ import annotations

import argparse
import fnmatch
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_SRC = HERE.parent.parent
sys.path.insert(0, str(HERE.parent / "hooks"))
import scan_pii  # noqa: E402

PATHS_FILE = "tools/sync/personal-paths.txt"
DENY_FILE = "tools/sync/denylist.txt"
ALWAYS_EXCLUDE = [PATHS_FILE, DENY_FILE]
MARKER_START = "PERSONAL" + ":START"
MARKER_END = "PERSONAL" + ":END"
# A marker counts only when it is the whole line: "<!-- X -->" or "# X".
_MARKER_LINE = r"^\s*(?:<!--\s*{m}\s*-->|#\s*{m})\s*$"
START_LINE = re.compile(_MARKER_LINE.format(m=re.escape(MARKER_START)))
END_LINE = re.compile(_MARKER_LINE.format(m=re.escape(MARKER_END)))
FENCE_LINE = re.compile(r"^\s*(```|~~~)")


@dataclass
class Item:
    rel: str
    data: bytes
    stripped_blocks: int = 0


def git_ls_files(root: Path) -> list[str]:
    out = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"], capture_output=True, check=True
    ).stdout
    return sorted(p for p in out.decode("utf-8").split("\0") if p)


def load_list(path: Path) -> list[str]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    return [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")]


def is_excluded(rel: str, patterns: list[str]) -> bool:
    rel = rel.replace("\\", "/")
    low = rel.lower()
    if low in (p.lower() for p in ALWAYS_EXCLUDE):
        return True
    name = low.rsplit("/", 1)[-1]
    parts = low.split("/")[:-1]
    dir_prefixes = ["/".join(parts[: k + 1]) for k in range(len(parts))]
    for pat in patterns:
        p = pat.replace("\\", "/").lower()
        anchored = p.startswith("/")  # "/name" matches only at the repo root
        p = p.lstrip("/")
        if p.endswith("/"):
            if any(fnmatch.fnmatchcase(d, p[:-1]) for d in dir_prefixes):
                return True
        elif anchored or "/" in p:
            if fnmatch.fnmatchcase(low, p):
                return True
        elif fnmatch.fnmatchcase(name, p):
            return True
    return False


def strip_personal(text: str) -> tuple[str, int]:
    kept: list[str] = []
    in_block = False
    in_fence = False
    blocks = 0
    for line in text.splitlines(keepends=True):
        # Markers inside fenced code blocks are examples, not markers.
        if not in_block and FENCE_LINE.match(line):
            in_fence = not in_fence
            kept.append(line)
            continue
        if in_fence:
            kept.append(line)
            continue
        if START_LINE.match(line):
            if in_block:
                raise ValueError("nested personal block")
            in_block = True
            continue
        if END_LINE.match(line):
            if not in_block:
                raise ValueError("personal block end without start")
            in_block = False
            blocks += 1
            continue
        if not in_block:
            kept.append(line)
    if in_block:
        raise ValueError("unterminated personal block")
    out = "".join(kept)
    if blocks:
        out = re.sub(r"\n{3,}", "\n\n", out)
    return out, blocks


def as_text(data: bytes) -> str | None:
    if b"\0" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def build(src: Path) -> list[Item]:
    patterns = load_list(src / PATHS_FILE)
    items: list[Item] = []
    for rel in git_ls_files(src):
        if is_excluded(rel, patterns):
            continue
        data = (src / rel).read_bytes()
        text = as_text(data)
        blocks = 0
        if text is not None and (MARKER_START in text or MARKER_END in text):
            try:
                stripped, blocks = strip_personal(text)
            except ValueError as exc:
                raise ValueError(f"{rel}: {exc}") from exc
            data = stripped.encode("utf-8")
        items.append(Item(rel=rel, data=data, stripped_blocks=blocks))
    return items


def compile_terms(terms: list[str]) -> list[tuple[str, re.Pattern]]:
    return [
        (t, re.compile(r"(?<![A-Za-z0-9])" + re.escape(t) + r"(?![A-Za-z0-9])", re.I))
        for t in terms
    ]


def scan(items: list[Item], deny_terms: list[str]) -> list[str]:
    findings: list[str] = []
    compiled = compile_terms(deny_terms)
    for item in items:
        for pat in scan_pii.BLOCKED_PATH_PATTERNS:
            if re.search(pat, item.rel.lower()):
                findings.append(f"{item.rel}: blocked file name/location ({pat})")
        text = scan_pii.extract_text(item.rel, item.data)
        if text is None:
            findings.append(f"{item.rel}: could not inspect contents")
            continue
        for label, rx in scan_pii.CONTENT_PATTERNS.items():
            if rx.search(text):
                findings.append(f"{item.rel}: contains {label}")
        for term, rx in compiled:
            if rx.search(text):
                findings.append(f"{item.rel}: contains denylisted term '{term}'")
    return findings


def write(items: list[Item], dst: Path, dry_run: bool) -> tuple[list[str], list[str]]:
    wanted = {i.rel for i in items}
    changed: list[str] = []
    for item in items:
        target = dst / item.rel
        if target.exists() and target.read_bytes() == item.data:
            continue
        changed.append(item.rel)
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(item.data)
    deleted = [rel for rel in git_ls_files(dst) if rel not in wanted]
    if not dry_run:
        for rel in deleted:
            (dst / rel).unlink(missing_ok=True)
    return changed, deleted


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", type=Path, default=DEFAULT_SRC, help="private workspace root")
    ap.add_argument("--dst", type=Path, required=True, help="public repo clone root")
    ap.add_argument("--dry-run", action="store_true", help="report only, write nothing")
    args = ap.parse_args(argv)

    src, dst = args.src.resolve(), args.dst.resolve()
    if src == dst:
        print("sync: --src and --dst must differ")
        return 2
    if not (dst / ".git").exists():
        print(f"sync: {dst} is not a git clone")
        return 2

    try:
        items = build(src)
    except ValueError as exc:
        print(f"sync: {exc}")
        return 1

    findings = scan(items, load_list(src / DENY_FILE))
    if findings:
        print("sync: ABORTED, nothing written. Fix these in the private workspace:")
        for f in findings:
            print(f"  - {f}")
        return 1

    changed, deleted = write(items, dst, args.dry_run)
    mode = "DRY RUN" if args.dry_run else "SYNCED"
    stripped = [i.rel for i in items if i.stripped_blocks]
    print(f"sync: {mode}: {len(items)} files in mirror, {len(changed)} written, {len(deleted)} deleted")
    for rel in changed:
        print(f"  write  {rel}")
    for rel in deleted:
        print(f"  delete {rel}")
    for rel in stripped:
        print(f"  strip  {rel} (personal blocks removed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
