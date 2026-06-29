from __future__ import annotations

import importlib.util
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "check_towncrier.py"
SPEC = importlib.util.spec_from_file_location("check_towncrier", SCRIPT_PATH)
assert SPEC is not None
assert SPEC.loader is not None
check_towncrier = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check_towncrier)


def test_diff_only_changes_version_lines_allows_release_version_bump() -> None:
    diff = """diff --git a/pyproject.toml b/pyproject.toml
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -7 +7 @@ name = "pytunnel"
-version = "0.1.0"
+version = "0.1.0.post1"
diff --git a/uv.lock b/uv.lock
--- a/uv.lock
+++ b/uv.lock
@@ -960 +960 @@ name = "pytunnel"
-version = "0.1.0"
+version = "0.1.0.post1"
"""

    assert check_towncrier.diff_only_changes_version_lines(diff)


def test_diff_only_changes_version_lines_rejects_non_version_changes() -> None:
    diff = """diff --git a/pyproject.toml b/pyproject.toml
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -8 +8 @@ version = "0.1.0"
-description = "Sync and async Python APIs for controlling SSH tunnels."
+description = "Updated description."
"""

    assert not check_towncrier.diff_only_changes_version_lines(diff)


def test_version_only_change_requires_only_release_version_files() -> None:
    assert {"pyproject.toml", "uv.lock"} == check_towncrier.VERSION_ONLY_FILES
