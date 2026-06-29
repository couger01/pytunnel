from __future__ import annotations

import argparse
import sys
from pathlib import Path


def extract_release_notes(changelog: str, version: str) -> str:
    headings = (f"## [{version}]", f"## {version}")
    lines = changelog.splitlines()

    start_index: int | None = None
    for index, line in enumerate(lines):
        if line.startswith(headings):
            start_index = index + 1
            break

    if start_index is None:
        msg = f"Could not find changelog section for version {version}."
        raise ValueError(msg)

    end_index = len(lines)
    for index in range(start_index, len(lines)):
        if lines[index].startswith("## "):
            end_index = index
            break

    notes = "\n".join(lines[start_index:end_index]).strip()
    if not notes:
        msg = f"Changelog section for version {version} is empty."
        raise ValueError(msg)
    return notes + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract a Towncrier-generated changelog section for GitHub releases.",
    )
    parser.add_argument("version")
    parser.add_argument("changelog", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args(argv)

    try:
        notes = extract_release_notes(args.changelog.read_text(encoding="utf-8"), args.version)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1

    args.output.write_text(notes, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
