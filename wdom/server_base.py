#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import webbrowser

from wdom import options


def open_browser(url, browser=None):
    if browser is None:
        options.check_options('browser')
        browser = options.config.browser
    if browser in webbrowser._browsers:
        webbrowser.get(browser).open(url)
    else:
        webbrowser.open(url)
