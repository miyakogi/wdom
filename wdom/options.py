#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module defines options for wdom and wraps ``tornado.options``.
Do not use ``tornado.options`` directly.
"""

from argparse import ArgumentParser
from tornado.log import define_logging_options

__all__ = [
    'parser',
    'config',
    'parse_command_line',
]


class ArgumentParser(ArgumentParser):
    def define(self, *args, **kwargs):
        '''Fake ``tornado.options.define``.'''
        arg = args[0]
        if not arg.startswith('-'):
            arg = '--' + arg
        arg = arg.replace('_', '-')
        self.add_argument(arg, *args[1:], **kwargs)

    def add_parse_callback(self, *args, **kwargs):
        '''fake method for ``tornado.options.options``'''
        pass


def parse_command_line():
    '''Parse command line options and set options in ``tornado.options``.'''
    import tornado.options
    global config
    parser.parse_known_args(namespace=config)
    for k, v in vars(config).items():
        if k.startswith('log'):
            tornado.options.options.__setattr__(k, v)
    return config


parser = ArgumentParser(prog='WDOM', argument_default=None)
config = parser.parse_args([])
define_logging_options(parser)

parser.define('--debug', default=False, action='store_const', const=True,
              help='Enable debug mode. Debug mode enables `--autoreload`'
              ' (dafualt: False).')
parser.define('--address', default='localhost',
              help='Address to run server (default: `localhost`).')
parser.define('--port', default=8888, type=int,
              help='Port to run server (defualt: 8888).'
              ' To use arbitrary free port, use 0.')
parser.define('--autoreload', default=False, action='store_const', const=True,
              help='Enable autoreload when any file changed (default: False).')
parser.define('--theme', default=None, type=str,
              help='Choose theme name to use with wdom.themes module.'
              'By default (None) or unavailable name, use `wdom.tag`.')
parser.define(
    '--auto-shutdown', default=False, action='store_const', const=True,
    help='Terminate server process when all connections (browser tabs) closed'
    ' (default: False).')
parser.define('--shutdown-wait', default=1.0, type=float,
              help='Seconds to wait for auto-shutdown when all connections'
              'closed (default: 1.0 [sec]).')
parser.define(
    '--open-browser', default=False, action='store_const', const=True,
    help='Open browser automatically (default: False).')
parser.define('--browser', default=None, help='Browser name to open.'
              ' Only affects when used with --open-browser option.'
              ' Available values are keys of `webbrowser._browsers`.'
              ' When not specified or specified invalid value, open system\'s'
              ' default browser (default: None).')
parse_command_line()
