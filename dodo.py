#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Doit task definitions."""

DOIT_CONFIG = {
    'default_tasks': [
        'check',
    ],
    'continue': True,
    'verbosity': 1,
    'num_process': 8,
    'par_type': 'thread',
}


def task_cleanup() -> dict:
    """Cleanup project."""
    return {
        'actions': ['make clean'],
    }


def task_flake8() -> dict:
    """Run flake8 check."""
    return {
        'actions': ['flake8 setup.py wdom tests'],
    }


def task_mypy() -> dict:
    """Run mypy check."""
    return {
        'actions': ['mypy -i wdom'],
    }


def task_pydocstyle() -> dict:
    """Run docstyle check."""
    return {
        'actions': ['pydocstyle wdom'],
    }


def task_docs() -> dict:
    """Build sphinx document."""
    return {
        'actions': ['sphinx-build -q -W -j 4 -b html docs docs/_build/html'],
    }


def task_check() -> dict:
    """Run flake8/mypy/pydocstyle/docs tasks."""
    return {
        'actions': None,
        'task_dep': ['flake8', 'mypy', 'pydocstyle', 'docs']
    }


def task_test_fast() -> dict:
    return {
        'actions': [
            'python -m unittest tests/test_*.py 2>&1',
        ],
    }


def task_test_slow() -> dict:
    return {
        'actions': [
            'python -m unittest tests/slow/test_*.py 2>&1',
        ],
    }


def task_test_server() -> dict:
    return {
        'actions': [
            'python -m unittest tests/server/test_*.py 2>&1',
        ],
    }


def task_test_browser_local() -> dict:
    return {
        'actions': [
            'python -m unittest tests/browser/local/test_*.py 2>&1',
        ],
    }


def task_test_browser_remote() -> dict:
    return {
        'actions': [
            'python -m unittest tests/browser/remote/test_*.py 2>&1',
        ],
    }


def task_test_browser_server() -> dict:
    return {
        'actions': [
            'python -m unittest tests/browser/server/test_*.py 2>&1',
        ],
    }

def task_test_pyppeteer() -> dict:
    return {
        'actions': [
            'python -m unittest tests/browser2/test_*.py 2>&1',
        ],
    }


def task_test() -> dict:
    return {
        'actions': None,
        'task_dep': [
            'test_fast',
            'test_slow',
            'test_server',
            'test_browser_local',
            'test_browser_remote',
            'test_browser_server',
            'test_pyppeteer',
        ]
    }
