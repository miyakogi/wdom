#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging

from wdom import options
from wdom.log import configure_logger

logger = logging.getLogger(__name__)

options.check_options('theme')
configure_logger()
curdir = os.path.dirname(os.path.abspath(__file__))
theme = options.config.theme
if theme:
    if theme.endswith('.py'):
        theme = theme.replace('.py', '')
    theme_list = sorted([file.replace('.py', '')
                         for file in os.listdir(curdir)
                         if not file.startswith('_')])
    if theme in theme_list:
        # import theme
        logger.info('Use theme: {}'.format(theme))
        exec('from wdom.themes.{} import *'.format(theme))
    else:
        logger.warn('Unknown theme "{}" was specified. Use default.'.format(theme))
        logger.warn('Available themes: {}'.format(', '.join(theme_list)))
        from wdom.tag import *
else:
    # Use default
    logger.info('No theme specified. Use default theme.')
    from wdom.tag import *
