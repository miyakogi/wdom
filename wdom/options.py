#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module defines options for wdom and wraps ``tornado.options``.
Do not use ``tornado.options`` directly.
"""

from argparse import ArgumentParser, SUPPRESS
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


parser = ArgumentParser(prog='WDOM', argument_default=None)
config = parser.parse_args([])
define_logging_options(parser)

parser.define('--debug', default=False, action='store_const', const=True)
parser.define('--address', default='localhost')
parser.define('--port', default=8888)
parser.define('--autoreload', default=False, action='store_const', const=True)
parser.define('--theme', default=None)
parser.define('--temptheme', default=None, help='Only for internal use.')

parser.define('-b', default=SUPPRESS, nargs='*',
              help='Fake option for sphinx-build.')
parser.define('-d', default=SUPPRESS, nargs='*',
              help='Fake option for sphinx-build.')
parser.define('-s', default=SUPPRESS, nargs='?',
              help='Fake option for pytest.')
parser.define('-v', default=SUPPRESS, nargs='?',
              help='Fake option for pytest.')
parser.define('--junitxml', default=SUPPRESS, help='Fake option for pytest.')
parser.define('--cov', default=SUPPRESS, help='Fake option for pytest-cov.')
parser.define('--cov-report', default=SUPPRESS,
              help='Fake option for pytest-cov.')


def parse_command_line(*args, **kwargs):
    '''Parse command line options and set options in ``tornado.options``.'''
    import tornado.options
    global config
    config = parser.parse_args()
    for k, v in vars(config).items():
        if k.startswith('log'):
            tornado.options.options.__setattr__(k, v)


if __name__ == '__main__':
    config.log_rotate_mode = 'size'
    config.logging
    parse_command_line()
