#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Doit task definitions."""

DOIT_CONFIG = {
    'default_tasks': [
        'flake8',
        'mypy',
        'pydocstyle',
        'sphinx',
    ],
    'continue': True,
    'verbosity': 1,
    'num_process': 4,
    'par_type': 'thread',
}


def task_flake8():  # type: ignore
    """Run flake8 check."""
    return {
        'actions': ['flake8 wdom setup.py'],
    }


def task_mypy():   # type: ignore
    """Run mypy check."""
    return {
        'actions': ['mypy wdom'],
    }


def task_pydocstyle():   # type: ignore
    """Run docstyle check."""
    return {
        'actions': ['pydocstyle wdom'],
    }


def task_sphinx():   # type: ignore
    """Build sphinx document."""
    return {
        'actions': ['sphinx-build -q -W -E -b html docs docs/_build/html'],
    }
