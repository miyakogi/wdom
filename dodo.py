#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def task_flake8():
    """Run flake8 check."""
    return {
        'actions': ['flake8 wdom setup.py'],
    }


def task_mypy():
    """Run mypy check."""
    return {
        'actions': ['mypy wdom'],
    }


def task_pydocstyle():
    """Run docstyle check."""
    return {
        'actions': ['pydocstyle wdom'],
    }


def task_sphinx():
    """Build sphinx document."""
    return {
        'actions': ['sphinx-build -q -W -E -b html docs docs/_build/html'],
    }
