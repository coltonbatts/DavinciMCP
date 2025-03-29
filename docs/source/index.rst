Welcome to DavinciMCP's documentation!
====================================

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License: MIT

.. image:: https://img.shields.io/badge/python-3.8+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python: 3.8+

DavinciMCP is a Python interface for controlling DaVinci Resolve with support for Model Context Protocol (MCP) and Gemini AI integration.

Features
--------

- Direct control of DaVinci Resolve through its Python API
- Integration with Google's Gemini AI for intelligent video editing assistance
- Cross-platform support (macOS, Windows, Linux)
- Natural Language Processing (NLP) to translate text commands into editing operations
- Media analysis capabilities for shot detection and optimizing long takes
- Command pattern implementation for extensible operations
- Feedback mechanism to explain editing decisions
- Error handling and logging
- Modern GUI interface with timeline visualization

Installation
------------

From PyPI:

.. code-block:: bash

   pip install DavinciMCP

From source:

.. code-block:: bash

   git clone https://github.com/coltonbatts/DavinciMCP.git
   cd DavinciMCP
   pip install -e .

Quick Start
----------

After installation, use the ``davincimcp`` command:

.. code-block:: bash

   # Start GUI mode
   davincimcp gui

   # Start interactive CLI mode
   davincimcp interactive

   # Execute a command
   davincimcp cmd "Add a cross dissolve transition that's 1.5 seconds"

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   usage
   configuration
   gui

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/core
   api/commands
   api/media
   api/utils
   api/ui

.. toctree::
   :maxdepth: 1
   :caption: Development

   contributing
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search` 