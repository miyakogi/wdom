#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from typing import Union

from tornado.log import LogFormatter

from wdom.options import config


# Setup root logger
root_logger = logging.getLogger('wdom')  # Root logger
_log_handler = logging.StreamHandler()
fmt = '%(color)s[%(levelname)1.1s:%(name)s]%(end_color)s '
fmt += '%(message)s'
formatter = LogFormatter(fmt=fmt)
_log_handler.setFormatter(formatter)
root_logger.addHandler(_log_handler)
root_logger.propagate = False


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


def configure_logger(level=None, *args, **kwargs):
    set_loglevel(level)
