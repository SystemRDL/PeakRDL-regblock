# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('../src/'))

import datetime

# -- Project information -----------------------------------------------------

project = 'PeakRDL-regblock'
copyright = '%d, Alex Mykyta' % datetime.datetime.now().year
author = 'Alex Mykyta'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    "sphinxcontrib.wavedrom",
]
render_using_wavedrompy = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_book_theme"

html_theme_options = {
    "repository_url": "https://github.com/SystemRDL/PeakRDL-regblock",
    "path_to_docs": "docs",
    "use_download_button": False,
    "use_source_button": True,
    "use_repository_button": True,
    "use_issues_button": True,
}


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []


rst_epilog = """
.. |iERR| image:: /img/err.svg
        :width: 18px
        :class: no-scaled-link

.. |iWARN| image:: /img/warn.svg
        :width: 18px
        :class: no-scaled-link

.. |iOK| image:: /img/ok.svg
        :width: 18px
        :class: no-scaled-link

.. |NO| replace:: |iERR| Not Supported

.. |EX| replace:: |iWARN| Experimental

.. |OK| replace:: |iOK| Supported

"""
