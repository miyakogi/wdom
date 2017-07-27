#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Utility functions and constants."""

import sys
from os import path
import logging

from wdom import options

# if freezed by cx_freeze, _static and _template dirs are copied to lib dir.
if getattr(sys, 'frozen', False):
    root_dir = path.join(path.dirname(sys.executable), 'lib')
else:
    root_dir = path.dirname(path.abspath(__file__))

STATIC_DIR = path.join(root_dir, '_static')
TEMPLATE_DIR = path.join(root_dir, '_template')

"""
Include these directories when freeze your app by cx_freeze.

Example:

    from cx_Freeze import setup
    form wdom.util import INCLUDE_DIRS
    setup(..., options = {'build_exe': {'include_files': INCLUDE_DIRS}}, ...)

"""
INCLUDE_DIRS = [STATIC_DIR, TEMPLATE_DIR]


def install_asyncio() -> None:
    """Ensure that asyncio's io-loop is installed to tornado."""
    from tornado.ioloop import IOLoop
    from tornado.platform.asyncio import AsyncIOMainLoop
    if not IOLoop.initialized():
        AsyncIOMainLoop().install()


def suppress_logging() -> None:
    """Suppress log output to stdout.

    This function is intended to be used in test's setup. This function removes
    log handler of ``wdom`` logger and set NullHandler to suppress log.
    """
    options.root_logger.removeHandler(options._log_handler)
    options.root_logger.addHandler(logging.NullHandler())
