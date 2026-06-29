# Development

Install dependencies:

```bash
uv sync --group dev
```

Run all default nox checks:

```bash
uv run nox
```

Run individual checks:

```bash
uv run nox -s lint
uv run nox -s typecheck
uv run nox -s docs
uv run nox -s changelog
uv run nox -s tests
```

Build the documentation site:

```bash
uv run nox -s docs
```

## Documentation Style

Public API docstrings use the numpydoc style. Use NumPy-style sections such as
`Parameters`, `Returns`, and `Raises` for exported classes, functions, methods, and
properties. The Sphinx configuration parses these docstrings with Napoleon's NumPy
docstring support.

Preview changelog fragments:

```bash
uv run nox -s changelog
```

Install pre-commit hooks with `prek`:

```bash
uv run prek install
```

The test matrix in `noxfile.py` targets Python 3.10 through Python 3.15.

```{include} ../newsfragments/README.md
```
