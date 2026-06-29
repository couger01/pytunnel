from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "extract_towncrier_release_notes.py"
SPEC = importlib.util.spec_from_file_location("extract_towncrier_release_notes", SCRIPT_PATH)
assert SPEC is not None
assert SPEC.loader is not None
release_notes = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release_notes)


def test_extract_release_notes_for_bracketed_towncrier_heading() -> None:
    changelog = """# Changelog

<!-- towncrier release notes start -->

## [0.2.0] - 2026-06-28

### Features

- Added release automation.

## [0.1.0] - 2026-06-01

### Features

- Added initial API.
"""

    notes = release_notes.extract_release_notes(changelog, "0.2.0")

    assert notes == "### Features\n\n- Added release automation.\n"


def test_extract_release_notes_fails_when_version_is_missing() -> None:
    with pytest.raises(ValueError, match=r"0\.3\.0"):
        release_notes.extract_release_notes("# Changelog\n", "0.3.0")


def test_extract_release_notes_fails_when_section_is_empty() -> None:
    changelog = """# Changelog

## [0.2.0] - 2026-06-28

## [0.1.0] - 2026-06-01
"""

    with pytest.raises(ValueError, match="empty"):
        release_notes.extract_release_notes(changelog, "0.2.0")
