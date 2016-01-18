#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from wdom import options

logger = logging.getLogger(__name__)


def configure_logger(level=None):
    logger = logging.getLogger('wdom')

    if 'logging' not in options.config:
        options.parse_command_line()

    if level is not None:
        level = level
    elif options.config.logging:
        level = getattr(logging, options.config.logging.upper())
    else:
        level = logging.WARN
    logger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)

    from tornado.log import LogFormatter
    fmt = '%(color)s[%(levelname)1.1s:%(name)s]%(end_color)s '
    fmt += '%(message)s'
    formatter = LogFormatter(fmt=fmt)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.propagate = False
