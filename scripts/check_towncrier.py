from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Sequence

VERSION_ONLY_FILES = frozenset({"pyproject.toml", "uv.lock"})


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    changed_files = collect_changed_files(args.compare_with, staged=args.staged)

    if is_version_only_change(changed_files, args.compare_with, staged=args.staged):
        print("Skipping towncrier check for version-only release branch changes.")
        return 0

    return subprocess.run(
        [
            "towncrier",
            "check",
            "--compare-with",
            args.compare_with,
            *(["--staged"] if args.staged else []),
        ],
        check=False,
    ).returncode


def parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run towncrier check unless the branch only bumps release versions.",
    )
    parser.add_argument(
        "--compare-with",
        default="origin/main",
        help="Branch or ref to compare with. Defaults to origin/main.",
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Include staged files in the change set.",
    )
    return parser.parse_args(argv)


def collect_changed_files(compare_with: str, *, staged: bool) -> set[str]:
    changed_files = set(
        _run_git("diff", "--name-only", f"{compare_with}...HEAD").stdout.splitlines(),
    )
    if staged:
        changed_files.update(_run_git("diff", "--name-only", "--cached").stdout.splitlines())
    return changed_files


def is_version_only_change(
    changed_files: set[str],
    compare_with: str,
    *,
    staged: bool,
) -> bool:
    if not changed_files or not changed_files <= VERSION_ONLY_FILES:
        return False

    branch_diff = _run_git(
        "diff",
        "--unified=0",
        f"{compare_with}...HEAD",
        "--",
        *VERSION_ONLY_FILES,
    ).stdout
    staged_diff = ""
    if staged:
        staged_diff = _run_git(
            "diff",
            "--unified=0",
            "--cached",
            "--",
            *VERSION_ONLY_FILES,
        ).stdout

    return diff_only_changes_version_lines(f"{branch_diff}\n{staged_diff}")


def diff_only_changes_version_lines(diff: str) -> bool:
    changed_lines = [
        line
        for line in diff.splitlines()
        if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))
    ]
    return bool(changed_lines) and all(_is_version_line(line[1:]) for line in changed_lines)


def _is_version_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("version = ") and stripped.count('"') >= 2


def _run_git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        check=True,
        text=True,
        capture_output=True,
    )


if __name__ == "__main__":
    sys.exit(main())
