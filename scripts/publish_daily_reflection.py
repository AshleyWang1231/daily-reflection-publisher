#!/usr/bin/env python3
"""Publish a confirmed daily reflection markdown file to a GitHub repo."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path


DEFAULT_REPO_DIR = Path(os.environ.get("DAILY_REFLECTION_REPO_DIR", "~/.daily-reflection-publisher/repo")).expanduser()


def run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    if cmd and cmd[0] == "git":
        cmd = ["git", "-c", "http.version=HTTP/1.1", *cmd[1:]]
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def fail(message: str, code: int = 1) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(code)


def validate_date(value: str) -> str:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD")
    return value


def ensure_repo(repo_url: str, repo_dir: Path) -> Path:
    if repo_dir.exists():
        if not (repo_dir / ".git").is_dir():
            fail(f"repo dir exists but is not a git repo: {repo_dir}")
        return repo_dir

    repo_dir.parent.mkdir(parents=True, exist_ok=True)
    if not remote_has_heads(repo_url):
        print(f"Remote has no branches; initializing empty repo at {repo_dir}")
        repo_dir.mkdir(parents=True, exist_ok=True)
        run(["git", "init", "-b", "main"], cwd=repo_dir)
        run(["git", "remote", "add", "origin", repo_url], cwd=repo_dir)
        return repo_dir

    print(f"Cloning {repo_url} into {repo_dir}")
    run(["git", "clone", repo_url, str(repo_dir)])
    return repo_dir


def remote_has_heads(repo_url: str) -> bool:
    result = run(["git", "ls-remote", "--heads", repo_url], check=False)
    if result.returncode != 0:
        fail(f"cannot inspect remote heads for {repo_url}:\n{result.stderr.strip()}")
    return bool(result.stdout.strip())


def ensure_clean_enough(repo_dir: Path, entry_path: Path) -> None:
    status = run(["git", "status", "--short"], cwd=repo_dir).stdout.splitlines()
    unrelated = []
    entry_rel = entry_path.as_posix()
    for line in status:
        path = line[3:] if len(line) > 3 else ""
        if path and path != entry_rel and not path.startswith(f"{entry_rel}/"):
            unrelated.append(line)
    if unrelated:
        fail(
            "repo has unrelated local changes; refusing to publish:\n"
            + "\n".join(unrelated)
        )


def list_tracked_files(repo_dir: Path) -> list[str]:
    result = run(["git", "ls-files"], cwd=repo_dir, check=False)
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line.strip()]


def choose_entry_path(repo_dir: Path, date: str, explicit_output: str | None) -> Path:
    if explicit_output:
        rel = Path(explicit_output)
        if rel.is_absolute() or ".." in rel.parts:
            fail("--output-path must be a safe repo-relative path")
        return rel

    tracked = list_tracked_files(repo_dir)
    candidates = [
        f"daily/{date}.md",
        f"logs/{date}.md",
        f"entries/{date}.md",
        f"{date}.md",
    ]
    for candidate in candidates:
        parent = Path(candidate).parent.as_posix()
        if parent == ".":
            continue
        if any(path.startswith(f"{parent}/") for path in tracked):
            return Path(candidate)

    return Path("daily") / f"{date}.md"


def get_default_branch(repo_dir: Path) -> str:
    result = run(["git", "symbolic-ref", "refs/remotes/origin/HEAD"], cwd=repo_dir, check=False)
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip().rsplit("/", 1)[-1]

    for branch in ("main", "master"):
        exists = run(["git", "rev-parse", "--verify", f"origin/{branch}"], cwd=repo_dir, check=False)
        if exists.returncode == 0:
            return branch

    current = run(["git", "branch", "--show-current"], cwd=repo_dir).stdout.strip()
    return current or "main"


def ensure_branch(repo_dir: Path) -> str:
    current = run(["git", "branch", "--show-current"], cwd=repo_dir).stdout.strip()
    if current:
        return current

    branch = get_default_branch(repo_dir)
    checkout = run(["git", "checkout", branch], cwd=repo_dir, check=False)
    if checkout.returncode != 0:
        run(["git", "checkout", "-b", branch], cwd=repo_dir)
    return branch


def has_upstream(repo_dir: Path) -> bool:
    result = run(["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], cwd=repo_dir, check=False)
    return result.returncode == 0 and bool(result.stdout.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", required=True, type=validate_date, help="Entry date in YYYY-MM-DD format")
    parser.add_argument("--input", required=True, type=Path, help="Path to the confirmed markdown entry")
    parser.add_argument(
        "--repo-url",
        default=os.environ.get("DAILY_REFLECTION_REPO_URL"),
        help="Git remote URL. Can also be set with DAILY_REFLECTION_REPO_URL.",
    )
    parser.add_argument("--repo-dir", default=DEFAULT_REPO_DIR, type=Path, help="Local clone directory")
    parser.add_argument("--output-path", help="Repo-relative markdown path. Defaults to discovered convention or daily/YYYY-MM-DD.md")
    parser.add_argument("--overwrite", action="store_true", help="Allow replacing an existing entry file")
    parser.add_argument("--no-push", action="store_true", help="Commit locally but do not push")
    parser.add_argument("--dry-run", action="store_true", help="Print planned action without writing, committing, or pushing")
    args = parser.parse_args()

    input_path = args.input.expanduser().resolve()
    if not input_path.is_file():
        fail(f"input markdown file does not exist: {input_path}")

    if not args.repo_url:
        fail(
            "missing repository URL. Pass --repo-url https://github.com/YOUR_USERNAME/YOUR_REPO.git "
            "or set DAILY_REFLECTION_REPO_URL."
        )

    content = input_path.read_text(encoding="utf-8")
    if not content.strip():
        fail("input markdown file is empty")

    repo_dir = ensure_repo(args.repo_url, args.repo_dir.expanduser().resolve())
    if remote_has_heads(args.repo_url):
        run(["git", "fetch", "--all", "--prune"], cwd=repo_dir, check=False)
    branch = ensure_branch(repo_dir)

    entry_rel = choose_entry_path(repo_dir, args.date, args.output_path)
    entry_abs = repo_dir / entry_rel

    if entry_abs.exists() and not args.overwrite:
        fail(f"entry already exists: {entry_abs}. Re-run with --overwrite only after user approval.")

    ensure_clean_enough(repo_dir, entry_rel)

    print(f"Repository: {repo_dir}")
    print(f"Branch: {branch}")
    print(f"Entry: {entry_rel.as_posix()}")
    print(f"Input: {input_path}")

    if args.dry_run:
        print("Dry run only; no files changed.")
        return 0

    entry_abs.parent.mkdir(parents=True, exist_ok=True)
    entry_abs.write_text(content.rstrip() + "\n", encoding="utf-8")

    run(["git", "add", entry_rel.as_posix()], cwd=repo_dir)
    diff_cached = run(["git", "diff", "--cached", "--quiet"], cwd=repo_dir, check=False)
    if diff_cached.returncode == 0:
        print("No changes to commit.")
        return 0

    commit_message = f"Add {args.date} daily reflection"
    run(["git", "commit", "-m", commit_message], cwd=repo_dir)

    if not args.no_push:
        if has_upstream(repo_dir):
            run(["git", "push"], cwd=repo_dir)
        else:
            run(["git", "push", "-u", "origin", branch], cwd=repo_dir)

    commit = run(["git", "rev-parse", "--short", "HEAD"], cwd=repo_dir).stdout.strip()
    print(f"Published commit: {commit}")
    print(f"Published file: {entry_abs}")
    if args.no_push:
        print("Push skipped because --no-push was set.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f"Command failed: {' '.join(exc.cmd)}", file=sys.stderr)
        if exc.stdout:
            print(exc.stdout, file=sys.stderr)
        if exc.stderr:
            print(exc.stderr, file=sys.stderr)
        raise SystemExit(exc.returncode)
