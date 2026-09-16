"""Run a headless skill probe without letting it reach a real workspace.

Three guards, in order:
  1. Isolation. The arguments are checked before anything is created: a sandbox or a
     working directory inside the repository is refused, because that is the mistake
     this harness exists to prevent.
  2. Sandbox. The plugin under test is copied to a temp folder holding only
     `.claude-plugin/` and `skills/`. Pointing `--plugin-dir` at the repository
     itself is what let a skill mistake the repo for a workspace and write to it.
  3. Tripwire. The repository is fingerprinted before and after the probe. Anything
     added, changed, or removed is reported and the run exits non-zero.

The tripwire covers the worktree, the parts of `.git` that a commit moves, the names
of any checkouts under `.worktrees/`, and folders left behind empty. A probe that runs
`git add -A && git commit` leaves every worktree file byte-identical, so a tripwire
that skipped `.git` would call that clean.

The tripwire only compares paths, permission bits, and hashes. It never reads file
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
import threading
import time
from pathlib import Path

# Copied into the sandbox. Everything else in the repo stays out of it.
PLUGIN_PARTS = (".claude-plugin", "skills")

# A folder holding any of these looks like a workspace to a skill, so the
# sandbox must never contain one.
WORKSPACE_MARKERS = ("profile.md", "paypool.md", "roster.md", "ledger.md")

# Never copied into the sandbox: caches, and the repository's own history.
COPY_IGNORE = ("__pycache__", ".pytest_cache", "node_modules", ".git", ".worktrees")

# Skipped by the tripwire's worktree walk: churn that says nothing about a leak.
SNAPSHOT_SKIP_DIRS = {"__pycache__", ".pytest_cache", "node_modules"}

# Walked by hand instead of by the worktree walk, each for its own reason below.
GIT_DIR = ".git"
WORKTREES_DIR = ".worktrees"

# The parts of `.git` a commit moves. Everything else under it (objects/, logs/,
# hooks/ samples, FETCH_HEAD, ORIG_HEAD, COMMIT_EDITMSG, lock files) churns during
# ordinary reads and would drown the report without saying anything about a leak.
GIT_FILES = ("HEAD", "index", "packed-refs")
GIT_TREES = ("refs",)

# How long to wait for a killed process, and for its reader thread, to go away.
KILL_GRACE_SECONDS = 10

# The published release and the copy under test both answer to the same
# descriptions; without this the result reflects whichever the session preferred.
DISABLE_INSTALLED = {"enabledPlugins": {"acqdemo@acqdemo": False}}


def repo_root(start=None):
    """The repository to watch. A path that does not exist is a typo, not an empty repo."""
    if start is None:
        start = Path(__file__).resolve().parents[2]
    start = Path(start)
    if not start.is_dir():
        raise SystemExit(f"probe: {start} does not exist or is not a directory; check --repo")
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
        shutil.copytree(source, dest / part, ignore=shutil.ignore_patterns(*COPY_IGNORE))
    assert_no_workspace(dest)
    return dest


def fingerprint(path):
    """Hash plus permission bits, or None if the file went away mid-walk.

    Everything is hashed. A size-and-mtime shortcut for large files sounds thrifty and
    is a hole: rewriting the first bytes of a file and restoring its mtime with
    os.utime reads as untouched. A full hash of this repository takes tens of
    milliseconds.
    """
    path = Path(path)
    try:
        stat = path.stat()
    except OSError:
        return None
    mode = stat.st_mode & 0o777
    try:
        return "sha:%s:%o" % (hashlib.sha256(path.read_bytes()).hexdigest(), mode)
    except OSError:
        return "unreadable:%d:%o" % (stat.st_size, mode)


def git_snapshot(root):
    """Fingerprint the parts of `.git` a commit moves, and the commit HEAD resolves to."""
    root = Path(root)
    git = root / GIT_DIR
    state = {}
    if not git.exists():
        return state
    if git.is_file():  # a linked worktree: .git is a pointer file
        mark = fingerprint(git)
        return {GIT_DIR: mark} if mark is not None else {}
    for name in GIT_FILES:
        mark = fingerprint(git / name)
        if mark is not None:
            state[f"{GIT_DIR}/{name}"] = mark
    for tree in GIT_TREES:
        for folder, _dirs, files in os.walk(git / tree):
            for name in files:
                path = Path(folder) / name
                mark = fingerprint(path)
                if mark is not None:
                    state[path.relative_to(root).as_posix()] = mark
    head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                          capture_output=True, text=True)
    if head.returncode == 0:
        state["git:HEAD"] = "commit:" + head.stdout.strip()
    return state


def worktree_snapshot(root):
    """Name the checkouts under `.worktrees/` without walking into them.

    A worktree is a second checkout of the whole repository. Hashing one would double
    the snapshot and every ordinary edit inside it would trip the wire. What matters
    is that a probe created or removed one.
    """
    base = Path(root) / WORKTREES_DIR
    if not base.is_dir():
        return {}
    try:
        names = sorted(p.name for p in base.iterdir())
    except OSError:
        return {}
    return {f"{WORKTREES_DIR}/{name}": "worktree" for name in names}


def snapshot(root):
    """Map every watched path under `root` to a fingerprint."""
    root = Path(root)
    state = {}
    for folder, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs
                         if d not in SNAPSHOT_SKIP_DIRS and d not in (GIT_DIR, WORKTREES_DIR))
        here = Path(folder)
        if not dirs and not files and here != root:
            # os.walk reports files, so a folder created and left empty is otherwise
            # invisible. A skill that makes FY26/evidence/ and writes nothing yet is
            # still a skill that reached the repository.
            state[here.relative_to(root).as_posix() + "/"] = "empty-dir"
        for name in files:
            path = here / name
            mark = fingerprint(path)
            if mark is not None:
                state[path.relative_to(root).as_posix()] = mark
    state.update(git_snapshot(root))
    state.update(worktree_snapshot(root))
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
    """Refuse a run that could reach the repository. Called before anything is created."""
    problems = []
    if is_inside(sandbox, repo):
        problems.append(f"--plugin-dir {sandbox} is inside the repository")
    if is_inside(cwd, repo):
        problems.append(f"working directory {cwd} is inside the repository")
    if problems:
        raise SystemExit("probe: " + "; ".join(problems))


def kill_tree(proc):
    """Kill the child and anything it started.

    proc.kill() reaches only the direct child. With Bash in --allowed-tools a
    grandchild can outlive it and keep writing after the "after" snapshot is taken,
    which the tripwire would then report as clean.
    """
    if proc.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)],
                       capture_output=True)
    else:
        import signal
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except OSError:
            pass
    try:
        proc.kill()
    except OSError:
        pass


def run_prompt(prompt, sandbox, cwd, timeout=180, allowed_tools="Skill", command=None):
    """Stream one session, stopping at the first Skill call, the result, or the deadline.

    The stdout loop runs on its own thread. `for line in proc.stdout` blocks until a
    line arrives, so a deadline evaluated inside that loop never fires on a process
    that hangs before printing anything. Returns (skill, seconds).
    """
    command = list(command) if command else claude_command(sandbox, allowed_tools)
    started = time.time()
    deadline = started + timeout
    # A process group (POSIX) gives kill_tree something to aim at; on Windows
    # taskkill walks the tree by pid instead.
    extra = {} if os.name == "nt" else {"start_new_session": True}
    proc = subprocess.Popen(command + [prompt],
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                            text=True, encoding="utf-8", errors="replace",
                            cwd=str(cwd), **extra)
    found = ["none"]

    def read():
        try:
            for line in proc.stdout:
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if event.get("type") == "assistant":
                    for part in event.get("message", {}).get("content", []):
                        if part.get("type") == "tool_use" and part.get("name") == "Skill":
                            found[0] = part.get("input", {}).get("skill", "?")
                if found[0] != "none" or event.get("type") == "result":
                    return
        except (OSError, ValueError):
            return  # the pipe was closed under us once the deadline passed

    reader = threading.Thread(target=read, daemon=True)
    reader.start()
    reader.join(max(0.0, deadline - time.time()))
    kill_tree(proc)
    try:
        proc.wait(timeout=KILL_GRACE_SECONDS)
    except subprocess.TimeoutExpired:
        pass
    try:
        proc.stdout.close()
    except OSError:
        pass
    reader.join(timeout=KILL_GRACE_SECONDS)
    return found[0], time.time() - started


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
                        help="fingerprint the repository twice with no probe, to test the tripwire")
    parser.add_argument("--allowed-tools", default="Skill")
    parser.add_argument("--timeout", type=float, default=180)
    parser.add_argument("--sandbox", default=None,
                        help="where to build the plugin copy (default: a temp folder). "
                             "A path inside the repository is refused.")
    parser.add_argument("--cwd", default=None,
                        help="working directory for the probe (default: a temp folder). "
                             "A path inside the repository is refused.")
    args = parser.parse_args(argv)

    repo = repo_root(args.repo)
    sandbox = (Path(args.sandbox).resolve() if args.sandbox
               else Path(tempfile.gettempdir()) / "acq-plugin-under-test")
    cwd = (Path(args.cwd).resolve() if args.cwd
           else Path(tempfile.mkdtemp(prefix="acq-probe-ws-")))

    before = snapshot(repo)
    if not before:
        raise SystemExit(f"probe: {repo} holds no files to watch; check --repo")
    if args.check_only:
        return report_tripwire(diff_snapshots(before, snapshot(repo)), repo)

    if not args.prompt:
        parser.error("a prompt is required unless --check-only is given")

    # Before anything is created: a guard that fires after the copy is written would
    # blame the probe for the copy.
    check_isolation(repo, sandbox, cwd)
    build_sandbox(repo, sandbox)
    cwd.mkdir(parents=True, exist_ok=True)
    print(f"sandbox {sandbox}\nscratch {cwd}")

    skill, seconds = run_prompt(args.prompt, sandbox, cwd,
                                timeout=args.timeout, allowed_tools=args.allowed_tools)
    print(f"RESULT {skill} after {seconds:.1f}s")
    return report_tripwire(diff_snapshots(before, snapshot(repo)), repo)


if __name__ == "__main__":
    sys.exit(main())
