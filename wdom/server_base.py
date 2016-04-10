#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import webbrowser

from wdom import options


def check_options():
    if (('port' not in options.config) or
            ('address' not in options.config) or
            ('browser' not in options.config)):
        options.parse_command_line()


def open_browser(url, browser):
    if browser in webbrowser._browsers:
        webbrowser.get(browser).open(url)
    else:
        webbrowser.open(url)
