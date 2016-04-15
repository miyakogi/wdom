#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import logging

from wdom.options import config
from wdom.log import configure_logger

logger = logging.getLogger(__name__)

configure_logger()
curdir = os.path.dirname(os.path.abspath(__file__))
theme = config.theme
if theme:
    if theme.endswith('.py'):
        theme = re.sub(r'\.py[codx]?$', '', theme)
    theme_list = [re.sub(r'\.py[codx]?$', '', file)
                  for file in os.listdir(curdir)
                  if not file.startswith('_')]
    if theme in theme_list:
        # import theme
        logger.info('Use theme: {}'.format(theme))
        exec('from wdom.themes.{} import *'.format(theme))
    else:
        logger.warn(
            'Unknown theme "{}" was specified. Use default.'.format(theme))
        # Remove duplicated module name (*.py and *.pyc may exists)
        logger.warn(
            'Available themes: {}'.format(', '.join(sorted(set(theme_list)))))
        from wdom.tag import *
else:
    # Use default
    logger.info('No theme specified. Use default theme.')
    from wdom.tag import *
