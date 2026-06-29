# Changelog Policy

`pytunnel` uses Towncrier to build `CHANGELOG.md` from small news fragments.

## Fragment names

Add one fragment for every user-visible change:

```text
<issue-or-pr-number>.<type>.md
```

Use the GitHub issue or pull request number when the change is tied to one.

For changes that do not have a related issue or pull request number yet, use Towncrier's
`+title` form:

```text
+<short-title>.<type>.md
```

The title should be lowercase, hyphen-separated, and stable enough to identify the
fragment during review. Towncrier will render these fragments without an issue link.

Supported fragment types:

- `feature`: new functionality or public API additions
- `bugfix`: bug fixes and behavior corrections
- `doc`: documentation-only changes
- `removal`: removed functionality or breaking removals
- `misc`: maintenance changes that users may still care about

Examples:

```text
42.feature.md
108.bugfix.md
203.doc.md
+release-policy.doc.md
+tooling-cleanup.misc.md
```

## Fragment content

Write fragments as a concise changelog sentence in past tense or imperative release-note
style. Do not include headings, issue numbers, or bullet markers; Towncrier adds those.

Good:

```text
Added async SSH tunnel support backed by AsyncSSH.
```

Avoid:

```text
- #42 Added async SSH tunnel support.
```

## Release preview

Preview the generated changelog:

```bash
uv run nox -s changelog
```

See `RELEASE.md` for the full release process, including generating release notes from a
release pull request and tagging the merge commit.
