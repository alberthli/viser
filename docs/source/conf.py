# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/stable/config

import os
from typing import Dict, List

import viser

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#

# -- Project information -----------------------------------------------------

project = "viser"
copyright = "2024"
author = "brentyi"

version: str = os.environ.get("VISER_VERSION_STR_OVERRIDE", viser.__version__)

# Formatting!
#     0.1.30 => v0.1.30
#     dev => dev
if not version.isalpha():
    version = "v" + version

# The full version, including alpha/beta/rc tags
release = ""


# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.mathjax",
    "sphinx.ext.githubpages",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    # "sphinx.ext.inheritance_diagram",
    "sphinx.ext.viewcode",
    "sphinxcontrib.programoutput",
    "sphinxcontrib.ansi",
    "sphinxcontrib.googleanalytics",  # google analytics extension https://github.com/sphinx-contrib/googleanalytics/tree/master
]
programoutput_use_ansi = True
html_ansi_stylesheet = "black-on-white.css"

# Intersphinx mapping for cross-references to external documentation
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", (None, "python-inv.txt"))
}
html_static_path = ["_static"]
html_theme_options = {
    "light_css_variables": {
        "color-code-background": "#f4f4f4",
        "color-code-foreground": "#000",
    },
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/nerfstudio-project/viser",
            "html": """
            <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
            </svg>
        """,
            "class": "",
        },
    ],
    "light_logo": "logo.svg",
    "dark_logo": "logo.svg",
}

# Pull documentation types from hints
autodoc_typehints = "both"
autodoc_class_signature = "separated"
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "undoc-members": True,
    "inherited-members": True,
    "exclude-members": "__init__, __post_init__",
    "imported-members": True,
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
source_suffix = ".rst"
# source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language: str = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path .
exclude_patterns: List[str] = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "default"


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"
html_title = "viser"


# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ["_static"]

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
# html_sidebars = {}


# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "viser_doc"


# -- Options for Github output ------------------------------------------------

sphinx_to_github = True
sphinx_to_github_verbose = True
sphinx_to_github_encoding = "utf-8"


# -- Options for LaTeX output ------------------------------------------------

latex_elements: Dict[str, str] = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',
    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        master_doc,
        "viser.tex",
        "viser",
        "brentyi",
        "manual",
    ),
]


# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, "viser", "viser documentation", [author], 1)]


# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "viser",
        "viser",
        author,
        "viser",
        "viser",
        "Miscellaneous",
    ),
]


# -- Extension configuration --------------------------------------------------

# Google Analytics ID
googleanalytics_id = "G-RRGY51J5ZH"

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# -- Setup function ----------------------------------------


def skip_dict_methods(app, what, name, obj, skip, options):
    """Skip inherited dict methods when documenting TypedDict classes."""
    # List of dict methods to exclude from TypedDict documentation
    dict_methods = {
        "__new__",
        "__init__",
        "__delitem__",
        "__getitem__",
        "__iter__",
        "__len__",
        "__setitem__",
        "clear",
        "copy",
        "fromkeys",
        "get",
        "items",
        "keys",
        "pop",
        "popitem",
        "setdefault",
        "update",
        "values",
        "__contains__",
        "__delattr__",
        "__dir__",
        "__eq__",
        "__format__",
        "__ge__",
        "__getattribute__",
        "__gt__",
        "__hash__",
        "__le__",
        "__lt__",
        "__ne__",
        "__reduce__",
        "__reduce_ex__",
        "__repr__",
        "__setattr__",
        "__sizeof__",
        "__str__",
        "__subclasshook__",
    }

    if what == "class" and name in dict_methods:
        return True
    return skip


def setup(app):
    app.add_css_file("css/custom.css")
    app.connect("autodoc-skip-member", skip_dict_methods)


# -- Napoleon settings -------------------------------------------------------

# Settings for parsing non-sphinx style docstrings. We use Google style in this
# project.
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True
napoleon_type_aliases = None
napoleon_attr_annotations = True
