#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module defines options for wdom and wraps ``tornado.options``.
Do not use ``tornado.options`` directly.
"""

import sys
import logging
from argparse import ArgumentParser, Namespace
import re
from typing import Union

from tornado.log import LogFormatter

__all__ = [
    'parser',
    'config',
    'root_logger',
    'set_loglevel',
    'parse_command_line',
]

# Setup root logger
root_logger = logging.getLogger('wdom')  # Root logger
_log_handler = logging.StreamHandler()
fmt = '%(color)s[%(levelname)1.1s:%(name)s]%(end_color)s '
fmt += '%(message)s'
formatter = LogFormatter(fmt=fmt)
_log_handler.setFormatter(formatter)
root_logger.addHandler(_log_handler)
root_logger.propagate = False

# local logger
logger = logging.getLogger(__name__)

# setup argument parser
config = Namespace()
parser = ArgumentParser(prog='WDOM', argument_default=None)
parser.add_argument(
    '--logging', choices=['debug', 'info', 'warn', 'error'],
    help='Set the log level (dafualt: `info`).',
)
parser.add_argument(
    '--debug', default=False, action='store_const', const=True,
    help='Enable debug mode (dafualt: False).'
    ' Debug mode enables `--autoreload` and set the default log level `debug`.'
)
parser.add_argument(
    '--address', default='localhost',
    help='Address to run server (default: `localhost`).'
)
parser.add_argument(
    '--port', default=8888, type=int,
    help='Port to run server (defualt: 8888). If 0, use arbitrary free port.',
)
parser.add_argument(
    '--autoreload', default=False, action='store_const', const=True,
    help='Watch files and restart when any files changed (default: False).',
)
parser.add_argument(
    '--theme', default=None, type=str,
    help='Choose theme name to use with wdom.themes module.'
    ' By default (None) or unavailable name, use `wdom.tag`.'
)
parser.add_argument(
    '--auto-shutdown', default=False, action='store_const', const=True,
    help='Terminate server process when all connections (browser tabs) closed'
    ' (default: False).',
)
parser.add_argument(
    '--shutdown-wait', default=1.0, type=float,
    help='Seconds to wait until shutdown after all connections closed'
    ' when --auto-shutdown is enabled (default: 1.0 [sec]).',
)
parser.add_argument(
    '--open-browser', default=False, action='store_const', const=True,
    help='Open browser automatically (default: False).',
)
parser.add_argument(
    '--browser', default=None, help='Browser name to open.'
    ' Only affects when used with --open-browser option.'
    ' Available values are keys of `webbrowser._browsers`.'
    ' When not specified or specified invalid value, open system\'s'
    ' default browser (default: None).',
)


def level_to_int(level: Union[str, int]):
    if isinstance(level, int):
        if logging.NOTSET <= level <= logging.FATAL:
            return level
        else:
            raise ValueError('Log level must be 0 <= level <= 50,'
                             'but gat: {}'.format(level))
    elif isinstance(level, str):
        try:
            return getattr(logging, level.upper())
        except AttributeError:
            raise ValueError('Invalid log level: {}'.format(level))
    else:
        raise TypeError(
            'Log level must be int (0 ~ 50) or string,'
            'but gat type: {}'.format(type(level)))


def set_loglevel(level=None):
    if level is not None:
        lv = level_to_int(level)
    elif config.logging:
        lv = level_to_int(config.logging)
    elif config.debug:
        lv = logging.DEBUG
    else:
        lv = logging.INFO
    root_logger.setLevel(lv)
    _log_handler.setLevel(lv)


def parse_command_line():
    '''Parse command line options and set options in ``tornado.options``.'''
    import tornado.options
    _, unkown_args = parser.parse_known_args(namespace=config)
    set_loglevel()
    if unkown_args and not re.search(r'py\.test[-.0-9]*$', sys.argv[0]):
        # warn when get unknown argument
        # if run in test, skip warning since test runner adds some arguments
        logger.warning('Unknown Arguments: {}'.format(unkown_args))
        parser.print_help()
    for k, v in vars(config).items():
        if k.startswith('log'):
            tornado.options.options.__setattr__(k, v)
    return config


parse_command_line()
