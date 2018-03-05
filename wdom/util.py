#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Utility functions and constants."""

import sys
from os import path
import logging

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
    pass
    # from tornado.ioloop import IOLoop
    # from tornado.platform.asyncio import AsyncIOMainLoop
    # if not IOLoop.initialized():
    #     AsyncIOMainLoop().install()


def suppress_logging() -> None:
    """Suppress log output to stdout.

    This function is intended to be used in test's setup. This function removes
    log handler of ``wdom`` logger and set NullHandler to suppress log.
    """
    from wdom import options
    options.root_logger.removeHandler(options._log_handler)
    options.root_logger.addHandler(logging.NullHandler())


def reset() -> None:
    """Reset all wdom objects.

    This function clear all connections, elements, and resistered custom
    elements. This function also makes new document/application and set them.
    """
    from wdom.document import get_new_document, set_document
    from wdom.element import Element
    from wdom.server import _tornado
    from wdom.window import customElements

    set_document(get_new_document())
    _tornado.connections.clear()
    _tornado.set_application(_tornado.Application())
    Element._elements_with_id.clear()
    Element._element_buffer.clear()
    customElements.reset()
