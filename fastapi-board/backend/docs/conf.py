# Configuration file for the Sphinx documentation builder.
#
# Full list of built-in configuration values:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
# Point Sphinx at the backend package root so autodoc can import app modules
# without needing the package to be installed.
sys.path.insert(0, os.path.abspath(".."))

# Provide dummy environment variables so app.database can be imported during
# documentation builds without a real PostgreSQL server available.
os.environ.setdefault("DATABASE_URL", "postgresql://user:password@localhost:5432/boarddb")

# ---------------------------------------------------------------------------
# Project information
# ---------------------------------------------------------------------------
project = "FastAPI Board"
copyright = "2025, livinglifeincolor"
author = "livinglifeincolor"
release = "1.0.0"

# ---------------------------------------------------------------------------
# General configuration
# ---------------------------------------------------------------------------
extensions = [
    # Pull docstrings from Python source files automatically.
    "sphinx.ext.autodoc",
    # Support Google-style and NumPy-style docstrings.
    "sphinx.ext.napoleon",
    # Add "[source]" links so readers can browse the implementation.
    "sphinx.ext.viewcode",
    # Render type annotations in the signature and description sections.
    "sphinx_autodoc_typehints",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# ---------------------------------------------------------------------------
# autodoc options
# ---------------------------------------------------------------------------
# Show members in the order they appear in the source file.
autodoc_member_order = "bysource"

# Include both the class-level and __init__ docstrings for classes.
autoclass_content = "both"

# Show type annotations as part of the parameter description (not signature).
autodoc_typehints = "description"

# Do not skip members that have no docstring.
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "private-members": False,
    "show-inheritance": True,
    # Do not pull in imported FastAPI helpers — their Markdown docstrings
    # are not RST-compatible and would cause parse warnings/errors.
    "exclude-members": "Depends,HTTPException,Query,APIRouter",
}

# Suppress known harmless warnings:
#  - Pydantic v2 registers Field descriptors twice when autodoc processes them.
#  - sphinx_autodoc_typehints uses a Sphinx API scheduled for removal in v10.
suppress_warnings = [
    "app.add_directive_to_domain",  # duplicate object descriptions from Pydantic
]

# Treat 'duplicate object description' as an ignored warning (not a build error).
nitpick_ignore_regex = [
    (r".*", r"duplicate object description.*"),
]

# ---------------------------------------------------------------------------
# Napoleon settings (Google-style docstrings)
# ---------------------------------------------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_rtype = True

# ---------------------------------------------------------------------------
# HTML output options
# ---------------------------------------------------------------------------
html_theme = "furo"
html_static_path = ["_static"]

html_theme_options = {
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
}

# Displayed in the browser tab and the top of each page.
html_title = f"{project} {release} Documentation"
