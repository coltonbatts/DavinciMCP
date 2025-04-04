#!/usr/bin/env python3
"""
Setup script for DavinciMCP package.
"""

from setuptools import setup, find_packages
import os

# Read the contents of README.md
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

# Read requirements from requirements.txt
with open("requirements.txt", encoding="utf-8") as f:
    requirements = f.read().splitlines()

# Development dependencies
dev_requirements = [
    'pytest>=7.0.0',
    'pytest-mock>=3.10.0',
    'pytest-cov>=4.1.0',
    'black>=23.0.0',
    'isort>=5.12.0',
    'flake8>=6.1.0',
    'mypy>=1.5.0',
    'pre-commit>=3.5.0',
    'sphinx>=7.0.0',
    'sphinx-rtd-theme>=1.3.0',
]

setup(
    name="DavinciMCP",
    version="0.1.0",
    description="Python interface for controlling DaVinci Resolve with Gemini AI integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Colton Batts",
    author_email="coltonbatts@gmail.com",
    url="https://github.com/coltonbatts/DavinciMCP",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        'dev': dev_requirements,
        'docs': ['sphinx>=7.0.0', 'sphinx-rtd-theme>=1.3.0'],
        'test': ['pytest>=7.0.0', 'pytest-mock>=3.10.0', 'pytest-cov>=4.1.0'],
    },
    entry_points={
        "console_scripts": [
            "davincimcp=davincimcp.cli:main",
        ],
    },
) 