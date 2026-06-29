from __future__ import annotations

import sys
from importlib.metadata import version as package_version
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

project = "pytunnel"
author = "pytunnel contributors"
copyright = "2026, pytunnel contributors"  # noqa: A001
release = package_version("pytunnel")
version = release

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "pydata_sphinx_theme"
html_title = "pytunnel"
html_static_path = ["_static"]
html_theme_options = {
    "github_url": "https://github.com/ecoughlin/pytunnel",
    "navbar_align": "left",
    "show_toc_level": 2,
}

autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_typehints_format = "short"
napoleon_google_docstring = False
napoleon_numpy_docstring = True

myst_enable_extensions = [
    "colon_fence",
    "deflist",
]
