#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from wdom.options import config
from wdom.themes import theme_list, logger

theme = config.theme

if theme:
    if theme.endswith('.py'):
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
        from wdom.tag import *
else:
    # Use default
    logger.info('No theme specified. Use default theme.')
    from wdom.tag import *
    name = 'default'
    project_url = ''
    project_repository = ''
    license = ''
    license_url = ''
    css_files = []
    js_files = []
    headers = []
