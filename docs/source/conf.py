import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

project = 'ufs_plot_utils'
copyright = '2026, Chan-Hoo Jeon'
author = 'Chan-Hoo Jeon'
release = '1.0.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'myst_parser',
    'sphinxcontrib.mermaid',
]

autosummary_generate = True
napoleon_google_docstring = True
napoleon_numpy_docstring = False

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
