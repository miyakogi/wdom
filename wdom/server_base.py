#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import re
import copy
import pathlib
import webbrowser

from tornado import autoreload

from wdom import options


exclude_patterns = [
    r'node_modules',
    r'__pycache__',
    r'\..*',
]
_exclude_patterns_re = []
_exclude_patterns_prev = []


def _compile_exclude_patterns():
    global _exclude_patterns_re, _exclude_patterns_prev
    if _exclude_patterns_prev == exclude_patterns:
        return
    else:
        _exclude_patterns_prev = copy.copy(exclude_patterns)
    for pat in exclude_patterns:
        _exclude_patterns_re.append(re.compile(pat))


def _is_exclude(name:str):
    return any(pat.match(name) for pat in _exclude_patterns_re)


def _add_watch_path(path:pathlib.Path):
    if _is_exclude(path.name):
        return
    elif path.is_dir():
        for f in path.iterdir():
            _add_watch_path(f)
    elif path.is_file():
        autoreload.watch(str(path))


def watch_dir(path:str):
    options.check_options('autoreload', 'debug')
    _compile_exclude_patterns()
    if options.config.autoreload or options.config.debug:
        # Add files to watch for autoreload
        p = pathlib.Path(path)
        p.resolve()
        _add_watch_path(p)


def open_browser(url, browser=None):
    if '--open-browser' in sys.argv:
        # Remove open browser to prevent making new tab on reload
        sys.argv.remove('--open-browser')
    if browser is None:
        options.check_options('browser')
        browser = options.config.browser
    if browser in webbrowser._browsers:
        webbrowser.get(browser).open(url)
    else:
        webbrowser.open(url)
