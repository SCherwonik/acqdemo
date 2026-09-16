"""Run a headless skill probe without letting it reach a real workspace.

Three guards, in order:
  1. Sandbox. The plugin under test is copied to a temp folder holding only
     `.claude-plugin/` and `skills/`. Pointing `--plugin-dir` at the repository
     itself is what let a skill mistake the repo for a workspace and write to it.
  2. Scratch cwd. Every probe runs in a throwaway temp folder, never in the repo.
  3. Tripwire. The repository is hashed before and after the probe. Anything
     added, changed, or removed is reported and the run exits non-zero.

The tripwire only compares paths, sizes, and hashes. It never reads file
contents for meaning, never judges what a file is for, and never deletes.

Usage:
  python tools/probe/run_probe.py "Where am I in the AcqDemo cycle?"
  python tools/probe/run_probe.py --check-only
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# Copied into the sandbox. Everything else in the repo stays out of it.
PLUGIN_PARTS = (".claude-plugin", "skills")

# A folder holding any of these looks like a workspace to a skill, so the
# sandbox must never contain one.
WORKSPACE_MARKERS = ("profile.md", "paypool.md", "roster.md", "ledger.md")

# Skipped by the tripwire: churn that says nothing about a leak.
SNAPSHOT_SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".worktrees", "node_modules"}

# Above this size, compare size and mtime instead of hashing (PDFs, exports).
HASH_LIMIT_BYTES = 1 << 20

# The published release and the copy under test both answer to the same
# descriptions; without this the result reflects whichever the session preferred.
DISABLE_INSTALLED = {"enabledPlugins": {"acqdemo@acqdemo": False}}


def repo_root(start=None):
    start = Path(start or Path(__file__).resolve().parents[2])
    out = subprocess.run(["git", "-C", str(start), "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True)
    if out.returncode:
        return start
    return Path(out.stdout.strip())


def is_inside(path, parent):
    try:
        Path(path).resolve().relative_to(Path(parent).resolve())
        return True
    except ValueError:
        return False


def root_workspace_markers(folder):
    """Marker files sitting at the top of `folder`, which is what a skill reads as a workspace.

    Skill templates and the persona examples carry these names several folders
    down and are fine; only the top level fools the workspace search.
    """
    folder = Path(folder)
    return sorted(p.name for p in folder.iterdir() if p.is_file() and p.name in WORKSPACE_MARKERS)


def assert_no_workspace(folder):
    """Stop before launch if the folder a skill will see looks like a workspace."""
    strays = root_workspace_markers(folder)
    if strays:
        raise SystemExit("probe: %s contains workspace files, refusing to run: %s"
                         % (folder, ", ".join(strays)))


def build_sandbox(repo, dest):
    """Copy just the plugin out of `repo` into `dest`. Raise if a workspace follows it."""
    repo, dest = Path(repo), Path(dest)
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    for part in PLUGIN_PARTS:
        source = repo / part
        if not source.exists():
            raise SystemExit(f"probe: {source} is missing; is {repo} the plugin repository?")
        shutil.copytree(source, dest / part,
                        ignore=shutil.ignore_patterns(*SNAPSHOT_SKIP_DIRS))
    assert_no_workspace(dest)
    return dest


def snapshot(root):
    """Map every file under `root` to a fingerprint. Large files use size and mtime."""
    root = Path(root)
    state = {}
    for folder, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SNAPSHOT_SKIP_DIRS]
        for name in files:
            path = Path(folder) / name
            try:
                stat = path.stat()
            except OSError:
                continue
            key = path.relative_to(root).as_posix()
            if stat.st_size > HASH_LIMIT_BYTES:
                state[key] = f"big:{stat.st_size}:{stat.st_mtime_ns}"
                continue
            try:
                state[key] = "sha:" + hashlib.sha256(path.read_bytes()).hexdigest()
            except OSError:
                state[key] = f"unreadable:{stat.st_size}"
    return state


def diff_snapshots(before, after):
    added = sorted(k for k in after if k not in before)
    removed = sorted(k for k in before if k not in after)
    changed = sorted(k for k in after if k in before and before[k] != after[k])
    return {"added": added, "changed": changed, "removed": removed}


def claude_command(sandbox, allowed_tools="Skill", extra=()):
    return [shutil.which("claude") or "claude", "-p",
            "--plugin-dir", str(sandbox),
            "--settings", json.dumps(DISABLE_INSTALLED),
            "--allowedTools", allowed_tools,
            "--no-session-persistence",
            "--output-format", "stream-json", "--verbose", *extra]


def check_isolation(repo, sandbox, cwd):
    """Refuse a run that could reach the repository."""
    problems = []
    if is_inside(sandbox, repo):
        problems.append(f"--plugin-dir {sandbox} is inside the repository")
    if is_inside(cwd, repo):
        problems.append(f"working directory {cwd} is inside the repository")
    if problems:
        raise SystemExit("probe: " + "; ".join(problems))


def run_prompt(prompt, sandbox, cwd, timeout=180, allowed_tools="Skill"):
    """Stream one session, stopping at the first Skill call. Returns (skill, seconds)."""
    started = time.time()
    proc = subprocess.Popen(claude_command(sandbox, allowed_tools) + [prompt],
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                            text=True, encoding="utf-8", errors="replace", cwd=str(cwd))
    result = "none"
    for line in proc.stdout:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "assistant":
            for part in event.get("message", {}).get("content", []):
                if part.get("type") == "tool_use" and part.get("name") == "Skill":
                    result = part.get("input", {}).get("skill", "?")
        if result != "none" or event.get("type") == "result" or time.time() - started > timeout:
            break
    proc.kill()
    return result, time.time() - started


def report_tripwire(changes, repo):
    if not any(changes.values()):
        print(f"tripwire clean: {repo} untouched")
        return 0
    print(f"TRIPWIRE: the probe reached {repo}. Nothing was deleted; review and revert by hand.")
    for label in ("added", "changed", "removed"):
        for key in changes[label]:
            print(f"  {label:8} {key}")
    print("  revert with: git -C \"%s\" status" % repo)
    return 2


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("prompt", nargs="?", help="prompt to send")
    parser.add_argument("--repo", default=None, help="plugin repository (default: this one)")
    parser.add_argument("--check-only", action="store_true",
                        help="hash the repository twice with no probe, to test the tripwire")
    parser.add_argument("--allowed-tools", default="Skill")
    parser.add_argument("--timeout", type=float, default=180)
    args = parser.parse_args(argv)

    repo = repo_root(args.repo)
    sandbox = Path(tempfile.gettempdir()) / "acq-plugin-under-test"
    cwd = Path(tempfile.mkdtemp(prefix="acq-probe-ws-"))

    before = snapshot(repo)
    if args.check_only:
        return report_tripwire(diff_snapshots(before, snapshot(repo)), repo)

    if not args.prompt:
        parser.error("a prompt is required unless --check-only is given")

    build_sandbox(repo, sandbox)
    check_isolation(repo, sandbox, cwd)
    print(f"sandbox {sandbox}\nscratch {cwd}")

    skill, seconds = run_prompt(args.prompt, sandbox, cwd,
                                timeout=args.timeout, allowed_tools=args.allowed_tools)
    print(f"RESULT {skill} after {seconds:.1f}s")
    return report_tripwire(diff_snapshots(before, snapshot(repo)), repo)


if __name__ == "__main__":
    sys.exit(main())
