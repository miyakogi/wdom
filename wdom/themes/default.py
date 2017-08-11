#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# flake8: noqa


"""Keep this module for backward compatibility."""

import re

from wdom.options import config
from wdom.themes import logger, theme_list

theme = config.theme

if theme:
    theme = re.sub(r'\.py[codx]?$', '', theme)
    if theme in theme_list:
        # import theme
        logger.info('Use theme: {}'.format(theme))
        exec('from wdom.themes.{} import *'.format(theme))
    else:
        logger.warning(
            'Unknown theme "{}" was specified. Use default.'.format(theme))
        # Remove duplicated module name (*.py and *.pyc may exists)
        logger.warning(
            'Available themes: {}'.format(', '.join(theme_list)))
        from wdom.themes import *
        name = 'default'
else:
    logger.info('No theme specified. Use default theme.')
    from wdom.themes import *
    name = 'default'
