import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parents[2].resolve()
sys.path.insert(0, str(ROOT_DIR))

project = "neologism"
copyright = "2021, Attila Szakacs"
author = "Attila Szakacs"
release = Path(ROOT_DIR, "VERSION").read_text().rstrip()
extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}
intersphinx_disabled_domains = ["std"]

templates_path = ["_templates"]

html_theme = "sphinx_rtd_theme"
