import sys
from importlib.metadata import version as _package_version
from pathlib import Path

ROOT_DIR = Path(__file__).parents[2].resolve()
sys.path.insert(0, str(ROOT_DIR))

project = "neologism"
copyright = "2021-2026, Attila Szakacs"
author = "Attila Szakacs"
release = _package_version("neologism")
extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
    "networkx": ("https://networkx.org/documentation/stable/", None),
}
intersphinx_disabled_domains = ["std"]

templates_path = ["_templates"]

html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "navigation_depth": 3,
    "collapse_navigation": False,
}

doctest_global_setup = """
from neologism import DCFG, Rule
"""
