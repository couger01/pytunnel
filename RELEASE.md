# Release Policy

This project keeps `main` releasable at all times. A release is prepared in a pull
request, merged only after the generated changelog and version bump are reviewed, and
tagged on the resulting merge commit.

## Versioning policy

`pytunnel` uses Semantic Versioning. Versions have the form `MAJOR.MINOR.PATCH`:

- Increment `MAJOR` for incompatible public API changes.
- Increment `MINOR` for backward-compatible functionality.
- Increment `PATCH` for backward-compatible bug fixes, documentation corrections, and
  packaging or maintenance fixes.

Pre-release versions may use SemVer-compatible suffixes such as alpha, beta, or release
candidate versions when testing a release before marking it stable.

## Main branch policy

`main` must always represent a valid release candidate:

- All required checks must pass before merging.
- User-visible changes must include a Towncrier fragment in `newsfragments/`.
- Public API changes must be documented in `README.md` or another appropriate docs file.
- Breaking changes must use a `removal` fragment and clearly describe the migration path.
- Release-only changes must also go through pull request review.

Do not merge work that knowingly leaves packaging, tests, type checking, linting, or
release notes broken. If a follow-up is required, keep it in the same pull request or
delay the merge.

## Change fragments

Every pull request with user-visible impact should add exactly one fragment unless the
change naturally belongs in multiple changelog sections.

Fragment names should use the pull request or issue number when the change is tied to
one:

```text
<number>.<type>.md
```

For changes without a related issue or pull request number, use Towncrier's `+title`
form:

```text
+<short-title>.<type>.md
```

Supported types are documented in `newsfragments/README.md`.

Run this before requesting review:

```bash
uv run nox -s changelog
```

The draft changelog must read cleanly on its own. Reviewers should treat unclear,
duplicative, or missing fragments as release blockers.

## Preparing a release pull request

Create a release branch from the current `main`:

```bash
git switch main
git pull --ff-only
git switch -c release/<version>
```

Check the current package version:

```bash
uv version --short
```

Update the package version with `uv version`. Use an explicit version when the target is
already known:

```bash
uv version <version>
```

Or use a SemVer bump:

```bash
uv version --bump patch
uv version --bump minor
uv version --bump major
```

Build the Towncrier release notes:

```bash
uv run towncrier build --version <version>
```

This updates `CHANGELOG.md` and removes the consumed fragments. Review the changelog
before committing. Edit the source fragments and rebuild if the generated notes need
content changes.

Run the release checks:

```bash
uv run nox
```

Commit the version bump, generated changelog, lockfile changes if any, and removed
fragments:

```bash
git add pyproject.toml uv.lock CHANGELOG.md newsfragments
git commit -m "Release <version>"
```

Open a pull request titled:

```text
Release <version>
```

The release pull request should not include unrelated code changes.

## Merging and tagging

After approval and passing checks, merge the release pull request into `main`.

Tag the merge commit, not the release branch commit. First update local `main`:

```bash
git switch main
git pull --ff-only
```

Confirm that `HEAD` is the merge commit for the release pull request, then create an
annotated version tag:

```bash
git tag -a v<version> -m "Release <version>"
git push origin v<version>
```

The tag name must match the released package version with a leading `v`, for example
`v0.1.0`.

Pushing a `v<version>` tag starts the release workflow. The workflow verifies that the
tag version matches `uv version --short`, builds the package with `uv build`, extracts
the matching Towncrier section from `CHANGELOG.md`, and creates a GitHub release with
the built distributions attached.

## Post-release

After tagging:

- Confirm the tag points at the merge commit on `main`.
- Confirm `CHANGELOG.md` contains the released version.
- Confirm `newsfragments/` contains only unreleased fragments and policy files.
- Start the next development cycle from `main`.
