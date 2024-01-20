# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import sys
from unittest.mock import MagicMock
sys.modules['numpy'] = MagicMock()
sys.path.insert(0, os.path.abspath(os.path.join('..', '..')))
# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'VEGA'
copyright = '2024, LL'
author = 'LL'
release = '0.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc"]

templates_path = ['_templates']
exclude_patterns = []

autodoc_mock_imports = ["virgo", "SoapySDR", "cv2", "PySide6", "serial", "skyfield", "gnuradio"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']


html_theme_options = {

    "light_css_variables": {
        "color-brand-primary" : "black",
        "color-brand-content" : "black"
    },
    "dark_css_variables": {
        "color-brand-primary" : "white",
        "color-brand-content" : "white"
    },


    "light_logo": "logoCallistaLight.png",
    "dark_logo" : "logoCallistaDark.png",
    "sidebar_hide_name":True
}
