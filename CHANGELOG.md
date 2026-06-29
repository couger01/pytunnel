# Changelog

All notable changes to this project are recorded here.

<!-- towncrier release notes start -->

## [0.1.0] - 2026-06-29

### Features

- Added a native asyncio SSH tunnel API backed by AsyncSSH, including async lifecycle methods, async context manager support, and local port forwarding.
- Added a synchronous SSH tunnel API backed by Paramiko, including manual open and close methods, context manager support, and local port forwarding.
- Added shared tunnel configuration and status reporting for connected, disconnected, and lost connection states.
- Added typed package exceptions for tunnel configuration, connection, and lifecycle errors.

### Bug Fixes

- Fetched `origin/main` explicitly in the Prek CI job so `towncrier check` can compare changed files reliably.
- Made the Towncrier Prek hook compare against `origin/main` explicitly so CI does not depend on default branch detection.
- Removed the intersphinx dependency from the documentation build so warning-as-error builds do not depend on fetching external inventories.
- Restored Read the Docs to the standard Sphinx build configuration so the generated site is published through the normal Sphinx artifact path.

### Documentation

- Added Read the Docs configuration for building the Sphinx documentation site with uv-managed dependencies.
- Added a Sphinx documentation site using the PyData theme.
- Documented numpydoc as the public API docstring style and added docstrings for exported APIs.
- Documented the Semantic Versioning policy and the use of `uv version` for viewing and updating release versions.
- Documented the release policy for keeping main releasable, preparing Towncrier release notes in a pull request, and tagging the merge commit.

### Miscellaneous

- Added GitHub Actions checks for the test matrix, Prek hooks, and Sphinx documentation builds.
- Added Prek hooks for ty type checking and Towncrier fragment validation.
- Added Towncrier configuration and changelog fragment policy.
- Added a tag-triggered GitHub Actions release workflow which builds the package with `uv build`, attaches the distributions, and uses the matching Towncrier changelog section as release notes.
- Switched Prek hook configuration from `.pre-commit-config.yaml` to native `prek.toml`.
